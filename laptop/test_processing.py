import cv2
import numpy as np
import os
import json

# Configuration
INPUT_DIRECTORY = "./photos"
OUTPUT_DIRECTORY = "./debug_output"
LED_COUNT = 2
ANGLES = [0, 90, 180, 270]  # Degrees
IMAGE_CENTER = (320, 240)  # Assume 1024x768 resolution; adjust if different
ROTATION_POINT = (256,256)

def imageBP(fp, led_id, angle):
    image = cv2.imread(fp)
    orig = image.copy()
    gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
    # gray = cv2.GaussianBlur(gray, (blurAmount, blurAmount), 0)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)

    image = orig.copy()
    cv2.circle(image, maxLoc, 2, (255, 0, 0), 2)
    # Save the result
    # debug_image_path = os.path.join(base_path, "debug_overlay.jpg")
    debug_image_path = os.path.join(OUTPUT_DIRECTORY, os.path.basename(f"led_{led_id}_angle_{angle}_debug.jpg"))

    cv2.imwrite(debug_image_path, image)
    print(f"Debug overlay saved at: {debug_image_path}")

    return minVal, maxVal, minLoc, maxLoc

def calculate_3d_coordinates(positions_2d):
    """Estimate the 3D coordinates of an LED based on its 2D positions at multiple angles."""
    angel0Pos = positions_2d[0]
    angel90Pos = positions_2d[90]
    angel180Pos = positions_2d[180]
    angel270Pos = positions_2d[270]

    angel03d = (0, angel0Pos[0], angel0Pos[1])
    angel903d = (angel90Pos[0],0, angel90Pos[1])
    angel1803d = (0, angel180Pos[0], angel180Pos[1])
    angel2703d = ( angel270Pos[0],0, angel270Pos[1])

    correction_matrix = (-1 , -1, 1)

    first_coord = (angel903d[0], angel03d[1], (angel03d[2] + angel903d[2]) / 2)
    second_coord_raw = (angel2703d[0], angel1803d[1], (angel2703d[2] + angel1803d[2]) / 2)
    second_coord = tuple(a * b for a, b in zip(second_coord_raw, correction_matrix))

    avg_coord = tuple((a + b) / 2 for a, b in zip(first_coord, second_coord))

    print(f"Calculated 3d coord at {avg_coord}")
    return avg_coord

def process_led_images(led_id):
    """Process the 'on' and 'off' images for a specific LED and return its 3D coordinates."""
    positions_2d = {}
    for angle in ANGLES:
        on_image_path = os.path.join(INPUT_DIRECTORY, f"angle_{angle}", f"led_on_{led_id}.jpg")
        # off_image_path = os.path.join(INPUT_DIRECTORY, f"angle_{angle}", f"led_off_{led_id}.jpg")
        # Calculate difference and thresholded images
        # _, thresholded = calculate_difference_image(on_image_path, off_image_path)

        # Find 2D coordinates
        # cx, cy, contour = find_led_coordinates(thresholded)
        minVal, maxVal, minLoc, led_coordinates = imageBP(on_image_path, led_id, angle)
        ax, ay = led_coordinates
        rx =  ax - ROTATION_POINT[0]
        ry =  ay - ROTATION_POINT[1]

        positions_2d[angle] = (rx,ry)

        print(f"LED detected at: {(rx,ry)}")

    # Dynamically calculate the rotation radius for this LED

    # Estimate 3D coordinates
    return calculate_3d_coordinates(positions_2d)


def main():
    led_positions_3d = []
    try:
        for led_id in range(LED_COUNT):
            print(f"Processing LED {led_id}...")
            led_3d_coords = process_led_images(led_id)
            led_positions_3d.append({
                "led_id": led_id,
                "x": led_3d_coords[0],
                "y": led_3d_coords[1],
                "z": led_3d_coords[2],
            })
            print(f"LED {led_id} detected at ({led_3d_coords[0]:.2f}, {led_3d_coords[1]:.2f}, {led_3d_coords[2]:.2f}).")
    except KeyboardInterrupt:
        print("Processing interrupted by user.")
    finally:
        # Save LED positions to a JSON file
        output_file = os.path.join(OUTPUT_DIRECTORY, "led_positions_3d.json")
        os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(led_positions_3d, f, indent=4)
        print(f"3D LED positions saved to: {output_file}")


if __name__ == "__main__":
    main()