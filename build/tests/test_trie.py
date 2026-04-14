from squaredle.trie import Trie


def test_insert_and_contains() -> None:
    trie = Trie()
    trie.insert("שלומ")

    assert trie.contains("שלומ")
    assert not trie.contains("שלו")


def test_has_prefix() -> None:
    trie = Trie()
    trie.insert("שלומ")

    assert trie.has_prefix("של")
    assert trie.has_prefix("שלומ")
    assert not trie.has_prefix("מה")


def test_child_navigation() -> None:
    trie = Trie()
    trie.insert("שלומ")

    node = trie.root.children["ש"].children["ל"]
    assert not node.is_word

    end = node.children["ו"].children["מ"]
    assert end.is_word
