from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

# Load environment variables from a local .env file if present
try:
    from dotenv import load_dotenv  # type: ignore
    # Load .env from current working directory
    load_dotenv()
    # Also try loading from the backend package directory explicitly
    from pathlib import Path
    load_dotenv(Path(__file__).parent / ".env")
except Exception:
    pass

try:
    from langchain_openai import ChatOpenAI  # type: ignore
except Exception:
    ChatOpenAI = None  # type: ignore

try:
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
except Exception:
    ChatGoogleGenerativeAI = None  # type: ignore


app = FastAPI()

# Enable CORS for local dev and simple hosting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptRequest(BaseModel):
    prompt: str


def _get_llm():
    """Pick an available LLM backend based on environment variables.

    Strict priority: If GOOGLE_API_KEY is set, use Gemini only.
    We do NOT fall back to OpenAI when a Google key exists to avoid accidental 401s.
    """
    # Hard-clear OpenAI for this process to avoid inheriting machine/user keys
    os.environ["OPENAI_API_KEY"] = ""
    google_key = os.getenv("GOOGLE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    force_provider = (os.getenv("FORCE_PROVIDER") or "").strip().lower()

    # Allow explicit override via FORCE_PROVIDER
    if force_provider == "gemini":
        if ChatGoogleGenerativeAI is None:
            raise RuntimeError("langchain-google-genai not installed. Run: pip install langchain-google-genai")
        if not google_key:
            raise RuntimeError("GOOGLE_API_KEY not set while FORCE_PROVIDER=gemini")
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3, google_api_key=google_key)

    if force_provider == "openai":
        # Intentionally disabled to prevent accidental OpenAI usage
        raise RuntimeError("OpenAI provider disabled. Use GOOGLE_API_KEY or unset FORCE_PROVIDER.")

    # Default priority: Gemini if available, else OpenAI
    if google_key:
        if ChatGoogleGenerativeAI is None:
            raise RuntimeError("langchain-google-genai not installed. Run: pip install langchain-google-genai")
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3, google_api_key=google_key)

    # Do not fallback to OpenAI

    return None


def _get_provider_status():
    google_key = bool(os.getenv("GOOGLE_API_KEY"))
    openai_key = bool(os.getenv("OPENAI_API_KEY"))
    if google_key:
        provider = "gemini"
    elif openai_key:
        provider = "openai"
    else:
        provider = "none"
    return {"provider": provider, "has_google_key": google_key, "has_openai_key": openai_key}


@app.get("/api/status")
async def status():
    return _get_provider_status()


@app.post("/api/agent")
async def agent_endpoint(request: PromptRequest):
    llm = _get_llm()

    # If no provider configured, return a helpful message instead of failing
    if llm is None:
        return {
            "answer": "LLM not configured. Set GOOGLE_API_KEY for Gemini or OPENAI_API_KEY for OpenAI and restart the server.",
        }
    try:
        response = llm.invoke(request.prompt)
        content = getattr(response, "content", None) or str(response)
        return {"answer": content}
    except Exception as e:
        # Return a safe JSON payload so frontend doesn't see 500s
        return {"answer": f"Provider error: {e}"}
