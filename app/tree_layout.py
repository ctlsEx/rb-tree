from __future__ import annotations

from dataclasses import dataclass

from app.red_black_tree import NodeColor, TreeNode


@dataclass(frozen=True)
class VisualNode:
    value: int
    color: NodeColor
    level: int
    slot: int


class TreeLayout:
    def __init__(self, root: TreeNode | None) -> None:
        self.root = root

    def by_levels(self) -> list[list[VisualNode | None]]:
        height = self._height(self.root)
        if height == 0:
            return []

        levels: list[list[VisualNode | None]] = []
        queue: list[tuple[TreeNode | None, int, int]] = [(self.root, 0, 0)]

        while queue:
            node, level, slot = queue.pop(0)
            if level >= height:
                continue

            while len(levels) <= level:
                levels.append([])
            while len(levels[level]) <= slot:
                levels[level].append(None)

            if node is None:
                levels[level][slot] = None
                queue.append((None, level + 1, slot * 2))
                queue.append((None, level + 1, slot * 2 + 1))
                continue

            levels[level][slot] = VisualNode(node.value, node.color, level, slot)
            queue.append((node.left, level + 1, slot * 2))
            queue.append((node.right, level + 1, slot * 2 + 1))

        return levels

    def _height(self, node: TreeNode | None) -> int:
        if node is None:
            return 0
        return 1 + max(self._height(node.left), self._height(node.right))

