"""Kontrol volume sistem berdasarkan jarak jempol–telunjuk."""

import platform
import subprocess
import sys

import config
from gesture_detector import GestureDetector


class VolumeController:
    """Normalisasi jarak jari ke persen volume dan terapkan ke OS."""

    def __init__(
        self,
        min_dist: float = config.VOL_MIN_DIST,
        max_dist: float = config.VOL_MAX_DIST,
    ):
        self.min_dist = min_dist
        self.max_dist = max_dist
        self.volume_percent = 0.0
        self._volume_ctrl = None
        self._init_os_volume()

    def _init_os_volume(self):
        """Inisialisasi API volume sesuai sistem operasi."""
        if platform.system() != "Windows":
            return

        try:
            from pycaw.pycaw import AudioUtilities

            devices = AudioUtilities.GetSpeakers()
            self._volume_ctrl = devices.EndpointVolume
        except Exception as exc:
            print(f"[Peringatan] Volume Windows tidak tersedia: {exc}", file=sys.stderr)
            self._volume_ctrl = None

    def compute_volume_percent(self, landmarks) -> float:
        """Hitung persen volume dari jarak jempol (L4) ke telunjuk (L8)."""
        dist = GestureDetector.euclidean_distance(
            landmarks[4].x, landmarks[4].y,
            landmarks[8].x, landmarks[8].y,
        )
        span = self.max_dist - self.min_dist
        if span <= 0:
            return 0.0

        volume = (dist - self.min_dist) / span * 100
        self.volume_percent = max(0.0, min(100.0, volume))
        return self.volume_percent

    def apply_volume(self, enabled: bool = True):
        """Terapkan volume_percent ke speaker sistem jika mode volume aktif."""
        if not enabled:
            return

        pct = int(self.volume_percent)
        system = platform.system()

        if system == "Windows" and self._volume_ctrl is not None:
            self._volume_ctrl.SetMasterVolumeLevelScalar(
                self.volume_percent / 100, None
            )
        elif system == "Darwin":
            subprocess.run(
                ["osascript", "-e", f"set volume output volume {pct}"],
                check=False,
            )
        elif system == "Linux":
            subprocess.run(
                ["amixer", "-D", "pulse", "sset", "Master", f"{pct}%"],
                check=False,
            )

    def get_thumb_index_distance(self, landmarks) -> float:
        """Jarak jempol–telunjuk untuk visualisasi."""
        return GestureDetector.euclidean_distance(
            landmarks[4].x, landmarks[4].y,
            landmarks[8].x, landmarks[8].y,
        )
