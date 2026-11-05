#!/bin/bash
#
# ollama-helper.sh - Gestor rápido de modelos de Ollama en macOS.
#
# Objetivo: operar con qwen3.5:9b / qwen3.8:27b controlando el contexto para
# no provocar swap en equipos con RAM ajustada.
#
# Uso: ./ollama-helper.sh
#
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OLLAMA_API="http://127.0.0.1:11434"
MODELO_RAPIDO="qwen3.5:9b"
MODELO_PROFUNDO="qwen3.8:27b"
CTX_RAPIDO=16384
CTX_PROFUNDO=8192

ok()    { printf '✅ %s\n' "$*"; }
aviso() { printf '⚠️  %s\n' "$*"; }
error() { printf '❌ %s\n' "$*" >&2; }

ollama_arriba() {
    curl -s -m 2 "$OLLAMA_API/api/version" >/dev/null 2>&1
}

asegurar_ollama() {
    if ollama_arriba; then
        return 0
    fi
    aviso "Ollama no responde en $OLLAMA_API. Intentando arrancarlo..."
    open -a Ollama >/dev/null 2>&1 || true
    for _ in $(seq 1 15); do
        if ollama_arriba; then
            ok "Ollama en marcha"
            return 0
        fi
        sleep 1
    done
    error "No se pudo arrancar Ollama. Abre la app manualmente e inténtalo de nuevo."
    return 1
}

mostrar_cargados() {
    asegurar_ollama || return 1
    echo "Modelos cargados en memoria:"
    ollama ps
    echo
    echo "Modelos instalados:"
    ollama list
}

verificar_ram() {
    local bytes
    bytes=$(sysctl -n hw.memsize 2>/dev/null || echo 0)
    if [ "$bytes" -gt 0 ]; then
        awk -v b="$bytes" 'BEGIN { printf "RAM total: %.1f GB\n", b / 1024 / 1024 / 1024 }'
    else
        echo "RAM total: (no disponible)"
    fi
    echo -n "Swap: "
    sysctl -n vm.swapusage 2>/dev/null || echo "(no disponible)"
    echo
    echo "Procesos de Ollama:"
    ps aux | grep -E 'Ollama.app|llama-server' | grep -v grep \
        | awk '{ printf "  PID %-6s CPU %5s%% MEM %5s%%  %s\n", $2, $3, $4, $11 }'
}

precargar() {
    local modelo="$1"
    local ctx="$2"
    local respuesta

    asegurar_ollama || return 1

    echo "Descargando/verificando $modelo ..."
    if ! ollama pull "$modelo"; then
        error "No se pudo obtener $modelo"
        return 1
    fi

    echo "Precargando $modelo con contexto $ctx ..."
    respuesta=$(curl -s -m 900 "$OLLAMA_API/api/generate" \
        -d "{\"model\":\"$modelo\",\"prompt\":\"hola\",\"stream\":false,\"keep_alive\":\"5m\",\"options\":{\"num_predict\":1,\"num_ctx\":$ctx}}" \
        | tr -d '\n' | tail -c 200)
    if [ -z "$respuesta" ]; then
        error "Ollama no respondió al precargar $modelo"
        return 1
    fi
    ok "$modelo listo (contexto $ctx, keep_alive 5m)"
    echo
    ollama ps
}

mostrar_recomendaciones() {
    cat <<'EOF'
RECOMENDACIONES PARA EVITAR SWAP
================================

1. Contexto máximo recomendado
   - qwen3.5:9b  -> 8192 - 16384 tokens
   - qwen3.8:27b -> 4096 - 8192 tokens
   - Evita 32768 tokens con el modelo de 27B: dispara el uso de RAM/VRAM.

2. Estrategia de uso
   - Usa 9B para tareas rápidas (autocompletado, refactors pequeños, dudas).
   - Usa 27B para tareas profundas (diseño, análisis largo, revisión).
   - No mantengas ambos cargados a la vez: `ollama stop <modelo>` libera RAM.

3. Configuración en clientes (Cline, Continue, etc.)
   - Endpoint Ollama: http://localhost:11434
   - Modelo: qwen3.5:9b
   - num_ctx: 8192-16384 (menos contexto = menos memoria)

4. Diagnóstico
   - `ollama ps` muestra modelo, tamaño y % en GPU/CPU.
   - `sysctl vm.swapusage` indica si el sistema está paginando.
   - Si aparece swap en uso alto, reduce num_ctx o cambia a un modelo menor.

5. Limpieza de disco
   - Ollama 0.40.x no tiene `ollama prune`.
   - Audita blobs huérfanos: python3 scripts/03_auditoria_blobs_huerfanos.py
   - Borra los huérfanos:      python3 scripts/03_auditoria_blobs_huerfanos.py --delete
EOF
}

auditar_blobs() {
    local script="$SCRIPT_DIR/scripts/03_auditoria_blobs_huerfanos.py"
    if [ ! -f "$script" ]; then
        error "No se encuentra $script"
        return 1
    fi
    python3 "$script"
}

menu() {
    cat <<EOF
========================================
  Ollama Model Manager (evitar swap)
========================================

1. Ver modelos cargados e instalados
2. Verificar RAM y swap
3. Cargar $MODELO_RAPIDO (contexto $CTX_RAPIDO)
4. Cargar $MODELO_PROFUNDO (contexto $CTX_PROFUNDO)
5. Mostrar recomendaciones
6. Auditar blobs huérfanos (solo informe)
7. Salir
EOF
}

while true; do
    echo
    menu
    read -r -p "Seleccione opción: " opcion || exit 0
    echo
    case "$opcion" in
        1) mostrar_cargados ;;
        2) verificar_ram ;;
        3) precargar "$MODELO_RAPIDO" "$CTX_RAPIDO" ;;
        4) precargar "$MODELO_PROFUNDO" "$CTX_PROFUNDO" ;;
        5) mostrar_recomendaciones ;;
        6) auditar_blobs ;;
        7) echo "Hasta luego."; exit 0 ;;
        *) error "Opción no válida: $opcion" ;;
    esac
done
