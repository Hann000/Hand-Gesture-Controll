"""Palet warna dan helper gambar UI modern (OpenCV)."""

import cv2


class C:
    """Warna BGR."""
    BG = (28, 24, 20)
    PANEL = (40, 36, 32)
    PANEL_BORDER = (70, 62, 55)
    TEXT = (240, 240, 245)
    TEXT_DIM = (160, 155, 150)
    ACCENT = (255, 180, 60)
    CYAN = (255, 210, 80)
    GREEN = (120, 220, 100)
    PURPLE = (220, 120, 255)
    ORANGE = (80, 160, 255)
    RED = (100, 100, 255)
    BLUE = (255, 160, 80)
    MUTED = (90, 85, 80)

    CURSOR_ZONE = (255, 200, 80)
    HAND_LINE = (200, 255, 180)
    HAND_DOT = (255, 255, 255)
    HAND_GLOW = (180, 255, 220)


def blend_overlay(frame, overlay, alpha: float):
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def rounded_rect(
    img,
    x1: int, y1: int, x2: int, y2: int,
    color: tuple, radius: int = 10, thickness: int = -1,
):
    """Gambar persegi dengan sudut membulat."""
    if thickness < 0:
        cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, -1)
        cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, -1)
        for cx, cy in (
            (x1 + radius, y1 + radius),
            (x2 - radius, y1 + radius),
            (x1 + radius, y2 - radius),
            (x2 - radius, y2 - radius),
        ):
            cv2.circle(img, (cx, cy), radius, color, -1)
    else:
        cv2.line(img, (x1 + radius, y1), (x2 - radius, y1), color, thickness)
        cv2.line(img, (x1 + radius, y2), (x2 - radius, y2), color, thickness)
        cv2.line(img, (x1, y1 + radius), (x1, y2 - radius), color, thickness)
        cv2.line(img, (x2, y1 + radius), (x2, y2 - radius), color, thickness)
        for cx, cy in (
            (x1 + radius, y1 + radius),
            (x2 - radius, y1 + radius),
            (x1 + radius, y2 - radius),
            (x2 - radius, y2 - radius),
        ):
            cv2.ellipse(img, (cx, cy), (radius, radius), 0, 0, 360, color, thickness)


def glass_panel(frame, x: int, y: int, w: int, h: int, alpha: float = 0.72):
    """Panel semi-transparan gelap."""
    overlay = frame.copy()
    rounded_rect(overlay, x, y, x + w, y + h, C.PANEL, radius=14, thickness=-1)
    rounded_rect(overlay, x, y, x + w, y + h, C.PANEL_BORDER, radius=14, thickness=1)
    blend_overlay(frame, overlay, alpha)


def ascii_safe(text: str) -> str:
    """OpenCV hanya menampilkan ASCII dengan benar."""
    replacements = {
        "\u2014": "-", "\u2013": "-", "\u2192": "->",
        "\u2502": "|", "\u2713": "OK", "\u2022": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("ascii", "ignore").decode("ascii")


def put_text(
    frame, text: str, pos: tuple, scale: float = 0.5,
    color: tuple = C.TEXT, thickness: int = 1, shadow: bool = True,
):
    """Teks dengan bayangan halus (ASCII only)."""
    text = ascii_safe(text)
    font = cv2.FONT_HERSHEY_SIMPLEX
    if shadow:
        cv2.putText(
            frame, text, (pos[0] + 1, pos[1] + 1),
            font, scale, (0, 0, 0), thickness + 1, cv2.LINE_AA,
        )
    cv2.putText(frame, text, pos, font, scale, color, thickness, cv2.LINE_AA)


def put_text_block(
    frame, lines, x: int, y: int, scale: float = 0.38,
    color: tuple = C.TEXT, line_gap: int = 18,
):
    """Beberapa baris teks berurutan."""
    for i, line in enumerate(lines):
        put_text(frame, line, (x, y + i * line_gap), scale, color, 1)


def draw_badge(frame, x: int, y: int, label: str, active: bool, accent: tuple):
    """Badge status kecil."""
    pad_x, pad_y = 10, 6
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
    bw, bh = tw + pad_x * 2, th + pad_y * 2
    overlay = frame.copy()
    bg = accent if active else C.MUTED
    rounded_rect(overlay, x, y, x + bw, y + bh, bg, radius=8, thickness=-1)
    blend_overlay(frame, overlay, 0.85 if active else 0.6)
    put_text(frame, label, (x + pad_x, y + th + pad_y - 2), 0.42, C.TEXT, 1, shadow=False)


def gradient_bar_vertical(frame, x, y, w, h, percent: float, color_top: tuple, color_bot: tuple):
    """Bar vertikal dengan gradien."""
    rounded_rect(frame, x, y, x + w, y + h, (45, 42, 38), radius=6, thickness=-1)
    fill_h = int(h * percent / 100)
    if fill_h <= 0:
        return
    y_start = y + h - fill_h
    for i in range(fill_h):
        t = i / max(fill_h, 1)
        c = tuple(int(color_top[j] * (1 - t) + color_bot[j] * t) for j in range(3))
        cv2.line(frame, (x + 2, y_start + i), (x + w - 2, y_start + i), c, 1)


def corner_brackets(frame, x1, y1, x2, y2, color: tuple, length: int = 28, thickness: int = 2):
    """Sudut bracket modern untuk zona kursor."""
    pts = [
        ((x1, y1 + length), (x1, y1), (x1 + length, y1)),
        ((x2 - length, y1), (x2, y1), (x2, y1 + length)),
        ((x1, y2 - length), (x1, y2), (x1 + length, y2)),
        ((x2 - length, y2), (x2, y2), (x2, y2 - length)),
    ]
    for a, b, c in pts:
        cv2.line(frame, a, b, color, thickness, cv2.LINE_AA)
        cv2.line(frame, b, c, color, thickness, cv2.LINE_AA)


def glow_circle(frame, center: tuple, radius: int, color: tuple, rings: int = 3):
    """Lingkaran dengan efek glow."""
    overlay = frame.copy()
    for i in range(rings, 0, -1):
        r = radius + i * 4
        alpha_color = tuple(int(c * (0.15 + 0.1 * i)) for c in color)
        cv2.circle(overlay, center, r, alpha_color, 2, cv2.LINE_AA)
    cv2.circle(overlay, center, radius, color, 2, cv2.LINE_AA)
    blend_overlay(frame, overlay, 0.5)
    cv2.circle(frame, center, max(3, radius // 3), color, -1, cv2.LINE_AA)
