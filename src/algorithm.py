from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class NodeColor(str, Enum):
    RED = "red"
    BLACK = "black"


@dataclass
class TreeNode:
    value: int
    color: NodeColor = NodeColor.RED
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None
    parent: Optional["TreeNode"] = None

    @property
    def is_red(self) -> bool:
        return self.color == NodeColor.RED


class RedBlackTree:
    def __init__(self) -> None:
        self.root: Optional[TreeNode] = None
        self.steps: list[str] = []

    def clear(self) -> None:
        self.root = None
        self.steps = []

    def insert(self, value: int) -> bool:
        self.steps = []
        if self.root is None:
            self.root = TreeNode(value=value, color=NodeColor.BLACK)
            self.steps.append(f"{value} virou a raiz preta.")
            return True

        parent: Optional[TreeNode] = None
        current = self.root
        while current is not None:
            parent = current
            if value == current.value:
                self.steps.append(f"{value} ja existe; valores repetidos foram ignorados.")
                return False
            current = current.left if value < current.value else current.right

        node = TreeNode(value=value, parent=parent)
        if parent is not None and value < parent.value:
            parent.left = node
        elif parent is not None:
            parent.right = node

        self.steps.append(f"{value} entrou como no vermelho.")
        self._fix_insert(node)
        if self.root is not None:
            self.root.color = NodeColor.BLACK
        return True

    def values_in_order(self) -> list[int]:
        values: list[int] = []

        def walk(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            walk(node.left)
            values.append(node.value)
            walk(node.right)

        walk(self.root)
        return values

    def _fix_insert(self, node: TreeNode) -> None:
        while node.parent is not None and node.parent.is_red:
            grandparent = node.parent.parent
            if grandparent is None:
                break

            if node.parent == grandparent.left:
                uncle = grandparent.right
                if self._is_red(uncle):
                    self.steps.append("Pai e tio vermelhos: recoloracao.")
                    node.parent.color = NodeColor.BLACK
                    uncle.color = NodeColor.BLACK
                    grandparent.color = NodeColor.RED
                    node = grandparent
                else:
                    if node == node.parent.right:
                        self.steps.append("Caso esquerda-direita: rotacao a esquerda.")
                        node = node.parent
                        self._rotate_left(node)
                    self.steps.append("Caso esquerda-esquerda: rotacao a direita.")
                    node.parent.color = NodeColor.BLACK
                    grandparent.color = NodeColor.RED
                    self._rotate_right(grandparent)
            else:
                uncle = grandparent.left
                if self._is_red(uncle):
                    self.steps.append("Pai e tio vermelhos: recoloracao.")
                    node.parent.color = NodeColor.BLACK
                    uncle.color = NodeColor.BLACK
                    grandparent.color = NodeColor.RED
                    node = grandparent
                else:
                    if node == node.parent.left:
                        self.steps.append("Caso direita-esquerda: rotacao a direita.")
                        node = node.parent
                        self._rotate_right(node)
                    self.steps.append("Caso direita-direita: rotacao a esquerda.")
                    node.parent.color = NodeColor.BLACK
                    grandparent.color = NodeColor.RED
                    self._rotate_left(grandparent)

    def _rotate_left(self, node: TreeNode) -> None:
        pivot = node.right
        if pivot is None:
            return

        node.right = pivot.left
        if pivot.left is not None:
            pivot.left.parent = node

        pivot.parent = node.parent
        if node.parent is None:
            self.root = pivot
        elif node == node.parent.left:
            node.parent.left = pivot
        else:
            node.parent.right = pivot

        pivot.left = node
        node.parent = pivot

    def _rotate_right(self, node: TreeNode) -> None:
        pivot = node.left
        if pivot is None:
            return

        node.left = pivot.right
        if pivot.right is not None:
            pivot.right.parent = node

        pivot.parent = node.parent
        if node.parent is None:
            self.root = pivot
        elif node == node.parent.right:
            node.parent.right = pivot
        else:
            node.parent.left = pivot

        pivot.right = node
        node.parent = pivot

    @staticmethod
    def _is_red(node: Optional[TreeNode]) -> bool:
        return node is not None and node.color == NodeColor.RED

