import cv2
import numpy as np
import os
import json

# Configuration
INPUT_DIRECTORY = "./photos"
OUTPUT_DIRECTORY = "./debug_output"
LED_COUNT = 1
ANGLES = [0, 90, 180, 270]  # Degrees
IMAGE_CENTER = (320, 240)
# ROTATION_AXIS = None
ROTATION_AXIS = [(266, 150), (263, 400)]
DEBUG_MODE = True
TURN_DIRECTION = "left"
def calculate_difference_image(on_image_path, off_image_path):
    """Calculate the difference where the image got brighter."""
    on_image = cv2.imread(on_image_path, cv2.IMREAD_GRAYSCALE)
    off_image = cv2.imread(off_image_path, cv2.IMREAD_GRAYSCALE)

    if on_image is None or off_image is None:
        raise FileNotFoundError(f"Could not load images: {on_image_path} or {off_image_path}")

    # Subtract 'off' image from 'on' image to detect brightening
    diff = cv2.subtract(on_image, off_image)

    # Apply Gaussian blur to smooth the difference image
    diff = cv2.GaussianBlur(diff, (5, 5), 0)

    # Apply a threshold to isolate significant brightness changes
    _, thresholded = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    return diff, thresholded

def find_led_coordinates(diff_image):
    """
    Find the coordinates of the LED by identifying the brightest 1% of pixels
    and calculating their center of mass.
    """
    # Flatten the image and sort pixel intensities
    flat_diff = diff_image.flatten()
    sorted_indices = np.argsort(flat_diff)[::-1]  # Sort in descending order

    # Determine the intensity threshold for the brightest 1% of pixels
    threshold_index = int(0.0005 * len(sorted_indices))  # Top 1%
    intensity_threshold = flat_diff[sorted_indices[threshold_index]]

    # Create a binary mask for the brightest pixels
    brightest_mask = (diff_image >= intensity_threshold).astype(np.uint8)

    # Find coordinates of the brightest pixels
    brightest_coords = np.column_stack(np.where(brightest_mask > 0))

    if len(brightest_coords) == 0:
        raise ValueError("No bright pixels found in the image.")

    # Calculate the center of mass (average of the coordinates)
    cx = int(np.mean(brightest_coords[:, 1]))
    cy = int(np.mean(brightest_coords[:, 0]))

    return cx, cy, brightest_mask
def add_debug_overlay(original_image_path, output_path, cx, cy, brightest_mask, led_id, angle):
    """
    Add a debug overlay to the image to visualize the brightest pixels,
    the calculated center of mass (LED location), and the rotation axis (line).
    """
    original_image = cv2.imread(original_image_path)

    # Overlay the brightest pixels in blue
    overlay = original_image.copy()
    overlay[brightest_mask > 0] = [255, 0, 0]  # Brightest pixels in blue
    debug_image = cv2.addWeighted(overlay, 0.5, original_image, 0.5, 0)

    # Draw the center point (calculated LED location)
    cv2.circle(debug_image, (cx, cy), 5, (0, 0, 255), -1)

    # Annotate LED ID and coordinates
    cv2.putText(
        debug_image,
        f"LED {led_id}: ({cx}, {cy})",
        (cx + 10, cy - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 255),
        2,
    )

    # Draw the rotation axis as a line
    cv2.line(debug_image, ROTATION_AXIS[0], ROTATION_AXIS[1], (0, 255, 0), 2)  # Line in green

    # Add axis points text
    cv2.putText(
        debug_image,
        f"Axis P1 ({ROTATION_AXIS[0][0]}, {ROTATION_AXIS[0][1]})",
        (ROTATION_AXIS[0][0] + 10, ROTATION_AXIS[0][1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        2,
    )
    cv2.putText(
        debug_image,
        f"Axis P2 ({ROTATION_AXIS[1][0]}, {ROTATION_AXIS[1][1]})",
        (ROTATION_AXIS[1][0] + 10, ROTATION_AXIS[1][1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        2,
    )

    # Draw a line connecting the LED location to the axis
    closest_point = get_closest_point_on_line((cx, cy), ROTATION_AXIS[0], ROTATION_AXIS[1])
    cv2.line(debug_image, (cx, cy), closest_point, (255, 255, 0), 1)

    # Save the debug image
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    debug_output_path = os.path.join(OUTPUT_DIRECTORY, os.path.basename(output_path))
    cv2.imwrite(debug_output_path, debug_image)
    print(f"Debug image with axis saved to: {debug_output_path}")

def get_closest_point_on_line(point, line_start, line_end):
    """
    Calculate the closest point on a line segment to a given point in 2D space.
    """
    px, py = point
    x1, y1 = line_start
    x2, y2 = line_end

    # Line vector and point projection
    line_vec = np.array([x2 - x1, y2 - y1])
    point_vec = np.array([px - x1, py - y1])
    line_len = np.dot(line_vec, line_vec)
    if line_len == 0:  # Line segment is a single point
        return line_start

    projection = np.dot(point_vec, line_vec) / line_len
    projection = max(0, min(1, projection))  # Clamp to [0, 1] for segment
    closest_point = np.array([x1, y1]) + projection * line_vec
    return int(closest_point[0]), int(closest_point[1])


def calculate_dynamic_radius(positions_2d, axis):
    """
    Calculate the rotation radius dynamically based on the average perpendicular
    distance from the rotation axis (line).
    """
    line_start, line_end = axis
    distances = []
    for cx, cy in positions_2d:
        closest_point = get_closest_point_on_line((cx, cy), line_start, line_end)
        distance = np.sqrt((cx - closest_point[0]) ** 2 + (cy - closest_point[1]) ** 2)
        distances.append(distance)
    return np.mean(distances)

def calculate_3d_coordinates(positions_2d, rotation_radius):
    """
    Estimate the 3D coordinates of an LED based on its 2D positions at multiple angles.
    Properly account for the geometry and avoid symmetric averaging mistakes.
    """
    coords_3d = []
    for angle_deg, (cx, cy) in zip(ANGLES, positions_2d):
        angle_rad = np.deg2rad(angle_deg)
        x = rotation_radius * np.cos(angle_rad)
        y = rotation_radius * np.sin(angle_rad)
        z = cy  # Use the y-coordinate as depth (z-axis) from the 2D image
        coords_3d.append((x, y, z))

    # Compute averages directly in 3D space
    avg_x = np.mean([p[0] for p in coords_3d])
    avg_y = np.mean([p[1] for p in coords_3d])
    avg_z = np.mean([p[2] for p in coords_3d])  # Z-axis remains straightforward

    if DEBUG_MODE:
        print("3D Coordinates Debug Data:")
        for idx, coord in enumerate(coords_3d):
            print(f"Angle {ANGLES[idx]}°: X={coord[0]:.2f}, Y={coord[1]:.2f}, Z={coord[2]:.2f}")

    return avg_x, avg_y, avg_z


def process_led_images(led_id):
    """
    Process the 'on' and 'off' images for a specific LED and return its 3D coordinates.
    """
    positions_2d = []
    for angle in ANGLES:
        on_image_path = os.path.join(INPUT_DIRECTORY, f"angle_{angle}", f"led_on_{led_id}.jpg")
        off_image_path = os.path.join(INPUT_DIRECTORY, f"angle_{angle}", f"led_off_{led_id}.jpg")

        # Calculate difference and thresholded images
        diff_image, _ = calculate_difference_image(on_image_path, off_image_path)

        # Find 2D coordinates
        cx, cy, brightest_mask = find_led_coordinates(diff_image)
        positions_2d.append((cx, cy))

        # Save debug overlay
        add_debug_overlay(
            on_image_path,
            f"led_{led_id}_angle_{angle}_debug.jpg",
            cx,
            cy,
            brightest_mask,
            led_id,
            angle,
        )

    # Dynamically calculate the rotation radius for this LED
    rotation_radius = calculate_dynamic_radius(positions_2d, ROTATION_AXIS)

    debug_2d_positions_file = os.path.join(OUTPUT_DIRECTORY, "positions_2d.json")
    with open(debug_2d_positions_file, "w") as debug_file:
        json.dump({"led_positions_2d": positions_2d}, debug_file, indent=4)
    print(f"2D positions saved to: {debug_2d_positions_file}")

    # Estimate 3D coordinates
    return calculate_3d_coordinates(positions_2d, rotation_radius)

def select_rotation_axis(image_path):
    """
    Let the user manually select two points for the rotation axis on the image.
    """
    global ROTATION_AXIS
    ROTATION_AXIS = []
    points = []

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            print(f"Point selected: ({x}, {y})")
            if len(points) == 2:
                print(f"Rotation axis set: {points}")
                cv2.destroyWindow("Select Rotation Axis")

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")

    cv2.imshow("Select Rotation Axis", image)
    cv2.setMouseCallback("Select Rotation Axis", mouse_callback)

    # Wait until points are selected
    while len(points) < 2:
        cv2.waitKey(1)

    # Cleanup windows
    cv2.destroyAllWindows()

    ROTATION_AXIS = points
    return points

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

    if DEBUG_MODE:
        print(f"Solid Debugging Mode Enabled: {led_positions_3d}")

# Ensure rotation axis is selected before running
if __name__ == "__main__":
    if ROTATION_AXIS is None:
        example_image_path = os.path.join(INPUT_DIRECTORY, "angle_0", "led_on_0.jpg")

        if os.path.exists(example_image_path):
            print("Please select two points to define the rotation axis.")
            ROTATION_AXIS = select_rotation_axis(example_image_path)  # User selects the axis
    print(f"Selected Rotation Axis: {ROTATION_AXIS}")

    main()
