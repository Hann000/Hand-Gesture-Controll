"""Kontrol kursor mouse dengan pemetaan zona dan smoothing EMA."""

import pyautogui

import config


class CursorController:
    """Memetakan posisi jari telunjuk ke koordinat layar penuh."""

    def __init__(self, alpha: float = config.SMOOTHING_ALPHA):
        self.alpha = alpha
        self.screen_width, self.screen_height = pyautogui.size()
        self._prev_x = self.screen_width / 2
        self._prev_y = self.screen_height / 2
        pyautogui.FAILSAFE = True

    @staticmethod
    def _map_axis(value: float, zone_min: float, zone_max: float) -> float:
        """Petakan koordinat normalisasi dalam zona aktif ke rentang 0.0–1.0."""
        span = zone_max - zone_min
        if span <= 0:
            return value
        mapped = (value - zone_min) / span
        return max(0.0, min(1.0, mapped))

    def _to_screen_coords(self, index_x: float, index_y: float):
        """Konversi landmark telunjuk ke piksel layar via zona aktif kamera."""
        mapped_x = self._map_axis(
            index_x, config.CURSOR_ZONE_MIN_X, config.CURSOR_ZONE_MAX_X
        )
        mapped_y = self._map_axis(
            index_y, config.CURSOR_ZONE_MIN_Y, config.CURSOR_ZONE_MAX_Y
        )
        return mapped_x * self.screen_width, mapped_y * self.screen_height

    def update(self, index_x: float, index_y: float):
        """
        Terapkan pemetaan zona + EMA smoothing lalu gerakkan kursor.

        index_x, index_y: koordinat normalisasi MediaPipe (0.0–1.0).
        """
        target_x, target_y = self._to_screen_coords(index_x, index_y)

        curr_x = (self.alpha * target_x) + ((1 - self.alpha) * self._prev_x)
        curr_y = (self.alpha * target_y) + ((1 - self.alpha) * self._prev_y)

        self._prev_x = curr_x
        self._prev_y = curr_y

        pyautogui.moveTo(curr_x, curr_y)
        return curr_x, curr_y
