"""Natural-language answers about grid risk: Gemini when enabled, rules otherwise.

The deterministic rules path means the ``/api/ask`` endpoint works with zero cloud
credentials (and is testable in CI). Every answer is tagged with its source.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.schemas import RiskRankRow


def answer_question(
    question: str,
    ranking: list[RiskRankRow],
    *,
    use_gemini: bool = False,
    model: str = "",
    project: str = "",
    location: str = "",
) -> tuple[str, str]:
    """Answer a question about current grid risk. Returns ``(answer, source)``."""
    if use_gemini:
        try:  # pragma: no cover - needs Vertex AI / Gemini
            answer = _gemini_answer(
                question, ranking, model=model, project=project, location=location
            )
            return answer, "gemini"
        except Exception:  # pragma: no cover - fall back to rules on any failure
            pass
    return _rules_answer(ranking), "rules"


def _rules_answer(ranking: list[RiskRankRow]) -> str:
    """Deterministic, data-grounded summary used when Gemini is disabled/unavailable."""
    if not ranking:
        return "No forecast data is available yet."
    top = ranking[0]
    at_risk = [r for r in ranking if r.risk_band in ("high", "critical")]
    summary = (
        f"Highest projected risk is {top.zone} at {top.risk_score:.0f}/100 "
        f"({top.risk_band}): forecast {top.forecast_kwh:.0f} kWh vs capacity "
        f"{top.capacity_kwh:.0f} kWh."
    )
    if at_risk:
        names = ", ".join(r.zone for r in at_risk)
        return f"{summary} {len(at_risk)} zone(s) need attention: {names}."
    return f"{summary} All zones are within safe limits."


def _gemini_answer(
    question: str, ranking: list[RiskRankRow], *, model: str, project: str, location: str
) -> str:  # pragma: no cover - needs Vertex AI / Gemini
    """Ask Gemini, grounding the answer strictly in the current risk ranking."""
    from google import genai

    client = genai.Client(vertexai=True, project=project, location=location)
    context = "\n".join(
        f"{r.zone}: risk {r.risk_score} ({r.risk_band}), forecast {r.forecast_kwh} kWh, "
        f"capacity {r.capacity_kwh} kWh"
        for r in ranking
    )
    prompt = (
        "You are a grid operations assistant. Using only this zone risk data:\n"
        f"{context}\n\nAnswer concisely for an operations planner: {question}"
    )
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text or "No answer generated."
