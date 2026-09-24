from google.genai import types
from backend.llm import client, MODEL, generate_reply
from backend.governor import INSTRUCTIONS

SAFE_FALLBACK = "Let's think about this together. What have you tried so far, and where did you get stuck?"


def is_safe(question, level_name, instruction, reply):
    if level_name == "full":
        return True  # the full solution is allowed at the top level

    prompt = (
        f"Student question: {question}\n"
        f"Allowed help level: {level_name} ({instruction})\n"
        f"Tutor reply: {reply}\n\n"
        "Does the tutor reply give MORE help than the allowed level, "
        "for example by stating the final answer or the complete solution? "
        "Answer with exactly one word: LEAK or SAFE."
    )
    r = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0),
    )
    verdict = (r.text or "").upper()
    return "SAFE" in verdict and "LEAK" not in verdict


def guarded_reply(question, attempt, level_name, instruction, max_tries=2):
    for tries in range(1, max_tries + 1):
        reply = generate_reply(question, attempt, level_name, instruction)
        if is_safe(question, level_name, instruction, reply):
            return {"reply": reply, "guard_passed": True, "tries": tries}
    return {"reply": SAFE_FALLBACK, "guard_passed": False, "tries": max_tries}


if __name__ == "__main__":
    q = "Solve 2x+3=11"
    ins = INSTRUCTIONS["question"]
    print("Leaky reply safe?", is_safe(q, "question", ins, "The answer is x = 4."))
    print("Good reply safe?", is_safe(q, "question", ins, "What could you do first to isolate x?"))