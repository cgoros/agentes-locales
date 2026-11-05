#!/usr/bin/env python3
"""
⚠️  OBSOLETO COMO DETECTOR DE DUPLICADOS — SOLO INFORMATIVO.

Este script agrupa los blobs por TAMAÑO de archivo. En Ollama cada blob se
identifica por el SHA256 de su contenido, así que dos blobs con el mismo
tamaño pero hash distinto son contenido DISTINTO (por ejemplo, los tensores
individuales de un modelo safetensors/MLX: cientos de ellos pesan exactamente
lo mismo). Los grupos que este script marca como "duplicados" NO son
borrables: eliminar esos blobs rompe los modelos.

Para saber qué se puede borrar de verdad usa:
    python3 scripts/03_auditoria_blobs_huerfanos.py
"""

import os
import sys
import hashlib
from collections import defaultdict

def get_blob_size(filepath):
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0

def get_file_hash(filepath, chunk_size=8192):
    try:
        hasher = hashlib.md5()
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, OSError):
        return None

def analyze_blobs(blobs_dir, report_file=None):
    print(f"=== ANÁLISIS DE DUPLICADOS EN {blobs_dir} ===")
    print("⚠️  AVISO: agrupa por TAMAÑO; estos grupos NO son duplicados reales.")
    print("   No borres estos blobs. Usa scripts/03_auditoria_blobs_huerfanos.py")
    print()
    
    if not os.path.exists(blobs_dir):
        print(f"❌ Directorio no existe: {blobs_dir}")
        return False
    
    blobs_by_size = defaultdict(list)
    blobs_by_hash = defaultdict(list)
    total_files = 0
    total_size = 0
    gguf_files = []
    
    print("📊 Escaneando blobs...")
    
    for root, dirs, files in os.walk(blobs_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            size = get_blob_size(filepath)
            
            if size > 0:
                total_files += 1
                total_size += size
                blobs_by_size[size].append(filepath)
                if size > 100 * 1024 * 1024:
                    file_hash = get_file_hash(filepath)
                    if file_hash:
                        blobs_by_hash[file_hash].append(filepath)
                if filename.endswith(".gguf"):
                    gguf_files.append(filepath)
    
    print(f"✅ Encontrados: {total_files} archivos, {total_size / (1024**3):.2f} GB totales")
    print(f"   Archivos GGUF: {len(gguf_files)}")
    
    if report_file:
        with open(report_file, "w") as f:
            f.write(f"Reporte de duplicados en {blobs_dir}\n")
            f.write(f"Generado: {os.path.basename(report_file)}\n")
            f.write("=" * 60 + "\n\n")
            f.write("--- TAMAÑOS ÚNICOS ---\n\n")
            for size in sorted(blobs_by_size.keys(), reverse=True):
                count = len(blobs_by_size[size])
                size_mb = size / (1024**2)
                f.write(f"{size_mb:>10.2f} MB: {count} archivo(s)\n")
            f.write("\n--- BLOBS CON MÚLTIPLES COPIAS ---\n\n")
            duplicates_found = False
            for size, paths in blobs_by_size.items():
                if len(paths) > 1:
                    duplicates_found = True
                    size_mb = size / (1024**2)
                    f.write(f"Tamaño: {size_mb:.2f} MB | Copias: {len(paths)}\n")
                    f.write(f"  Archivos:\n")
                    for path in paths:
                        f.write(f"    - {path}\n")
                    f.write("\n")
            if not duplicates_found:
                f.write("No se encontraron duplicados por tamaño.\n")
            f.write("\n--- ARCHIVOS GGUF ---\n\n")
            for gguf in gguf_files:
                size = get_blob_size(gguf)
                size_mb = size / (1024**2)
                f.write(f"{size_mb:>10.2f} MB: {gguf}\n")
    
    print("\n📈 Tamaños únicos:")
    for size in sorted(blobs_by_size.keys(), reverse=True):
        count = len(blobs_by_size[size])
        size_mb = size / (1024**2)
        wasted = (count - 1) * size
        wasted_mb = wasted / (1024**2)
        if wasted_mb > 0:
            print(f"  {size_mb:>10.2f} MB: {count} archivo(s) | Potencialmente duplicado: {wasted_mb:.2f} MB")
        else:
            print(f"  {size_mb:>10.2f} MB: {count} archivo(s)")
    print("\n🔍 Blobs con múltiples copias:")
    duplicates_found = False
    for size, paths in sorted(blobs_by_size.items(), key=lambda x: len(x[1]), reverse=True):
        if len(paths) > 1:
            duplicates_found = True
            size_mb = size / (1024**2)
            wasted = (len(paths) - 1) * size
            wasted_mb = wasted / (1024**2)
            print(f"  {size_mb:>10.2f} MB: {len(paths)} copias | Podrías ahorrar: {wasted_mb:.2f} MB")
            print(f"    Archivos:")
            for path in paths:
                print(f"      - {path}")
    if not duplicates_found:
        print("  No se encontraron duplicados por tamaño.")
    print("\n🎯 Blobs GRANDES con múltiples copias (>500MB):")
    large_duplicates = False
    for size, paths in sorted(blobs_by_size.items(), key=lambda x: x[0], reverse=True):
        if len(paths) > 1 and size > 500 * 1024 * 1024:
            large_duplicates = True
            size_mb = size / (1024**2)
            wasted = (len(paths) - 1) * size
            wasted_mb = wasted / (1024**2)
            print(f"  {size_mb:>10.2f} MB: {len(paths)} copias | Podrías ahorrar: {wasted_mb:.2f} MB")
            print(f"    Archivos:")
            for path in paths:
                print(f"      - {path}")
    if not large_duplicates:
        print("  No se encontraron blobs grandes con múltiples copias.")
    print("\n💾 ESPACIO POTENCIALMENTE RECUPERABLE:")
    wasted_space = 0
    for size, paths in blobs_by_size.items():
        if len(paths) > 1:
            wasted_space += (len(paths) - 1) * size
    print(f"  Total duplicados: {wasted_space / (1024**3):.2f} GB")
    return True

def main():
    blobs_dir = os.path.expanduser("~/.ollama/models/blobs")
    report_file = os.path.expanduser("~/ollama_duplicados_report.txt")
    print("\n🔍 Inicializando análisis de duplicados...")
    print(f"   Directorio: {blobs_dir}")
    print()
    
    success = analyze_blobs(blobs_dir, report_file)
    if success:
        print("\n" + "=" * 60)
        print("✅ ANÁLISIS COMPLETADO")
        print(f"   Reporte guardado en: {report_file}")
        print("=" * 60)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())