#!/usr/bin/env python3
"""
03_auditoria_blobs_huerfanos.py

Audita ~/.ollama/models/blobs distinguiendo:
  - Blobs EN USO: referenciados por algún manifest de `manifests/` o
    `manifests-v2/`, resolviendo recursivamente manifest lists
    (application/vnd.ollama.manifest.list.v2+json) y symlinks.
  - Blobs HUÉRFANOS: no referenciados por ningún manifest. Son restos de
    modelos desinstalados / descargas canceladas (en Ollama < 0.40 no hay
    `ollama prune` que los elimine).

IMPORTANTE: no se usa el tamaño como criterio de duplicado. Dos blobs con el
mismo tamaño pero hash distinto son contenido distinto (p. ej. los tensores
individuales de un modelo safetensors/MLX: muchos pesan exactamente lo mismo)
y borrarlos rompería el modelo. Solo se eliminan blobs NO referenciados.

Uso:
    python3 03_auditoria_blobs_huerfanos.py             # dry-run (solo informe)
    python3 03_auditoria_blobs_huerfanos.py --delete    # borra huérfanos (pide confirmación)
    python3 03_auditoria_blobs_huerfanos.py --delete --yes
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

MODELS_DIR = Path.home() / ".ollama" / "models"
BLOBS_DIR = MODELS_DIR / "blobs"
MANIFEST_DIRS = [MODELS_DIR / "manifests", MODELS_DIR / "manifests-v2"]
METADATA_DIR = MODELS_DIR / "metadata"

MANIFEST_MEDIA_TYPES = (
    "application/vnd.ollama.manifest.list.v2+json",
    "application/vnd.docker.distribution.manifest.v2+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.oci.image.index.v1+json",
)


def digest_to_blob_name(digest):
    """sha256:abc... -> sha256-abc... (nombre de archivo en blobs/)."""
    return digest.replace(":", "-")


def blob_size(path):
    try:
        return path.stat().st_size
    except OSError:
        return 0


def human(size_bytes):
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.2f} {unit}"
        size /= 1024


def collect_referenced_blobs():
    """Recorre todos los manifests.

    Devuelve (referenced, missing_layers, warnings):
      - referenced: nombres de blob en uso.
      - missing_layers: digests de config/layers ausentes (estado roto).
      - warnings: variantes de manifest no descargadas (normal: p. ej. un
        manifest list ofrece mlx y gguf y solo se instaló uno).
    """
    referenced = set()
    missing_layers = set()
    warnings = []
    visited = set()

    def walk_manifest(path):
        real = Path(os.path.realpath(path))
        key = str(real)
        if key in visited:
            return
        visited.add(key)

        # El propio archivo de manifest es un blob (los de manifests-v2 son
        # symlinks a blobs/sha256-...).
        if real.name.startswith("sha256-"):
            referenced.add(real.name)

        try:
            data = json.loads(real.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            warnings.append(f"No se pudo leer {path}: {exc}")
            return

        entries = []
        config = data.get("config")
        if isinstance(config, dict):
            entries.append(config)
        entries.extend(data.get("layers") or [])
        entries.extend(data.get("manifests") or [])

        for entry in entries:
            digest = entry.get("digest")
            if not digest:
                continue
            blob_name = digest_to_blob_name(digest)
            referenced.add(blob_name)
            blob_path = BLOBS_DIR / blob_name
            if entry.get("mediaType") in MANIFEST_MEDIA_TYPES:
                if blob_path.is_file():
                    walk_manifest(blob_path)
                else:
                    warnings.append(
                        f"Variante no descargada: {blob_name} (desde {real.name})"
                    )
            elif not blob_path.is_file():
                missing_layers.add(blob_name)

    for directory in MANIFEST_DIRS:
        if not directory.is_dir():
            continue
        for root, _dirs, files in os.walk(directory):
            for name in files:
                walk_manifest(Path(root) / name)
    return referenced, missing_layers, warnings


def metadata_blobs():
    """Blobs con metadata propia (modelos locales cargados/creados)."""
    if not METADATA_DIR.is_dir():
        return set()
    return {p.name[:-len(".json")] for p in METADATA_DIR.glob("sha256-*.json")}


def blobs_in_use_by_processes():
    """Blobs que procesos vivos tienen abiertos (llama-server --model ...)."""
    protected = set()
    try:
        out = subprocess.run(
            ["ps", "-Axo", "command"], capture_output=True, text=True, check=False
        ).stdout
    except OSError:
        return protected
    for line in out.splitlines():
        if "--model" not in line:
            continue
        parts = line.split()
        for index, part in enumerate(parts):
            if part == "--model" and index + 1 < len(parts):
                protected.add(Path(parts[index + 1]).name)
    return protected


def list_blobs():
    if not BLOBS_DIR.is_dir():
        return {}
    return {p.name: p for p in BLOBS_DIR.iterdir() if p.is_file()}


def build_plan():
    referenced, missing_layers, warnings = collect_referenced_blobs()
    metadata = metadata_blobs()

    all_blobs = list_blobs()
    protected = blobs_in_use_by_processes() | metadata

    orphans = [name for name in all_blobs if name not in referenced]
    kept = []
    skipped_in_use = []
    skipped_metadata = []
    for name in orphans:
        if name in metadata:
            skipped_metadata.append(name)
        elif name in protected:
            skipped_in_use.append(name)
        else:
            kept.append(name)

    kept.sort(key=lambda n: blob_size(all_blobs[n]), reverse=True)
    return {
        "referenced": referenced,
        "all_blobs": all_blobs,
        "orphans": kept,
        "skipped_in_use": skipped_in_use,
        "skipped_metadata": skipped_metadata,
        "missing": sorted(missing_layers),
        "warnings": warnings,
    }


def print_report(plan):
    all_blobs = plan["all_blobs"]
    referenced_present = [n for n in plan["referenced"] if n in all_blobs]
    referenced_bytes = sum(blob_size(all_blobs[n]) for n in referenced_present)
    orphan_bytes = sum(blob_size(all_blobs[n]) for n in plan["orphans"])
    total_bytes = sum(blob_size(p) for p in all_blobs.values())

    print("=" * 68)
    print(" AUDITORÍA DE BLOBS DE OLLAMA")
    print("=" * 68)
    print(f" Blobs en disco ................ {len(all_blobs):>5}  ({human(total_bytes)})")
    print(f" Blobs referenciados por manifests {len(referenced_present):>5}  ({human(referenced_bytes)})")
    print(f" Blobs huérfanos (borrables) .... {len(plan['orphans']):>5}  ({human(orphan_bytes)})")
    if plan["skipped_in_use"]:
        print(f" Huérfanos protegidos (en uso) .. {len(plan['skipped_in_use']):>5}")
    if plan["skipped_metadata"]:
        print(f" Blobs con metadata local ....... {len(plan['skipped_metadata']):>5}")
    print()

    if plan["warnings"]:
        print(" AVISOS:")
        for warning in plan["warnings"]:
            print(f"   - {warning}")
        print()

    print(" TOP 20 HUÉRFANOS MÁS GRANDES:")
    for name in plan["orphans"][:20]:
        print(f"   {human(blob_size(all_blobs[name])):>10}  {name}")
    if len(plan["orphans"]) > 20:
        print(f"   ... y {len(plan['orphans']) - 20} más")
    print()
    print(f" ESPACIO RECUPERABLE: {human(orphan_bytes)} "
          f"({orphan_bytes / (1024 ** 3):.2f} GB)")
    print()
    return orphan_bytes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delete", action="store_true",
                        help="Elimina los blobs huérfanos (por defecto solo informa)")
    parser.add_argument("--yes", action="store_true",
                        help="No pedir confirmación interactiva con --delete")
    args = parser.parse_args()

    plan = build_plan()
    orphan_bytes = print_report(plan)

    if plan["missing"]:
        print("❌ ABORTADO: hay blobs referenciados que no existen en disco. "
              "El estado es inconsistente; no se borrará nada.")
        for name in plan["missing"][:10]:
            print(f"   - falta {name}")
        return 1

    if not plan["orphans"]:
        print("✅ No hay blobs huérfanos que eliminar.")
        return 0

    if not args.delete:
        print("ℹ️  Modo dry-run. Para eliminar los huérfanos:")
        print("     python3 03_auditoria_blobs_huerfanos.py --delete")
        return 0

    if not args.yes:
        total = len(plan["orphans"])
        answer = input(f"¿Eliminar {total} blobs huérfanos ({human(orphan_bytes)})? "
                       "Escribe 'si' para continuar: ")
        if answer.strip().lower() != "si":
            print("❌ Operación cancelada.")
            return 1

    deleted = 0
    freed = 0
    for name in plan["orphans"]:
        path = plan["all_blobs"][name]
        size = blob_size(path)
        try:
            path.unlink()
        except OSError as exc:
            print(f"  ✗ {name}: {exc}")
            continue
        deleted += 1
        freed += size
    print(f"\n✅ Eliminados {deleted} blobs. Liberados {human(freed)} "
          f"({freed / (1024 ** 3):.2f} GB).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
