def classify(answers: set[str]) -> str:
    count = len(answers)
    if count >= 60:
        return "hard"
    if count >= 35:
        return "medium"
    return "easy"
