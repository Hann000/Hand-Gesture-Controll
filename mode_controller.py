"""Mode eksklusif dengan pergantian via gestur tangan (tanpa keyboard)."""

import time
from enum import Enum
from typing import Optional

import config
from gesture_detector import GestureDetector


class AppMode(Enum):
    CURSOR = "cursor"
    SCROLL = "scroll"
    VOLUME = "volume"


MODE_INFO = {
    AppMode.CURSOR: {
        "label": "KURSOR",
        "switch": "Telunjuk+tengah V, tahan diam",
        "hint": "Telunjuk di zona emas",
        "hint2": "Klik: telunjuk + tengah rapat",
    },
    AppMode.SCROLL: {
        "label": "SCROLL",
        "switch": "Jempol + manis, tahan diam",
        "hint": "Tahan jempol + manis",
        "hint2": "Geser tangan naik / turun",
    },
    AppMode.VOLUME: {
        "label": "VOLUME",
        "switch": "Jempol + kelingking, tahan diam",
        "hint": "Tahan telunjuk+tengah: lock/unlock",
        "hint2": "Jarak jempol+telunjuk atur volume",
    },
}


class ModeController:
    """Ganti mode dengan gestur tahan-diam."""

    def __init__(self, default: AppMode = AppMode.CURSOR):
        self.mode = default
        self.switch_progress = 0.0
        self.pending_switch_label = ""
        self.cursor_switch_type = ""
        self._hold_mode: Optional[AppMode] = None
        self._hold_start = 0.0
        self._last_wrist_y: Optional[float] = None
        self._last_switch_time = 0.0

    @staticmethod
    def _finger_up(landmarks, tip: int, pip: int) -> bool:
        m = config.MODE_SWITCH_FINGER_MARGIN
        return landmarks[tip].y < landmarks[pip].y - m

    @staticmethod
    def _thumb_folded(landmarks) -> bool:
        return landmarks[4].y > landmarks[3].y

    def _is_peace_sign_pose(self, landmarks) -> bool:
        """
        Peace sign: telunjuk + tengah teracung membentuk V.
        Lebih sulit terpicu tidak sengaja dibanding telapak terbuka.
        """
        if not self._finger_up(landmarks, 8, 6):
            return False
        if not self._finger_up(landmarks, 12, 10):
            return False
        if self._finger_up(landmarks, 16, 14):
            return False
        if self._finger_up(landmarks, 20, 18):
            return False
        if not self._thumb_folded(landmarks):
            return False

        spread = GestureDetector.euclidean_distance(
            landmarks[8].x, landmarks[8].y,
            landmarks[12].x, landmarks[12].y,
        )
        return spread >= config.MODE_SWITCH_PEACE_MIN_SPREAD

    def _is_thumb_ring_pinch(self, landmarks) -> bool:
        d = GestureDetector.euclidean_distance(
            landmarks[4].x, landmarks[4].y,
            landmarks[16].x, landmarks[16].y,
        )
        return d < config.MODE_SWITCH_PINCH_THRESHOLD

    def _is_thumb_pinky_pinch(self, landmarks) -> bool:
        d = GestureDetector.euclidean_distance(
            landmarks[4].x, landmarks[4].y,
            landmarks[20].x, landmarks[20].y,
        )
        return d < config.MODE_SWITCH_PINCH_THRESHOLD

    def detect_switch_pose(self, landmarks) -> Optional[AppMode]:
        if self._is_thumb_pinky_pinch(landmarks):
            self.cursor_switch_type = ""
            return AppMode.VOLUME
        if self._is_thumb_ring_pinch(landmarks):
            self.cursor_switch_type = ""
            return AppMode.SCROLL
        if self._is_peace_sign_pose(landmarks):
            self.cursor_switch_type = "peace"
            return AppMode.CURSOR
        self.cursor_switch_type = ""
        return None

    def _hold_duration(self, pose: AppMode) -> float:
        if pose == AppMode.CURSOR:
            if self.mode != AppMode.CURSOR:
                return config.MODE_SWITCH_CURSOR_HOLD_FROM_OTHER_SEC
            return config.MODE_SWITCH_CURSOR_HOLD_SEC
        return config.MODE_SWITCH_HOLD_SEC

    def _hand_is_still(self, landmarks, pose: Optional[AppMode]) -> bool:
        wrist_y = landmarks[0].y
        if self._last_wrist_y is None:
            self._last_wrist_y = wrist_y
            return True
        limit = (
            config.MODE_SWITCH_CURSOR_MOVE_THRESHOLD
            if pose == AppMode.CURSOR
            else config.MODE_SWITCH_MOVE_THRESHOLD
        )
        still = abs(wrist_y - self._last_wrist_y) < limit
        self._last_wrist_y = wrist_y
        return still

    def update_gesture_switch(self, landmarks) -> bool:
        pose = self.detect_switch_pose(landmarks)
        now = time.time()

        if pose is None or not self._hand_is_still(landmarks, pose):
            self._reset_hold()
            return False

        if self._hold_mode != pose:
            self._hold_mode = pose
            self._hold_start = now

        hold_sec = self._hold_duration(pose)
        held = now - self._hold_start
        self.switch_progress = min(1.0, held / hold_sec)
        self.pending_switch_label = MODE_INFO[pose]["label"]

        if held < hold_sec:
            return False

        if (now - self._last_switch_time) < config.MODE_SWITCH_COOLDOWN_SEC:
            self._reset_hold()
            return False

        if pose == self.mode:
            self._reset_hold()
            return False

        self.mode = pose
        self._last_switch_time = now
        self._reset_hold()
        return True

    def _reset_hold(self):
        self._hold_mode = None
        self._hold_start = 0.0
        self.switch_progress = 0.0
        self.pending_switch_label = ""
        self._last_wrist_y = None

    @property
    def label(self) -> str:
        return MODE_INFO[self.mode]["label"]

    @property
    def hint(self) -> str:
        return MODE_INFO[self.mode]["hint"]

    def is_cursor(self) -> bool:
        return self.mode == AppMode.CURSOR

    def is_scroll(self) -> bool:
        return self.mode == AppMode.SCROLL

    def is_volume(self) -> bool:
        return self.mode == AppMode.VOLUME
