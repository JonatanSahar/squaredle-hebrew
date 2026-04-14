def classify(answers: set[str]) -> str:
    count = len(answers)
    if count >= 60:
        return "easy"
    if count >= 35:
        return "medium"
    return "hard"
