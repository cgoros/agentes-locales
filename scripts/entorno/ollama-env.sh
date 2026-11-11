#!/bin/bash
#
# ollama-env.sh — Configuración recomendada de memoria para Ollama.
#
# ESTE ARCHIVO NO SE EJECUTA DIRECTAMENTE como un script normal: se "sourcea"
# para exportar variables al entorno de la terminal (o se añaden sus líneas
# a ~/.zshrc). Las variables deben existir ANTES de arrancar el servidor de
# Ollama (la app de escritorio o `ollama serve`); si ya está corriendo,
# reinícialo para que surtan efecto.
#
# Uso puntual (esta terminal):
#   source scripts/entorno/ollama-env.sh
#
# Permanente: añadir al final de ~/.zshrc esta línea:
#   source ~/Documents/wks/pruebas/agentes-locales/scripts/entorno/ollama-env.sh
#
# --- Ciclo de vida del modelo en RAM -------------------------------------
# Cuánto tiempo mantiene Ollama el modelo cargado tras la última petición.
#   "30m"  → mantener caliente durante la sesión de curso (recomendado)
#   "0"    → descargar inmediatamente al terminar (máxima RAM libre)
#   "-1"   → mantener cargado indefinidamente
export OLLAMA_KEEP_ALIVE="${OLLAMA_KEEP_ALIVE:-30m}"

# --- Límite de peticiones en paralelo ------------------------------------
# Cada petición concurrente extra consume RAM (KV cache adicional).
# Para un solo agente local, 1 es suficiente.
export OLLAMA_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-1}"

# --- Contexto (KV cache) --------------------------------------------------
# IMPORTANTE: el contexto NO se configura de forma fiable por variable de
# entorno en todas las versiones de Ollama. En tu caso detectamos el proceso
# arrancado con `-c 16200` (contexto 16200), que consume RAM extra.
# Se controla por petición (`options.num_ctx` en la API) o por Modelfile:
#
#   PARAMETER num_ctx 8192
#
# Si el curso no necesita contexto largo, 4096–8192 es un buen equilibrio.
# (No se exporta aquí para no falsear el comportamiento según la versión.)
#
# --- Nota sobre la RAM "libre" -------------------------------------------
# No hace falta "purgar" ni matar procesos: macOS reclama la memoria
# inactive/speculative automáticamente cuando un modelo la necesita.
# Usa `./verificar_memoria.sh` para comprobar si cabe antes de lanzar.
