# Curso: De Cero a Master en LLMs Locales, Agentes y Orquestación Multiagente

**Hardware:** Mac Apple Silicon M5 · 24 GB RAM unificada · macOS (2026)
**Stack base ya instalado:** Ollama · LM Studio · LM Studio Bionic
**Objetivo:** Pasar de usuario de chatbots a diseñador de sistemas de agentes (Prompt → Loop → Graph → Multiagente) ejecutándose 100 % en local.

> **Cómo usar este documento.** Marca las casillas `[ ]` a medida que completes cada paso. Cada módulo tiene un *Entregable* que demuestra que puedes pasar al siguiente. Abre este archivo en VS Code y usa `Cmd+Shift+V` para ver la vista renderizada.

---

## Índice

0. [Diagnóstico y fundamentos del hardware](#módulo-0--diagnóstico-y-fundamentos-del-hardware)
1. [Instalación y configuración del stack](#módulo-1--instalación-y-configuración-del-stack-completo)
2. [Prompt Engineering para agentes](#módulo-2--prompt-engineering-para-agentes)
3. [Loop Engineering](#módulo-3--loop-engineering-el-agente-que-se-corrige-solo)
4. [Graph Engineering con LangGraph](#módulo-4--graph-engineering-del-loop-al-grafo-de-agentes)
5. [Multiagente y proyecto final](#módulo-5--multiagente-y-proyecto-final)
6. [Calendario de 10 semanas](#módulo-6--calendario-de-10-semanas-seguimiento)
7. [Apéndices](#apéndice-a--solución-de-problemas-frecuentes)

---

## Módulo 0 — Diagnóstico y fundamentos del hardware

### 0.1. Qué puede y qué no puede hacer tu M5 de 24 GB

| Sí puedes | No debes intentar |
|---|---|
| Modelos densos de **9B–27B en Q4** (≈6–18 GB). | Modelos de **70B** (ni cuantizados). |
| Modelos **MoE** con pocos parámetros activos (ej. 35B-A3B). | *Fan-out* masivo de agentes con modelos de 27B. |
| Contextos de **decenas de miles de tokens** con margen. | Contextos de 256K con un modelo de 18 GB cargado. |
| Orquestar varios agentes **en serie** o con modelos pequeños en paralelo. | Ejecutar dos modelos de 27B simultáneamente con fluidez. |

**Regla de oro:** la RAM es compartida entre pesos del modelo, KV cache y el resto del sistema. Un modelo de 18 GB en Q4 deja muy poco margen para contexto largo; para agentes con muchas herramientas, prioriza modelos de **9B–14B** o usa el 27B con prompts compactos.

**Decisión de este curso (24 GB):** los ejercicios de multiagente se harán con **un solo `qwen3.5:9b`** cargado una vez y reutilizado por todos los roles (agente A, agente B y orquestador/sintetizador), probando **agentes en paralelo** (fan-out / fan-in). El 27B queda para pruebas puntuales de calidad, **nunca** para multiagente concurrente, porque no hay RAM para dos modelos grandes a la vez.

- [ ] He leído y entendido las limitaciones de mi hardware.

### 0.2. Diagnóstico del entorno actual

Ejecuta en Terminal:

```bash
# 1. Verificar Homebrew
brew --version

# 2. Verificar Python (necesitarás 3.10+)
python3 --version

# 3. Verificar Ollama y modelos
ollama --version
ollama list

# 4. Comprobar que el servidor de Ollama responde
curl -s http://localhost:11434/api/tags | head -20

# 5. Verificar el CLI de LM Studio
lms status
lms ls

# 6. Comprobar si Bionic tiene modelos o está sirviendo
ls -la ~/.lmstudio/models 2>/dev/null | head
```

- [ ] Homebrew instalado y funcional.
- [ ] Python 3.10+ disponible.
- [ ] Ollama responde en `localhost:11434`.
- [ ] `lms` reconocido y LM Studio localizado.

**Nota sobre Bionic.** LM Studio Bionic es el **agente de LM Studio para modelos abiertos** (coding, research, documentos). No sustituye a LM Studio: se apoya en su runtime para la inferencia local y añade una capa de agente con edición de código, búsqueda agéntica y manejo de archivos. En este curso lo usarás como *banco de pruebas visual* de tareas agénticas, pero la orquestación programática la harás con Ollama + Python/LangGraph.

---

## Módulo 1 — Instalación y configuración del stack completo

### 1.1. Herramientas base

Si en el diagnóstico faltó algo, instálalo ahora.

```bash
# Homebrew (si no lo tienes)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python moderno (si el del sistema es antiguo)
brew install python@3.12

# Git (normalmente ya viene, pero por si acaso)
brew install git
```

- [ ] Homebrew, Python 3.12 y Git listos.

### 1.2. Ollama: configuración como servicio

Aunque ya lo tengas, asegúrate de que arranca automáticamente y de que el servidor está accesible.

```bash
# Instalación/actualización vía Homebrew
brew install ollama
# o, si ya está instalado:
brew upgrade ollama

# Arrancar el servicio en segundo plano
brew services start ollama

# Verificar
curl http://localhost:11434/api/tags
```

- [ ] Ollama corre como servicio y responde en el puerto 11434.

### 1.3. LM Studio y Bionic: servidor local y CLI

LM Studio expone una API compatible con OpenAI en el puerto **1234** por defecto. El CLI `lms` viene incluido en versiones recientes de LM Studio (0.2.22+).

```bash
# Comprobar el estado del servidor de LM Studio
lms status

# Arrancar el servidor si no está activo
lms server start

# Listar modelos descargados en LM Studio
lms ls
```

Si `lms` no está en el PATH, abre LM Studio, ve a **Developer** y verifica que el servidor esté iniciado; el binario `lms` suele estar en `~/.lmstudio/bin/lms`. Puedes añadirlo al PATH:

```bash
echo 'export PATH="$HOME/.lmstudio/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

- [ ] `lms server start` funciona y el servidor responde en `http://localhost:1234`.
- [ ] `lms ls` lista al menos un modelo (si no, lo harás en el paso 1.4).

### 1.4. Modelos: qué descargar y en qué orden

Para 24 GB, la guía de referencia de octubre de 2026 es clara: **Qwen3.8 27B** (≈18 GB en Q4) es la mejor opción “todo terreno” para agentes, con un **79.8 % en Terminal-Bench 2.1**; para desarrollo rápido y bucles con mucho contexto, **Qwen3.5 9B** (≈6.6–7.6 GB) es el caballo de batalla.

Descarga **primero el 9B** (te permite iterar sin esperas) y **luego el 27B** (para cuando necesites calidad).

> **Nota del curso:** todos los ejercicios de agentes y el multiagente en paralelo se hacen con **`qwen3.5:9b`** (un solo modelo en RAM). El `qwen3.8:27b` se reserva para tareas puntuales de calidad que no requieran concurrencia.

```bash
# Modelo ligero para desarrollo de lógica de agentes y loops
ollama pull qwen3.5:9b

# Modelo “todo terreno” para el nodo orquestador y tareas de calidad
ollama pull qwen3.8:27b

# Verificar que ambos están y que soportan tool calling (tag "tools")
ollama list
```

**Alternativas útiles** (no las descargues todas; elige según necesidad):

- **`gpt-oss:20b`** (≈14 GB): buen *function calling* nativo, Apache 2.0.
- **`qwen3.6:35b`** (MoE, ≈23–24 GB): rápido por tokens activos, pero roza el límite de tu RAM; úsalo solo para experimentos puntuales.

- [ ] `qwen3.5:9b` descargado y ejecutable (`ollama run qwen3.5:9b`).
- [ ] `qwen3.8:27b` descargado.
- [ ] Confirmado que ambos tienen la etiqueta `tools` en `ollama list`.

### 1.5. Verificación crítica: tool calling real

Un agente sin *tool calling* es solo un chatbot. Antes de escribir una línea de Python, comprueba que el modelo emite llamadas a funciones estructuradas.

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

**Qué buscar:** en la respuesta debe aparecer un bloque `tool_calls` con `"name": "get_weather"` y `"arguments": "{\"city\":\"Madrid\"}"`. Los modelos modernos de Ollama (Qwen 3.5, Gemma 4, Llama 3.1+) soportan esto de forma nativa: el modelo emite `tool_calls` estructurados y tu código los ejecuta.

- [ ] El `curl` devuelve un `tool_calls` válido (no texto plano).
- [ ] Repetido el test con `qwen3.8:27b`.

### 1.6. Entorno Python para agentes

Crea un entorno virtual dedicado para no contaminar el Python del sistema.

```bash
mkdir -p ~/agentes-locales && cd ~/agentes-locales
python3 -m venv .venv
source .venv/bin/activate

# Cliente oficial de Ollama
pip install ollama

# LangGraph + LangChain para Graph Engineering
pip install langgraph langchain langchain-ollama

# Utilidades
pip install python-dotenv rich
```

- [ ] Entorno `.venv` creado y activado.
- [ ] `pip list` muestra `langgraph`, `langchain-ollama` y `ollama`.

### 1.7. VS Code: extensión Cline apuntando a Ollama

1. Abre VS Code → Extensiones → busca **Cline** → Instalar.
2. Abre la configuración de Cline (icono de engranaje).
3. **API Provider:** `Ollama`.
4. **Base URL:** `http://localhost:11434`.
5. **Model:** selecciona `qwen3.5:9b` (para iterar rápido) o `qwen3.8:27b` (para calidad).
6. **Context Window:** pon al menos **32K tokens** para que el agente no pierda el hilo.
7. En **Features**, activa **Use Compact Prompt** (reduce el consumo de contexto en modelos locales).

Prueba: pide a Cline *“Crea un archivo hola.py que imprima ‘hola’ y ejecútalo”*. Debe pedirte aprobación antes de ejecutar comandos.

- [ ] Cline instalado y conectado a Ollama.
- [ ] Prueba de creación/ejecución de archivo completada con aprobación manual.

### 1.8. (Opcional) Aider para refactors con git

Aider es una herramienta de terminal que convierte cada cambio en un commit de git, lo que te da un historial reversible ideal para agentes de código.

```bash
pip install aider-chat

# Configurar el endpoint de Ollama
export OLLAMA_API_BASE=http://127.0.0.1:11434

# Ejecutar Aider con el modelo local
aider --model ollama_chat/qwen3.5:9b
```

- [ ] Aider instalado y capaz de hacer un commit con un modelo local.

---

## Módulo 2 — Prompt Engineering para agentes

### 2.1. Del prompt de chatbot al prompt de especificación

Un prompt de agente debe tener cinco partes:

1. **Rol acotado:** no “eres útil”, sino “eres un agente que solo puede usar las herramientas X, Y, Z”.
2. **Herramientas y cuándo usarlas:** descripciones claras y nombres cualificados.
3. **Formato de salida rígido:** si esperas JSON, dilo explícitamente y prohíbe texto adicional.
4. **Condiciones de parada:** “detente cuando el test pase” o “tras 3 intentos devuelve `NO_ENCONTRADO`”.
5. **Presupuesto:** número máximo de pasos o tokens.

### 2.2. Ejercicio: agente de resumen con salida JSON estricta

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

**Criterio de éxito:** ejecútalo **10 veces** con el mismo texto. Debe devolver JSON válido las 10 veces. Si falla, endurece el system prompt (prohíbe más explícitamente, baja la temperatura).

- [ ] Script creado y ejecutado.
- [ ] 10/10 ejecuciones con JSON parseable.

**Entregable del módulo:** un agente de un solo paso que transforma texto en JSON estructurado de forma fiable.

---

## Módulo 3 — Loop Engineering: el agente que se corrige solo

### 3.1. La anatomía de un Loop

El ciclo mínimo es: **Trigger → Act → Verify → (Retry con nuevo contexto | Exit)**. Lo más difícil no es el bucle, sino la **condición de parada**: un Loop mal diseñado no falla ruidosamente, sigue consumiendo tokens hasta que lo matas.

Un Loop robusto necesita: disparador, ejecución, verificación (preferiblemente determinista, no otro LLM), estado persistido, límite de iteraciones y memoria externa.

### 3.2. Ejercicio: loop que corrige un archivo hasta cumplir una condición

Crea `loop_simple.py`. El objetivo es que un archivo `poema.txt` tenga exactamente 4 líneas y ninguna palabra prohibida (“guerra”, “odio”).

```python
import ollama, pathlib, json, re

ARCHIVO = pathlib.Path("poema.txt")
ESTADO = pathlib.Path("loop_estado.json")
MAX_ITER = 5

def verificar(texto: str) -> tuple[bool, str]:
    lineas = [l for l in texto.splitlines() if l.strip()]
    if len(lineas) != 4:
        return False, f"Tiene {len(lineas)} líneas; deben ser 4."
    prohibidas = {"guerra", "odio"}
    encontradas = prohibidas & set(re.findall(r"\w+", texto.lower()))
    if encontradas:
        return False, f"Contiene palabras prohibidas: {encontradas}."
    return True, "OK"

def generar(intento: int, feedback: str) -> str:
    prompt = f"""Escribe un poema de exactamente 4 líneas sobre la lluvia.
    {feedback}
    Devuelve solo el poema, sin títulos ni comentarios."""
    resp = ollama.chat(
        model="qwen3.5:9b",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.7},
    )
    return resp["message"]["content"].strip()

def main():
    estado = {"iteracion": 0, "historial": []}
    feedback = ""
    for i in range(1, MAX_ITER + 1):
        texto = generar(i, feedback)
        ok, motivo = verificar(texto)
        estado["iteracion"] = i
        estado["historial"].append({"intento": i, "texto": texto, "ok": ok, "motivo": motivo})
        if ok:
            ARCHIVO.write_text(texto)
            ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=2))
            print(f"✅ Éxito en intento {i}")
            return
        feedback = f"El intento anterior falló: {motivo}. Corrige eso."
    ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=2))
    print("❌ No se alcanzó el criterio en el límite de iteraciones.")

if __name__ == "__main__":
    main()
```

**Criterio de éxito:** el script termina solo (éxito o límite), deja `poema.txt` y `loop_estado.json`, y puedes inspeccionar por qué fallaron los intentos anteriores.

- [ ] Script ejecutado y terminado autónomamente.
- [ ] `loop_estado.json` contiene el historial de intentos.

**Entregable del módulo:** un Loop funcional con verificación determinista y estado persistido.

---

## Módulo 4 — Graph Engineering: del Loop al grafo de agentes

### 4.1. Cuándo un Loop ya no basta

Un Loop es el grafo más pequeño posible (un nodo con auto-bucle). Solo debes pasar a un grafo multi-nodo cuando la tarea **realmente se divide en subtareas que requieren handoff entre especialistas**. Si un solo agente puede hacerlo, un grafo es sobreingeniería.

Elementos de un grafo:

- **Nodos:** agentes especializados o funciones deterministas.
- **Aristas:** secuenciales, condicionales, de fan-out o fan-in.
- **Estado compartido:** un objeto que viaja por el grafo y que cada nodo lee y escribe.

### 4.2. Ejercicio: grafo de 3 nodos con LangGraph

El grafo tendrá: **Planificador → Redactor → Revisor**, con una arista condicional que devuelve al Redactor si el Revisor rechaza.

```python
# grafo_langgraph.py
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen3.5:9b", temperature=0.3)

class Estado(TypedDict):
    tema: str
    plan: str
    borrador: str
    revision: str
    aprobado: bool
    intentos: int

def planificador(estado: Estado) -> Estado:
    resp = llm.invoke(f"Haz un plan de 3 puntos para un texto sobre: {estado['tema']}. Sé breve.")
    return {"plan": resp.content, "intentos": 0, "aprobado": False}

def redactor(estado: Estado) -> Estado:
    prompt = f"Tema: {estado['tema']}\nPlan: {estado['plan']}\n"
    if estado.get("revision"):
        prompt += f"Corrige según esta crítica: {estado['revision']}\n"
    prompt += "Escribe el texto final (máx. 150 palabras)."
    resp = llm.invoke(prompt)
    return {"borrador": resp.content, "intentos": estado["intentos"] + 1}

def revisor(estado: Estado) -> Estado:
    prompt = f"Revisa este texto. Si es aceptable responde solo 'OK'. Si no, da una crítica breve.\n\n{estado['borrador']}"
    resp = llm.invoke(prompt)
    ok = resp.content.strip().upper().startswith("OK")
    return {"revision": "" if ok else resp.content, "aprobado": ok}

def decidir(estado: Estado) -> Literal["redactor", "fin"]:
    if estado["aprobado"] or estado["intentos"] >= 3:
        return "fin"
    return "redactor"

builder = StateGraph(Estado)
builder.add_node("planificador", planificador)
builder.add_node("redactor", redactor)
builder.add_node("revisor", revisor)

builder.set_entry_point("planificador")
builder.add_edge("planificador", "redactor")
builder.add_edge("redactor", "revisor")
builder.add_conditional_edges("revisor", decidir, {"redactor": "redactor", "fin": END})

grafo = builder.compile()

if __name__ == "__main__":
    resultado = grafo.invoke({"tema": "la computación local", "plan": "", "borrador": "", "revision": "", "aprobado": False, "intentos": 0})
    print("Aprobado:", resultado["aprobado"])
    print("Intentos:", resultado["intentos"])
    print("\n--- Texto final ---\n", resultado["borrador"])
```

**Criterio de éxito:** el grafo termina solo, el contador de intentos no supera 3, y si el revisor rechaza, el redactor recibe la crítica como contexto.

- [ ] `langgraph` y `langchain-ollama` importan sin error.
- [ ] El grafo se ejecuta de principio a fin con un modelo local.
- [ ] El estado final contiene `aprobado` y `intentos` coherentes.

**Entregable del módulo:** un grafo de 3 nodos con arista condicional funcionando 100 % en local.

---

## Módulo 5 — Multiagente y proyecto final

### 5.1. De un grafo de 3 nodos a un sistema multiagente en paralelo

El patrón que vamos a probar es **fan-out / fan-in con un único modelo**:

```
                      ┌──► [Agente A] ──┐
[Tarea] ─► [Orquestador]                ├─► [Sintetizador] ─► [Entregable]
                      └──► [Agente B] ──┘
```

- **Orquestador**: recibe la tarea, la descompone y lanza **dos agentes en paralelo**.
- **Agente A** y **Agente B**: trabajan **simultáneamente** sobre subtareas distintas.
- **Sintetizador**: espera ambas salidas (fan-in) y las **fusiona** en un entregable único.

**Clave para 24 GB de RAM:** los tres roles usan el **mismo modelo `qwen3.5:9b`**, cargado una sola vez. En LangGraph cada nodo hace su propia llamada a `ChatOllama`, pero Ollama reutiliza el mismo peso en memoria: no se duplica la RAM por tener "tres agentes". El 27B no entra en este patrón (ocuparía ~16,5 GB y no habría margen para dos ramas concurrentes).

El grafo en LangGraph sería:

```
START ─► orquestador ─┬─► agente_a ─┐
                      └─► agente_b ─┴─► sintetizador ─► END
```

El **fan-out** se logra añadiendo dos aristas desde `orquestador`, y el **fan-in** con dos aristas hacia `sintetizador`. LangGraph espera a que ambas ramas terminen antes de ejecutar el nodo de síntesis.

### 5.2. Proyecto final: “Agente de mantenimiento de repositorio (en paralelo)”

Construye un sistema con LangGraph que:

1. Se dispare manualmente (o por cambio en un directorio).
2. **Orquestador**: lee la petición y reparte el trabajo a dos agentes.
3. **Agente A – Analista**: lee TODOs/issues de archivos `.py` (nodo parcialmente determinista).
4. **Agente B – Implementador**: propone un parche **en paralelo** al Analista.
5. **Sintetizador**: fusiona el análisis y el parche en una propuesta única y coherente.
6. Un **Verificador** determinista (linter/test) valida el resultado; si falla, la arista condicional devuelve al Sintetizador/Implementador con el error como contexto.
7. Persista el estado en JSON/SQLite para reanudar tras cerrar el portátil.
8. **Todos los roles LLM usan `qwen3.5:9b`** (un único peso en RAM); el 27B queda para pruebas puntuales de calidad fuera del bucle multiagente.

**Criterio de éxito:** el sistema reparte la tarea entre dos agentes en paralelo, el sintetizador produce una salida única, el verificador la valida y, si falla, itera al menos una vez sin intervención manual, todo en local con 24 GB.

- [ ] Nodo Investigador añadido y funcionando con archivos locales.
- [ ] Proyecto final ejecutado de principio a fin.
- [ ] Estado persistido y reanudable.

---

## Módulo 6 — Calendario de 10 semanas (seguimiento)

| Semana | Foco | Entregable | Hecho |
|---|---|---|---|
| **1** | Stack: Ollama, LM Studio, modelos, tool calling | `curl` con `tool_calls` válido + Cline conectado | `[ ]` |
| **2** | Prompt Engineering para agentes | Agente de resumen JSON 10/10 | `[ ]` |
| **3** | Loop Engineering | `loop_simple.py` con estado persistido | `[ ]` |
| **4** | LangGraph básico | Grafo Planificador→Redactor→Revisor | `[ ]` |
| **5** | Aristas condicionales y estado | Grafo que itera con crítica del Revisor | `[ ]` |
| **6** | Nodo determinista (lectura de archivos) | Investigador + Redactor integrados | `[ ]` |
| **7** | Cline + Aider en flujo real | Cambio multi-archivo revisado en git | `[ ]` |
| **8** | Persistencia y presupuesto | Loop o grafo que sobrevive a reinicios | `[ ]` |
| **9** | Proyecto final: diseño | Diagrama del grafo + esqueleto de código | `[ ]` |
| **10** | Proyecto final: ejecución | Agentes en paralelo + orquestador (todo `qwen3.5:9b`) en local | `[ ]` |

---

## Apéndice A — Solución de problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `curl localhost:11434` no responde | Ollama no está corriendo como servicio | `brew services restart ollama` |
| Cline no lista modelos | El servidor no está activo o la URL es incorrecta | Verifica `http://localhost:11434` y que `ollama list` funcione |
| El modelo devuelve texto en vez de `tool_calls` | El modelo no soporta tools o el prompt no las declara | Usa `qwen3.5:9b` o `qwen3.8:27b` (tag `tools`) y revisa el esquema |
| LangGraph se queda colgado | El grafo no tiene arista de salida o el modelo no responde | Añade un límite de iteraciones en la arista condicional |
| El Mac se ralentiza con el 27B | Contexto demasiado largo o RAM insuficiente | Baja el contexto, usa `qwen3.5:9b` o cierra apps pesadas |
| Bionic no encuentra modelos | Bionic usa el runtime de LM Studio; el modelo debe estar descargado en LM Studio | Descarga el modelo desde LM Studio o desde Bionic y verifica `lms ls` |

---

## Apéndice B — Referencias rápidas de comandos

```bash
# Ollama
ollama list                      # modelos descargados
ollama ps                        # modelos cargados en memoria
ollama run qwen3.5:9b            # chat interactivo
brew services restart ollama     # reiniciar servicio

# LM Studio / Bionic
lms status                       # estado del servidor
lms server start                 # arrancar API local (puerto 1234)
lms ls                           # modelos en disco
lms ps                           # modelos cargados

# Entorno Python
source ~/agentes-locales/.venv/bin/activate
pip install -U langgraph langchain-ollama ollama

# Aider
export OLLAMA_API_BASE=http://127.0.0.1:11434
aider --model ollama_chat/qwen3.5:9b
```

---

## Apéndice C — Estructura de carpetas recomendada

```
~/agentes-locales/
├── .venv/                     # entorno virtual Python
├── curso-agentes-locales.md   # este documento
├── prompt_agente.py           # Módulo 2
├── loop_simple.py             # Módulo 3
├── grafo_langgraph.py         # Módulo 4
├── proyecto_final/            # Módulo 5
│   ├── grafo.py
│   ├── fuentes/
│   └── estado.json
└── notas/
    └── aprendizajes.md        # tu diario de curso
```

---

## Apéndice D — Extensiones recomendadas de VS Code

| Extensión | Para qué |
|---|---|
| **Cline** | Agente de código conectado a Ollama |
| **Markdown All in One** | Atajos, TOC automático y preview mejorada |
| **Markdown Checkboxes** | Casillas `[ ]` interactivas en el editor |
| **Python** (Microsoft) | IntelliSense, debugger, linting |
| **Even Better TOML** | Para configuración de proyectos |
| **GitLens** | Historial de commits (útil con Aider) |

---

**Fin del documento.**

Guarda este archivo como `curso-agentes-locales.md`, ábrelo en VS Code con `Cmd+Shift+V` para ver la versión renderizada, y marca las casillas a medida que completas cada paso. Cuando termines el Módulo 1, vuelve y comparte la salida de `ollama list` y el resultado del `curl` de tool calling para validar que la base está sólida antes de entrar en Loop Engineering.