# Estado del Módulo 1 — Stack local

Última verificación: 2026-10-31.

## Qué hay instalado

| Pieza | Estado | Detalle |
|---|---|---|
| Homebrew | ✅ | 7.0.13 (prefix `/opt/homebrew`, **arm64**) |
| Python | ✅ | 3.12.9 (`/Library/Frameworks/Python.framework/Versions/3.12`) |
| Git | ✅ | 2.54.0 (Apple Git-157) · nativo arm64, sin `arch -arm64` |
| Ollama | ✅ | 0.40.13 · **Ollama.app** (no Homebrew), sirviendo en `127.0.0.1:11434` |
| LM Studio | ✅ | app 0.4.28 · CLI `lms` en `~/.lmstudio/bin` · servidor ON en `:1234` |
| Modelos | ✅ | `qwen3.5:9b` (5,7 GB) y `qwen3.8:27b` (16 GB) importados desde GGUF + `nomic-embed-text` |
| venv | ✅ | `.venv` (Python 3.12.9) en la raíz del proyecto |
| Paquetes | ✅ | `ollama` 0.6.3, `langchain` 1.4.7, `langchain-ollama` 1.1.0, `langgraph` 1.2.19, `python-dotenv`, `rich` |
| Cline | ✅ | `saoudrizwan.claude-dev` 4.1.26 (proveedor configurado en la UI) |
| Aider | ✅ | `aider-chat` 0.86.2 dentro de `.venv` |

## Desviaciones respecto al documento del curso

1. **Ollama no está instalado con Homebrew.** Vino con `Ollama.app`, que ya arranca solo y ocupa el puerto 11434.
   No ejecutes `brew install ollama` / `brew services start ollama` mientras la app esté activa: dos servidores peleando por el mismo puerto.
2. **El venv vive en la raíz del proyecto**, no en `~/agentes-locales`. Activar con:
   `cd agentes-locales && source .venv/bin/activate`.
3. **Los modelos se importaron desde GGUF de HuggingFace**, no con `ollama pull`.
   Motivo: el CDN de blobs de Ollama (`*.r2.cloudflarestorage.com`) no es accesible desde esta red
   (`dial tcp 172.64.66.1:443: i/o timeout`), mientras que `huggingface.co` descarga a ~30 MB/s.
   Cuando la red lo permita, `ollama pull qwen3.5:9b` / `ollama pull qwen3.8:27b` sustituirán los modelos locales por los builds oficiales.
   Las recetas de importación quedan guardadas en `Modelfile.qwen3.5-9b` y `Modelfile.qwen3.8-27b`.
4. El test de tool calling del curso espera `arguments` como **string JSON**; Ollama 0.40 devuelve un **objeto**. Ambos son válidos para el cliente Python y para LangChain.
5. El 27B se creó con `num_ctx 16384` (no 32K) para no arriesgar swap con 24 GB de RAM.
   Cargó en ~6 s sin swap (`vm.swapusage` = 0) y respondió el tool call en ~10 s.

## Git (resuelto: arm64 nativo)

Hasta el 2026-10-31 el terminal arrancaba en **x86_64 (Rosetta)** mientras las CommandLineTools
son arm64, y `git` fallaba con `libxcrun ... need 'x86_64'`; había que usar
`arch -arm64 /usr/bin/git ...`.

Tras la migración del **2026-11-11** (`uname -m` = `arm64`, sin Rosetta ni MacPorts), `git`
funciona directamente:

```bash
git status
git add -A
git commit -m "..."
```

## Comandos de trabajo

```bash
source .venv/bin/activate                # entorno del curso
./ollama-helper.sh                       # gestor de modelos: ver / cargar / RAM+swap / auditar blobs
./scripts/entorno/verificar_memoria.sh   # pre-flight: ¿cabe el modelo en RAM?
git status                               # git nativo arm64
```

## Modelos

```bash
# Importación local desde GGUF (vía usada mientras el CDN de Ollama esté bloqueado)
ollama create qwen3.5:9b  -f Modelfile.qwen3.5-9b
ollama create qwen3.8:27b -f Modelfile.qwen3.8-27b

# Cuando la red lo permita, la vía oficial del curso:
# ollama pull qwen3.5:9b
# ollama pull qwen3.8:27b
```

Los `.gguf` de `gguf/` **ya se eliminaron** el 2026-11-11 junto con `.logs/`: `ollama create`
copió los pesos a `~/.ollama/models`, así que eran ~21 GB duplicados. Verificado después del
borrado: `qwen3.5:9b` sigue respondiendo (100 % GPU, contexto 8192). Para reimportar habría que
volver a descargar los GGUF de HuggingFace y usar `Modelfile.qwen3.5-9b` / `Modelfile.qwen3.8-27b`.

## Resultados de las pruebas (Módulo 1)

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

## ⚠️ Distinción clave: Modelo vs. Modo de Cline

Dos conceptos **independientes** que se suelen confundir:

### Eje A — El MODELO (qué cerebro usas)
- `qwen3.5:9b` = rápido, para iterar, tareas sencillas
- `qwen3.8:27b` = profundo, para razonamiento complejo, arquitectura

**Cómo cambiarlo**: UI de Cline (engranaje) → **Model**.

### Eje B — El MODO de Cline (qué comportamiento tiene el agente)
- **Plan mode** = solo explora/analiza/propone, **NO edita archivos**.
- **Act mode** = **sí ejecuta**: edita, crea archivos, corre comandos.

**Cómo cambiarlo**: UI de Cline → toggle **Plan/Act**.

El curso **no pide** cambiar dinámicamente entre modelos. Elige uno en la UI y úsalo según su propósito.

## Planteamiento multiagente (para el curso)

Por el límite de **24 GB de RAM**, el multiagente se hará con **un único modelo `qwen3.5:9b`
cargado una sola vez** y reutilizado por todos los roles. Se probarán **agentes en paralelo**:

```
          ┌── Agente A (p. ej. Investigador) ──┐
Tarea ───►  Orquestador                          ├──► Sintetizador ──► Entregable
          └── Agente B (p. ej. Redactor)    ──┘
```

- **Agente A** y **Agente B** trabajan **en paralelo** sobre la misma tarea.
- El **Orquestador/Sintetizador** reparte el trabajo y **fusiona** ambas salidas en un único resultado.
- El 27B queda para pruebas puntuales de calidad, **nunca** para multiagente en paralelo.

Detalle en `curso-agentes-locales.md` (Módulo 5).

---

## Migración a arm64 (2026-11-11)

Estado final del entorno tras la migración completa:

- Homebrew x86_64 (`/usr/local`) → **Homebrew 7.0.13 en `/opt/homebrew`** (arm64).
- **MacPorts eliminado** por completo (`/opt/local`, ~479 MB) y restos de `/usr/local`
  limpiados (symlinks roto y directorios huérfanos).
- `~/.zprofile` corregido (dejaba el `PATH` vacío) y `~/.bashrc` ahora carga `brew shellenv`.
- Los **GGUF fuente (21 GB)** y los **logs de descarga** eliminados: los modelos viven
  solo en `~/.ollama/models`.
- Scripts one-shot de la migración **archivados fuera del repo** en
  `~/homebrew_migracion_backup_2026-11-11/scripts-memory-cleaner/`.
- En el repo quedan solo las utilidades vivas: `scripts/entorno/ollama-env.sh` (sourceado
  desde `~/.zshrc`) y `scripts/entorno/verificar_memoria.sh`.

> Nota VS Code: si el terminal intenta lanzar `/usr/local/bin/bash`, cierra la pestaña
> de terminal antigua y abre una nueva. El perfil por defecto ya apunta a `/bin/bash` y
> `terminal.integrated.enablePersistentSessions` está desactivado para no restaurar
> terminales de sesiones anteriores.
