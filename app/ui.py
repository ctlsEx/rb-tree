from __future__ import annotations

import asyncio
import math
import random
import re

import flet as ft
import flet.canvas as cv

from src.native_tree import NodeColor, RedBlackTree, TreeNode


class RedBlackTreeApp:
    CANVAS_WIDTH = 936
    CANVAS_HEIGHT = 444

    def __init__(self) -> None:
        self.tree = RedBlackTree()
        self.current_values: list[int] = []
        self.current_step = 0
        self.is_playing = False
        self.animation_value: int | None = None
        self.animation_scale = 1.0
        self.operation_token = 0

        self.info = ft.Text(
            "Lista vazia",
            color="#dbeafe",
            size=12,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        self.input_box = ft.TextField(
            label="Lista",
            width=966,
            height=54,
            hint_text="Ex: 41, 38, 31, 12, 19, 8",
            on_submit=self._load_list_from_input,
        )
        self.play_button = ft.OutlinedButton(
            "Play",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._toggle_play,
        )
        self.previous_button = ft.OutlinedButton("<", on_click=self._previous_step, width=52)
        self.next_button = ft.OutlinedButton(">", on_click=self._next_step, width=52)
        self.last_button = ft.OutlinedButton(
            "Last",
            icon=ft.Icons.LAST_PAGE,
            on_click=self._last_step,
        )
        self.node_overlay = ft.Stack(
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGHT,
            controls=[],
        )
        self.tree_canvas = cv.Canvas(
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGHT,
            shapes=[],
            content=self.node_overlay,
        )

    def run(self) -> None:
        ft.app(target=self._main)

    def _main(self, page: ft.Page) -> None:
        self.page = page
        page.title = "Arvore Rubro-Negra"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 17
        self._fix_window_size(page, width=1000, height=678)
        page.bgcolor = "#111827"

        page.add(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[ft.Container(expand=True), self.info],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    self.input_box,
                    ft.Row(
                        controls=[
                            ft.FilledButton("Inserir", icon=ft.Icons.ADD, on_click=self._load_list_from_input),
                            ft.OutlinedButton(
                                "Random",
                                icon=ft.Icons.SHUFFLE,
                                on_click=self._generate_random_list,
                            ),
                            self.previous_button,
                            self.play_button,
                            self.next_button,
                            self.last_button,
                            ft.OutlinedButton("Limpar", icon=ft.Icons.DELETE_OUTLINE, on_click=self._clear),
                        ],
                        wrap=True,
                        spacing=8,
                    ),
                    ft.Container(
                        content=self.tree_canvas,
                        bgcolor="#0f172a",
                        border=ft.Border(
                            left=ft.BorderSide(1, "#334155"),
                            top=ft.BorderSide(1, "#334155"),
                            right=ft.BorderSide(1, "#334155"),
                            bottom=ft.BorderSide(1, "#334155"),
                        ),
                        border_radius=8,
                        padding=12,
                        height=470,
                    ),
                ],
                expand=True,
                spacing=10,
            )
        )
        self._refresh()

    def _fix_window_size(self, page: ft.Page, width: int, height: int) -> None:
        page.window_width = width
        page.window_height = height
        page.window_min_width = width
        page.window_max_width = width
        page.window_min_height = height
        page.window_max_height = height
        page.window_resizable = False

        window = getattr(page, "window", None)
        if window is not None:
            window.width = width
            window.height = height
            window.min_width = width
            window.max_width = width
            window.min_height = height
            window.max_height = height
            window.resizable = False

    def _load_list_from_input(self, event: ft.ControlEvent) -> None:
        values = self._parse_values(self.input_box.value)
        self._stop_playback()
        if not values:
            self.current_values = []
            self._show_step(0, update_page=False)
            self._set_info("Lista invalida")
            self._refresh()
            return

        self.current_values = values
        self._show_step(0, update_page=False)
        self._set_info(f"{len(values)} valores | step 0/{len(values)}")
        self._refresh()

    def _generate_random_list(self, event: ft.ControlEvent) -> None:
        self._stop_playback()
        size = random.randint(5, 100)
        self.current_values = random.sample(range(1, 1000), size)
        self.input_box.value = ", ".join(str(value) for value in self.current_values)
        self._show_step(0, update_page=False)
        self._set_info(f"{size} valores aleatorios | step 0/{size}")
        self._refresh()

    def _clear(self, event: ft.ControlEvent) -> None:
        self._stop_playback()
        self.current_values = []
        self.current_step = 0
        self.tree.clear()
        self.input_box.value = ""
        self._set_info("Lista vazia")
        self._refresh()

    def _toggle_play(self, event: ft.ControlEvent) -> None:
        if not self.current_values:
            self._set_info("Carregue uma lista para iniciar")
            self._refresh()
            return

        if self.is_playing:
            self._stop_playback()
            self._refresh()
            return

        self.is_playing = True
        self.operation_token += 1
        token = self.operation_token
        self._set_play_label("Pause")
        self._refresh()
        self.page.run_task(self._play_loop, token)

    async def _play_loop(self, token: int) -> None:
        while self._operation_is_active(token, require_playing=True):
            if self.current_step >= len(self.current_values):
                self._show_step(0, status="Reiniciando sequencia")
                await asyncio.sleep(0.55)
                if not self._operation_is_active(token, require_playing=True):
                    return

            next_step = self.current_step + 1
            value = self.current_values[next_step - 1]
            completed = await self._animate_step(
                next_step,
                value,
                mode="add",
                token=token,
                require_playing=True,
            )
            if not completed:
                return
            await asyncio.sleep(0.55)

    async def _previous_step(self, event: ft.ControlEvent) -> None:
        self._stop_playback()
        token = self.operation_token
        if not self.current_values:
            self._refresh()
            return
        if self.current_step <= 0:
            self._show_step(0)
            return
        value = self.current_values[self.current_step - 1]
        await self._animate_step(
            self.current_step - 1,
            value,
            mode="remove",
            token=token,
        )

    async def _next_step(self, event: ft.ControlEvent) -> None:
        self._stop_playback()
        token = self.operation_token
        if not self.current_values:
            self._refresh()
            return
        if self.current_step >= len(self.current_values):
            self._show_step(len(self.current_values))
            return
        value = self.current_values[self.current_step]
        await self._animate_step(
            self.current_step + 1,
            value,
            mode="add",
            token=token,
        )

    def _last_step(self, event: ft.ControlEvent) -> None:
        self._stop_playback()
        if not self.current_values:
            self._refresh()
            return

        total = len(self.current_values)
        self._show_step(total, status=f"Arvore completa | step {total}/{total}")

    async def _animate_step(
        self,
        step: int,
        value: int,
        mode: str,
        token: int,
        require_playing: bool = False,
    ) -> bool:
        scales = [0.68, 0.86, 1.08, 1.0] if mode == "add" else [1.06, 0.86, 0.62]
        target_step = step if mode == "add" else step + 1
        self._show_step(target_step, status=self._step_label(target_step), update_page=False)

        for frame, scale in enumerate(scales):
            if not self._operation_is_active(token, require_playing):
                return False
            self.animation_value = value
            self.animation_scale = scale
            self._refresh(update_hints=frame == 0)
            await asyncio.sleep(0.10)

        if not self._operation_is_active(token, require_playing):
            return False
        self.animation_value = None
        self.animation_scale = 1.0
        if mode == "remove":
            self._show_step(step, status=self._step_label(step), update_page=True)
        else:
            self._set_info(self._step_label(step))
            self._refresh(update_hints=False)
        return True

    def _show_step(self, step: int, status: str | None = None, update_page: bool = True) -> None:
        self.current_step = max(0, min(step, len(self.current_values)))
        self.tree.clear()
        for value in self.current_values[: self.current_step]:
            self.tree.insert(value)
        self._set_info(status or self._step_label(self.current_step))
        if update_page:
            self._refresh()

    def _step_label(self, step: int) -> str:
        total = len(self.current_values)
        if total == 0:
            return "Lista vazia"
        if step == 0:
            return f"{total} valores | step 0/{total}"
        value = self.current_values[step - 1]
        return f"{total} valores | step {step}/{total} | valor {value}"

    def _stop_playback(self) -> None:
        self.is_playing = False
        self.operation_token += 1
        self.animation_value = None
        self.animation_scale = 1.0
        self._set_play_label("Play")

    def _set_play_label(self, label: str) -> None:
        self.play_button.content = label
        self.play_button.icon = ft.Icons.PAUSE if label == "Pause" else ft.Icons.PLAY_ARROW

    def _operation_is_active(self, token: int, require_playing: bool = False) -> bool:
        if token != self.operation_token:
            return False
        return self.is_playing if require_playing else True

    def _refresh(self, update_hints: bool = True) -> None:
        shapes, hints = self._build_tree_visuals(include_hints=update_hints)
        self.tree_canvas.shapes = shapes
        if hints is not None:
            self.node_overlay.controls = hints
        has_values = bool(self.current_values)
        self.play_button.disabled = not has_values
        self.previous_button.disabled = not has_values or self.current_step <= 0
        self.next_button.disabled = not has_values or self.current_step >= len(self.current_values)
        self.last_button.disabled = not has_values or self.current_step >= len(self.current_values)
        self.page.update()

    def _parse_values(self, raw_text: str) -> list[int]:
        numbers = [int(match) for match in re.findall(r"-?\d+", raw_text)]
        seen: set[int] = set()
        unique_numbers: list[int] = []
        for number in numbers:
            if number in seen:
                continue
            seen.add(number)
            unique_numbers.append(number)
        return unique_numbers

    def _build_tree_visuals(
        self,
        include_hints: bool = True,
    ) -> tuple[list[cv.Shape], list[ft.Control] | None]:
        if self.tree.root is None:
            empty_tree = cv.Text(
                self.CANVAS_WIDTH / 2,
                self.CANVAS_HEIGHT / 2,
                "Arvore vazia",
                style=ft.TextStyle(color="#94a3b8", size=24),
                alignment=ft.Alignment(0, 0),
                text_align=ft.TextAlign.CENTER,
            )
            return [empty_tree], [] if include_hints else None

        positions: dict[int, tuple[float, float]] = {}
        order = 0

        def place(node: TreeNode | None, depth: int) -> None:
            nonlocal order
            if node is None:
                return
            place(node.left, depth + 1)
            positions[id(node)] = (float(order), float(depth))
            order += 1
            place(node.right, depth + 1)

        place(self.tree.root, 0)
        total_nodes = max(order, 1)
        max_depth = int(max(depth for _, depth in positions.values()))
        canvas_width = self.CANVAS_WIDTH
        canvas_height = self.CANVAS_HEIGHT
        margin_x = 50.0
        margin_y = 46.0
        usable_width = canvas_width - (margin_x * 2)
        usable_height = canvas_height - (margin_y * 2)
        content_width = min(usable_width, max(total_nodes - 1, 0) * 92.0)
        content_height = min(usable_height, max_depth * 86.0)
        horizontal_gap = content_width / max(total_nodes - 1, 1)
        vertical_gap = content_height / max(max_depth, 1)
        origin_x = (canvas_width - content_width) / 2
        origin_y = (canvas_height - content_height) / 2
        horizontal_limit = 24.0 if total_nodes == 1 else horizontal_gap * 0.36
        vertical_limit = 24.0 if max_depth == 0 else vertical_gap * 0.30
        base_radius = max(2.4, min(24.0, horizontal_limit, vertical_limit))

        def point(node: TreeNode) -> tuple[float, float]:
            x_index, depth = positions[id(node)]
            x = canvas_width / 2 if total_nodes == 1 else origin_x + x_index * horizontal_gap
            y = origin_y + depth * vertical_gap
            return x, y

        def node_radius(node: TreeNode) -> float:
            scale = self.animation_scale if node.value == self.animation_value else 1.0
            return base_radius * scale

        shapes: list[cv.Shape] = []
        hints: list[ft.Control] | None = [] if include_hints else None
        edge_paint = ft.Paint(color="#64748b", stroke_width=2.3, style=ft.PaintingStyle.STROKE)

        def draw_edges(node: TreeNode | None) -> None:
            if node is None:
                return
            x1, y1 = point(node)
            for child in [node.left, node.right]:
                if child is None:
                    continue
                x2, y2 = point(child)
                dx = x2 - x1
                dy = y2 - y1
                distance = max(math.hypot(dx, dy), 1.0)
                start_radius = node_radius(node)
                end_radius = node_radius(child)
                shapes.append(
                    cv.Line(
                        x1 + (dx / distance) * start_radius,
                        y1 + (dy / distance) * start_radius,
                        x2 - (dx / distance) * end_radius,
                        y2 - (dy / distance) * end_radius,
                        paint=edge_paint,
                    )
                )
                draw_edges(child)

        def draw_nodes(node: TreeNode | None) -> None:
            if node is None:
                return
            draw_nodes(node.left)
            x, y = point(node)
            radius = node_radius(node)
            fill = "#dc2626" if node.color == NodeColor.RED else "#020617"
            stroke = "#fecaca" if node.color == NodeColor.RED else "#94a3b8"
            if node.value == self.animation_value:
                shapes.append(
                    cv.Circle(
                        x,
                        y,
                        radius + max(3.0, base_radius * 0.38),
                        paint=ft.Paint(color="#2563eb", style=ft.PaintingStyle.FILL),
                    )
                )
            shapes.append(cv.Circle(x, y, radius, paint=ft.Paint(color=fill, style=ft.PaintingStyle.FILL)))
            shapes.append(
                cv.Circle(
                    x,
                    y,
                    radius,
                    paint=ft.Paint(color=stroke, stroke_width=2.4, style=ft.PaintingStyle.STROKE),
                )
            )
            shapes.append(
                cv.Text(
                    x,
                    y,
                    str(node.value),
                    style=ft.TextStyle(
                        color="#ffffff",
                        size=max(
                            3.0,
                            min(
                                16.0,
                                radius * 0.78,
                                (radius * 2.35) / max(len(str(node.value)), 1),
                            ),
                        ),
                        weight=ft.FontWeight.BOLD,
                    ),
                    alignment=ft.Alignment(0, 0),
                    text_align=ft.TextAlign.CENTER,
                    max_lines=1,
                )
            )
            if hints is not None:
                hints.append(self._build_node_hint(node, x, y, base_radius))
            draw_nodes(node.right)

        draw_edges(self.tree.root)
        draw_nodes(self.tree.root)
        return shapes, hints

    def _build_node_hint(
        self,
        node: TreeNode,
        x: float,
        y: float,
        radius: float,
    ) -> ft.Container:
        description = self._relationship_description(node)
        summary = self._relationship_summary(node)
        button_size = max(10.0, min(19.0, radius * 0.82))
        icon_size = max(7.0, min(13.0, radius * 0.58))
        return ft.Container(
            content=ft.Text(
                "!",
                color="#93c5fd",
                size=icon_size,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            alignment=ft.Alignment(0, 0),
            tooltip=description,
            width=button_size,
            height=button_size,
            left=max(0.0, min(self.CANVAS_WIDTH - button_size, x - button_size / 2)),
            top=max(0.0, y - radius - button_size - 3.0),
            on_click=lambda event, text=summary: self._show_relationship(text),
        )

    def _show_relationship(self, text: str) -> None:
        self._set_info(text, tooltip=text)
        self.page.update(self.info)

    def _set_info(self, text: str, tooltip: str | None = None) -> None:
        self.info.value = text
        self.info.tooltip = tooltip

    def _relationship_summary(self, node: TreeNode) -> str:
        color = "vermelho" if node.color == NodeColor.RED else "preto"
        if node.parent is None:
            relationship = "raiz da arvore"
        else:
            side = "esquerdo" if node.parent.left is node else "direito"
            relationship = f"filho {side} de {node.parent.value}"

        left = str(node.left.value) if node.left is not None else "nenhum"
        right = str(node.right.value) if node.right is not None else "nenhum"
        return f"No {node.value}: {color} | {relationship} | filhos E: {left}, D: {right}"

    def _relationship_description(self, node: TreeNode) -> str:
        color = "vermelho" if node.color == NodeColor.RED else "preto"
        if node.parent is None:
            relationship = "Este no e a raiz e nao possui pai."
        else:
            side = "esquerdo" if node.parent.left is node else "direito"
            relationship = f"Este no e filho {side} de {node.parent.value}."

        left = str(node.left.value) if node.left is not None else "nenhum"
        right = str(node.right.value) if node.right is not None else "nenhum"
        return (
            f"No {node.value}\n"
            f"Cor: {color}\n"
            f"Parentesco: {relationship}\n"
            f"Filho esquerdo: {left}\n"
            f"Filho direito: {right}"
        )
