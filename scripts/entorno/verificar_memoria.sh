#!/bin/bash
#
# verificar_memoria.sh — Pre-flight check de memoria para modelos locales (Ollama).
#
# Solo lectura: NO mata procesos, NO pide sudo, NO modifica nada.
# Comprueba si cabe el modelo indicado (o un tamaño en GB) antes de lanzarlo.
#
# Uso:
#   ./verificar_memoria.sh                 # comprueba qwen3.5:9b (modelo del curso)
#   ./verificar_memoria.sh qwen3.8:27b     # comprueba un modelo instalado
#   ./verificar_memoria.sh --size 18       # comprueba un tamaño arbitrario en GB
#   ./verificar_memoria.sh --help          # ayuda
#
# Variables:
#   MARGEN_GB   margen de seguridad sobre el tamaño del modelo (default: 1.5)
#
# Códigos de salida:
#   0 = OK / AJUSTADO   2 = NO CABE   1 = error de ejecución

set -uo pipefail

MODELO_DEFAULT="qwen3.5:9b"
MARGEN_GB="${MARGEN_GB:-1.5}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# ---------- ayuda ----------
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    sed -n '2,20p' "$0"
    exit 0
fi

# ---------- argumentos ----------
ARG1="${1:-$MODELO_DEFAULT}"
MODELO=""
SIZE_OVERRIDE_GB=""

if [ "$ARG1" = "--size" ]; then
    if [ -z "${2:-}" ]; then
        echo "Error: --size requiere un valor en GB (p.ej. --size 18)." >&2
        exit 1
    fi
    SIZE_OVERRIDE_GB="$2"
    MODELO="(tamaño personalizado)"
else
    MODELO="$ARG1"
fi

# ---------- RAM total ----------
TOTAL_BYTES=$(sysctl -n hw.memsize 2>/dev/null || echo 0)
TOTAL_GB=$(awk "BEGIN{printf \"%.1f\", $TOTAL_BYTES/1073741824}")

# ---------- memoria disponible real (free + inactive + speculative + purgeable) ----------
VMSTAT=$(vm_stat 2>/dev/null)
if [ -z "$VMSTAT" ]; then
    echo -e "${RED}✗ No se pudo ejecutar vm_stat.${NC}" >&2
    exit 1
fi

PAGE_SIZE=$(echo "$VMSTAT" | awk '/page size of/ {gsub(/[^0-9]/,"",$8); print $8}')
[ -z "$PAGE_SIZE" ] && PAGE_SIZE=4096

PAGES_FREE=$(echo "$VMSTAT" | awk '/^Pages free:/ {gsub(/\./,"",$3); print $3}')
PAGES_INACT=$(echo "$VMSTAT" | awk '/^Pages inactive:/ {gsub(/\./,"",$3); print $3}')
PAGES_SPEC=$(echo "$VMSTAT" | awk '/^Pages speculative:/ {gsub(/\./,"",$3); print $3}')
PAGES_PURGE=$(echo "$VMSTAT" | awk '/^Pages purgeable:/ {gsub(/\./,"",$3); print $3}')
: "${PAGES_FREE:=0}"
: "${PAGES_INACT:=0}"
: "${PAGES_SPEC:=0}"
: "${PAGES_PURGE:=0}"

DISPO_GB=$(awk "BEGIN{printf \"%.1f\", ($PAGES_FREE+$PAGES_INACT+$PAGES_SPEC+$PAGES_PURGE)*$PAGE_SIZE/1073741824}")

# ---------- tamaño del modelo ----------
MODELO_GB=""

if [ -n "$SIZE_OVERRIDE_GB" ]; then
    MODELO_GB="$SIZE_OVERRIDE_GB"
else
    if ! command -v ollama >/dev/null 2>&1; then
        echo -e "${RED}✗ 'ollama' no está en el PATH.${NC}" >&2
        exit 1
    fi

    SIZE_STR=$(ollama list 2>/dev/null | awk -v m="$MODELO" '
        { if ($1==m || $1==m":latest") { print $3" "$4; exit } }')

    if [ -z "$SIZE_STR" ]; then
        echo -e "${RED}✗ Modelo '$MODELO' no encontrado en 'ollama list'.${NC}" >&2
        echo "   Modelos disponibles:" >&2
        ollama list 2>/dev/null | tail -n +2 | awk '{print "   - "$1" ("$3" "$4")"}' >&2
        echo "   (También puedes pasar un tamaño: --size <GB>)" >&2
        exit 1
    fi

    VAL=$(echo "$SIZE_STR" | awk '{print $1}')
    UNIT=$(echo "$SIZE_STR" | awk '{print $2}')
    case "$UNIT" in
        TB) MODELO_GB=$(awk "BEGIN{printf \"%.2f\", $VAL*1024}") ;;
        GB) MODELO_GB=$(awk "BEGIN{printf \"%.2f\", $VAL}") ;;
        MB) MODELO_GB=$(awk "BEGIN{printf \"%.2f\", $VAL/1024}") ;;
        KB) MODELO_GB=$(awk "BEGIN{printf \"%.3f\", $VAL/1048576}") ;;
        B)  MODELO_GB=$(awk "BEGIN{printf \"%.3f\", $VAL/1073741824}") ;;
        *)  echo -e "${RED}✗ Unidad de tamaño no reconocida: '$UNIT'${NC}" >&2; exit 1 ;;
    esac
fi

# ---------- requerimiento y veredicto ----------
REQ_GB=$(awk "BEGIN{printf \"%.1f\", $MODELO_GB + $MARGEN_GB}")

ESTADO=$(awk -v d="$DISPO_GB" -v m="$MODELO_GB" -v r="$REQ_GB" 'BEGIN{
    if (d+0 >= r+0)      print "OK";
    else if (d+0 >= m+0) print "AJUSTADO";
    else                 print "NOCABE";
}')

echo ""
echo -e "${CYAN}📊 Verificación de memoria${NC}"
echo "=========================================="
printf "  Modelo             : %s\n" "$MODELO"
printf "  Tamaño del modelo  : %s GB\n" "$MODELO_GB"
printf "  Margen seguridad   : %s GB\n" "$MARGEN_GB"
printf "  Requerimiento est. : %s GB\n" "$REQ_GB"
echo "------------------------------------------"
printf "  RAM total          : %s GB\n" "$TOTAL_GB"
printf "  Memoria disponible : %s GB\n" "$DISPO_GB"
echo "------------------------------------------"
echo ""

RC=0
case "$ESTADO" in
    OK)
        echo -e "${GREEN}✅ OK${NC} — Hay margen suficiente para cargar el modelo."
        ;;
    AJUSTADO)
        echo -e "${YELLOW}⚠️  AJUSTADO${NC} — Cabe, pero sin margen de seguridad."
        echo "   Sugerencias: reduce num_ctx, cierra apps pesadas (VS Code, navegador)"
        echo "                o usa OLLAMA_KEEP_ALIVE=0 para descargar al terminar."
        ;;
    NOCABE)
        echo -e "${RED}❌ NO CABE${NC} — La memoria disponible es menor que el modelo."
        echo "   Sugerencias: usa una cuantización menor (Q4), un modelo más pequeño"
        echo "                o libera memoria cerrando aplicaciones."
        RC=2
        ;;
esac

echo ""
echo "ℹ️  'Disponible' = free + inactive + speculative + purgeable."
echo "    macOS puede reclamar más memoria bajo presión; es orientativo, no garantía."
echo ""

exit $RC
