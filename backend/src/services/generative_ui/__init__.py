"""Controlled Generative UI foundation (H-019). Template-bound, sandboxed-ready HTML snippets only."""

from src.services.generative_ui.generation_service import generate_render_response
from src.services.generative_ui.validation_service import validate_render_request

__all__ = ["generate_render_response", "validate_render_request"]
