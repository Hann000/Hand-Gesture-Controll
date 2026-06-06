"""Wrapper MediaPipe Hand Landmarker (Tasks API) untuk deteksi landmark tangan."""

import time
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import config
from ui_theme import C

MODEL_PATH = Path(__file__).parent / "models" / "hand_landmarker.task"

# Koneksi antar landmark untuk menggambar skeleton tangan
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
    (5, 9), (9, 13), (13, 17),
]


class HandTracker:
    """Mendeteksi 21 landmark tangan dari frame kamera."""

    def __init__(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model tidak ditemukan: {MODEL_PATH}\n"
                "Jalankan: python download_model.py"
            )

        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(MODEL_PATH)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=config.MAX_NUM_HANDS,
            min_hand_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )
        self._detector = vision.HandLandmarker.create_from_options(options)
        self._start_time = time.time()
        self._last_result = None

    def process(self, rgb_frame):
        """Proses frame RGB dan kembalikan hasil deteksi."""
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int((time.time() - self._start_time) * 1000)
        self._last_result = self._detector.detect_for_video(mp_image, timestamp_ms)
        return self._last_result

    def draw_landmarks(self, frame, hand_landmarks):
        """Gambar skeleton tangan di frame BGR."""
        h, w = frame.shape[:2]

        for connection in HAND_CONNECTIONS:
            start = hand_landmarks[connection[0]]
            end = hand_landmarks[connection[1]]
            x1, y1 = int(start.x * w), int(start.y * h)
            x2, y2 = int(end.x * w), int(end.y * h)
            cv2.line(frame, (x1, y1), (x2, y2), C.HAND_LINE, 2, cv2.LINE_AA)

        for landmark in hand_landmarks:
            cx, cy = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(frame, (cx, cy), 5, C.HAND_GLOW, 1, cv2.LINE_AA)
            cv2.circle(frame, (cx, cy), 3, C.HAND_DOT, -1, cv2.LINE_AA)

    def get_landmarks(self, results):
        """Ambil daftar landmark tangan pertama, atau None jika tidak terdeteksi."""
        if results is None or not results.hand_landmarks:
            return None
        return results.hand_landmarks[0]

    def close(self):
        """Lepaskan resource MediaPipe."""
        self._detector.close()
