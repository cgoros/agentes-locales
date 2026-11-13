# Estado del Módulo 1 — Stack local

Última verificación: 2026-11-11.

## Qué hay instalado

| Pieza | Estado | Detalle |
|---|---|---|
| Homebrew | ✅ | 7.0.13 (prefix `/opt/homebrew`, **arm64**) |
| Python | ✅ | 3.12.9 (`/Library/Frameworks/Python.framework/Versions/3.12`) |
| Git | ✅ | 2.54.0 (Apple Git-157) · nativo arm64, sin `arch -arm64` |
| Ollama | ✅ | 0.40.13 · **Ollama.app** (no Homebrew), sirviendo en `127.0.0.1:11434` |
| LM Studio | ✅ | app 0.4.28 · CLI `lms` en `~/.lmstudio/bin` · servidor **OFF** en `:1234` (arráncalo con `lms server start` si lo necesitas) |
| Modelos | ✅ | `qwen3.5:9b` (5,7 GB, GGUF Q4_K_M) · `qwen3.8:27b` (18 GB, **safetensors nvfp4 / runner MLX**) · `nomic-embed-text` (274 MB) |
| venv | ✅ | `.venv` (Python 3.12.9) en la raíz del proyecto |
| Paquetes | ✅ | `ollama` 0.6.3, `langchain` 1.4.7, `langchain-ollama` 1.1.0, `langgraph` 1.2.19, `python-dotenv`, `rich` |
| Cline | ✅ | `saoudrizwan.claude-dev` 4.1.26 (proveedor configurado en la UI) |
| Aider | ✅ | `aider-chat` 0.86.2 dentro de `.venv` |

## Desviaciones respecto al documento del curso

1. **Ollama no está instalado con Homebrew.** Vino con `Ollama.app`, que ya arranca solo y ocupa el puerto 11434.
   No ejecutes `brew install ollama` / `brew services start ollama` mientras la app esté activa: dos servidores peleando por el mismo puerto.
2. **El venv vive en la raíz del proyecto**, no en `~/agentes-locales`. Activar con:
   `cd agentes-locales && source .venv/bin/activate`.
3. **Los modelos se importaron desde GGUF de HuggingFace**, no con `ollama pull` (el 9B sigue así; el 27B actual ya es `safetensors`/nvfp4 → ver punto 6).
   Motivo: el CDN de blobs de Ollama (`*.r2.cloudflarestorage.com`) no es accesible desde esta red
   (`dial tcp 172.64.66.1:443: i/o timeout`), mientras que `huggingface.co` descarga a ~30 MB/s.
   Cuando la red lo permita, `ollama pull qwen3.5:9b` / `ollama pull qwen3.8:27b` sustituirán los modelos locales por los builds oficiales.
   Las recetas de importación quedan guardadas en `Modelfile.qwen3.5-9b` y `Modelfile.qwen3.8-27b`.
4. El test de tool calling del curso espera `arguments` como **string JSON**; Ollama 0.40 devuelve un **objeto**. Ambos son válidos para el cliente Python y para LangChain.
5. El 27B se creó con `num_ctx 16384` (no 32K) para no arriesgar swap con 24 GB de RAM.
   Histórico (2026-10-31): cargó en ~6 s sin swap (`vm.swapusage` = 0) y respondió el tool call en ~10 s.
6. **El `qwen3.8:27b` instalado hoy NO es el GGUF del `Modelfile`.** `curl /api/tags` devuelve
   `format: safetensors` + `quantization: nvfp4`, y `ollama ps` lo ejecuta con `RUNNER mlx`
   (`ollama show` no le muestra `num_ctx`). El 9B sí sigue siendo el GGUF `Qwen3.5-9B-Q4_K_M.gguf`.
7. **Medición de RAM del 2026-11-11 (24 GiB):** con el 9B cargado el swap usado era 47,5 MB;
   al cargar el 27B (18 GB, ctx 8192) el swap subió a **4 064,6 MB (≈4 GiB)** y el archivo de swap
   pasó de 1 GB a 5 GB. Tras `ollama stop qwen3.8:27b` el swap **no vuelve a 0** (quedó en ~3,7 GiB).
   → El 27B ocupa el **75 % de la RAM solo en pesos**: incumple la regla del 70 % incluso sin KV cache.

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
| Tool calling `qwen3.8:27b` | ✅ `tool_calls → get_weather{"city":"Madrid"}` (2026-10-31: load 6 s, sin swap) |
| `ChatOllama` + `LangGraph` | ✅ nodo único START→END devuelve texto |
| LM Studio API (:1234) | ⚠️ servidor **OFF** hoy (`lms status`); se enciende con `lms server start` |
| RAM/swap cargando el 27B (2026-11-11) | ⚠️ swap 47,5 MB → **4 064,6 MB**; 18 GB = 75 % de la RAM → no cabe con holgura |

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
- Credential helper de git repuntado con `gh auth setup-git`: ya no usa el
  `/usr/local/bin/gh` inexistente, sino `/opt/homebrew/bin/gh`.
- Los **GGUF fuente (21 GB)** y los **logs de descarga** eliminados: los modelos viven
  solo en `~/.ollama/models`.
- Scripts one-shot de la migración **archivados fuera del repo** en
  `~/homebrew_migracion_backup_2026-11-11/scripts-memory-cleaner/`.
- En el repo quedan solo las utilidades vivas: `scripts/entorno/ollama-env.sh` (sourceado
  desde `~/.zshrc`) y `scripts/entorno/verificar_memoria.sh`.
- **`.venv` recreado en arm64**: el anterior se creó bajo Rosetta y su `pydantic_core` era
  un `.so` x86_64, así que `import ollama` fallaba con `incompatible architecture`.
  Ahora contiene el stack del curso (`requirements.txt`) + `aider-chat` 0.86.2.
- `pip check` muestra dos avisos de pins cruzados, ambos benignos y verificados:
  `aider-chat` pinnea `certifi==2026.1.4` mientras `langchain-core` pide ≥2026.10.19, y
  `httpx2` (vía `langsmith`) pide `idna>=3.18` frente a `idna==3.11` de aider.

> Nota VS Code: si el terminal intenta lanzar `/usr/local/bin/bash`, cierra la pestaña
> de terminal antigua y abre una nueva. El perfil por defecto ya apunta a `/bin/bash` y
> `terminal.integrated.enablePersistentSessions` está desactivado para no restaurar
> terminales de sesiones anteriores.

---

## Sistema de estudio: profesor Cline (2026-11-11)

El curso se estudia con **Cline como profesor**, no como "hacedor". El rol está
definido en [`CLAUDE.md`](./CLAUDE.md), que Cline carga automáticamente al abrir
el workspace (funciona con cualquier modelo: DeepSeek-v4, qwen local, etc.).

- **Arranque de cada sesión:** escribir `modo profesor`.
- **Progreso:** las casillas `[ ]` / `[x]` de `curso-agentes-locales.md` son la
  única fuente de verdad; las marca el alumno (o se pide `márcalo`).
- **Ayuda:** `no entiendo <tema>`, `pista`, `revísame <fichero>`, `hazlo tú`, `progreso`.
- **Enfoque:** el curso se recorre **desde 1.1 en modo repaso**, aunque el entorno
  ya esté montado, para detectar cualquier cosa que se hubiera escapado.
- **Guía completa para el alumno:** sección *"Cómo estudiar con el profesor
  (Cline)"* del `README.md`.


---

## Punto de retorno (2026-11-12)

**Hecho:** prácticas **1.1–1.5** ✅ y el **clasificador de 1.6** (1 de 5 mini-agentes):
`clasificador.py` (contrato de 4 claves + `validar()` determinista) y `bateria.py`
(6 casos difíciles con respuesta esperada). Medido en este equipo: `--test 10` → **10/10**;
batería → **6/6 coherentes**; `"no va."` estable **3/3** en `estado`.

**Aprendizajes de la sesión** (los que costaron):

- `--test 10` mide la **forma**, no el **contenido**: un JSON puede ser válido y falso.
  Hace falta un banco de casos con respuesta esperada (= antesala de 2.2).
- Los criterios de urgencia estaban en un **dict de Python** → el modelo no los veía.
  Una regla que el modelo no lee no existe: van en el `SYSTEM`.
- `otro`/`nula` mezclaba *"no es un ticket"* con *"faltan datos"* → se añadió `estado`
  (enum de 3: `ok` / `insuficiente` / `no_ticket`).
- Coherencia en código: `not(A and B) = not A or not B` (De Morgan). Con `or` en vez de
  `and`, el validador rechaza **todos** los tickets buenos (falsos positivos).
- **Antes de ejecutar**, `which python`: hay un venv x86_64 de otro proyecto
  (`~/Documents/tests/deepseek_api_test/venv`) que revienta al importar `ollama`.

```bash
cd ~/Documents/wks/pruebas/agentes-locales
source .venv/bin/activate      # prompt (.venv) — el intruso es (venv)
which python                   # .../agentes-locales/.venv/bin/python
.venv/bin/python clasificador.py --test 10
.venv/bin/python bateria.py
```

**Siguiente parada:** los 4 mini-agentes restantes de 1.6 — (1) **temperaturas 0.1 vs 0.9**,
(2) extractor de entidades, (3) corrector con restricciones, (4) generador YAML.

**Decisión de diseño pendiente** (para el primer `get_time` en Python):

- `get_time(city)` → cómodo para el usuario, pero tu código necesita un mapa
  ciudad → zona (`"Madrid" → "Europe/Madrid"`).
- `get_time(timezone)` → el modelo entrega la zona IANA directamente; cero mapa,
  pero el usuario tiene que "hablar en zonas".

**Recordatorio técnico:** ejecutar **todos** los `tool_calls` del array, no solo
`tool_calls[0]`; y devolver cada resultado con `role: "tool"`.

**Ficheros de prueba de la sesión** (en `/tmp`, fuera del repo, se borran al reiniciar):
`/tmp/tool_27b.json` y `/tmp/tool_dos.json`. Si desaparecen, se regeneran en 1 minuto.

