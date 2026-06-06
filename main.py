"""
Entry point — Kontrol Volume dan Kursor Berbasis Gerakan Jari.

Mode eksklusif: ganti mode via gestur tangan (tanpa keyboard/mouse).
"""

import os
import sys

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["GLOG_minloglevel"] = "2"

import cv2

import config
from cursor_controller import CursorController
from gesture_detector import GestureDetector
from hand_tracker import HandTracker
from mode_controller import ModeController
from ui_overlay import (
    HUD,
    UIState,
    draw_click_indicator,
    draw_cursor_zone,
    draw_mode_switch_indicator,
    draw_scroll_indicator,
    draw_volume_adjust_indicator,
    draw_volume_lock_indicator,
)
from scroll_controller import ScrollController
from volume_controller import VolumeController


def main():
    print("Membuka kamera...", flush=True)
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    if not cap.isOpened():
        print("Error: Tidak dapat membuka kamera. Periksa CAMERA_INDEX di config.py.")
        sys.exit(1)

    print("Memuat model pelacakan tangan...", flush=True)
    tracker = HandTracker()
    cursor = CursorController()
    gestures = GestureDetector()
    scroll = ScrollController()
    volume = VolumeController()
    modes = ModeController()
    hud = HUD()

    print("", flush=True)
    print("=== Aplikasi berjalan ===", flush=True)
    print(f"Jendela '{config.WINDOW_TITLE}' akan muncul.", flush=True)
    print("", flush=True)
    print("GANTI MODE (tahan diam):", flush=True)
    print("  Telunjuk+tengah (V)  -> Mode Kursor (tahan ~1 dtk)", flush=True)
    print("  Jempol + manis rapat -> Mode Scroll", flush=True)
    print("  Jempol + kelingking  -> Mode Volume", flush=True)
    print("  Mode Volume: tahan telunjuk+tengah -> lock/unlock volume", flush=True)
    print("", flush=True)
    print("Tekan Q di jendela kamera untuk keluar.", flush=True)
    print("", flush=True)

    prev_mode = modes.mode

    try:
        while True:
            success, frame = cap.read()
            if not success:
                print("Error: Gagal membaca frame kamera.")
                break

            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = tracker.process(rgb)
            landmarks = tracker.get_landmarks(results)

            ui = UIState(
                hand_detected=landmarks is not None,
                active_mode=modes.mode.value,
                mode_label=modes.label,
                mode_hint=modes.hint,
                switch_progress=modes.switch_progress,
                switch_target=modes.pending_switch_label,
            )

            if landmarks is not None:
                if modes.update_gesture_switch(landmarks):
                    print(f"Mode aktif: {modes.label}", flush=True)
                    ui.active_mode = modes.mode.value
                    ui.mode_label = modes.label
                    ui.mode_hint = modes.hint
                    ui.switch_progress = modes.switch_progress
                    ui.switch_target = modes.pending_switch_label

                if modes.mode != prev_mode:
                    if modes.is_volume():
                        gestures.reset_volume_lock()
                    prev_mode = modes.mode

                ui.switch_progress = modes.switch_progress
                ui.switch_target = modes.pending_switch_label

                draw_mode_switch_indicator(frame, landmarks, modes)
                tracker.draw_landmarks(frame, landmarks)

            if modes.is_cursor():
                draw_cursor_zone(frame)

            if landmarks is not None:
                if modes.is_cursor():
                    ui.cursor_pos = cursor.update(landmarks[8].x, landmarks[8].y)
                    gestures.check_click(landmarks)
                    ui.click_status = gestures.status
                    ui.click_distance = gestures.get_click_distance(landmarks)
                    draw_click_indicator(
                        frame, landmarks, ui.click_distance, config.CLICK_THRESHOLD
                    )

                elif modes.is_scroll():
                    scroll.update(landmarks)
                    ui.scroll_status = scroll.status
                    draw_scroll_indicator(
                        frame,
                        landmarks,
                        scroll.get_hold_distance(landmarks),
                        scroll.status,
                    )

                elif modes.is_volume():
                    gestures.check_volume_lock_toggle(landmarks)
                    ui.volume_locked = gestures.volume_locked
                    ui.volume_lock_status = gestures.volume_lock_status
                    ui.volume_lock_progress = gestures.volume_lock_progress

                    draw_volume_lock_indicator(
                        frame,
                        landmarks,
                        gestures.get_click_distance(landmarks),
                        gestures.volume_lock_progress,
                        gestures.volume_locked,
                    )

                    if not gestures.volume_locked:
                        volume.compute_volume_percent(landmarks)
                        volume.apply_volume(enabled=True)
                        draw_volume_adjust_indicator(
                            frame,
                            landmarks,
                            volume.get_thumb_index_distance(landmarks),
                        )

                    ui.volume_percent = volume.volume_percent
                    ui.volume_enabled = not gestures.volume_locked
                    ui.volume_status = gestures.volume_lock_status

            hud.render(frame, ui)
            cv2.imshow(config.WINDOW_TITLE, frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\nDihentikan oleh pengguna.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        tracker.close()


if __name__ == "__main__":
    main()
