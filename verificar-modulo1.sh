#!/usr/bin/env bash
# Verificación del Módulo 1 — Instalación y configuración del stack completo
# Uso:  cd agentes-locales && ./verificar-modulo1.sh
# Todo el stack es local (Ollama + LM Studio + Python/LangGraph).

set -uo pipefail

PROYECTO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELO_LIGERO="qwen3.5:9b"
MODELO_ORQUESTADOR="qwen3.8:27b"

OK=0
KO=0
WARN=0

if [ -t 1 ]; then
  G=$'\033[32m'; R=$'\033[31m'; Y=$'\033[33m'; B=$'\033[1m'; N=$'\033[0m'
else
  G=""; R=""; Y=""; B=""; N=""
fi

ok()   { printf "${G}✅ %s${N}\n" "$1"; OK=$((OK+1)); }
ko()   { printf "${R}❌ %s${N}\n" "$1"; KO=$((KO+1)); }
warn() { printf "${Y}⚠️  %s${N}\n" "$1"; WARN=$((WARN+1)); }
seccion() { printf "\n${B}%s${N}\n" "$1"; }

# ---------------------------------------------------------------- 0/1.1 base
seccion "1.1 Herramientas base"

if command -v brew >/dev/null 2>&1; then
  ok "Homebrew $(brew --version | head -1 | awk '{print $2}')"
else
  ko "Homebrew no encontrado"
fi

if command -v python3 >/dev/null 2>&1; then
  PYV=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
  PYMAJ=${PYV%%.*}; PYMIN=${PYV##*.}
  if [ "$PYMAJ" -eq 3 ] && [ "$PYMIN" -ge 10 ]; then
    ok "Python $PYV ($(command -v python3))"
  else
    ko "Python $PYV: el curso pide 3.10+"
  fi
else
  ko "python3 no encontrado"
fi

if command -v git >/dev/null 2>&1; then
  ok "$(git --version)"
else
  ko "git no encontrado"
fi

# ---------------------------------------------------------------- 1.2 Ollama
seccion "1.2 Ollama (servicio en :11434)"

if command -v ollama >/dev/null 2>&1; then
  ok "CLI ollama $(ollama --version 2>/dev/null | awk '{print $NF}') ($(command -v ollama))"
  if brew list --versions ollama >/dev/null 2>&1; then
    ok "Ollama instalado vía Homebrew (brew services disponible)"
  else
    warn "Ollama no está instalado vía Homebrew (probablemente Ollama.app). NO ejecutes 'brew install ollama' con la app en marcha: tendrías dos servidores peleando por el puerto 11434."
  fi
else
  ko "CLI ollama no encontrado"
fi

if curl -s -m 5 http://localhost:11434/api/tags >/dev/null 2>&1; then
  ok "API de Ollama responde en http://localhost:11434"
else
  ko "La API de Ollama no responde (arranca Ollama.app o 'brew services start ollama')"
fi

# ---------------------------------------------------------------- 1.3 LM Studio
seccion "1.3 LM Studio + CLI lms (:1234)"

if command -v lms >/dev/null 2>&1; then
  ok "CLI lms en $(command -v lms)"
else
  ko "CLI lms no está en el PATH (export PATH=\"\$HOME/.lmstudio/bin:\$PATH\")"
fi

if lms status 2>/dev/null | grep -q "ON"; then
  ok "Servidor de LM Studio ON"
elif lms status 2>/dev/null | grep -q "OFF"; then
  ko "Servidor de LM Studio OFF → 'lms server start'"
else
  warn "No se pudo leer 'lms status'"
fi

if curl -s -m 5 http://localhost:1234/v1/models >/dev/null 2>&1; then
  ok "API OpenAI-compatible responde en http://localhost:1234/v1/models"
else
  warn "El puerto 1234 no responde (opcional para el curso: la orquestación va por Ollama)"
fi

# ---------------------------------------------------------------- 1.4 modelos
seccion "1.4 Modelos en Ollama"

LISTADO="$(ollama list 2>/dev/null || true)"
for m in "$MODELO_LIGERO" "$MODELO_ORQUESTADOR"; do
  if printf '%s\n' "$LISTADO" | awk -v m="$m" '$1==m {found=1} END {exit !found}'; then
    TAM=$(printf '%s\n' "$LISTADO" | awk -v m="$m" '$1==m {print $3$4}')
    ok "$m descargado ($TAM)"
  else
    ko "$m NO descargado → 'ollama pull $m'"
  fi
done

if printf '%s\n' "$LISTADO" | grep -q "nomic-embed-text"; then
  ok "nomic-embed-text presente (útil para RAG en módulos 4-5)"
else
  warn "Sin modelo de embeddings (opcional hasta el módulo de RAG)"
fi

# ---------------------------------------------------------------- 1.5 tool calling
seccion "1.5 Tool calling real"

MODELO_TEST=""
for m in "$MODELO_LIGERO" "$MODELO_ORQUESTADOR"; do
  if printf '%s\n' "$LISTADO" | awk -v m="$m" '$1==m {found=1} END {exit !found}'; then
    MODELO_TEST="$m"; break
  fi
done

if [ -z "$MODELO_TEST" ]; then
  ko "Sin modelos de chat instalados: no se puede probar tool calling"
else
  RESPUESTA=$(curl -s -m 180 http://localhost:11434/api/chat -d "{
    \"model\": \"$MODELO_TEST\",
    \"messages\": [{\"role\": \"user\", \"content\": \"¿Qué tiempo hace en Madrid?\"}],
    \"tools\": [{\"type\": \"function\", \"function\": {
      \"name\": \"get_weather\",
      \"description\": \"Obtiene el tiempo de una ciudad\",
      \"parameters\": {\"type\": \"object\", \"properties\": {\"city\": {\"type\": \"string\"}}, \"required\": [\"city\"]}
    }}],
    \"stream\": false
  }" 2>/dev/null)

  if printf '%s' "$RESPUESTA" | grep -q '"tool_calls"'; then
    ok "$MODELO_TEST emite tool_calls (agente viable)"
    printf '%s' "$RESPUESTA" | python3 -c 'import json,sys; d=json.load(sys.stdin); print("   →", json.dumps(d["message"]["tool_calls"], ensure_ascii=False)[:200])' 2>/dev/null || true
  else
    ko "$MODELO_TEST NO emitió tool_calls: $(printf '%s' "$RESPUESTA" | head -c 200)"
  fi
fi

# ---------------------------------------------------------------- 1.6 Python
seccion "1.6 Entorno Python para agentes"

VENV="$PROYECTO/.venv"
if [ -x "$VENV/bin/python" ]; then
  ok "venv en $VENV ($("$VENV/bin/python" -V 2>&1))"
  for p in ollama langgraph langchain langchain-ollama python-dotenv rich; do
    V=$("$VENV/bin/python" -c "import importlib.metadata as m; print(m.version('$p'))" 2>/dev/null)
    if [ -n "$V" ]; then ok "  $p $V"; else ko "  $p NO instalado"; fi
  done
else
  ko "No existe $VENV → 'python3 -m venv .venv && source .venv/bin/activate && pip install ollama langgraph langchain langchain-ollama python-dotenv rich'"
fi

# ---------------------------------------------------------------- 1.7/1.8 extras
seccion "1.7 / 1.8 VS Code y extras"

if command -v code >/dev/null 2>&1 && code --list-extensions 2>/dev/null | grep -qi "saoudrizwan.claude-dev"; then
  ok "Extensión Cline instalada ($(code --list-extensions --show-versions 2>/dev/null | grep -i saoudrizwan.claude-dev))"
else
  ko "Extensión Cline no detectada (id: saoudrizwan.claude-dev)"
fi
warn "La configuración de Cline (Provider=Ollama, Base URL, Context Window ≥32K, Compact Prompt) se valida en la UI, no por CLI."

if [ -x "$VENV/bin/aider" ] || command -v aider >/dev/null 2>&1; then
  ok "Aider instalado (opcional 1.8)"
else
  warn "Aider no instalado (opcional: pip install aider-chat)"
fi

# ---------------------------------------------------------------- resumen
seccion "Resumen"
printf "  %sOK: %d%s   %sAvisos: %d%s   %sFallos: %d%s\n" "$G" "$OK" "$N" "$Y" "$WARN" "$N" "$R" "$KO" "$N"
if [ "$KO" -gt 0 ]; then
  printf "${R}Módulo 1 incompleto: resuelve los fallos antes de pasar al Módulo 2.${N}\n"
  exit 1
fi
printf "${G}Módulo 1 verificado.${N}\n"

