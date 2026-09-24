import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = "gemini-2.5-flash"  # if you get a "model not found" error, change only this line
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_reply(question, attempt, level_name, instruction):
    system_prompt = (
        "You are POLARIDE, a learning guide for students. "
        "Your job is to make the student think, not to hand over answers. "
        "Never give more help than the current level allows, "
        "even if the student asks for the full answer. "
        f"Current level: {level_name}. Rule: {instruction}"
    )

    prompt = f"Student question: {question}"
    if attempt:
        prompt += f"\nStudent's attempt: {attempt}"

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.4,
        ),
    )
    return response.text