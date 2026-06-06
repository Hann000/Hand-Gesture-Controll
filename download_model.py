"""Unduh model pelacakan tangan (hand_landmarker.task)."""

import urllib.request
from pathlib import Path

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)
MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "hand_landmarker.task"


def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if MODEL_PATH.exists():
        print(f"Model sudah ada: {MODEL_PATH}")
        return

    print(f"Mengunduh model ke {MODEL_PATH} ...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Selesai.")


if __name__ == "__main__":
    main()
