from fastapi import APIRouter
from pydantic import BaseModel
import pandas as pd
import os

router = APIRouter()

# Load alumni data from the actual path within this project
CSV_PATHS = [
    os.path.join(os.path.dirname(__file__), "alumni.csv"),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "App", "alumni.csv"),
]

_df = None
for path in CSV_PATHS:
    if os.path.exists(path):
        _df = pd.read_csv(path)
        break

# request body
class PromptRequest(BaseModel):
    prompt: str

@router.post("/api/agent")
def agent_api(req: PromptRequest):
    if _df is None:
        return {"answer": "alumni.csv not found. Place it under App/alumni.csv"}

    # naive echo with alumni context for now to avoid requiring cloud LLMs here
    alumni_data = _df.head(5).to_string(index=False)
    return {"answer": f"Task: {req.prompt}\n\nSample alumni data:\n{alumni_data}"}
