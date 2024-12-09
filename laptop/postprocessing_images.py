import cv2
import numpy as np
import os
import json

# Configuration
INPUT_DIRECTORY = "./photos"
OUTPUT_DIRECTORY = "./debug_output"
LED_COUNT = 10
ANGLES = [0, 90, 180, 270]  # Degrees
IMAGE_CENTER = (320, 240)  # Assume 1024x768 resolution; adjust if different


def calculate_difference_image(on_image_path, off_image_path):
    """Calculate the difference between 'on' and 'off' images to isolate the LED."""
    on_image = cv2.imread(on_image_path, cv2.IMREAD_GRAYSCALE)
    off_image = cv2.imread(off_image_path, cv2.IMREAD_GRAYSCALE)

    if on_image is None or off_image is None:
        raise FileNotFoundError(f"Could not load images: {on_image_path} or {off_image_path}")

    # Subtract 'off' image from 'on' image
    diff = cv2.absdiff(on_image, off_image)

    # Apply Gaussian blur to reduce noise
    diff = cv2.GaussianBlur(diff, (5, 5), 0)

    # Threshold the difference image
    _, thresholded = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)
    return diff, thresholded


def find_led_coordinates(thresholded_image):
    """Find the coordinates of the brightest region (LED) in the thresholded image."""
    contours, _ = cv2.findContours(thresholded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("No LED detected in the thresholded image.")

    # Find the largest contour
    largest_contour = max(contours, key=cv2.contourArea)

    # Calculate the center of the contour
    moments = cv2.moments(largest_contour)
    if moments["m00"] == 0:
        raise ValueError("Invalid contour moments.")
    cx = int(moments["m10"] / moments["m00"])
    cy = int(moments["m01"] / moments["m00"])
    return cx, cy, largest_contour


def add_debug_overlay(original_image_path, output_path, cx, cy, contour, led_id, angle):
    """Add a debug overlay to the image to visualize detected LED coordinates."""
    original_image = cv2.imread(original_image_path)

    # Draw the contour
    cv2.drawContours(original_image, [contour], -1, (0, 255, 0), 2)

    # Draw the center point
    cv2.circle(original_image, (cx, cy), 5, (0, 0, 255), -1)

    # Add coordinates text
    cv2.putText(
        original_image,
        f"LED {led_id} Angle {angle} ({cx}, {cy})",
        (cx + 10, cy - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 0, 0),
        2,
    )

    # Add center of the image for reference
    cv2.circle(original_image, IMAGE_CENTER, 5, (255, 255, 0), -1)
    cv2.line(original_image, (cx, cy), IMAGE_CENTER, (255, 255, 0), 1)

    # Save the debug image
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    debug_output_path = os.path.join(OUTPUT_DIRECTORY, os.path.basename(output_path))
    cv2.imwrite(debug_output_path, original_image)
    print(f"Debug image saved to: {debug_output_path}")


def calculate_dynamic_radius(positions_2d):
    """Calculate the rotation radius dynamically based on the average distance from the center."""
    distances = []
    for cx, cy in positions_2d:
        distance = np.sqrt((cx - IMAGE_CENTER[0]) ** 2 + (cy - IMAGE_CENTER[1]) ** 2)
        distances.append(distance)
    return np.mean(distances)


def calculate_3d_coordinates(positions_2d, rotation_radius):
    """Estimate the 3D coordinates of an LED based on its 2D positions at multiple angles."""
    coords_3d = []
    for angle_deg, (cx, cy) in zip(ANGLES, positions_2d):
        angle_rad = np.deg2rad(angle_deg)
        x = rotation_radius * np.cos(angle_rad)
        y = rotation_radius * np.sin(angle_rad)
        z = cy  # Use the y-coordinate as depth (z-axis) since camera is fixed
        coords_3d.append((x, y, z))

    # Average the calculated 3D positions for better accuracy
    avg_x = np.mean([p[0] for p in coords_3d])
    avg_y = np.mean([p[1] for p in coords_3d])
    avg_z = np.mean([p[2] for p in coords_3d])
    return avg_x, avg_y, avg_z


def process_led_images(led_id):
    """Process the 'on' and 'off' images for a specific LED and return its 3D coordinates."""
    positions_2d = []
    for angle in ANGLES:
        on_image_path = os.path.join(INPUT_DIRECTORY, f"angle_{angle}", f"led_on_{led_id}.jpg")
        off_image_path = os.path.join(INPUT_DIRECTORY, f"angle_{angle}", f"led_off_{led_id}.jpg")

        # Calculate difference and thresholded images
        _, thresholded = calculate_difference_image(on_image_path, off_image_path)

        # Find 2D coordinates
        cx, cy, contour = find_led_coordinates(thresholded)
        positions_2d.append((cx, cy))

        # Save debug overlay
        add_debug_overlay(
            on_image_path,
            f"led_{led_id}_angle_{angle}_debug.jpg",
            cx,
            cy,
            contour,
            led_id,
            angle,
        )

    # Dynamically calculate the rotation radius for this LED
    rotation_radius = calculate_dynamic_radius(positions_2d)

    # Estimate 3D coordinates
    return calculate_3d_coordinates(positions_2d, rotation_radius)


def main():
    led_positions_3d = []
    try:
        for led_id in range(LED_COUNT):
            try:
                print(f"Processing LED {led_id}...")
                led_3d_coords = process_led_images(led_id)
                led_positions_3d.append({
                    "led_id": led_id,
                    "x": led_3d_coords[0],
                    "y": led_3d_coords[1],
                    "z": led_3d_coords[2],
                })
                print(f"LED {led_id} detected at ({led_3d_coords[0]:.2f}, {led_3d_coords[1]:.2f}, {led_3d_coords[2]:.2f}).")
            except Exception as e:
                print(f"Error processing LED {led_id}: {e}")
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
