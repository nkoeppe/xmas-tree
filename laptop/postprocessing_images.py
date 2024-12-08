import cv2
import numpy as np
import os

# Configuration
INPUT_DIRECTORY = "./photos"
OUTPUT_DIRECTORY = "./debug_output"
LED_COUNT = 10


def calculate_difference_image(on_image_path, off_image_path):
    """Calculate the difference between the 'on' and 'off' images to isolate the LED."""
    on_image = cv2.imread(on_image_path, cv2.IMREAD_GRAYSCALE)
    off_image = cv2.imread(off_image_path, cv2.IMREAD_GRAYSCALE)

    if on_image is None or off_image is None:
        raise FileNotFoundError(f"Could not load images: {on_image_path} or {off_image_path}")

    # Ensure images are of the same size
    if on_image.shape != off_image.shape:
        raise ValueError("Mismatch in image dimensions between 'on' and 'off' images.")

    # Subtract the 'off' image from the 'on' image
    diff = cv2.absdiff(on_image, off_image)

    # Apply Gaussian blur to reduce noise
    diff = cv2.GaussianBlur(diff, (5, 5), 0)

    # Threshold the difference image
    _, thresholded = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)
    return diff, thresholded


def find_led_coordinates(thresholded_image):
    """Find the coordinates of the brightest region (LED) in the thresholded image."""
    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresholded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("No LED detected in the thresholded image.")

    # Find the largest contour, assuming it's the LED
    largest_contour = max(contours, key=cv2.contourArea)

    # Calculate the center of the contour
    moments = cv2.moments(largest_contour)
    if moments["m00"] == 0:
        raise ValueError("Invalid contour moments.")
    cx = int(moments["m10"] / moments["m00"])
    cy = int(moments["m01"] / moments["m00"])
    return cx, cy, largest_contour


def add_debug_overlay(original_image_path, output_path, cx, cy, contour):
    """Add debug overlay to the image to visualize detected LED coordinates."""
    original_image = cv2.imread(original_image_path)

    # Draw the contour
    cv2.drawContours(original_image, [contour], -1, (0, 255, 0), 2)

    # Draw the center point
    cv2.circle(original_image, (cx, cy), 5, (0, 0, 255), -1)

    # Add coordinates text
    cv2.putText(
        original_image,
        f"({cx}, {cy})",
        (cx + 10, cy - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 0, 0),
        2,
    )

    # Save the debug image
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    debug_output_path = os.path.join(OUTPUT_DIRECTORY, os.path.basename(output_path))
    cv2.imwrite(debug_output_path, original_image)
    print(f"Debug image saved to: {debug_output_path}")


def process_led_images(led_id):
    """Process the 'on' and 'off' images for a specific LED."""
    on_image_path = os.path.join(INPUT_DIRECTORY, f"led_on_{led_id}.jpg")
    off_image_path = os.path.join(INPUT_DIRECTORY, f"led_off_{led_id}.jpg")

    # Calculate difference and thresholded images
    diff, thresholded = calculate_difference_image(on_image_path, off_image_path)

    # Find LED coordinates
    cx, cy, largest_contour = find_led_coordinates(thresholded)

    # Save debug image
    add_debug_overlay(on_image_path, f"led_debug_{led_id}.jpg", cx, cy, largest_contour)

    return cx, cy


def main():
    led_positions = []
    try:
        for led_id in range(LED_COUNT):
            try:
                print(f"Processing LED {led_id}...")
                cx, cy = process_led_images(led_id)
                led_positions.append({"led_id": led_id, "x": cx, "y": cy})
                print(f"LED {led_id} detected at ({cx}, {cy}).")
            except Exception as e:
                print(f"Error processing LED {led_id}: {e}")
    except KeyboardInterrupt:
        print("Processing interrupted by user.")
    finally:
        # Save LED positions to a JSON file
        output_file = os.path.join(OUTPUT_DIRECTORY, "led_positions.json")
        os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
        with open(output_file, "w") as f:
            import json
            json.dump(led_positions, f, indent=4)
        print(f"LED positions saved to: {output_file}")


if __name__ == "__main__":
    main()
