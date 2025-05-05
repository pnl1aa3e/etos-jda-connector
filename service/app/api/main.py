import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.glogger import setup_glogger
from app.settings import settings

setup_glogger(
    app_name=settings.app_name,
    environment=settings.environment,
    level=settings.log_level,
)

logger = logging.getLogger(__name__)
app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    return """
    <html>
    Welcome to the Etos JDA Integrations. <br>
    Spec - SwaggerUI : <a href="/docs">/docs</a>. <br>
    </html>
    """