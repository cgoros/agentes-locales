# Agentes Locales — Workspace del curso

Workspace del curso **"De Cero a Master en LLMs Locales, Agentes y Orquestación
Multiagente"**, ejecutándose 100 % en local con Ollama.

**Hardware:** Mac Apple Silicon M5 · 24 GB RAM unificada · macOS (2026) · **arm64 nativo**
**Stack:** Ollama · LM Studio · Python 3.12 + LangGraph 1.2 · Aider 0.86 · Cline

> **Documento central del curso:** [`curso-agentes-locales.md`](./curso-agentes-locales.md).
> Marca las casillas `[ ]` a medida que completes cada módulo. Abre los `.md` en
> VS Code con `Cmd+Shift+V` para ver la vista renderizada.

---

## Índice

1. [El núcleo: el curso](#el-núcleo-el-curso)
2. [Cómo estudiar con el profesor (Cline)](#cómo-estudiar-con-el-profesor-cline)
3. [Estado actual del entorno](#estado-actual-del-entorno)
4. [Estructura del workspace](#estructura-del-workspace)
5. [Funciones disponibles](#funciones-disponibles)
6. [Distinción clave: duplicados vs. huérfanos](#distinción-clave-duplicados-vs-huérfanos)
7. [Flujo de mantenimiento de Ollama](#flujo-de-mantenimiento-de-ollama)
8. [Gestión de modelos (GGUF vs. pull)](#gestión-de-modelos-gguf-vs-pull)
9. [Configuración de agentes de código](#configuración-de-agentes-de-código)
10. [Planteamiento multiagente (agentes en paralelo)](#planteamiento-multiagente-agentes-en-paralelo)
11. [Git y .gitignore](#git-y-gitignore)
12. [Solución de problemas](#solución-de-problemas)
13. [Hoja de ruta del curso](#hoja-de-ruta-del-curso)

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

**Estado del estudio:** el curso se recorre **desde el principio en modo repaso**
(1.1 → 1.7 → Entregable E1 → Etapas 2–3), aunque el entorno ya esté montado y
`prompt_agente.py` funcione (JSON estricto **10/10** en ~9 s). Las casillas de
`curso-agentes-locales.md` se marcan a medida que el profesor confirma cada práctica.

---

## Cómo estudiar con el profesor (Cline)

Cline actúa como **profesor** gracias a [`CLAUDE.md`](./CLAUDE.md), que se carga
automáticamente al abrir este workspace (no hay que configurar nada en la UI y
funciona con cualquier modelo: DeepSeek-v4, qwen local, etc.).

> **Compatibilidad:** Cline lee `CLAUDE.md` automáticamente. Si tu versión no lo
> hiciera, abre *Settings → Custom Instructions* y pega:
> `Actúa como el profesor definido en ./CLAUDE.md (curso de agentes locales).`

### Rutina de cada sesión

1. Abre VS Code en este workspace y escribe en Cline: **"modo profesor"**.
2. Te sitúa leyendo las casillas de `curso-agentes-locales.md` y te lanza la
   siguiente práctica.
3. Haz el ejercicio tú. Cuando necesites ayuda:

   | Escribes... | Cline hace... |
   |---|---|
   | `no entiendo <tema>` | Explicación desde cero, sin dar por sabido nada |
   | `pista` | Una sola pista, sin la solución |
   | `revísame <fichero>` | Lo ejecuta, mide (10/10, tiempos) y dice qué falla y por qué |
   | `hazlo tú` | Lo resuelve como *ejemplo resuelto* (después reescríbelo tú) |
   | `progreso` | Resumen de lo hecho y lo que falta |

4. Al terminar una práctica, **márcala tú** en `curso-agentes-locales.md`
   (`[ ]` → `[x]`). También puedes pedir: **"márcalo"**.
5. Antes de avanzar pregunta: **"¿paso al siguiente?"**.

> **Repaso desde el principio:** el curso arranca con **todas las casillas sin
> marcar** para poder repasar 1.1–1.7 aunque ya tengas parte hecha. El profesor
> verifica cada práctica con 1–2 comandos; lo que ya domines se marca rápido.

### Seguimiento del progreso

- **Única fuente de verdad:** las casillas `[ ]` / `[x]` de `curso-agentes-locales.md`.
- **Quién marca:** tú, al superar la práctica. El profesor verifica, pero no marca
  salvo que pidas "márcalo".
- **Apuntes y desviaciones:** `NOTAS-MODULO1.md`.
- **La hoja de ruta** (16 semanas, al final de este README y del curso) es
  planificación, no progreso.
- **Regla del curso:** no pases de práctica hasta que funcione (p. ej. 10/10 JSON).

---

## Estado actual del entorno

Verificado el **2026-11-11**, tras la migración completa a **arm64 nativo**
(histórico y detalles en [`NOTAS-MODULO1.md`](./NOTAS-MODULO1.md)):

| Pieza | Estado | Detalle |
|---|---|---|
| Arquitectura | ✅ | `arm64` nativo · sin Rosetta · sin MacPorts |
| Homebrew | ✅ | 7.0.13 en `/opt/homebrew` (arm64) |
| Python | ✅ | 3.12.9 (framework python.org, universal) |
| Git | ✅ | 2.54.0 (Apple Git-157) · `git` funciona directo (ya **no** hace falta `arch -arm64`) |
| Ollama | ✅ | 0.40.13 · **Ollama.app** (no Homebrew) · `127.0.0.1:11434` |
| LM Studio | ✅ | 0.4.28 · CLI `lms` en `~/.lmstudio/bin` · servidor en `:1234` |
| Modelos | ✅ | `qwen3.5:9b` (5,7 GB), `qwen3.8:27b` (18 GB), `nomic-embed-text` (274 MB) |
| venv | ✅ | `.venv` Python 3.12.9 **arm64** (recreado el 2026-11-11) · `source .venv/bin/activate` |
| Paquetes | ✅ | `ollama` 0.6.3, `langchain` 1.4.7, `langchain-ollama` 1.1.0, `langgraph` 1.2.19, `python-dotenv` 1.2.1, `rich` 14.3.2 · ver `requirements.txt` |
| Agentes de código | ✅ | Cline (`saoudrizwan.claude-dev` 4.1.26) · Aider `aider-chat` 0.86.2 en `.venv` |
| Disco | ✅ | Solo `~/.ollama/models` (22 GB). Los GGUF fuente y los logs ya se eliminaron |

**Desviaciones importantes respecto al curso:**
1. Ollama **no** está instalado con Homebrew (vino con `Ollama.app`). No ejecutes
   `brew install ollama` / `brew services start ollama` mientras la app esté activa.
2. El venv vive en la raíz del proyecto: `cd agentes-locales && source .venv/bin/activate`.
3. Los modelos se importaron **desde GGUF de HuggingFace**, no con `ollama pull`
   (el CDN de blobs de Ollama no era accesible desde esta red). Recetas en `Modelfile.*`.
   Los `.gguf` ya se borraron: `ollama create` copió los pesos a `~/.ollama/models`.
4. El 27B se creó con `num_ctx 16384` (no 32K) para evitar swap con 24 GB de RAM.

---

## Estructura del workspace

```
agentes-locales/
├── README.md                    # este documento (índice y funciones)
├── curso-agentes-locales.md     # NÚCLEO: el curso completo (3 etapas)
├── NOTAS-MODULO1.md             # estado real de la Etapa 1 + desviaciones
├── prompt_agente.py             # ENTREGABLE 1.6: agente de resumen (JSON estricto)
├── ollama-helper.sh             # gestor unificado de modelos (menú interactivo)
├── Modelfile.qwen3.5-9b         # receta de importación GGUF del 9B
├── Modelfile.qwen3.8-27b        # receta de importación GGUF del 27B
├── .aider.conf.yml              # config de Aider → Ollama
├── .cline/env                   # config de Cline → Ollama
├── .gitignore                   # exclusión de artefactos locales
├── requirements.txt             # dependencias del curso (pip install -r ...)
├── scripts/
│   ├── 01_analisis_duplicados.py        # OBSOLETO: solo informativo (por tamaño)
│   ├── 03_auditoria_blobs_huerfanos.py  # auditor real de blobs (SHA256/manifests)
│   └── entorno/
│       ├── ollama-env.sh                # variables de Ollama (sourceado desde ~/.zshrc)
│       └── verificar_memoria.sh         # pre-flight: ¿cabe el modelo en RAM?
└── .venv/                       # (ignorado) entorno virtual Python 3.12
```

Los modelos viven solo en `~/.ollama/models` (22 GB). **No** hay copias `.gguf`
en el repo: se eliminaron tras importarlos con `ollama create`.

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

### 4. `scripts/entorno/verificar_memoria.sh` — pre-flight de RAM

Comprueba si un modelo **cabe en memoria antes de cargarlo**. Solo lectura: no
mata procesos, no pide sudo, no modifica nada.

```bash
./scripts/entorno/verificar_memoria.sh               # comprueba qwen3.5:9b
./scripts/entorno/verificar_memoria.sh qwen3.8:27b   # un modelo instalado
./scripts/entorno/verificar_memoria.sh --size 18     # tamaño arbitrario en GB
```

Códigos de salida: `0` = OK/ajustado · `2` = no cabe · `1` = error.

### 5. `scripts/entorno/ollama-env.sh` — variables de Ollama

Se **sourcea** (no se ejecuta). Ya está enganchado en `~/.zshrc`, así que cada
terminal arranca con:

| Variable | Valor | Efecto |
|---|---|---|
| `OLLAMA_KEEP_ALIVE` | `30m` | mantiene el modelo caliente durante la sesión |
| `OLLAMA_NUM_PARALLEL` | `1` | una sola petición concurrente (sin KV cache extra) |

Modo puntual sin reiniciar la terminal: `source scripts/entorno/ollama-env.sh`.

### 6. `prompt_agente.py` — entregable del módulo 1.6

Agente de un paso que resume texto y devuelve **solo JSON** (`format="json"`),
con `think=False` (Qwen3 razonaba ~50 s por llamada) y presupuesto `num_predict`.

```bash
.venv/bin/python prompt_agente.py            # una ejecución (JSON formateado)
.venv/bin/python prompt_agente.py --test 10  # criterio de éxito: 10/10 (≈9 s)
```

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

Estado de referencia (2026-11-11): 0 blobs huérfanos, disco de Ollama en ~22 GB.

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

Los `.gguf` de `gguf/` eran los pesos fuente y **ya se eliminaron** (21 GB
liberados): `ollama create` copió los pesos a `~/.ollama/models`. Si alguna vez
hay que reimportar, descarga de nuevo los GGUF de HuggingFace y usa los
`Modelfile.*` (las recetas sí están en el repo).

---

## Configuración de agentes de código

Dos herramientas apuntan a Ollama en `http://localhost:11434`:

- **Cline** → `.cline/env` (`CLINE_ASSISTANT_MODEL`, `CLINE_ASSISTANT_OLLAMA_HOST`)
- **Aider** → `.aider.conf.yml` (`model: qwen3.5:9b`, `ollama_host`) — instalado en `.venv` (`aider-chat` 0.86.2)

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

El repo solo versiona el curso, las notas, los scripts y las configuraciones de
agentes: **nada pesado** (los modelos viven en `~/.ollama/models`). `git`
funciona directamente, sin `arch -arm64` (arm64 nativo desde el 2026-11-11).

---

## Solución de problemas

| Síntoma | Causa | Solución |
|---|---|---|
| `curl localhost:11434` no responde | Ollama no está corriendo | Abre `Ollama.app` o ejecuta `./ollama-helper.sh` |
| El modelo devuelve texto en vez de `tool_calls` | El modelo no soporta tools o el prompt no las declara | Usa `qwen3.5:9b` / `qwen3.8:27b` (tag `tools`) |
| El Mac se ralentiza con el 27B | Contexto/swap excesivo | Baja `num_ctx`, usa `qwen3.5:9b` o `ollama stop` |
| Dos servidores Ollama en conflicto | `brew` + `Ollama.app` a la vez | Mantén solo `Ollama.app`; no uses `brew services` |

---

## Hoja de ruta del curso

| Semana | Etapa | Foco | Entregable |
|---|---|---|---|
| 1 | 🟢 1 | Stack + tool calling | `curl` con `tool_calls` válido (✅ hecho) |
| 2 | 🟢 1 | Prompt Engineering | `prompt_agente.py` (JSON 10/10) ✅ |
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
