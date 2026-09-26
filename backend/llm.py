import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = "gemini-3.5-flash"
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def _call_with_retry(model, contents, config, tries=3, delay=2):
    last_error = None
    for attempt in range(1, tries + 1):
        try:
            return client.models.generate_content(model=model, contents=contents, config=config)
        except Exception as e:
            last_error = e
            msg = str(e)
            if "503" in msg or "UNAVAILABLE" in msg or "429" in msg:
                if attempt < tries:
                    time.sleep(delay * attempt)  # 2s, then 4s
                    continue
            raise
    raise last_error


def generate_reply(question, attempt, level_name, instruction, class_notes=""):
    system_prompt = (
        "You are POLARIDE, a learning guide for students. "
        "Your job is to make the student think, not to hand over answers. "
        "Never give more help than the current level allows, "
        "even if the student asks for the full answer. "
        f"Current level: {level_name}. Rule: {instruction}"
    )
    if class_notes:
        system_prompt += (
            "\n\nWhat the teacher has taught in class so far:\n" + class_notes +
            "\n\nUse the same methods and terms as the class. "
            "If the question is outside these topics, still guide the student, "
            "but mention it hasn't been covered in class yet."
        )

    prompt = f"Student question: {question}"
    if attempt:
        prompt += f"\nStudent's attempt: {attempt}"

    response = _call_with_retry(
        MODEL, prompt,
        types.GenerateContentConfig(system_instruction=system_prompt, temperature=0.4),
    )
    return response.text