import json
import os
from google.genai import types
from backend.llm import client, MODEL

KB_FILE = "knowledge_base.json"

PROMPT = (
    "You are a classroom assistant. From this lecture, return ONLY JSON with two keys: "
    '"summary" (max 5 sentences) and "topics" (a list of short topic names covered).'
)


def load_kb():
    if os.path.exists(KB_FILE):
        with open(KB_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"lectures": []}


def save_kb(kb):
    with open(KB_FILE, "w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2)


def process_lecture(filename, data, content_type):
    if content_type and content_type.startswith("audio/"):
        contents = [types.Part.from_bytes(data=data, mime_type=content_type), PROMPT]
    else:
        text = data.decode("utf-8", errors="ignore")
        contents = [PROMPT + "\n\nLecture text:\n" + text]

    r = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json", temperature=0.2
        ),
    )
    result = json.loads(r.text)

    kb = load_kb()
    kb["lectures"].append(
        {"file": filename, "summary": result["summary"], "topics": result["topics"]}
    )
    save_kb(kb)
    return result
def get_class_notes():
    kb = load_kb()
    parts = []
    for lec in kb["lectures"]:
        parts.append(f"Summary: {lec['summary']}\nTopics: {', '.join(lec['topics'])}")
    return "\n\n".join(parts)