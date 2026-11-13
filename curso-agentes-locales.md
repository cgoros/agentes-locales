# Curso: De Cero a Master en LLMs Locales, Agentes y Orquestación Multiagente

**Hardware:** Mac Apple Silicon M5 · 24 GB RAM unificada · macOS (2026)
**Stack base:** Ollama · LM Studio · LM Studio Bionic · Python 3.12 + LangGraph
**Objetivo:** Pasar de usuario de chatbots a **diseñador de sistemas de agentes** (Prompt → Loop → Graph → Multiagente en paralelo), ejecutándose 100 % en local.

> **Cómo usar este documento.** El curso está dividido en **3 etapas** (Iniciación, Intermedio y Avanzado). Cada etapa tiene varios módulos, y cada módulo termina con **ejercicios de práctica** y un **entregable**. No pases de etapa hasta completar su entregable. Abre este archivo en VS Code con `Cmd+Shift+V` para ver la vista renderizada y marca las casillas `[ ]` a medida que avanzas.

---

## Índice

### 🟢 Etapa 1 — Iniciación (fundamentos y tu primer agente)
- [1.1 Tu hardware y sus límites](#11-tu-hardware-y-sus-límites)
- [1.2 Stack local real](#12-stack-local-real-ollama-lm-studio-git)
- [1.3 Modelos: 9B vs. 27B, GGUF vs. pull](#13-modelos-9b-vs-27b-gguf-vs-pull)
- [1.4 Tool calling](#14-tool-calling-el-corazón-de-un-agente)
- [1.5 Entorno Python](#15-entorno-python-para-agentes)
- [1.6 Prompt Engineering](#16-prompt-engineering-para-agentes)
- [1.7 VS Code + Cline (+ Aider)](#17-vs-code--cline-opcional-aider)
- [🎯 Entregable de la Etapa 1](#-entregable-de-la-etapa-1)

### 🟡 Etapa 2 — Intermedio (loops, verificación y grafos)
- [2.1 Anatomía de un loop](#21-anatomía-de-un-loop)
- [2.2 Verificación determinista](#22-verificación-determinista-vs-llm)
- [2.3 Estado y memoria](#23-estado-y-memoria)
- [2.4 Presupuesto y parada](#24-presupuesto-y-condiciones-de-parada)
- [2.5 LangGraph](#25-langgraph-el-grafo-de-agentes)
- [2.6 Grafo condicional](#26-grafo-planificador--redactor--revisor)
- [2.7 Nodos deterministas](#27-nodos-deterministas-archivos-y-tests)
- [🎯 Entregable de la Etapa 2](#-entregable-de-la-etapa-2)

### 🔴 Etapa 3 — Avanzado (multiagente en paralelo y proyecto final)
- [3.1 Tools propias](#31-tools-propias-con-bind_tools)
- [3.2 Multiagente en paralelo](#32-multiagente-en-paralelo-fan-out--fan-in)
- [3.3 Orquestador y Sintetizador](#33-orquestador-y-sintetizador)
- [3.4 Persistencia y reanudación](#34-persistencia-y-reanudación)
- [3.5 Observabilidad](#35-observabilidad-y-depuración)
- [3.6 Cline + Aider en el flujo](#36-cline--aider-en-el-flujo-real)
- [3.7 Proyecto final](#37-proyecto-final-agente-de-mantenimiento-de-repositorio-en-paralelo)
- [🎯 Entregable de la Etapa 3](#-entregable-de-la-etapa-3)

### Extras
- [Calendario de 16 semanas](#calendario-de-16-semanas)
- [Apéndice A — Solución de problemas](#apéndice-a--solución-de-problemas-frecuentes)
- [Apéndice B — Comandos rápidos](#apéndice-b--referencias-rápidas-de-comandos)
- [Apéndice C — Estructura real del workspace](#apéndice-c--estructura-real-del-workspace)
- [Apéndice D — Extensiones de VS Code](#apéndice-d--extensiones-recomendadas-de-vs-code)
- [Apéndice E — Glosario y checklist de conceptos](#apéndice-e--glosario-y-checklist-de-conceptos)

---

## Cómo está organizado el curso

El aprendizaje de agentes sigue una progresión natural. Cada etapa añade una capa sobre la anterior:

| Etapa | Pregunta que responde | Herramienta mental |
|---|---|---|
| **🟢 1 — Iniciación** | ¿Cómo hablo con el modelo y le doy herramientas? | **Prompt** (un paso) |
| **🟡 2 — Intermedio** | ¿Cómo hago que se corrija y colabore por turnos? | **Loop** y **Grafo** |
| **🔴 3 — Avanzado** | ¿Cómo orquesto varios agentes a la vez? | **Multiagente (fan-out/fan-in)** |

**Ritmo sugerido:** 16 semanas (4 + 5 + 7). Puedes ir más rápido si tienes tiempo, pero **no te saltes la práctica**: el objetivo no es leer, es *construir y ajustar* agentes.

**Regla del curso:** si un ejercicio no funciona, no avances. Depura, ajusta el prompt, mide y repite. Aprender a *ajustar* es el 80 % del oficio.

---

# 🟢 ETAPA 1 — INICIACIÓN: fundamentos y tu primer agente funcional

**Duración sugerida:** 4 semanas · **Objetivo:** entender qué puede tu máquina, montar el stack, dominar *tool calling* y construir varios agentes de **un solo paso** robustos.

> Al terminar esta etapa sabrás **hablarle** al modelo y **darle herramientas**. Es el ladrillo de todo lo demás.

---

## 1.1. Tu hardware y sus límites

Antes de descargar nada, entiende tu máquina. Un Mac con **24 GB de RAM unificada** comparte memoria entre el sistema, el modelo (pesos), el *KV cache* (contexto) y tus apps. Si te pasas, el sistema empieza a hacer **swap** (usar disco como RAM) y todo se ralentiza.

| Sí puedes | No debes intentar |
|---|---|
| Modelos densos de **9B–27B en Q4** (≈6–18 GB). | Modelos de **70B** (ni cuantizados). |
| Modelos **MoE** con pocos parámetros activos (ej. 35B-A3B). | *Fan-out* masivo de agentes con modelos de 27B. |
| Contextos de **decenas de miles de tokens** con margen. | Contextos de 256K con un modelo de 18 GB cargado. |
| Orquestar varios agentes **en serie** o con modelos pequeños en paralelo. | Ejecutar dos modelos de 27B simultáneamente con fluidez. |

**Regla de oro:** la RAM es compartida entre pesos, KV cache y el resto del sistema. Un modelo de 18 GB en 4 bits deja muy poco margen para contexto largo; para agentes con muchas herramientas, prioriza modelos de **9B–14B** o usa el 27B con prompts compactos.

**Decisión de este curso (24 GB):** todos los ejercicios de agentes y el multiagente en paralelo se hacen con **un solo `qwen3.5:9b`** cargado una vez y reutilizado por todos los roles (agente A, agente B y orquestador/sintetizador), probando **agentes en paralelo** (fan-out / fan-in). El 27B queda para pruebas puntuales de calidad, **nunca** para multiagente concurrente.

**Medición real en este equipo (2026-11-11, 24 GiB):**

| Escenario | `ollama ps` | Swap usado | Páginas libres |
|---|---|---|---|
| `qwen3.5:9b` cargado e inactivo | 5,1 GB · 100 % GPU · ctx 16200 | 47,5 MB | 8 601 (≈0,13 GiB) |
| Cargando `qwen3.8:27b` (ctx 8192) | 18 GB · 100 % GPU · ctx 8192 · runner `mlx` | **4 064,6 MB (≈4,0 GiB)** | 6 639 (≈0,10 GiB) |
| Tras `ollama stop qwen3.8:27b` | (ninguno) | 4 211,3 MB (**no baja solo**) | 1 089 383 (≈16,6 GiB) |

Lo que demuestran estos números:

1. **18 GB de pesos = 75 % de la RAM total** → el 27B incumple la regla del 70 % **antes** de sumar el KV cache.
2. El swap creció de **1 GB a 5 GB de tamaño** y quedó **4 GiB en uso**: cargar el 27B con la app de escritorio abierta fuerza paginación real.
3. **El swap no vuelve a 0 al descargar el modelo**: macOS conserva el archivo y sus páginas. Solo se limpia reiniciando (o esperando a que el sistema las reclame).
4. Cargar el 27B costó **~9 s** de `load_duration` y la primera respuesta completa **~29 s**.

**Práctica 1.1** ✅

- [x] Anota cuánta RAM libre tienes antes de cargar un modelo (`vm.swapusage`, Activity Monitor).
- [x] Rellena tu propia tabla "qué cabe / qué no" para tus modelos.
- [x] Comprueba cuánto swap hay en reposo (`vm.swapusage`). → En reposo ya había **47,5 MB** usados (no 0), y tras la prueba del 27B el sistema quedó con **≈3,7 GiB** en uso: macOS no devuelve el swap solo.

---

## 1.2. Stack local real (Ollama, LM Studio, Git)

**Ollama** es el motor de inferencia local que usará el curso. En este equipo **viene con la app de escritorio `Ollama.app`**, que ya arranca sola y ocupa el puerto **11434**. **No** instales Ollama por Homebrew ni ejecutes `brew services start ollama` mientras la app esté activa: tendrías dos servidores peleando por el mismo puerto.

```bash
# Comprobar que Ollama responde
curl -s http://localhost:11434/api/tags | head -20
```

**LM Studio** expone una API compatible con OpenAI en el puerto **1234** y trae el CLI `lms`:

```bash
lms status
lms ls
```

**Git (arm64 nativo):** este equipo ya está migrado a **arm64 nativo** (Homebrew en `/opt/homebrew`, sin Rosetta ni MacPorts), así que `git` funciona directamente:

```bash
git status
git add -A
git commit -m "..."
```

> Histórico: hasta el 2026-10-31 la terminal arrancaba en x86_64 (Rosetta) y hacía falta
> `arch -arm64 /usr/bin/git ...`. Ese apaño **ya no es necesario**.

**Práctica 1.2** ✅

- [x] `curl` de `/api/tags` devuelve JSON. → 3 modelos (`qwen3.5:9b`, `qwen3.8:27b`, `nomic-embed-text:latest`).
- [x] `lms status` responde. → `Server: OFF` (el CLI existe en `~/.lmstudio/bin/lms`; el servidor de LM Studio **no** hace falta levantarlo en este curso).
- [x] `uname -m` muestra `arm64` y `git --version` responde sin `arch -arm64`. → `arm64`, `git version 2.54.0 (Apple Git-157)`.

---

## 1.3. Modelos: 9B vs. 27B, GGUF vs. pull

Para 24 GB, la guía de referencia (octubre de 2026) es clara: **Qwen3.8 27B** es la mejor opción "todo terreno" para calidad, con un **79,8 % en Terminal-Bench 2.1**; **Qwen3.5 9B** es el caballo de batalla para iterar rápido y bucles con mucho contexto.

Medido en este equipo con `ollama list` / `ollama show` (2026-11-11):

| Modelo | Tamaño en disco | Cuantización | Parámetros | ctx máx. | Capacidades |
|---|---|---|---|---|---|
| `qwen3.5:9b` | 5,7 GB | Q4_K_M | 9,0 B | 262 144 | tools, thinking, completion |
| `qwen3.8:27b` | 18 GB | nvfp4 (runner **mlx**) | 27,8 B | 262 144 | tools, thinking, vision, completion |

> Ojo: el 27B instalado **no** es el GGUF `UD-Q4_K_M` que describe `Modelfile.qwen3.8-27b`, sino una build **nvfp4 con runner MLX** (formato de la librería de Ollama, `requires 0.32.12`). Por eso `ollama show` no le muestra `num_ctx` y `ollama ps` lo ejecuta con `RUNNER mlx` en vez de `llamacpp`.

**Vía oficial** (cuando la red lo permite):

```bash
ollama pull qwen3.5:9b
ollama pull qwen3.8:27b
```

**Vía local desde GGUF** (la que sí se usó para el 9B en este equipo, porque el CDN de blobs de Ollama no era accesible desde esta red). Las recetas están en `Modelfile.qwen3.5-9b` y `Modelfile.qwen3.8-27b`:

```bash
ollama create qwen3.5:9b  -f Modelfile.qwen3.5-9b
ollama create qwen3.8:27b -f Modelfile.qwen3.8-27b
```

> **Estado real de los modelos instalados:** `qwen3.5:9b` sí procede de `Qwen3.5-9B-Q4_K_M.gguf` (formato `gguf`); `qwen3.8:27b` es hoy una build **`safetensors` + nvfp4** de la librería de Ollama, **no** el GGUF `UD-Q4_K_M` de su `Modelfile`. Los `.gguf` fuente se borraron (21 GB liberados), así que `ollama create ... -f Modelfile.*` solo sirve si vuelves a descargar los GGUF en `gguf/`.

**Alternativas útiles** (no las descargues todas):

- **`gpt-oss:20b`** (≈14 GB): buen *function calling* nativo, Apache 2.0.
- **`qwen3.6:35b`** (MoE, ≈23–24 GB): rápido por tokens activos, pero roza el límite de tu RAM; solo para experimentos puntuales.

**Contexto y RAM (real):** el `Modelfile.qwen3.5-9b` fija `num_ctx 8192`, pero el 9B cargado reporta `ctx 16200` (≈16K): algún cliente (Cline/Aider) pide más contexto al cargarlo. El 27B instalado no lleva `num_ctx` fijado, así que **el contexto se decide al cargar** (`./ollama-helper.sh` usa 8192). Regla práctica: cada 1K tokens de contexto extra con el 27B cuesta RAM de verdad y acerca el swap.

**Práctica 1.3** ✅

- [x] `ollama show qwen3.5:9b` y `ollama show qwen3.8:27b` muestran la capacidad `tools` (ojo: `ollama list` **no** lista capacidades, solo nombre/tamaño/fecha).
- [x] RAM/swap antes y después de cargar el 27B → `swap used` 47,5 MB → **4 064,6 MB** (tabla de medición real en 1.1).
- [x] `ollama ps` confirma qué modelo está en memoria → `qwen3.8:27b`, 18 GB, 100 % GPU, ctx 8192, `RUNNER mlx`.

---

## 1.4. Tool calling: el corazón de un agente

Un agente sin *tool calling* es solo un chatbot. El *tool calling* permite que el modelo **pida ejecutar una función** (buscar, leer un archivo, llamar a una API) y que tu código la ejecute. Antes de escribir Python, comprueba que el modelo lo hace de verdad.

```bash
curl -s http://localhost:11434/api/chat -d '{
  "model": "qwen3.5:9b",
  "messages": [{"role": "user", "content": "¿Qué tiempo hace en Madrid?"}],
  "tools": [{
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Obtiene el tiempo de una ciudad",
      "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"]
      }
    }
  }],
  "stream": false
}' | python3 -m json.tool
```

**Qué buscar:** un bloque `tool_calls` con `"name": "get_weather"` y `"arguments"`. Ollama 0.40 devuelve `arguments` como **objeto**; algunos ejemplos esperan **string JSON**. Ambos son válidos para el cliente Python y LangChain.

**Cómo se ejecuta el tool call (concepto):**

1. El modelo devuelve `tool_calls` (no ejecuta nada).
2. Tu código lee el nombre y los argumentos, **ejecuta** la función real.
3. Devuelves el resultado al modelo como mensaje `role: tool`.
4. El modelo genera la respuesta final.

**Práctica 1.4** ✅

- [x] El `curl` devuelve un `tool_calls` válido (no texto plano) → `get_weather{"city":"Madrid"}`, `arguments` como **objeto** y `content` vacío.
- [x] Repite el test con `qwen3.8:27b` → mismo formato de `tool_calls`, pero **32,95 s** frente a 3,05 s del 9B.
- [x] Define una **segunda** tool (ej. `get_time(city)` o `convert_currency`) y pide algo que requiera las dos → con `get_weather` + `get_weather_forecast` + `get_time` y la pregunta *"¿Qué tiempo hace en Madrid y qué hora es allí?"*, el modelo devuelve **dos `tool_calls` en el mismo mensaje** (`index` 0 y 1) y resuelve *"allí"* → `city: "Madrid"` por correferencia.

Medición real en este equipo (24 GiB, 2026-11-11). Recuerda: las duraciones de Ollama vienen en **nanosegundos** → divide entre `1e9`:

| Medición | `qwen3.5:9b` (1 tool) | `qwen3.8:27b` (1 tool) | `qwen3.5:9b` (3 tools, 2.ª llamada) |
|---|---|---|---|
| `total_duration` | 3,05 s | **32,95 s** | 1,27 s |
| `load_duration` | 1,06 s | **10,81 s** | 0,001 s (modelo caliente) |
| `prompt_eval_count` | 275 | 277 | 402 |
| `prompt_eval_cached_count` | 0 | 0 | **378 (94 %)** |
| `prompt_eval_duration` | 0,44 s ≈ **619 tok/s** | 20,77 s ≈ **13 tok/s** | 0,19 s |
| `eval_count` / `eval_duration` | 72 / 1,54 s ≈ 47 tok/s | 25 / 1,30 s ≈ **19 tok/s** | 52 / 1,08 s ≈ 48 tok/s |

Conclusiones medidas:

- **El prefill domina, no la generación.** Con el 27B, 20,8 s de 32,95 s (63 %) se fueron en *leer* el prompt, y solo 1,3 s en escribir. Y en el 9B el prefill va a 619 tok/s frente a 13 tok/s del 27B: **46× más lento** en la fase que un agente repite en cada paso. Con 3,3 GB de swap usados, ese prefill estaba paginando a disco.
- **Cada tool cuesta prompt en cada llamada:** 275 → 397 tokens solo por añadir dos herramientas (≈61 por tool). 20 tools ≈ 1 200 tokens fijos por paso.
- **KV cache:** con el mismo `system` + `tools`, Ollama reutiliza 378 de 402 tokens (`prompt_eval_cached_count`) y el total baja de 2,32 s a 1,27 s. Por eso el prompt estable va al principio y lo nuevo al final.
- **`arguments` es un objeto** (no string) tanto en 9B como en 27B, con Ollama 0.40.

> **Dos lecciones que valen más que el test:**
> 1. `tool_calls` es un **array**: si tu código ejecuta solo `tool_calls[0]`, la segunda herramienta nunca se ejecuta y el modelo responde a medias.
> 2. La `description` **no documenta, compite**: `get_weather` y `get_weather_forecast` con textos casi iguales son un bug esperando a pasar. Cada descripción debe decir cuándo SÍ y cuándo NO usar esa tool.

---

## 1.5. Entorno Python para agentes

Crea (o reutiliza) un entorno virtual dedicado. En este workspace ya existe `.venv` en la raíz del proyecto:

```bash
cd agentes-locales
source .venv/bin/activate

# Si tuvieras que crearlo desde cero:
# python3 -m venv .venv && source .venv/bin/activate

pip install ollama langgraph langchain langchain-ollama python-dotenv rich
```

> **Nota (2026-11-11):** el `.venv` se **recreó en arm64**. El anterior se había creado bajo
> Rosetta y fallaba al importar `ollama` (`pydantic_core` era un `.so` x86_64 →
> `incompatible architecture`). Si vuelves a ver ese error, borra `.venv`, recréalo con
> `python3 -m venv .venv` y reinstala.

**Práctica 1.5** ✅

- [x] `.venv` activado → prompt `(.venv)` y `which python` = `…/agentes-locales/.venv/bin/python`, **Python 3.12.9 arm64**.
- [x] `pip list` muestra `langgraph`, `langchain-ollama` y `ollama` → `ollama 0.6.3`, `langchain-ollama 1.1.0`, `langchain-core 1.8.0`, `langgraph 1.2.19` (+ `langgraph-checkpoint 4.3.1`, `langgraph-prebuilt 1.1.1`).
- [x] `python -c "import ollama, langgraph; print('OK')"` imprime `OK`.

> **Trampa a recordar:** si vuelve el error `incompatible architecture (have 'arm64', need 'x86_64')` al importar `ollama`, el `.venv` se creó bajo Rosetta → bórralo, recréalo con `python3 -m venv .venv` y reinstala. Ya pasó una vez (ver nota de arriba).

---

## 1.6. Prompt Engineering para agentes

Un prompt de agente debe tener **cinco partes**:

1. **Rol acotado:** no "eres útil", sino "eres un agente que solo puede usar las herramientas X, Y, Z".
2. **Herramientas y cuándo usarlas:** descripciones claras y nombres cualificados.
3. **Formato de salida rígido:** si esperas JSON, dilo explícitamente y prohíbe texto adicional.
4. **Condiciones de parada:** "detente cuando el test pase" o "tras 3 intentos devuelve `NO_ENCONTRADO`".
5. **Presupuesto:** número máximo de pasos o tokens.

### Ejercicio base: agente de resumen con salida JSON estricta

Crea `prompt_agente.py`:

```python
import ollama, json

SYSTEM = """Eres un agente de resumen. Recibes el contenido de un archivo de texto.
Debes devolver EXCLUSIVAMENTE un JSON válido con esta forma:
{"resumen": "<3 líneas>", "palabras_clave": ["...", "..."]}
No añadas explicaciones, markdown ni texto fuera del JSON.
Si el texto tiene menos de 10 palabras, devuelve {"error": "texto demasiado corto"}."""

def resumir(texto: str) -> dict:
    resp = ollama.chat(
        model="qwen3.5:9b",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": texto},
        ],
        format="json",  # fuerza JSON válido
        options={"temperature": 0.1},
    )
    return json.loads(resp["message"]["content"])

if __name__ == "__main__":
    muestra = "Los agentes locales permiten automatizar tareas sin enviar datos a la nube. " * 5
    print(resumir(muestra))
```

**Criterio de éxito:** ejecútalo **10 veces** con el mismo texto; debe devolver JSON válido las 10. Si falla, endurece el system prompt y baja la temperatura.

> **Rendimiento medido (2026-11-11):** `qwen3.5:9b` activa el *thinking* de Qwen3 y tarda
> **~50 s** por llamada. Con `think=False` y `num_predict` acotado baja a **~1 s** y sigue
> cumpliendo 10/10. El script de este workspace ya lo aplica:
> `.venv/bin/python prompt_agente.py --test 10` → `Resultado: 10/10` en ~9 s.

**Práctica 1.6 (varios mini-agentes de un paso)** — para cada uno: system prompt con los 5 elementos + criterio 10/10:

- [x] **Clasificador:** devuelve `{"categoria": "...", "confianza": 0-1}` para tickets de soporte.
  → hecho en `clasificador.py` con **contrato ampliado a 4 claves** (`categoria`, `urgencia`, `estado`, `comentario`) en lugar de `confianza` 0-1: un LLM no calibra ese número y no hay forma de validarlo. `--test 10` → **10/10** (~1 s/llamada con `think=False`); `bateria.py` (6 casos difíciles) → **6/6 coherentes**. Ver nota **[Diseño del clasificador]**.
- [ ] **Extractor de entidades:** devuelve `{"personas": [], "lugares": [], "fechas": []}`.
- [ ] **Corrector con restricciones:** corrige gramática **sin cambiar** el significado; devuelve `{"texto": "...", "cambios": [...]}`.
- [ ] **Generador YAML:** convierte un texto en YAML válido y bien indentado.
- [ ] **Compara temperaturas:** ejecuta el clasificador con `temperature` 0.1 vs 0.9 y explica las diferencias.

**[Diseño del clasificador]** — decisiones tomadas midiendo, no opinando:

| Decisión | Por qué |
|---|---|
| `urgencia` en vez de `confianza` 0-1 | Un 0.87 de un LLM no está calibrado y no se puede validar; un enum cerrado sí. |
| `categoria` como **lista cerrada** | Permite `validar()` determinista (`dato["categoria"] in CATEGORIA`). |
| `estado` ∈ {`ok`, `insuficiente`, `no_ticket`} | Resuelve una colisión: "no es un ticket" (la luna de queso) vs. "es un ticket sin datos" ("no va."). Un booleano `suficiente` no distinguía ambas. |
| **Criterios de urgencia dentro del SYSTEM** | Se escribieron primero como dict en Python y el modelo nunca los veía → `alta`/`media` oscilaban. Una regla que el modelo no lee no existe. |
| Regla de coherencia **en código** | `estado != "ok" → categoria="otro" y urgencia="nula"`; el prompt la pide y `validar()` la exige. Ojo: `and` fuera / `or` dentro (ley de De Morgan); con `or` el validador rechazaría todos los tickets buenos. |
| **Batería de casos** con respuesta esperada | `--test 10` prueba la *forma*; `bateria.py` prueba el *contenido*. Un JSON puede ser válido y falso (p. ej. `ok + otro + nula` pasa el validador y es un error de clasificación). |

Tres fallos que solo aparecieron al pasar tickets distintos: falta de bandeja `facturacion`, urgencia sin criterios (`alta` para "no me llegan los correos") y la colisión `otro/nula`. Los tres, corregidos y re-medidos.

---

## 1.7. VS Code + Cline (opcional: Aider)

**Cline** es el agente de código dentro de VS Code, apuntando a tu Ollama local:

1. Abre VS Code → Extensiones → busca **Cline** → Instalar.
2. Configuración (engranaje):
   - **API Provider:** `Ollama`
   - **Base URL:** `http://localhost:11434`
   - **Model:** `qwen3.5:9b` (iterar) o `qwen3.8:27b` (calidad)
   - **Context Window:** ≥ 32768 con el 9B; con el 27B mantén 16384
3. En **Features**, activa **Use Compact Prompt**.

Prueba: pide a Cline *"Crea un archivo hola.py que imprima 'hola' y ejecútalo"*. Debe pedirte **aprobación** antes de ejecutar comandos.

**Aider (opcional):** convierte cada cambio en un commit de git (historial reversible ideal para agentes de código).

```bash
pip install aider-chat
export OLLAMA_API_BASE=http://127.0.0.1:11434
aider --model ollama_chat/qwen3.5:9b
```

**Práctica 1.7**

- [ ] Cline instalado y conectado a Ollama.
- [ ] Prueba de creación/ejecución de archivo con aprobación manual.
- [ ] (Aider) Un commit hecho por Aider con el modelo local.

---

## 🎯 Entregable de la Etapa 1

Construye un **agente de un solo paso** que combine varias habilidades en un flujo simple:

- **`agente_etapa1.py`**: recibe un texto (archivo o stdin) y devuelve un único JSON con:
  - `resumen` (3 líneas),
  - `categoria` (clasificación del tema),
  - `entidades` (personas/lugares/fechas),
  - `palabras_clave`.
- Reutiliza los mini-agentes de 1.6. Si alguna parte falla, el JSON debe devolver `{"error": ...}` en ese campo (robustez).
- **Criterio de aceptación:** 10 de 10 ejecuciones producen JSON válido y coherente; ninguna lanza excepción por parseo.

- [ ] `agente_etapa1.py` creado y ejecutado 10 veces con JSON válido.
- [ ] Documentado en `notas/aprendizajes.md` qué prompt ajustaste y por qué.

> Al completar este entregable dominas **prompt + tools + formato estricto**. Estás listo para la Etapa 2.

---

# 🟡 ETAPA 2 — INTERMEDIO: loops, verificación y grafos

**Duración sugerida:** 5 semanas · **Objetivo:** pasar de "un paso" a **sistemas que se autocorrigen**: bucles con verificación determinista, estado persistente y grafos con aristas condicionales.

---

## 2.1. Anatomía de un loop

Un agente *loop* repite: **Trigger → Act → Verify → Retry** hasta cumplir una condición.

| Fase | Pregunta | Ejemplo |
|---|---|---|
| **Trigger** | ¿Qué dispara el trabajo? | Un test que falla, un archivo que cambió. |
| **Act** | ¿Qué hace el modelo? | Propone un parche de código. |
| **Verify** | ¿Cómo sé si funcionó? | Ejecutar el test fuera del LLM (**determinista**). |
| **Retry** | ¿Qué hago si falla? | Reintentar con el error como feedback. |

**Anti-patrón #1:** dejar que el LLM "verifique" su propio trabajo sin comprobación externa. Se autoengaña.

**Práctica 2.1**

- [ ] Dibuja (a mano o en Mermaid) el ciclo de un loop con sus 4 fases.
- [ ] Identifica en tu vida un proceso que se pueda convertir en loop.

---

## 2.2. Verificación determinista vs. LLM

La regla del curso: **lo que se pueda verificar con código, se verifica con código**.

| Verificación | Herramienta | Coste | Fiabilidad |
|---|---|---|---|
| ¿El JSON es válido? | `json.loads` | 0 | 100 % |
| ¿El test pasa? | `pytest` / `subprocess` | 0 | 100 % |
| ¿La salida es correcta semánticamente? | **LLM juez** | tokens | alta pero no infalible |

**Verificación determinista:**

```python
import json

def verificar_json(texto: str) -> bool:
    try:
        data = json.loads(texto)
        return all(k in data for k in ("resumen", "palabras_clave"))
    except json.JSONDecodeError:
        return False
```

**LLM juez (solo cuando no hay código posible):**

```python
JUEZ = """Compara la RESPUESTA con el CRITERIO y devuelve solo un JSON:
{"aprobado": true|false, "motivo": "<breve>"}"""

def juzgar(respuesta: str, criterio: str) -> dict:
    resp = ollama.chat(
        model="qwen3.5:9b",
        messages=[
            {"role": "system", "content": JUEZ},
            {"role": "user", "content": f"CRITERIO: {criterio}\nRESPUESTA: {respuesta}"},
        ],
        format="json",
        options={"temperature": 0},
    )
    return json.loads(resp["message"]["content"])
```

**Práctica 2.2**

- [ ] Escribe un verificador determinista para tu entregable E1 (caso sin parseo).
- [ ] Añade un juez LLM para lo que no se puede verificar con código.
- [ ] Combina ambos en `verificar(resultado) -> (bool, motivo)`.

---

## 2.3. Estado y memoria

Un loop sin estado repite errores. Guarda **cada intento** en un JSON o SQLite.

```json
{
  "objetivo": "corregir funcion.py hasta que pase los tests",
  "intentos": [
    {"n": 1, "parche": "...", "resultado": "FAIL: test_suma", "tiempo_s": 12},
    {"n": 2, "parche": "...", "resultado": "PASS", "tiempo_s": 9}
  ],
  "estado": "COMPLETADO"
}
```

**Cuándo usar qué:**

- **JSON:** pocos datos, inspección manual, prototipos.
- **SQLite:** muchos registros, consultas por estado, varios procesos.

**Práctica 2.3**

- [ ] Guarda el historial de intentos en `loop_estado.json`.
- [ ] Haz que el loop lea el estado previo al arrancar (reanudación básica).
- [ ] (Plus) Migra el estado a SQLite y consulta `SELECT * FROM intentos WHERE estado='FAIL'`.

---

## 2.4. Presupuesto y condiciones de parada

Todo loop necesita un **freno**: máximo de intentos, tiempo o tokens, y una salida limpia cuando se agota.

```python
MAX_INTENTOS = 3

for n in range(1, MAX_INTENTOS + 1):
    salida = actuar(estado)
    ok, motivo = verificar(salida)
    estado["intentos"].append({"n": n, "resultado": motivo})
    if ok:
        estado["estado"] = "COMPLETADO"
        break
else:
    estado["estado"] = "NO_LOGRADO"  # salida explícita, no excepción
guardar(estado, "loop_estado.json")
```

**Anti-patrón #2:** loop sin `break` ni presupuesto → ejecución infinita y RAM/CPU al 100 %.

**Práctica 2.4**

- [ ] Añade `MAX_INTENTOS`, `MAX_SEGUNDOS` y un estado `NO_LOGRADO` a tu loop.
- [ ] Fuerza un caso donde se agote el presupuesto y verifica la salida limpia.

---

## 2.5. LangGraph: el grafo de agentes

LangGraph modela un agente como un **grafo de estados**: nodos (funciones) y aristas (transiciones). Un loop es un grafo con una arista que vuelve atrás.

```bash
pip install langgraph langchain-ollama
```

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama

class Estado(TypedDict):
    tarea: str
    plan: str
    borrador: str
    revision: str
    aprobado: bool

llm = ChatOllama(model="qwen3.5:9b", temperature=0.1)

def planificador(estado: Estado) -> dict:
    plan = llm.invoke(f"Haz un plan de 3 pasos para: {estado['tarea']}").content
    return {"plan": plan}

def redactor(estado: Estado) -> dict:
    texto = llm.invoke(f"Escribe el texto siguiendo el plan:\n{estado['plan']}").content
    return {"borrador": texto}

def revisor(estado: Estado) -> dict:
    ok = len(estado["borrador"]) > 100  # verificación determinista
    return {"aprobado": ok, "revision": "OK" if ok else "DEMASIADO_CORTO"}

grafo = StateGraph(Estado)
grafo.add_node("planificador", planificador)
grafo.add_node("redactor", redactor)
grafo.add_node("revisor", revisor)

grafo.add_edge(START, "planificador")
grafo.add_edge("planificador", "redactor")
grafo.add_edge("redactor", "revisor")
grafo.add_edge("revisor", END)

app = grafo.compile()
print(app.invoke({"tarea": "Explica qué es un agente local"}))
```

**Práctica 2.5**

- [ ] Ejecuta el grafo anterior y guarda la salida.
- [ ] Añade al estado un campo `intentos` que se incremente en `redactor`.
- [ ] Cambia el `llm` a `qwen3.8:27b` y compara calidad/velocidad.

---

## 2.6. Grafo Planificador → Redactor → Revisor

El paso clave es la **arista condicional**: si el revisor no aprueba, volvemos al redactor.

```python
def decidir(estado: Estado) -> str:
    return "fin" if estado["aprobado"] else "reintentar"

grafo.add_conditional_edges("revisor", decidir, {
    "fin": END,
    "reintentar": "redactor",
})
```

Con esto el grafo **se autocorrige** sin código de loop manual. Añade un contador en el estado para no reintentar infinitamente:

```python
def redactor(estado: Estado) -> dict:
    n = estado.get("intentos", 0) + 1
    texto = llm.invoke(f"Mejora este borrador (intento {n}):\n{estado.get('borrador','')}").content
    return {"borrador": texto, "intentos": n}

def decidir(estado: Estado) -> str:
    if estado["aprobado"] or estado.get("intentos", 0) >= 3:
        return "fin"
    return "reintentar"
```

**Práctica 2.6**

- [ ] Convierte el grafo lineal de 2.5 en uno con arista condicional.
- [ ] Verifica que el flujo termina en ≤ 3 reintentos aunque el revisor siempre rechace.
- [ ] (Plus) Haz que el revisor devuelva una *crítica* que el redactor use como feedback.

---

## 2.7. Nodos deterministas (archivos y tests)

No todo debe hacerlo el LLM. Los mejores grafos tienen **nodos de código puro**:

```python
from pathlib import Path

def escribir_archivo(estado: Estado) -> dict:
    p = Path("salida.md")
    p.write_text(estado["borrador"], encoding="utf-8")
    return {"ruta": str(p)}

def ejecutar_tests(estado: Estado) -> dict:
    import subprocess
    r = subprocess.run(["python", "-m", "pytest", "-q"], capture_output=True, text=True)
    return {"aprobado": r.returncode == 0, "revision": r.stdout[-500:]}
```

**Práctica 2.7**

- [ ] Añade un nodo que escriba el resultado a un archivo.
- [ ] Añade un nodo que ejecute un test y marque `aprobado` según el exit code.
- [ ] Dibuja el grafo final diferenciando nodos LLM y deterministas.

---

## 🎯 Entregable de la Etapa 2

Un **grafo con loop interno autocorrectivo**:

- **`grafo_etapa2.py`**: `StateGraph` con al menos:
  - un nodo **determinista** (lee archivo / valida / ejecuta test),
  - dos nodos **LLM** (ej. planificador y redactor/crítico),
  - una **arista condicional** que reintente hasta aprobar o agotar presupuesto.
- Estado persistido en JSON o SQLite tras cada ejecución.
- **Criterio de aceptación:** ejecutar 5 tareas distintas; todas terminan en `COMPLETADO` o `NO_LOGRADO` con motivo, sin excepciones ni loops infinitos.

- [ ] `grafo_etapa2.py` funciona con 5 tareas distintas.
- [ ] Estado persistido y reanudable.
- [ ] Diagrama del grafo en `notas/` (Mermaid o imagen).

> Al completar este entregable dominas **loops + grafos + verificación**. Estás listo para el multiagente.

---

# 🔴 ETAPA 3 — AVANZADO: multiagente en paralelo y proyecto final

**Duración sugerida:** 7 semanas · **Objetivo:** construir un **sistema multiagente** con tools propias, ejecución **en paralelo (fan-out / fan-in)**, orquestador/sintetizador y persistencia, todo sobre un único `qwen3.5:9b`.

> En 24 GB no puedes cargar un modelo grande por agente. La solución profesional: **un solo peso en memoria, muchos roles lógicos**, coordinados por LangGraph.

---

## 3.1. Tools propias con bind_tools

Hasta ahora las tools eran esquemas JSON. Ahora las defines como funciones Python y las enlazas al modelo:

```python
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

@tool
def leer_archivo(ruta: str) -> str:
    """Devuelve el contenido de un archivo de texto."""
    with open(ruta, encoding="utf-8") as f:
        return f.read()[:4000]

@tool
def listar_python(directorio: str) -> list[str]:
    """Lista los archivos .py de un directorio."""
    from pathlib import Path
    return [p.name for p in Path(directorio).glob("*.py")]

llm = ChatOllama(model="qwen3.5:9b", temperature=0.1)
llm_con_tools = llm.bind_tools([leer_archivo, listar_python])

resp = llm_con_tools.invoke("¿Cuántos archivos .py hay en . y qué hace el primero?")
print(resp.tool_calls)
```

El flujo es el mismo: el modelo emite `tool_calls`, tú ejecutas y devuelves `ToolMessage`.

**Práctica 3.1**

- [ ] Crea una tool de lectura y otra de listado.
- [ ] Ejecuta un mini-loop: invoca → ejecuta `tool_calls` → devuelve `ToolMessage` → responde.
- [ ] Añade una tool determinista (`ejecutar_tests`) y úsala solo cuando haga falta.

---

## 3.2. Multiagente en paralelo (fan-out / fan-in)

**Fan-out:** lanzas N tareas a la vez. **Fan-in:** reúnes y sintetizas los resultados.

```
            ┌─ Agente A (rol: seguridad) ──┐
Tarea ──► ──┤                              ├──► Orquestador/Sintetizador ──► Salida
            └─ Agente B (rol: rendimiento)─┘
```

En LangGraph se usa un nodo que escribe a una **clave de lista** en el estado, y un nodo de reducción:

```python
from concurrent.futures import ThreadPoolExecutor

def agente_rol(rol: str, contexto: str) -> str:
    prompt = f"Actúa como experto en {rol}. Analiza y responde breve:\n{contexto}"
    return llm.invoke(prompt).content

def fan_out(estado: dict) -> dict:
    roles = ["seguridad", "rendimiento"]
    with ThreadPoolExecutor(max_workers=len(roles)) as ex:
        resultados = list(ex.map(lambda r: agente_rol(r, estado["contexto"]), roles))
    return {"parciales": resultados}
```

> **Nota 24 GB:** con `qwen3.5:9b` (≈6–7,6 GB) caben **2–3 agentes en paralelo** con margen; con el 27B, **solo 1** a la vez. Ollama sirve peticiones concurrentes al mismo modelo sin recargarlo.

**Práctica 3.2**

- [ ] Implementa fan-out con 2 roles sobre un mismo texto.
- [ ] Verifica con `ollama ps` que sigue cargado un único modelo.
- [ ] Mide el tiempo del paralelo vs. en serie.

---

## 3.3. Orquestador y Sintetizador

El orquestador **decide qué roles lanzar**; el sintetizador **fusiona** las salidas en una respuesta única.

```python
import json

def orquestador(contexto: str) -> list[str]:
    pregunta = ("Lista los roles expertos necesarios para analizar este texto, "
                f'en JSON: {{"roles": [...]}}\n\n{contexto[:2000]}')
    resp = llm.invoke(pregunta).content
    try:
        return json.loads(resp).get("roles", ["general"])
    except Exception:
        return ["general"]

def sintetizador(parciales: list[str]) -> str:
    unido = "\n\n---\n\n".join(parciales)
    prompt = ("Fusiona estos análisis en uno solo, sin repetir y sin inventar:\n\n" + unido)
    return llm.invoke(prompt).content
```

**Práctica 3.3**

- [ ] Haz que el orquestador decida los roles dinámicamente (no fijos).
- [ ] Añade los campos `parciales` y `sintesis` al estado del grafo.
- [ ] Mide cuántas llamadas al modelo hace el flujo completo.

---

## 3.4. Persistencia y reanudación

LangGraph trae **checkpointing**: guarda el estado tras cada nodo y permite reanudar.

```python
from langgraph.checkpoint.sqlite import SqliteSaver

memoria = SqliteSaver.from_conn_string("checkpoints.sqlite")
app = grafo.compile(checkpointer=memoria)

config = {"configurable": {"thread_id": "tarea-001"}}
app.invoke({"contexto": "..."}, config=config)
# Si el proceso muere, reanudas con el mismo thread_id:
app.invoke({}, config=config)
```

**Práctica 3.4**

- [ ] Compila un grafo con `SqliteSaver` y ejecútalo.
- [ ] Mata el proceso a mitad y reanuda con el mismo `thread_id`.
- [ ] Inspecciona la tabla de checkpoints y explica su estructura.

---

## 3.5. Observabilidad y depuración

Cuando hay 3 agentes en paralelo, sin trazas no sabes quién falló.

- **Logs estructurados:** cada llamada con `nodo`, `rol`, `tokens`, `ms`, `ok`.
- **LangSmith / LangFuse:** trazas visuales de LangGraph (opcional; cuestan red).
- **Local mínimo:** un `trazas.jsonl` con una línea por evento.

```python
import json, time

def traza(nodo: str, **datos):
    with open("trazas.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"t": time.time(), "nodo": nodo, **datos}, ensure_ascii=False) + "\n")
```

**Práctica 3.5**

- [ ] Añade `traza()` a los nodos de tu grafo.
- [ ] Genera un informe con `jq` o Python: nodos más lentos, nº de fallos.
- [ ] (Plus) Prueba LangSmith una vez y decide si compensa.

---

## 3.6. Cline + Aider en el flujo real

Integra el agente de código como **constructor** dentro del proyecto:

1. **Cline** para tareas interactivas multi-archivo (escribe, ejecuta, aprueba).
2. **Aider** para cambios rastreables en git (`--auto-commits`).
3. **Tu grafo** para tareas automáticas (análisis, revisión).

**Práctica 3.6**

- [ ] Haz un cambio multi-archivo con Cline y revísalo como PR.
- [ ] Haz un cambio con Aider y compara la historia de commits.
- [ ] Documenta cuándo usar Cline vs Aider vs tu grafo.

---

## 3.7. Proyecto final: agente de mantenimiento de repositorio en paralelo

**Objetivo:** un sistema que, dado un repositorio, ejecuta en paralelo:

| Hito | Semanas | Qué construyes |
|---|---|---|
| **H1 — Esqueleto** | 15 | Grafo con nodos `orquestador`, `fan_out`, `sintetizador`, `persistencia` |
| **H2 — Agentes A/B** | 15 | `Agente A (calidad de código)` y `Agente B (seguridad)` con tools propias |
| **H3 — Paralelo + fusión** | 16 | `ThreadPoolExecutor` 2–3 workers (todo 9b) + síntesis |
| **H4 — Persistencia + informe** | 16 | Checkpoints SQLite, reanudación y `informe.md` final |

**Arquitectura objetivo:**

```python
import operator
from typing import Annotated, TypedDict

class EstadoFinal(TypedDict):
    repo: str
    roles: list[str]
    parciales: Annotated[list[str], operator.add]  # fan-in
    sintesis: str
    informes: list[str]

# START → orquestador → fan_out → fan_in(sintetizador) → END
# checkpointer=SqliteSaver, thread_id por repo
```

**Criterios de aceptación:**

- [ ] Ejecutarse con **un único modelo cargado** (`ollama ps` muestra solo `qwen3.5:9b`).
- [ ] 2–3 agentes en paralelo por tarea; tiempo total < suma de tiempos en serie.
- [ ] Reanudable tras matar el proceso.
- [ ] Informe final `informe.md` con hallazgos de cada rol y síntesis.
- [ ] Ejecutable 10 veces seguidas sin fugas de RAM (vigila swap).

## 🎯 Entregable de la Etapa 3

El sistema `mtto_repo.py` del proyecto final cumpliendo todos los criterios anteriores, documentado en el `README.md` del proyecto:

- [ ] Código fuente funcional.
- [ ] Diagrama del grafo (Mermaid).
- [ ] Trazas `trazas.jsonl` + ejemplo de informe.
- [ ] Notas de aprendizajes (qué ajustaste, métricas antes/después).

> Has completado el curso: **construyes sistemas de agentes locales** con planificación, paralelismo y persistencia — sin salir de tu Mac.

---

# Calendario de 16 semanas

| Semana | Etapa | Foco | Entregable |
|---|---|---|---|
| 1 | 🟢 1 | Hardware + stack + modelos | Checklist + `ollama list` correcto |
| 2 | 🟢 1 | Tool calling | `curl` con `tool_calls` válido (✅ hecho) |
| 3 | 🟢 1 | Prompt engineering | `prompt_agente.py` (JSON 10/10) |
| 4 | 🟢 1 | Prompt avanzado + Cline | **E1**: `agente_etapa1.py` |
| 5 | 🟡 2 | Anatomía del loop + verificación | Loop con verificación determinista |
| 6 | 🟡 2 | Estado + presupuesto | `loop_estado.json` reanudable |
| 7 | 🟡 2 | LangGraph básico | `StateGraph` de 3 nodos |
| 8 | 🟡 2 | Grafo condicional | Autocorrección con ≤ 3 reintentos |
| 9 | 🟡 2 | Nodos deterministas | **E2**: `grafo_etapa2.py` |
| 10 | 🔴 3 | Tools propias | `bind_tools` con 2 tools reales |
| 11 | 🔴 3 | Fan-out / fan-in | 2 agentes en paralelo (9b) |
| 12 | 🔴 3 | Orquestador/Sintetizador | Salida fusionada |
| 13 | 🔴 3 | Persistencia | `SqliteSaver` + reanudación |
| 14 | 🔴 3 | Observabilidad + Cline/Aider | `trazas.jsonl` + PR multi-archivo |
| 15 | 🔴 3 | Proyecto final H1-H2 | Esqueleto + agentes A/B |
| 16 | 🔴 3 | Proyecto final H3-H4 | **E3**: `mtto_repo.py` completo |

**Ritmo flexible:** si vas sobrado, comprime las semanas de integración (4, 9, 14). Si vas justo, alarga la Etapa 3 a 9 semanas.

---

# Apéndice A — Solución de problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `curl localhost:11434` → connection refused | Ollama.app no está arrancada | Abre `Ollama.app`; **no** uses `brew services` |
| `ollama pull` se cuelga | CDN de blobs inaccesible | Vía GGUF + `Modelfile.*` + `ollama create` |
| El modelo ignora las tools | `tools` mal formado | Revisa `"type": "function"` y el JSON Schema |
| El modelo devuelve texto en vez de JSON | `format` no forzado | `format="json"` + `temperature` baja |
| El modelo "alucina" verificación | Verificación hecha por el LLM | Usa `pytest`/`json.loads` (determinista) |
| Swap disparado | Modelo grande + contexto largo | Baja `num_ctx` o usa el 9B |
| `invalid tool call arguments for "editor"` | Edición > ~6000 chars en una sola llamada | Divide en fragmentos pequeños |

---

# Apéndice B — Referencias rápidas de comandos

```bash
# Ollama
curl -s http://localhost:11434/api/tags | python3 -m json.tool
ollama list
ollama ps
ollama run qwen3.5:9b
ollama create qwen3.5:9b -f Modelfile.qwen3.5-9b

# LM Studio
lms status
lms ls

# Git (arm64 nativo)
git status
git diff --stat

# Python
source .venv/bin/activate
python -c "import ollama, langgraph; print('OK')"
```

---

# Apéndice C — Estructura real del workspace

```
agentes-locales/
├── README.md                     # índice operativo
├── curso-agentes-locales.md      # este curso (3 etapas)
├── NOTAS-MODULO1.md              # desviaciones reales respecto al curso
├── ollama-helper.sh              # helper: estado, RAM/swap, modelos
├── Modelfile.qwen3.5-9b          # receta desde GGUF (9B)
├── Modelfile.qwen3.8-27b         # receta desde GGUF (27B)
├── .aider.conf.yml               # config de Aider → Ollama
├── .cline/env                    # config de Cline → Ollama
├── scripts/
│   ├── 01_analisis_duplicados.py        # informativo (obsoleto)
│   ├── 03_auditoria_blobs_huerfanos.py  # auditor de blobs por SHA256
│   └── entorno/
│       ├── ollama-env.sh                # variables de Ollama (sourceado)
│       └── verificar_memoria.sh         # pre-flight de RAM
├── .venv/                        # entorno Python 3.12 (ignorado)
└── .gitignore
```

> Los modelos `qwen3.5:9b` / `qwen3.8:27b` ya están importados en `~/.ollama/models`.
> Los `.gguf` de origen se borraron para liberar 21 GB.

---

# Apéndice D — Extensiones recomendadas de VS Code

| Extensión | Para qué |
|---|---|
| **Cline** | Agente de código dentro del editor |
| **Markdown All in One** | Índices, preview, atajos |
| **Python** | Intérprete, linting, debugging |
| **SQLite Viewer** | Inspeccionar `checkpoints.sqlite` |
| **Even Better TOML** | `Modelfile` y configuraciones |
| **GitLens** | Historial de cambios del agente |

---

# Apéndice E — Glosario y checklist de conceptos

| Concepto | Definición breve |
|---|---|
| **Tool calling** | El modelo pide ejecutar una función; tu código la ejecuta |
| **Loop** | Ciclo Trigger→Act→Verify→Retry hasta cumplir condición |
| **Grafo** | Estados + nodos + aristas (LangGraph) |
| **Arista condicional** | Transición decidida por una función (p. ej. aprobado sí/no) |
| **Fan-out / fan-in** | Lanzar N tareas en paralelo y reunir resultados |
| **Checkpoint** | Estado persistido tras cada nodo (reanudable) |
| **Verificación determinista** | Comprobar con código (tests, JSON), no con el LLM |
| **MoE** | Mezcla de expertos: pocos parámetros activos por token |

**Checklist final:**

- [ ] Sé explicar la diferencia entre *prompt*, *loop* y *grafo*.
- [ ] Sé cuándo usar verificación determinista vs. LLM juez.
- [ ] Sé crear un grafo LangGraph con nodos LLM y deterministas.
- [ ] Sé montar fan-out con 2–3 agentes sobre un único modelo.
- [ ] Sé persistir y reanudar estado con `SqliteSaver`.
- [ ] Sé medir rendimiento (tiempos, swap, tokens).

---

*Curso de agentes locales — M5 24 GB. Todo lo que aparece aquí se ejecuta en tu Mac.*
