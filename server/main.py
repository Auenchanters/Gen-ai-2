"""FastAPI application: forecast / risk / alerts / ask endpoints with graceful degradation.

A single app serves the JSON API and (when built) the static frontend, so production is
one container and one origin. Routes depend on the repository *interface*, and external
integrations sit behind feature flags, so the whole surface is testable with no cloud
credentials.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server import __version__, ai, domain
from server.config import Settings, get_settings
from server.repository import ForecastRepository, get_repository
from server.schemas import Alert, AskRequest, AskResponse, Health, RiskRankRow, ZoneForecastPoint

_WEB_DIST = Path("web/dist")
_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data: https://fastapi.tiangolo.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "script-src 'self' https://cdn.jsdelivr.net; connect-src 'self'"
    ),
}


def repository_dep(settings: Settings = Depends(get_settings)) -> ForecastRepository:
    """FastAPI dependency that resolves the configured forecast repository."""
    return get_repository(settings)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(title="GridPulse API", version=__version__)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:8080"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_security_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers.update(_SECURITY_HEADERS)
        return response

    @app.get("/api/health")
    def health(settings: Settings = Depends(get_settings)) -> Health:
        """Report service health and which integrations are enabled."""
        return Health(
            status="ok",
            version=__version__,
            engine={"bigquery": settings.use_bigquery, "gemini": settings.use_gemini},
        )

    @app.get("/api/forecast")
    def get_forecast_points(
        zone: str | None = None, repo: ForecastRepository = Depends(repository_dep)
    ) -> list[ZoneForecastPoint]:
        """Return per-zone forecast points, optionally filtered to a single ``zone``."""
        forecast = repo.get_forecast()
        if zone is not None:
            forecast = forecast[forecast["zone"] == zone]
        return [
            ZoneForecastPoint(
                timestamp=row["timestamp"],
                zone=row["zone"],
                forecast_kwh=row["forecast_kwh"],
                capacity_kwh=row["capacity_kwh"],
                risk_score=row["risk_score"],
                risk_band=row["risk_band"],
            )
            for row in forecast.to_dict("records")
        ]

    @app.get("/api/risk")
    def get_risk(repo: ForecastRepository = Depends(repository_dep)) -> list[RiskRankRow]:
        """Return the current per-zone risk ranking, highest risk first."""
        return domain.latest_risk_ranking(repo.get_forecast())

    @app.get("/api/alerts")
    def get_alerts(repo: ForecastRepository = Depends(repository_dep)) -> list[Alert]:
        """Return actionable alerts for zones at high or critical risk."""
        return domain.alerts(repo.get_forecast())

    @app.post("/api/ask")
    def ask(
        request: AskRequest,
        repo: ForecastRepository = Depends(repository_dep),
        settings: Settings = Depends(get_settings),
    ) -> AskResponse:
        """Answer a natural-language question about current grid risk."""
        ranking = domain.latest_risk_ranking(repo.get_forecast())
        answer, source = ai.answer_question(
            request.question,
            ranking,
            use_gemini=settings.use_gemini,
            model=settings.gemini_model,
            project=settings.google_cloud_project,
            location=settings.google_cloud_location,
        )
        return AskResponse(answer=answer, source=source)

    if _WEB_DIST.is_dir():  # pragma: no cover - needs a built frontend
        app.mount("/", StaticFiles(directory=_WEB_DIST, html=True), name="web")
    else:

        @app.get("/")
        def root() -> dict[str, str]:
            """API index shown when no built frontend is mounted."""
            return {"name": "GridPulse API", "docs": "/docs", "health": "/api/health"}

    return app


app = create_app()
