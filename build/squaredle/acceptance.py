def accept_puzzle(answers: set[str], anchor: str) -> bool:
    count = len(answers)
    if not (10 <= count <= 100):
        return False
    if anchor not in answers:
        return False

    four_letter = sum(1 for word in answers if len(word) == 4)
    if four_letter / count > 0.70:
        return False

    if sum(1 for word in answers if len(word) >= 5) < 3:
        return False
    if sum(1 for word in answers if len(word) >= 6) < 1:
        return False
    if max(len(word) for word in answers) < 6:
        return False

    plurals = sum(1 for word in answers if word.endswith("ים") or word.endswith("ות"))
    if plurals / count > 0.35:
        return False

    return True
