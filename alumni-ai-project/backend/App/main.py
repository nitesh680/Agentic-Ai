from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

try:
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
except Exception:
    ChatGoogleGenerativeAI = None  # type: ignore

app = FastAPI()

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
    key = os.getenv("GOOGLE_API_KEY")
    if key and ChatGoogleGenerativeAI is not None:
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3, google_api_key=key)
    return None

@app.post("/api/agent")
async def agent(request: PromptRequest):
    llm = _get_llm()
    if llm is None:
        return {"answer": "Set GOOGLE_API_KEY to use Gemini backend."}
    response = llm.invoke(request.prompt)
    return {"answer": getattr(response, "content", None) or str(response)}
