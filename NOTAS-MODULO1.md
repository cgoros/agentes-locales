# Estado del Módulo 1 — Stack local

Última verificación: 2026-10-31.

## Qué hay instalado

| Pieza | Estado | Detalle |
|---|---|---|
| Homebrew | ✅ | 7.0.11 |
| Python | ✅ | 3.12.9 (`/Library/Frameworks/Python.framework/Versions/3.12`) |
| Git | ✅ | 2.50.1 (Apple Git-155) |
| Ollama | ✅ | 0.40.13 · **Ollama.app** (no Homebrew), sirviendo en `127.0.0.1:11434` |
| LM Studio | ✅ | app 0.4.28 · CLI `lms` en `~/.lmstudio/bin` · servidor ON en `:1234` |
| Modelos | ✅ | `qwen3.5:9b` (5,7 GB) y `qwen3.8:27b` (16 GB) importados desde GGUF + `nomic-embed-text` |
| venv | ✅ | `.venv` (Python 3.12.9) en la raíz del proyecto |
| Paquetes | ✅ | `ollama` 0.6.3, `langchain` 1.4.7, `langchain-ollama` 1.1.0, `langgraph` 1.2.19, `python-dotenv`, `rich` |
| Cline | ✅ | `saoudrizwan.claude-dev` 4.1.26 (config del proveedor: revisar en UI) |
| Aider | ⏳ | Opcional (1.8), no instalado |

## Desviaciones respecto al documento del curso

1. **Ollama no está instalado con Homebrew.** Vino con `Ollama.app`, que ya arranca solo y ocupa el puerto 11434.
   No ejecutes `brew install ollama` / `brew services start ollama` mientras la app esté activa: dos servidores peleando por el mismo puerto.
2. **El venv vive en la raíz del proyecto**, no en `~/agentes-locales`. Activar con:
   `cd agentes-locales && source .venv/bin/activate`.
3. **Los modelos se importaron desde GGUF de HuggingFace**, no con `ollama pull`.
   Motivo: el CDN de blobs de Ollama (`*.r2.cloudflarestorage.com`) no es accesible desde esta red
   (`dial tcp 172.64.66.1:443: i/o timeout`), mientras que `huggingface.co` descarga a ~30 MB/s.
   Cuando la red lo permita, `ollama pull qwen3.5:9b` / `ollama pull qwen3.8:27b` sustituirán los modelos locales por los builds oficiales.
4. El test de tool calling del curso espera `arguments` como **string JSON**; Ollama 0.40 devuelve un **objeto**. Ambos son válidos para el cliente Python y para LangChain.
5. El 27B se creó con `num_ctx 16384` (no 32K) para no arriesgar swap con 24 GB de RAM.
   Cargó en ~6 s sin swap (`vm.swapusage` = 0) y respondió el tool call en ~10 s.
   Si quieres 32K, edita `Modelfile.qwen3.8-27b` y vuelve a ejecutar `ollama create`.

## Ejercicio 1: "Hola Mundo" (1.1)

✅ `hola.py` creado y ejecutado con éxito en el entorno del venv.

## Comandos de trabajo

```bash
source .venv/bin/activate         # entorno del curso
./verificar-modulo1.sh            # re-verifica todo el módulo 1
python prueba_stack.py            # smoke test: ollama + langchain + langgraph
```

## Modelos

```bash
# Importación local desde GGUF (vía usada mientras el CDN de Ollama esté bloqueado)
ollama create qwen3.5:9b -f Modelfile.qwen3.5-9b
ollama create qwen3.8:27b -f Modelfile.qwen3.8-27b

# Cuando la red lo permita, la vía oficial del curso:
# ollama pull qwen3.5:9b
# ollama pull qwen3.8:27b
```

Los `.gguf` en `gguf/` pueden borrarse una vez importados: `ollama create` copia los pesos a `~/.ollama/models`.
Ocupan 21 GB, los mismos que ya tienes duplicados en `~/.ollama`:

```bash
rm -rf gguf/ .logs/    # libera ~21 GB sin afectar a los modelos de Ollama
```

## Resultados de las pruebas

| Prueba | Resultado |
|---|---|
| `curl /api/tags` (:11434) | ✅ responde |
| Tool calling `qwen3.5:9b` | ✅ `tool_calls → get_weather{"city":"Madrid"}` |
| Tool calling `qwen3.8:27b` | ✅ `tool_calls → get_weather{"city":"Madrid"}` (load 6 s, sin swap) |
| `ChatOllama` + `LangGraph` | ✅ nodo único START→END devuelve texto |
| LM Studio API (:1234) | ✅ `/v1/models` responde (solo embeddings cargados) |

## Pendiente en la UI de VS Code (1.7)

En Cline: **Provider** = `Ollama`, **Base URL** = `http://localhost:11434`,
**Model** = `qwen3.5:9b` (iterar) / `qwen3.8:27b` (calidad), **Context Window** ≥ 32768,
y activar **Use Compact Prompt** en *Features*.

