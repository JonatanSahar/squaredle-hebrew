from squaredle.difficulty import classify


def test_easy() -> None:
    answers = {f"אבגד{i}" for i in range(70)}
    assert classify(answers) == "easy"


def test_hard() -> None:
    answers = {f"אבגד{i}" for i in range(22)}
    assert classify(answers) == "hard"


def test_medium() -> None:
    answers = {f"אבגד{i}" for i in range(40)}
    assert classify(answers) == "medium"
