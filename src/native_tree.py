from __future__ import annotations

import ctypes
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class NodeColor(str, Enum):
    RED = "red"
    BLACK = "black"


@dataclass
class TreeNode:
    value: int
    color: NodeColor
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None
    parent: Optional["TreeNode"] = None

    @property
    def is_red(self) -> bool:
        return self.color == NodeColor.RED


class _CTreeNode(ctypes.Structure):
    pass


_CTreeNodePointer = ctypes.POINTER(_CTreeNode)
_CTreeNode._fields_ = [
    ("value", ctypes.c_int),
    ("color", ctypes.c_int),
    ("left", _CTreeNodePointer),
    ("right", _CTreeNodePointer),
    ("parent", _CTreeNodePointer),
]


def _library_path() -> Path:
    filename = {
        "win32": "algorithm.dll",
        "darwin": "libalgorithm.dylib",
    }.get(sys.platform, "libalgorithm.so")
    return Path(__file__).resolve().with_name(filename)


def _load_library() -> ctypes.CDLL:
    path = _library_path()
    if not path.exists():
        raise RuntimeError(
            f"Biblioteca nativa nao encontrada: {path}. "
            "Compile-a primeiro; no Windows, execute .\\build.ps1."
        )

    library = ctypes.CDLL(str(path))
    library.rb_tree_create.argtypes = []
    library.rb_tree_create.restype = ctypes.c_void_p
    library.rb_tree_destroy.argtypes = [ctypes.c_void_p]
    library.rb_tree_destroy.restype = None
    library.rb_tree_clear.argtypes = [ctypes.c_void_p]
    library.rb_tree_clear.restype = None
    library.rb_tree_insert.argtypes = [ctypes.c_void_p, ctypes.c_int]
    library.rb_tree_insert.restype = ctypes.c_int
    library.rb_tree_root.argtypes = [ctypes.c_void_p]
    library.rb_tree_root.restype = _CTreeNodePointer
    return library


_LIBRARY = _load_library()


class RedBlackTree:
    def __init__(self) -> None:
        self._handle = _LIBRARY.rb_tree_create()
        if not self._handle:
            raise MemoryError("Nao foi possivel criar a arvore rubro-negra.")
        self.root: Optional[TreeNode] = None
        self.steps: list[str] = []

    def __del__(self) -> None:
        handle = getattr(self, "_handle", None)
        if handle:
            _LIBRARY.rb_tree_destroy(handle)
            self._handle = None

    def clear(self) -> None:
        _LIBRARY.rb_tree_clear(self._handle)
        self.root = None
        self.steps = []

    def insert(self, value: int) -> bool:
        self.steps = []
        result = _LIBRARY.rb_tree_insert(self._handle, value)
        if result < 0:
            raise MemoryError("Falha de memoria ao inserir um no.")

        self.root = self._snapshot(_LIBRARY.rb_tree_root(self._handle))
        if result == 0:
            self.steps.append(f"{value} ja existe; valores repetidos foram ignorados.")
            return False

        self.steps.append(f"{value} foi inserido e balanceado pelo algoritmo em C.")
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

    @classmethod
    def _snapshot(
        cls,
        pointer: _CTreeNodePointer,
        parent: Optional[TreeNode] = None,
    ) -> Optional[TreeNode]:
        if not pointer:
            return None

        native_node = pointer.contents
        node = TreeNode(
            value=native_node.value,
            color=NodeColor.BLACK if native_node.color == 1 else NodeColor.RED,
            parent=parent,
        )
        node.left = cls._snapshot(native_node.left, node)
        node.right = cls._snapshot(native_node.right, node)
        return node
