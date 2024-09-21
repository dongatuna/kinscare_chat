import logging
import os

from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic

import uvicorn

from kinscare_chat.ai.openai_api import OpenAIAssistant
from kinscare_chat.server.routes.chats import router as router_chats

app = FastAPI()
app.include_router(router_chats)
security = HTTPBasic()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = '8080'
assistant = OpenAIAssistant(os.getenv("OPENAI_ASSISTANT_ID"))
router = APIRouter()


@app.get("/preview", tags=["Dev"])
async def get_preview_html():
    """
    Endpoint to retrieve an HTML file.

    :return: HTML file response.
    """
    html_file_path = os.path.join(os.path.dirname(__file__), "index.html")
    return FileResponse(html_file_path)

@app.get("/privacy-policy", tags=["Policies"])
async def get_privacy_policy_html():
    """
    Endpoint to retrieve an HTML file.

    :return: HTML file response.
    """
    html_file_path = os.path.join(os.path.dirname(__file__), "privacy-policy.html")
    return FileResponse(html_file_path)

@app.get("/")
async def read_root():
    """
    Root endpoint to check if the server is running.

    :return: JSON message indicating server status.
    """
    return {"message": "Kinscare Chat Backend."}

def run_server():
    """
    Run the FastAPI server with configurable host and port.
    """
    host = os.getenv("SERVER_HOST", DEFAULT_HOST)
    port = os.getenv("SERVER_PORT", DEFAULT_PORT)

    try:
        port = int(port)
    except ValueError as exc:
        raise ValueError(
            "SERVER_PORT environment variable must be a valid integer"
        ) from exc

    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()
