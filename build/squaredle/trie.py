from dataclasses import dataclass, field


@dataclass
class Node:
    children: dict[str, "Node"] = field(default_factory=dict)
    is_word: bool = False


class Trie:
    def __init__(self) -> None:
        self.root = Node()

    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            node = node.children.setdefault(char, Node())
        node.is_word = True

    def contains(self, word: str) -> bool:
        node = self._walk(word)
        return bool(node and node.is_word)

    def has_prefix(self, prefix: str) -> bool:
        return self._walk(prefix) is not None

    def _walk(self, text: str) -> Node | None:
        node = self.root
        for char in text:
            next_node = node.children.get(char)
            if next_node is None:
                return None
            node = next_node
        return node
