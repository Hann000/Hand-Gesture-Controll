"""UI overlay untuk aplikasi gesture control."""

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2

import config
from mode_controller import AppMode, MODE_INFO
from ui_theme import (
    C, corner_brackets, draw_badge, glass_panel, glow_circle,
    gradient_bar_vertical, put_text, put_text_block, rounded_rect,
)

MODE_COLORS = {
    AppMode.CURSOR: C.ACCENT,
    AppMode.SCROLL: C.PURPLE,
    AppMode.VOLUME: C.CYAN,
}

PANEL_LEFT = (16, 130, 218, 310)
PANEL_RIGHT_PAD = 250


@dataclass
class UIState:
    hand_detected: bool = False
    active_mode: str = "cursor"
    mode_label: str = "KURSOR"
    mode_hint: str = ""
    switch_progress: float = 0.0
    switch_target: str = ""
    cursor_pos: Optional[Tuple[float, float]] = None
    click_status: str = "IDLE"
    click_distance: Optional[float] = None
    scroll_status: str = "IDLE"
    volume_status: str = "LOCKED"
    volume_percent: float = 0.0
    volume_enabled: bool = False
    volume_locked: bool = True
    volume_lock_status: str = "LOCKED"
    volume_lock_progress: float = 0.0
    scroll_holding: bool = False


class HUD:
    """Dashboard overlay utama."""

    def render(self, frame, state: UIState):
        h, w = frame.shape[:2]
        self._draw_header(frame, w, state)
        self._draw_mode_banner(frame, w, state)
        self._draw_left_panel(frame, state)
        self._draw_right_panel(frame, w, state)
        self._draw_footer(frame, w, h)

    def _current_mode(self, state: UIState) -> AppMode:
        try:
            return AppMode(state.active_mode)
        except ValueError:
            return AppMode.CURSOR

    def _draw_header(self, frame, w: int, state: UIState):
        glass_panel(frame, 0, 0, w, 56, alpha=0.82)
        put_text(frame, "GESTURE CONTROL", (20, 36), 0.8, C.ACCENT, 2)
        put_text(frame, "Kontrol PC via gestur tangan", (20, 50), 0.38, C.TEXT_DIM, 1)

        badge = "HAND OK" if state.hand_detected else "NO HAND"
        draw_badge(frame, w - 128, 14, badge, state.hand_detected,
                   C.GREEN if state.hand_detected else C.RED)

    def _draw_mode_banner(self, frame, w: int, state: UIState):
        mode = self._current_mode(state)
        color = MODE_COLORS[mode]
        bx, bw, bh = w // 2 - 150, 300, 50

        glass_panel(frame, bx, 62, bw, bh, alpha=0.85)
        put_text(frame, f"MODE: {state.mode_label}", (bx + 16, 92), 0.68, color, 2)

        if state.switch_progress > 0 and state.switch_target:
            bar_x, bar_y, bar_w = bx + 16, 98, bw - 32
            rounded_rect(frame, bar_x, bar_y, bar_x + bar_w, bar_y + 8, (48, 46, 42), radius=3, thickness=-1)
            rounded_rect(
                frame, bar_x, bar_y,
                bar_x + int(bar_w * state.switch_progress), bar_y + 8,
                C.GREEN, radius=3, thickness=-1,
            )
            put_text(frame, f"Ganti ke {state.switch_target}", (bx + 16, 108), 0.34, C.GREEN, 1)
        else:
            put_text(frame, "Aktif", (bx + bw - 52, 92), 0.4, C.TEXT_DIM, 1)

    def _draw_left_panel(self, frame, state: UIState):
        x, y, pw, ph = PANEL_LEFT
        glass_panel(frame, x, y, pw, ph, alpha=0.78)
        mode = self._current_mode(state)
        info = MODE_INFO[mode]

        put_text(frame, "CARA PAKAI", (x + 16, y + 30), 0.46, C.TEXT_DIM, 1)
        put_text_block(
            frame,
            [info["hint"], info.get("hint2", "")],
            x + 16, y + 52, 0.38, MODE_COLORS[mode], 17,
        )

        put_text(frame, "GANTI MODE", (x + 16, y + 100), 0.46, C.TEXT_DIM, 1)
        put_text(frame, "Tahan diam ~0.7 dtk:", (x + 16, y + 120), 0.34, C.TEXT_DIM, 1)

        row_y = y + 142
        for m, minfo in MODE_INFO.items():
            active = m == mode
            color = MODE_COLORS[m] if active else C.TEXT_DIM
            mark = ">" if active else " "
            put_text(frame, f"{mark} {minfo['label']}", (x + 16, row_y), 0.4, color, 2 if active else 1)
            put_text(frame, minfo["switch"], (x + 24, row_y + 16), 0.32, C.TEXT_DIM, 1)
            row_y += 36

        if mode == AppMode.VOLUME:
            lock_label = "LOCK" if state.volume_locked else "ON"
            lock_color = C.MUTED if state.volume_locked else C.CYAN
            put_text(frame, f"VOL {lock_label}", (x + 16, y + ph - 50), 0.4, lock_color, 1)
            if state.volume_locked:
                rounded_rect(frame, x + 16, y + ph - 38, x + 38, y + ph - 10, (50, 48, 45), radius=4, thickness=-1)
            else:
                gradient_bar_vertical(frame, x + 16, y + ph - 38, 22, 28, state.volume_percent, C.CYAN, C.BLUE)
            put_text(frame, f"{int(state.volume_percent)}%", (x + 48, y + ph - 18), 0.5, lock_color, 1)

    def _draw_right_panel(self, frame, w: int, state: UIState):
        px = w - PANEL_RIGHT_PAD
        pw = 230
        x, y, ph = px, 130, 310
        glass_panel(frame, x, y, pw, ph, alpha=0.78)
        put_text(frame, "STATUS", (x + 16, y + 30), 0.46, C.TEXT_DIM, 1)

        mode = self._current_mode(state)
        cards = self._build_status_cards(state, mode)
        card_y = y + 52
        for card in cards:
            self._draw_mode_card(frame, x + 12, card_y, pw - 24, card)
            card_y += 50

    def _build_status_cards(self, state: UIState, mode: AppMode) -> list:
        if mode == AppMode.CURSOR:
            if state.click_status == "ACTIVE_CLICK":
                sub = "Klik terkirim"
            elif state.cursor_pos:
                sub = f"Pos {int(state.cursor_pos[0])}, {int(state.cursor_pos[1])}"
            else:
                sub = "Gerakkan telunjuk"
            return [
                ("Kursor", sub, state.hand_detected, C.ACCENT),
                ("Klik", "Telunjuk + tengah", state.click_status != "IDLE", C.RED),
            ]
        if mode == AppMode.SCROLL:
            sub = {
                "IDLE": "Siap scroll",
                "SCROLL_HOLD": "Geser naik/turun",
                "SCROLLING": "Scrolling...",
            }.get(state.scroll_status, state.scroll_status)
            return [("Scroll", sub, state.scroll_status != "IDLE", C.PURPLE)]
        if mode == AppMode.VOLUME:
            if state.volume_lock_status == "HOLD_LOCK":
                sub = f"Lock toggle {int(state.volume_lock_progress * 100)}%"
            elif state.volume_locked:
                sub = "Terkunci - tahan tel+tengah"
            else:
                sub = f"Aktif {int(state.volume_percent)}%"
            active = not state.volume_locked or state.volume_lock_status == "HOLD_LOCK"
            color = C.MUTED if state.volume_locked else C.CYAN
            return [("Volume", sub, active, color)]
        return []

    def _draw_mode_card(self, frame, x: int, y: int, w: int, card: tuple):
        title, subtitle, active, accent = card
        overlay = frame.copy()
        bg = (accent[0] // 6, accent[1] // 6, accent[2] // 6) if active else (36, 34, 32)
        rounded_rect(overlay, x, y, x + w, y + 42, bg, radius=8, thickness=-1)
        if active:
            rounded_rect(overlay, x, y, x + 3, y + 42, accent, radius=2, thickness=-1)
        cv2.addWeighted(overlay, 0.88, frame, 0.12, 0, frame)

        dot = accent if active else C.MUTED
        cv2.circle(frame, (x + 14, y + 21), 4, dot, -1, cv2.LINE_AA)
        put_text(frame, title, (x + 26, y + 17), 0.44, accent if active else C.TEXT_DIM, 1)
        put_text(frame, subtitle, (x + 26, y + 33), 0.34, C.TEXT, 1)

    def _draw_footer(self, frame, w: int, h: int):
        glass_panel(frame, 0, h - 40, w, 40, alpha=0.82)
        put_text(
            frame,
            "Ganti mode: tahan gestur  |  Q keluar",
            (20, h - 12), 0.42, C.TEXT_DIM, 1,
        )


def draw_mode_switch_indicator(frame, landmarks, modes):
    pose = modes.detect_switch_pose(landmarks)
    if pose is None or modes.switch_progress <= 0:
        return

    h, w = frame.shape[:2]
    color = MODE_COLORS.get(pose, C.GREEN)
    cx = int(landmarks[0].x * w)
    cy = int(landmarks[0].y * h)
    radius = int(28 + 18 * modes.switch_progress)

    overlay = frame.copy()
    cv2.circle(overlay, (cx, cy), radius, color, 2, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)

    if pose == AppMode.CURSOR:
        ix = (int(landmarks[8].x * w), int(landmarks[8].y * h))
        mx = (int(landmarks[12].x * w), int(landmarks[12].y * h))
        glow_circle(frame, ix, 12, color)
        glow_circle(frame, mx, 12, color)
        cv2.line(frame, ix, mx, color, 2, cv2.LINE_AA)
    elif pose == AppMode.SCROLL:
        tx = (int(landmarks[4].x * w), int(landmarks[4].y * h))
        rx = (int(landmarks[16].x * w), int(landmarks[16].y * h))
        glow_circle(frame, tx, 10, color)
        glow_circle(frame, rx, 10, color)
        cv2.line(frame, tx, rx, color, 2, cv2.LINE_AA)
    elif pose == AppMode.VOLUME:
        tx = (int(landmarks[4].x * w), int(landmarks[4].y * h))
        px = (int(landmarks[20].x * w), int(landmarks[20].y * h))
        glow_circle(frame, tx, 10, color)
        glow_circle(frame, px, 10, color)
        cv2.line(frame, tx, px, color, 2, cv2.LINE_AA)


def draw_cursor_zone(frame):
    h, w = frame.shape[:2]
    x1 = int(config.CURSOR_ZONE_MIN_X * w)
    x2 = int(config.CURSOR_ZONE_MAX_X * w)
    y1 = int(config.CURSOR_ZONE_MIN_Y * h)
    y2 = int(config.CURSOR_ZONE_MAX_Y * h)

    overlay = frame.copy()
    rounded_rect(overlay, x1, y1, x2, y2, C.CURSOR_ZONE, radius=4, thickness=-1)
    cv2.addWeighted(overlay, 0.05, frame, 0.95, 0, frame)
    corner_brackets(frame, x1, y1, x2, y2, C.CURSOR_ZONE, length=30, thickness=2)
    put_text(frame, "ZONA KURSOR", (x1 + 10, y1 + 24), 0.5, C.CURSOR_ZONE, 1)


def draw_volume_lock_indicator(
    frame, landmarks, click_distance: float, progress: float, locked: bool
):
    """Indikator toggle lock volume (telunjuk + tengah tahan)."""
    if click_distance >= config.VOLUME_LOCK_THRESHOLD and progress <= 0:
        return

    h, w = frame.shape[:2]
    ix = (int(landmarks[8].x * w), int(landmarks[8].y * h))
    mx = (int(landmarks[12].x * w), int(landmarks[12].y * h))
    color = C.GREEN if progress > 0 else (C.MUTED if locked else C.CYAN)

    glow_circle(frame, ix, 11, color)
    glow_circle(frame, mx, 11, color)
    cv2.line(frame, ix, mx, color, 2, cv2.LINE_AA)

    if progress > 0:
        label = "UNLOCK" if locked else "LOCK"
        put_text(frame, label, (ix[0] - 28, ix[1] - 26), 0.45, C.GREEN, 1)
    elif locked:
        put_text(frame, "LOCKED", (ix[0] - 30, ix[1] - 26), 0.42, C.MUTED, 1)


def draw_volume_adjust_indicator(frame, landmarks, distance: float):
    h, w = frame.shape[:2]
    tx = (int(landmarks[4].x * w), int(landmarks[4].y * h))
    ix = (int(landmarks[8].x * w), int(landmarks[8].y * h))
    glow_circle(frame, tx, 11, C.CYAN)
    glow_circle(frame, ix, 11, C.CYAN)
    cv2.line(frame, tx, ix, C.CYAN, 2, cv2.LINE_AA)


def draw_scroll_indicator(frame, landmarks, hold_distance: float, status: str):
    h, w = frame.shape[:2]
    tx = (int(landmarks[4].x * w), int(landmarks[4].y * h))
    rx = (int(landmarks[16].x * w), int(landmarks[16].y * h))
    wx, wy = int(landmarks[0].x * w), int(landmarks[0].y * h)

    if hold_distance >= config.SCROLL_HOLD_THRESHOLD:
        return

    color = C.PURPLE if status == "SCROLLING" else C.ORANGE
    glow_circle(frame, tx, 11, color)
    glow_circle(frame, rx, 11, color)
    cv2.line(frame, tx, rx, color, 2, cv2.LINE_AA)
    put_text(frame, "SCROLL", (rx[0] - 28, rx[1] - 24), 0.5, color, 1)
    cv2.arrowedLine(frame, (wx, wy + 36), (wx, wy - 36), color, 2, tipLength=0.25, line_type=cv2.LINE_AA)


def draw_click_indicator(frame, landmarks, click_distance: float, threshold: float):
    h, w = frame.shape[:2]
    ix = (int(landmarks[8].x * w), int(landmarks[8].y * h))
    mx = (int(landmarks[12].x * w), int(landmarks[12].y * h))
    near = click_distance < threshold
    color = C.RED if near else C.ACCENT
    glow_circle(frame, ix, 12, color)
    glow_circle(frame, mx, 12, color)
    cv2.line(frame, ix, mx, color, 2, cv2.LINE_AA)
    if near:
        put_text(frame, "CLICK", (ix[0] - 20, ix[1] - 26), 0.48, C.RED, 1)


def draw_volume_bar(frame, volume_percent: float, enabled: bool):
    pass


def draw_volume_toggle_indicator(frame, landmarks, toggle_distance: float, progress: float, enabled: bool):
    pass


def draw_status_panel(frame, **kwargs):
    pass
