"""Deteksi gesture tangan: klik dan pengukuran jarak."""

import math
import time

import pyautogui

import config


class GestureDetector:
    """Mendeteksi gesture klik berdasarkan kedekatan jari."""

    def __init__(
        self,
        click_threshold: float = config.CLICK_THRESHOLD,
        cooldown_sec: float = config.CLICK_COOLDOWN_SEC,
    ):
        self.click_threshold = click_threshold
        self.cooldown_sec = cooldown_sec
        self._last_click_time = 0.0
        self.status = "IDLE"

        self.volume_locked = config.VOLUME_LOCK_DEFAULT
        self.volume_lock_status = "LOCKED" if self.volume_locked else "UNLOCKED"
        self.volume_lock_progress = 0.0
        self._volume_lock_hold_start = 0.0
        self._last_volume_lock_toggle = 0.0

    @staticmethod
    def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
        """Hitung jarak Euclidean antara dua titik normalisasi."""
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def check_click(self, landmarks, scroll_holding: bool = False) -> bool:
        """
        Cek apakah gesture klik aktif (telunjuk + tengah rapat).
        Mengembalikan True jika klik berhasil dieksekusi.
        """
        if scroll_holding:
            self.status = "IDLE"
            return False

        dist = self.euclidean_distance(
            landmarks[8].x, landmarks[8].y,
            landmarks[12].x, landmarks[12].y,
        )

        if dist < self.click_threshold:
            current_time = time.time()
            if (current_time - self._last_click_time) > self.cooldown_sec:
                pyautogui.click()
                self._last_click_time = current_time
                self.status = "ACTIVE_CLICK"
                return True
            self.status = "COOLDOWN"
            return False

        self.status = "IDLE"
        return False

    def get_click_distance(self, landmarks) -> float:
        """Jarak antara telunjuk dan tengah (untuk visualisasi)."""
        return self.euclidean_distance(
            landmarks[8].x, landmarks[8].y,
            landmarks[12].x, landmarks[12].y,
        )

    def reset_volume_lock(self):
        """Reset lock saat masuk mode volume."""
        self.volume_locked = config.VOLUME_LOCK_DEFAULT
        self.volume_lock_status = "LOCKED" if self.volume_locked else "UNLOCKED"
        self.volume_lock_progress = 0.0
        self._volume_lock_hold_start = 0.0

    def check_volume_lock_toggle(self, landmarks) -> bool:
        """
        Toggle lock volume: tahan telunjuk + tengah rapat.

        Saat LOCKED, volume tidak berubah meski tangan bergerak.
        """
        dist = self.get_click_distance(landmarks)
        now = time.time()

        if dist < config.VOLUME_LOCK_THRESHOLD:
            if self._volume_lock_hold_start == 0.0:
                self._volume_lock_hold_start = now

            held = now - self._volume_lock_hold_start
            self.volume_lock_progress = min(1.0, held / config.VOLUME_LOCK_HOLD_SEC)

            if (
                held >= config.VOLUME_LOCK_HOLD_SEC
                and (now - self._last_volume_lock_toggle) > config.VOLUME_LOCK_COOLDOWN_SEC
            ):
                self.volume_locked = not self.volume_locked
                self._last_volume_lock_toggle = now
                self._volume_lock_hold_start = 0.0
                self.volume_lock_progress = 0.0
                self.volume_lock_status = "LOCKED" if self.volume_locked else "UNLOCKED"
                return True

            self.volume_lock_status = "HOLD_LOCK"
            return False

        self._volume_lock_hold_start = 0.0
        self.volume_lock_progress = 0.0
        self.volume_lock_status = "LOCKED" if self.volume_locked else "UNLOCKED"
        return False
