from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from config import settings

router = APIRouter(tags=["ui"])


@router.get("/", response_class=HTMLResponse)
async def dashboard() -> str:
    return """
    <html>
      <head><title>Agent Hub</title></head>
      <body>
        <h1>Agent Hub</h1>
        <p>Streamlit UI: <a href="{ui_url}">open dashboard</a></p>
      </body>
    </html>
    """.format(ui_url=settings.ui_base_url)
