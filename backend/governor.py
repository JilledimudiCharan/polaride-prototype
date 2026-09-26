LEVELS = ["question", "hint", "step", "partial", "full"]

INSTRUCTIONS = {
    "question": "Ask ONE guiding question that helps the student get started. Reveal nothing about the answer.",
    "hint": "Give ONE small hint pointing to the right concept. Do not solve anything.",
    "step": "Explain only the FIRST step of the approach. Stop there.",
    "partial": "Solve about half of the problem and leave the final part for the student.",
    "full": "Give the complete solution with a clear explanation.",
}

# Where each student is on each question: {(student_id, question): level_number}
progress = {}

# Overall usage per student (used later for the dependency score)
stats = {}


def decide_level(student_id, question, attempt=None):
    key = (student_id, question.strip().lower())
    is_new_question = key not in progress
    level = progress.get(key, 0)

    attempted = bool(attempt and attempt.strip())
    escalated = False

    # Climb the ladder only if the student has tried something
    if not is_new_question and attempted:
        level = min(level + 1, len(LEVELS) - 1)
        escalated = True

    progress[key] = level

    s = stats.setdefault(student_id, {"requests": 0, "escalations": 0})
    s["requests"] += 1
    if escalated:
        s["escalations"] += 1

    message = ""
    if not is_new_question and not attempted:
        message = "Try it yourself first and send your attempt to get the next level of help."

    return {
        "level_number": level,
        "level_name": LEVELS[level],
        "instruction": INSTRUCTIONS[LEVELS[level]],
        "message": message,
    }
def dependency_report():
    per_student = {}
    for (sid, _q), level in progress.items():
        per_student.setdefault(sid, []).append(level)

    report = []
    for sid, levels in per_student.items():
        avg = sum(levels) / len(levels)
        score = round(avg / (len(LEVELS) - 1) * 100)
        label = "Low" if score < 25 else "Moderate" if score < 60 else "High"
        report.append({
            "student_id": sid,
            "questions": len(levels),
            "ai_dependency_percent": score,
            "dependency_level": label,
            "requests": stats.get(sid, {}).get("requests", 0),
        })
    return report