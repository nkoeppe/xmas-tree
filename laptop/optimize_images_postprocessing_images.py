import cv2
import numpy as np
import os
import json
import cv2
from datetime import datetime

# Configuration
DIRECTORY = "./test_photos"


def image_bp(fp, dfp):
    image = cv2.imread(fp)
    if image is None:
        raise FileNotFoundError(f"Image not found at path: {fp}")

    orig = image.copy()
    image_flipped = cv2.flip(image, 0)  # Flip to match bottom-left coordinate system

    gray = cv2.cvtColor(image_flipped, cv2.COLOR_BGR2GRAY)
    (_, _, _, max_loc) = cv2.minMaxLoc(gray)

    # Overlay the detected LED position
    cv2.circle(image_flipped, max_loc, 2, (255, 0, 0), 2)

    os.makedirs(DIRECTORY, exist_ok=True)
    cv2.imwrite(dfp, orig)
    print(f"Debug overlay saved at: {dfp}")

    return max_loc

def capture_image(filename):
    """Capture image and save it."""
    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()
    if ret:
        cv2.imwrite(filename, frame)
    else:
        raise RuntimeError("Camera capture failed.")
    camera.release()

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    image_path = os.path.join(DIRECTORY, f"{timestamp}_test_led_debug.jpg")
    debug_image_path = os.path.join(DIRECTORY, f"{timestamp}_test_led_debug.jpg")
    capture_image(image_path)
    image_bp(image_path, debug_image_path)


if __name__ == "__main__":
    main()
