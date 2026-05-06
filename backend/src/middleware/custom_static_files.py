"""
MIDDLEWARE: custom_static_files
PURPOSE: StaticFiles subclass that adds no-cache headers for UI HTML
ENCODING: UTF-8 WITHOUT BOM
"""

from starlette.staticfiles import StaticFiles
from starlette.responses import Response


class NoCacheStaticFiles(StaticFiles):
    """
    StaticFiles that sets no-store, no-cache headers on responses.
    Used for /ui so HTML pages are not cached by browser or CDN.
    """

    def file_response(self, *args, **kwargs) -> Response:
        resp = super().file_response(*args, **kwargs)
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        resp.headers["CDN-Cache-Control"] = "no-cache"
        return resp
