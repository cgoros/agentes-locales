# Agentes Locales — Workspace del curso

Workspace del curso **"De Cero a Master en LLMs Locales, Agentes y Orquestación
Multiagente"**, ejecutándose 100 % en local con Ollama.

**Hardware:** Mac Apple Silicon M5 · 24 GB RAM unificada · macOS (2026)
**Stack:** Ollama · LM Studio · LM Studio Bionic · Python 3.12 + LangGraph

> **Documento central del curso:** [`curso-agentes-locales.md`](./curso-agentes-locales.md).
> Marca las casillas `[ ]` a medida que completes cada módulo. Abre los `.md` en
> VS Code con `Cmd+Shift+V` para ver la vista renderizada.

---

## Índice

1. [El núcleo: el curso](#el-núcleo-el-curso)
2. [Estado actual del entorno](#estado-actual-del-entorno)
3. [Estructura del workspace](#estructura-del-workspace)
4. [Funciones disponibles](#funciones-disponibles)
5. [Distinción clave: duplicados vs. huérfanos](#distinción-clave-duplicados-vs-huérfanos)
6. [Flujo de mantenimiento de Ollama](#flujo-de-mantenimiento-de-ollama)
7. [Gestión de modelos (GGUF vs. pull)](#gestión-de-modelos-gguf-vs-pull)
8. [Configuración de agentes de código](#configuración-de-agentes-de-código)
9. [Planteamiento multiagente (agentes en paralelo)](#planteamiento-multiagente-agentes-en-paralelo)
10. [Git y .gitignore](#git-y-gitignore)
11. [Solución de problemas](#solución-de-problemas)
12. [Hoja de ruta del curso](#hoja-de-ruta-del-curso)

---

## El núcleo: el curso

El archivo `curso-agentes-locales.md` es la referencia maestra. Sus **3 etapas**:

| Etapa | Contenido | Entregable |
|---|---|---|
| **🟢 1 — Iniciación** | Hardware, stack, modelos, tool calling, prompt engineering, Cline | Agente de un paso (JSON estricto 10/10) |
| **🟡 2 — Intermedio** | Loops (Trigger→Act→Verify→Retry), verificación, LangGraph, grafos condicionales | Grafo con loop interno que se autocorrige |
| **🔴 3 — Avanzado** | Tools propias, multiagente en paralelo (fan-out/fan-in), orquestador/sintetizador, persistencia | Proyecto final: agente de mantenimiento en paralelo (todo `qwen3.5:9b`) |

El calendario detallado (**16 semanas**) está al final del curso, repartido por etapas.

Los apéndices A–E cubren: solución de problemas, comandos rápidos, estructura real
del workspace, extensiones de VS Code y un glosario/checklist de conceptos.

**Progreso real:** Etapa 1, módulos **1.1–1.4** completados (hardware, stack, modelos
y tool calling verificado). Los scripts de 1.6 en adelante y las Etapas 2–3 aún no
se han creado (ver `NOTAS-MODULO1.md` para las desviaciones respecto al curso).

---

## Estado actual del entorno

Verificado el 2026-10-31 (detalle en [`NOTAS-MODULO1.md`](./NOTAS-MODULO1.md)):

| Pieza | Estado | Detalle |
|---|---|---|
| Homebrew | ✅ | 7.0.11 (prefix `/usr/local`, Rosetta) |
| Python | ✅ | 3.12.9 |
| Git | ⚠️ | 2.54.0 (Apple Git-157) · usar `arch -arm64 /usr/bin/git` (ver *Solución de problemas*) |
| Ollama | ✅ | 0.40.13 · **Ollama.app** (no Homebrew) · `127.0.0.1:11434` |
| LM Studio | ✅ | 0.4.28 · CLI `lms` en `~/.lmstudio/bin` · servidor en `:1234` |
| Modelos | ✅ | `qwen3.5:9b` (5,7 GB), `qwen3.8:27b` (16 GB), `nomic-embed-text` |
| venv | ✅ | `.venv` (Python 3.12.9) en la raíz del proyecto |
| Paquetes | ✅ | `ollama` 0.6.3, `langchain` 1.4.7, `langchain-ollama` 1.1.0, `langgraph` 1.2.19, `python-dotenv`, `rich` |

**Desviaciones importantes respecto al curso:**
1. Ollama **no** está instalado con Homebrew (vino con `Ollama.app`). No ejecutes
   `brew install ollama` / `brew services start ollama` mientras la app esté activa.
2. El venv vive en la raíz del proyecto: `cd agentes-locales && source .venv/bin/activate`.
3. Los modelos se importaron **desde GGUF de HuggingFace**, no con `ollama pull`
   (el CDN de blobs de Ollama no es accesible desde esta red). Recetas en `Modelfile.*`.
4. El 27B se creó con `num_ctx 16384` (no 32K) para evitar swap con 24 GB de RAM.

---

## Estructura del workspace

```
agentes-locales/
├── README.md                    # este documento (índice y funciones)
├── curso-agentes-locales.md     # NÚCLEO: el curso completo (3 etapas)
├── NOTAS-MODULO1.md             # estado real de la Etapa 1 + desviaciones
├── ollama-helper.sh             # gestor unificado de modelos (menú interactivo)
├── Modelfile.qwen3.5-9b         # receta de importación GGUF del 9B
├── Modelfile.qwen3.8-27b        # receta de importación GGUF del 27B
├── .aider.conf.yml              # config de Aider → Ollama
├── .cline/env                   # config de Cline → Ollama
├── .gitignore                   # exclusión de artefactos locales
├── scripts/
│   ├── 01_analisis_duplicados.py        # OBSOLETO: solo informativo (por tamaño)
│   └── 03_auditoria_blobs_huerfanos.py  # auditor real de blobs (SHA256/manifests)
├── .venv/                       # (ignorado) entorno virtual Python
├── gguf/                        # (ignorado) pesos fuente en GGUF (~21 GB)
└── .logs/                       # (ignorado) logs de descarga/importación
```

---

## Funciones disponibles

### 1. `ollama-helper.sh` — gestor unificado de modelos

```bash
./ollama-helper.sh
```

Menú interactivo (valida que Ollama esté arriba y lo arranca si no responde):

| Opción | Función | Detalle |
|---|---|---|
| **1** | Ver modelos | `ollama ps` (cargados en memoria) + `ollama list` (instalados) |
| **2** | Verificar RAM/swap | `sysctl hw.memsize`, `vm.swapusage`, procesos de Ollama |
| **3** | Cargar `qwen3.5:9b` | contexto `16384`, `keep_alive 5m` |
| **4** | Cargar `qwen3.8:27b` | contexto `8192`, `keep_alive 5m` |
| **5** | Recomendaciones | guía anti-swap + límites de contexto |
| **6** | Auditar blobs | dry-run del auditor de huérfanos (sin borrar) |
| **7** | Salir | |

Constantes configurables arriba del script: `MODELO_RAPIDO`, `MODELO_PROFUNDO`,
`CTX_RAPIDO=16384`, `CTX_PROFUNDO=8192`.

### 2. `scripts/03_auditoria_blobs_huerfanos.py` — auditor real de blobs

Detecta blobs **huérfanos** (no referenciados por ningún manifest) por **hash
(SHA256)**, resolviendo recursivamente manifest lists y symlinks. Es la única
forma segura de liberar disco en Ollama < 0.40 (no existe `ollama prune`).

```bash
python3 scripts/03_auditoria_blobs_huerfanos.py              # dry-run (solo informe)
python3 scripts/03_auditoria_blobs_huerfanos.py --delete     # borra (pide confirmación)
python3 scripts/03_auditoria_blobs_huerfanos.py --delete --yes
```

Seguridad: **aborta** si hay blobs referenciados ausentes (estado inconsistente)
y **protege** los blobs en uso y los que tienen metadata local.

### 3. `scripts/01_analisis_duplicados.py` — ⚠️ OBSOLETO (solo informativo)

Agrupa blobs por **tamaño** de archivo. Esos grupos **no** son duplicados reales:
los tensores de un modelo suelen compartir tamaño exacto con hash distinto.
**No borres nada basándote en este script.** Úsalo únicamente para estadísticas.

---

## Distinción clave: duplicados vs. huérfanos

| Concepto | Criterio | ¿Borrable? |
|---|---|---|
| **"Duplicados"** (tamaño) | Dos blobs con el mismo tamaño | ❌ **NO** — pueden ser tensores distintos |
| **Huérfanos** (hash) | Blob no referenciado por ningún manifest | ✅ Sí — restos de modelos desinstalados o descargas canceladas |

**Regla:** en Ollama un blob se identifica por el **SHA256 de su contenido**. El
tamaño nunca es criterio de borrado. La estrategia segura es la del
`03_auditoria_blobs_huerfanos.py`.

---

## Flujo de mantenimiento de Ollama

```bash
# 1. Estado rápido (modelos en memoria y en disco)
./ollama-helper.sh            # opción 1

# 2. Auditar blobs huérfanos sin riesgo
python3 scripts/03_auditoria_blobs_huerfanos.py

# 3. Si el informe muestra huérfanos, eliminarlos
python3 scripts/03_auditoria_blobs_huerfanos.py --delete

# 4. Liberar RAM si no vas a usar un modelo
ollama stop qwen3.8:27b
```

Estado de referencia: 0 blobs huérfanos, disco de Ollama en ~22,47 GB.

---

## Gestión de modelos (GGUF vs. pull)

Vía usada actualmente (CDN de Ollama bloqueado en esta red):

```bash
ollama create qwen3.5:9b  -f Modelfile.qwen3.5-9b
ollama create qwen3.8:27b -f Modelfile.qwen3.8-27b
```

Vía oficial cuando la red lo permita:

```bash
ollama pull qwen3.5:9b
ollama pull qwen3.8:27b
```

Los `.gguf` en `gguf/` son los pesos fuente. `ollama create` ya copió los pesos a
`~/.ollama/models`, por lo que `gguf/` puede borrarse si se necesita liberar
~21 GB (sin afectar a los modelos operativos): `rm -rf gguf/ .logs/`.

---

## Configuración de agentes de código

Dos herramientas apuntan a Ollama en `http://localhost:11434`:

- **Cline** → `.cline/env` (`CLINE_ASSISTANT_MODEL`, `CLINE_ASSISTANT_OLLAMA_HOST`)
- **Aider** → `.aider.conf.yml` (`model: qwen3.5:9b`, `ollama_host`) — opcional, aún no instalado

Eje **Modelo** (qué cerebro) vs. Eje **Modo** (Plan/Act): son independientes.
Recomendado: `qwen3.5:9b` para iterar rápido, `qwen3.8:27b` para calidad, con
`num_ctx` entre 8192–16384 para no provocar swap. Ver `NOTAS-MODULO1.md`.

---

## Planteamiento multiagente (agentes en paralelo)

Por el límite de **24 GB de RAM**, el multiagente se hará con **un único modelo
`qwen3.5:9b` cargado una sola vez** y reutilizado por todos los roles. Se probarán
**agentes en paralelo**:

```
          ┌── Agente A (p. ej. Investigador) ──┐
Tarea ───►  Orquestador                          ├──► Sintetizador ──► Entregable
          └── Agente B (p. ej. Redactor)    ──┘
```

- **Agente A** y **Agente B** trabajan **en paralelo** sobre la misma tarea.
- El **Orquestador/Sintetizador** reparte el trabajo y **fusiona** ambas salidas.
- El 27B queda para pruebas puntuales de calidad, **nunca** para multiagente en paralelo.

En LangGraph esto es un **fan-out** (Orquestador → A y B) y un **fan-in**
(A y B → Sintetizador). El mismo peso del 9b atiende ambas ramas sin duplicar RAM.

---

## Git y .gitignore

`.gitignore` excluye: `.venv/`, `.logs/`, `gguf/`, `__pycache__/`, `*.pyc`,
`.DS_Store`, `.env`.

⚠️ **Antes de hacer `git add/commit`, lee "Solución de problemas"** — el binario
de `git` falla bajo Rosetta en este equipo. Usa `arch -arm64 /usr/bin/git`.

---

## Solución de problemas

| Síntoma | Causa | Solución |
|---|---|---|
| `curl localhost:11434` no responde | Ollama no está corriendo | Abre `Ollama.app` o ejecuta `./ollama-helper.sh` |
| `git` lanza `libxcrun ... need 'x86_64'` | Terminal bajo **Rosetta** con CommandLineTools arm64 | Usa `arch -arm64 /usr/bin/git <cmd>` (o una terminal arm64 nativa); comprueba `uname -m` |
| El modelo devuelve texto en vez de `tool_calls` | El modelo no soporta tools o el prompt no las declara | Usa `qwen3.5:9b` / `qwen3.8:27b` (tag `tools`) |
| El Mac se ralentiza con el 27B | Contexto/swap excesivo | Baja `num_ctx`, usa `qwen3.5:9b` o `ollama stop` |
| Dos servidores Ollama en conflicto | `brew` + `Ollama.app` a la vez | Mantén solo `Ollama.app`; no uses `brew services` |

---

## Hoja de ruta del curso

| Semana | Etapa | Foco | Entregable |
|---|---|---|---|
| 1 | 🟢 1 | Stack + tool calling | `curl` con `tool_calls` válido (✅ hecho) |
| 2 | 🟢 1 | Prompt Engineering | `prompt_agente.py` (JSON 10/10) |
| 3 | 🟢 1 | Prompt avanzado (few-shot, clasificador, extractor) | 3 agentes de un paso funcionando |
| 4 | 🟢 1 | Cline + primer agente integrado | **Entregable E1** |
| 5 | 🟡 2 | Loops básicos | Loop con verificación y estado |
| 6 | 🟡 2 | Verificación determinista + estado | `loop_estado.json` con historial |
| 7 | 🟡 2 | LangGraph básico | `StateGraph` de 3 nodos |
| 8 | 🟡 2 | Grafo condicional | Grafo Planificador→Redactor→Revisor |
| 9 | 🟡 2 | Nodos deterministas + integración | **Entregable E2** |
| 10 | 🔴 3 | Tools propias (`bind_tools`) | Agente con 2 tools reales |
| 11 | 🔴 3 | Multiagente fan-out/fan-in | 2 agentes en paralelo (todo 9b) |
| 12 | 🔴 3 | Orquestador/Sintetizador | Salida fusionada única |
| 13 | 🔴 3 | Persistencia y reanudación | Grafo reanudable tras reinicio |
| 14 | 🔴 3 | Observabilidad + Cline/Aider | Trazas y logs claros |
| 15 | 🔴 3 | Proyecto final: diseño + hitos 1-2 | Esqueleto + agentes A/B |
| 16 | 🔴 3 | Proyecto final: ejecución + hitos 3-4 | **Entregable E3** en local |

---

*Workspace del curso de agentes locales. El núcleo del curso está en
`curso-agentes-locales.md`; este README es el índice operativo de las
herramientas disponibles.*
