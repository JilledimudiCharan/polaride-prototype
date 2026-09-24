import os
from dotenv import load_dotenv
from fastapi import FastAPI

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