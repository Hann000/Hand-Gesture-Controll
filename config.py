"""Konfigurasi konstanta untuk aplikasi kontrol gesture."""

# Kamera
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS_TARGET = 60

# MediaPipe
MAX_NUM_HANDS = 1
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7

# Kursor — zona aktif di tengah kamera dipetakan ke seluruh layar
# Semakin besar margin, semakin mudah mencapai ujung layar tanpa tangan keluar frame
CURSOR_ZONE_MIN_X = 0.12
CURSOR_ZONE_MAX_X = 0.88
CURSOR_ZONE_MIN_Y = 0.12
CURSOR_ZONE_MAX_Y = 0.88
SMOOTHING_ALPHA = 0.2

# Klik
CLICK_THRESHOLD = 0.05
CLICK_COOLDOWN_SEC = 0.5

# Volume — hanya aktif saat mode VOLUME
VOLUME_LOCK_DEFAULT = True
VOL_MIN_DIST = 0.03
VOL_MAX_DIST = 0.30
# Lock/unlock volume di mode VOLUME: tahan telunjuk + tengah rapat
VOLUME_LOCK_THRESHOLD = 0.05
VOLUME_LOCK_HOLD_SEC = 0.5
VOLUME_LOCK_COOLDOWN_SEC = 0.8

# Scroll TikTok — tahan jempol + manis, geser tangan naik/turun
SCROLL_HOLD_THRESHOLD = 0.06
SCROLL_MIN_DELTA = 0.003
SCROLL_STEP = 4
SCROLL_TRACK_LANDMARK = 0  # pergelangan tangan
SCROLL_INVERT = False

# Ganti mode via gestur (tahan diam, tanpa keyboard)
MODE_SWITCH_HOLD_SEC = 0.6
MODE_SWITCH_CURSOR_HOLD_SEC = 0.85
MODE_SWITCH_CURSOR_HOLD_FROM_OTHER_SEC = 1.0
MODE_SWITCH_COOLDOWN_SEC = 0.9
MODE_SWITCH_MOVE_THRESHOLD = 0.012
MODE_SWITCH_CURSOR_MOVE_THRESHOLD = 0.008
MODE_SWITCH_PINCH_THRESHOLD = 0.06
MODE_SWITCH_FINGER_MARGIN = 0.018
MODE_SWITCH_PEACE_MIN_SPREAD = 0.07

# UI
WINDOW_TITLE = "Gesture Control"
VOLUME_BAR_X = 50
VOLUME_BAR_Y = 150
VOLUME_BAR_WIDTH = 30
VOLUME_BAR_HEIGHT = 200
