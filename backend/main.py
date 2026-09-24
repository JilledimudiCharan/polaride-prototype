import os
from dotenv import load_dotenv
from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from backend.governor import decide_level

load_dotenv()  # reads GEMINI_API_KEY from your .env file

app = FastAPI(title="POLARIDE Prototype")


@app.get("/")
def home():
    return {"message": "POLARIDE is running"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "gemini_key_loaded": bool(os.getenv("GEMINI_API_KEY")),
    }
class AskRequest(BaseModel):
    student_id: str
    question: str
    attempt: Optional[str] = None


@app.post("/ask")
def ask(req: AskRequest):
    return decide_level(req.student_id, req.question, req.attempt)