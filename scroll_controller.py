"""Scroll TikTok: tahan jempol + manis, geser tangan naik/turun."""

import pyautogui

import config
from gesture_detector import GestureDetector


class ScrollController:
    """Hold jempol+manis, gerakkan tangan naik/turun untuk scroll."""

    def __init__(self):
        self.status = "IDLE"
        self.last_scroll_amount = 0
        self._prev_y = None

    @property
    def is_holding(self) -> bool:
        """Mode scroll aktif — nonaktifkan kursor, klik, dan volume."""
        return self.status in ("SCROLL_HOLD", "SCROLLING")

    def get_hold_distance(self, landmarks) -> float:
        """Jarak jempol–manis untuk deteksi hold scroll."""
        return GestureDetector.euclidean_distance(
            landmarks[4].x, landmarks[4].y,
            landmarks[16].x, landmarks[16].y,
        )

    def update(self, landmarks) -> int:
        """
        Tahan jempol + manis rapat, lalu geser tangan naik/turun.

        Tangan turun -> scroll ke video berikutnya
        Tangan naik   -> scroll ke video sebelumnya
        """
        self.last_scroll_amount = 0
        dist = self.get_hold_distance(landmarks)

        if dist >= config.SCROLL_HOLD_THRESHOLD:
            self._prev_y = None
            self.status = "IDLE"
            return 0

        track_y = landmarks[config.SCROLL_TRACK_LANDMARK].y

        if self._prev_y is None:
            self._prev_y = track_y
            self.status = "SCROLL_HOLD"
            return 0

        delta = track_y - self._prev_y
        self._prev_y = track_y

        if abs(delta) < config.SCROLL_MIN_DELTA:
            self.status = "SCROLL_HOLD"
            return 0

        steps = max(1, int(abs(delta) / config.SCROLL_MIN_DELTA))
        scroll_clicks = steps * config.SCROLL_STEP

        direction = -1 if delta > 0 else 1
        if config.SCROLL_INVERT:
            direction *= -1

        amount = scroll_clicks * direction
        pyautogui.scroll(amount)
        self.last_scroll_amount = amount
        self.status = "SCROLLING"
        return amount
