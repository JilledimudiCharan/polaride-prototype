from fastapi import FastAPI, UploadFile, File
from dotenv import load_dotenv
from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from backend.governor import decide_level, dependency_report
from backend.guard import guarded_reply
from backend.lecture import process_lecture, load_kb, get_class_notes, coverage_report
from fastapi.staticfiles import StaticFiles

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
    decision = decide_level(req.student_id, req.question, req.attempt)
    try:
        result = guarded_reply(
            req.question, req.attempt,
            decision["level_name"], decision["instruction"],
            class_notes=get_class_notes(),
        )
        decision.update(result)
    except Exception as e:
        decision["reply"] = None
        decision["error"] = f"Gemini call failed: {e}"
    return decision
@app.post("/lecture")
async def lecture(file: UploadFile = File(...)):
    data = await file.read()
    try:
        return process_lecture(file.filename, data, file.content_type)
    except Exception as e:
        return {"error": f"Lecture processing failed: {e}"}


@app.get("/knowledge")
def knowledge():
    return load_kb()
@app.get("/dashboard")
def dashboard():
    return {"syllabus": coverage_report(), "students": dependency_report()}
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")