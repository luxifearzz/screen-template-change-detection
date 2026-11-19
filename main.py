
import cv2
import numpy as np
import mss
import time
import pyautogui

# =====================================
# CONFIGURATION
# =====================================

TEMPLATE_PATH = "images/template.png"

MATCH_THRESHOLD = 0.92

# ค่าเฉลี่ยความแตกต่างของ Pixel (0-255)
CHANGE_THRESHOLD = 12.0

# ต้องพบการเปลี่ยนแปลงต่อเนื่องกี่เฟรม
CONFIRM_FRAMES = 3

SCAN_INTERVAL = 0.5
MONITOR_INTERVAL = 0.15

COUNTDOWN_SECONDS = 3

# =====================================
# COUNTDOWN
# =====================================


def countdown(seconds):

    print("\nPrepare your screen...")

    for remaining in range(seconds, 0, -1):

        print(
            f"\rStarting detection in {remaining} seconds...",
            end="",
            flush=True
        )

        time.sleep(1)

    print("\nDetection started!\n")

# =====================================
# LOAD TEMPLATE
# =====================================


template = cv2.imread(
    TEMPLATE_PATH,
    cv2.IMREAD_GRAYSCALE
)

if template is None:
    raise FileNotFoundError(TEMPLATE_PATH)

h, w = template.shape

print("Template loaded:", w, "x", h)


# =====================================
# SCREEN CAPTURE
# =====================================

sct = mss.mss()

# ใช้จอหลัก
monitor = sct.monitors[1]


def capture_screen():
    """Capture full primary screen."""
    image = np.array(sct.grab(monitor))
    return cv2.cvtColor(
        image,
        cv2.COLOR_BGRA2GRAY
    )


def capture_roi(x, y, w, h):
    """Capture only the detected region."""
    image = np.array(sct.grab({
        "left": monitor["left"] + x,
        "top": monitor["top"] + y,
        "width": w,
        "height": h
    }))

    return cv2.cvtColor(
        image,
        cv2.COLOR_BGRA2GRAY
    )


# =====================================
# STAGE 1: FULL SCREEN TEMPLATE SEARCH
# =====================================

def find_template():

    screen = capture_screen()

    result = cv2.matchTemplate(
        screen,
        template,
        cv2.TM_CCOEFF_NORMED
    )

    _, score, _, location = cv2.minMaxLoc(result)

    if score >= MATCH_THRESHOLD:

        x, y = location

        print(
            f"Template found: "
            f"x={x}, y={y}, score={score:.3f}"
        )

        return x, y

    return None


# =====================================
# EVENT HANDLER
# =====================================

def on_change_detected():

    print("\n!!! CHANGE DETECTED !!!")

    # =================================
    # TEST MOUSE CLICK
    # =================================
    # เปิดใช้งานบรรทัดด้านล่างเฉพาะเมื่อ
    # ทดสอบกับหน้าต่างและตำแหน่งที่ควบคุมได้

    pyautogui.click()

    print("Event triggered.")


# =====================================
# STAGE 2: ROI MONITORING
# =====================================

def monitor_roi(x, y):

    print("\nStart ROI monitoring")

    # เก็บภาพอ้างอิง ณ เวลาที่พบ Template
    baseline = capture_roi(x, y, w, h)

    changed_count = 0

    while True:

        current = capture_roi(x, y, w, h)

        # 1. ตรวจคะแนน Template ใน ROI
        result = cv2.matchTemplate(
            current,
            template,
            cv2.TM_CCOEFF_NORMED
        )

        match_score = float(result[0, 0])

        # 2. ตรวจความแตกต่างของ Pixel
        diff = cv2.absdiff(
            baseline,
            current
        )

        change_score = float(np.mean(diff))

        # 3. ตรวจว่ามีการเปลี่ยนแปลงหรือไม่
        is_changed = (
            match_score < MATCH_THRESHOLD
            or change_score > CHANGE_THRESHOLD
        )

        if is_changed:
            changed_count += 1
        else:
            changed_count = 0

        print(
            f"Match={match_score:.3f} | "
            f"Change={change_score:.2f} | "
            f"Count={changed_count}"
        )

        # 4. ยืนยันการเปลี่ยนแปลงต่อเนื่อง
        if changed_count >= CONFIRM_FRAMES:

            on_change_detected()
            break

        time.sleep(MONITOR_INTERVAL)


# =====================================
# MAIN LOOP
# =====================================

try:

    # Countdown ก่อนเริ่มตรวจจับ
    countdown(COUNTDOWN_SECONDS)

    print("Starting screen detection...")

    while True:

        location = find_template()

        if location is not None:

            x, y = location

            monitor_roi(x, y)

            break

        time.sleep(SCAN_INTERVAL)

except KeyboardInterrupt:

    print("\nProgram stopped by user.")

finally:

    sct.close()
