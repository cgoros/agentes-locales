"""Smoke test del stack Python del Módulo 1 (1.6).

Comprueba, contra el Ollama local:
  1. Cliente oficial `ollama` + tool calling estructurado.
  2. Integración `langchain-ollama` (ChatOllama).
  3. Un grafo mínimo de LangGraph con un nodo (base del Módulo 4).

Uso:  source .venv/bin/activate && python prueba_stack.py
"""

from __future__ import annotations

import json
import os

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from ollama import Client
from rich.console import Console
from typing_extensions import TypedDict

MODELO = os.getenv("MODELO", "qwen3.5:9b")
HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

console = Console()


def test_cliente_ollama() -> None:
    """1. Cliente oficial: listar modelos y forzar un tool_call."""
    cliente = Client(host=HOST)
    modelos = [m.model for m in cliente.list().models]
    console.print(f"[cyan]Modelos en Ollama:[/cyan] {', '.join(modelos)}")

    respuesta = cliente.chat(
        model=MODELO,
        messages=[{"role": "user", "content": "¿Qué tiempo hace en Madrid?"}],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Obtiene el tiempo de una ciudad",
                    "parameters": {
                        "type": "object",
                        "properties": {"city": {"type": "string"}},
                        "required": ["city"],
                    },
                },
            }
        ],
        think=False,
    )
    llamadas = respuesta.message.tool_calls or []
    assert llamadas, f"{MODELO} no emitió tool_calls"
    console.print(f"[green]✅ tool_calls:[/green] {json.dumps([c.function.name + ' ' + json.dumps(c.function.arguments) for c in llamadas], ensure_ascii=False)}")


def test_chat_ollama() -> None:
    """2. ChatOllama: la pieza que usarás en todos los grafos."""
    llm = ChatOllama(model=MODELO, base_url=HOST, temperature=0, num_ctx=8192)
    salida = llm.invoke([HumanMessage(content="Responde solo con la palabra: listo")])
    texto = salida.content if isinstance(salida.content, str) else str(salida.content)
    console.print(f"[green]✅ ChatOllama:[/green] {texto.strip()[:80]!r}")


class Estado(TypedDict):
    pregunta: str
    respuesta: str


def test_langgraph() -> None:
    """3. Grafo mínimo START → nodo → END (estructura del Módulo 4)."""
    llm = ChatOllama(model=MODELO, base_url=HOST, temperature=0, num_ctx=8192)

    def nodo_responder(estado: Estado) -> Estado:
        salida = llm.invoke([HumanMessage(content=estado["pregunta"])])
        contenido = salida.content if isinstance(salida.content, str) else str(salida.content)
        return {"respuesta": contenido}

    grafo = StateGraph(Estado)
    grafo.add_node("responder", nodo_responder)
    grafo.add_edge(START, "responder")
    grafo.add_edge("responder", END)

    resultado = grafo.compile().invoke({"pregunta": "Di 'hola' y nada más."})
    assert resultado["respuesta"].strip(), "el grafo devolvió una respuesta vacía"
    console.print(f"[green]✅ LangGraph:[/green] {resultado['respuesta'].strip()[:80]!r}")


if __name__ == "__main__":
    console.rule(f"Smoke test Módulo 1 · {MODELO}")
    test_cliente_ollama()
    test_chat_ollama()
    test_langgraph()
    console.print("\n[bold green]Stack Python operativo: ollama + langchain-ollama + langgraph.[/bold green]")
