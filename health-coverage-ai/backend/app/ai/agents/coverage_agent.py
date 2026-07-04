"""LangGraph coverage analysis agent.

Graph topology:
    START → retrieve_context → analyze_coverage → END

State flows linearly through the two nodes; errors short-circuit by setting
the `error` key, which is checked before calling the LLM.
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Optional

from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from app.ai.prompts.coverage_prompts import SYSTEM_PROMPT, build_user_prompt
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.rag.retriever import CoverageRetriever, RetrievedChunk

logger = logging.getLogger(__name__)

# ── State definition ──────────────────────────────────────────────────────────


class CoverageState(TypedDict):
    query: str
    affiliate: dict
    chunks: list[RetrievedChunk]
    coverage_result: str          # cubierto | no_cubierto | cubierto_con_condiciones
    response_text: str
    conditions: list[str]
    steps: list[dict]             # agent trace for the API response
    error: Optional[str]
    start_time: float


# ── Node implementations ──────────────────────────────────────────────────────


def _retrieve_node(state: CoverageState, retriever: CoverageRetriever) -> dict:
    """Query ChromaDB for the most relevant policy document chunks."""
    t0 = time.perf_counter()

    try:
        chunks = retriever.retrieve(state["query"])
    except Exception as exc:
        logger.warning("Retrieval failed: %s", exc)
        chunks = []

    elapsed = int((time.perf_counter() - t0) * 1000)
    step = {
        "step": "retrieve_context",
        "description": "Búsqueda semántica en documentos del plan (DOC1, DOC2, DOC3)",
        "result": f"{len(chunks)} fragmentos relevantes encontrados",
        "duration_ms": elapsed,
    }
    return {"chunks": chunks, "steps": state["steps"] + [step]}


async def _analyze_node(
    state: CoverageState, llm: OpenAIProvider
) -> dict:
    """Call the LLM with affiliate context + retrieved chunks → parse JSON."""
    if state.get("error"):
        return {}

    t0 = time.perf_counter()

    context = CoverageRetriever.format_context(state["chunks"])
    user_prompt = build_user_prompt(state["affiliate"], context, state["query"])

    try:
        raw = await llm.complete_with_system(
            system=SYSTEM_PROMPT,
            user=user_prompt,
            temperature=0.1,
            max_tokens=2000,
        )
        parsed = _parse_llm_response(raw)
    except Exception as exc:
        logger.error("LLM call failed: %s", exc)
        elapsed = int((time.perf_counter() - t0) * 1000)
        step = {
            "step": "analyze_coverage",
            "description": "Análisis de cobertura con LLM",
            "result": f"Error: {exc}",
            "duration_ms": elapsed,
        }
        return {
            "coverage_result": "no_cubierto",
            "response_text": (
                "No fue posible completar el análisis de cobertura en este momento. "
                "Por favor, inténtelo nuevamente."
            ),
            "conditions": [],
            "error": str(exc),
            "steps": state["steps"] + [step],
        }

    elapsed = int((time.perf_counter() - t0) * 1000)
    step = {
        "step": "analyze_coverage",
        "description": "Análisis de cobertura con LLM (GPT-4o)",
        "result": f"Resultado: {parsed.get('coverage_result', 'unknown')}",
        "duration_ms": elapsed,
    }
    return {
        "coverage_result": parsed.get("coverage_result", "no_cubierto"),
        "response_text": parsed.get("response_text", raw),
        "conditions": parsed.get("conditions", []),
        "steps": state["steps"] + [step],
    }


def _parse_llm_response(raw: str) -> dict:
    """
    Extract JSON from the LLM response.
    Handles cases where the model wraps the JSON in a code block.
    """
    # Strip markdown code blocks if present
    text = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()

    # Try to find a JSON object in the response
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    logger.warning("Could not parse LLM JSON response: %s", raw[:200])
    return {
        "coverage_result": "no_cubierto",
        "response_text": raw,
        "conditions": [],
    }


# ── Graph builder ─────────────────────────────────────────────────────────────


class CoverageAgent:
    """
    LangGraph-based coverage analysis agent.

    The compiled graph executes two nodes sequentially:
      1. retrieve_context — vector search in ChromaDB
      2. analyze_coverage — LLM reasoning with the retrieved context
    """

    def __init__(self, retriever: CoverageRetriever, llm: OpenAIProvider) -> None:
        self._retriever = retriever
        self._llm = llm
        self._graph = self._build_graph()

    def _build_graph(self):
        retriever = self._retriever
        llm = self._llm

        # Wrap nodes as closures that capture dependencies
        def retrieve(state: CoverageState) -> dict:
            return _retrieve_node(state, retriever)

        async def analyze(state: CoverageState) -> dict:
            return await _analyze_node(state, llm)

        graph: StateGraph = StateGraph(CoverageState)
        graph.add_node("retrieve_context", retrieve)
        graph.add_node("analyze_coverage", analyze)
        graph.set_entry_point("retrieve_context")
        graph.add_edge("retrieve_context", "analyze_coverage")
        graph.add_edge("analyze_coverage", END)
        return graph.compile()

    async def run(self, query: str, affiliate: dict) -> CoverageState:
        """Execute the full analysis graph and return the final state."""
        initial: CoverageState = {
            "query": query,
            "affiliate": affiliate,
            "chunks": [],
            "coverage_result": "no_cubierto",
            "response_text": "",
            "conditions": [],
            "steps": [],
            "error": None,
            "start_time": time.perf_counter(),
        }
        return await self._graph.ainvoke(initial)
