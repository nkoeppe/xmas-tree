import cv2
import numpy as np
import os
import json

# Configuration
INPUT_DIRECTORY = "./photos"
OUTPUT_DIRECTORY = "./debug_output"
LED_COUNT = 2
ANGLES = [0, 90, 180, 270]  # Degrees
ROTATION_POINT = None  # To be set dynamically based on user selection

def select_rotation_point(image_path):
    """Allow user to select the rotation point from an image."""
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    image_flipped = cv2.flip(image, 0)  # Flip to match bottom-left coordinate system
    selected_point = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Store rotation point and transform coordinates to bottom-left system
            selected_point.append((x, image.shape[0] - y))
            print(f"Selected rotation point: {selected_point[-1]}")
            cv2.destroyWindow("Select Rotation Point")

    cv2.imshow("Select Rotation Point", image_flipped)
    cv2.setMouseCallback("Select Rotation Point", click_event)

    while True:
        key = cv2.waitKey(1)
        if key == 27 or len(selected_point) > 0:  # ESC key or point selected
            break

    cv2.destroyAllWindows()

    if not selected_point:
        raise ValueError("No rotation point selected.")
    return selected_point[0]

def image_bp(fp, led_id, angle):
    image = cv2.imread(fp)
    if image is None:
        raise FileNotFoundError(f"Image not found at path: {fp}")

    orig = image.copy()
    gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
    (_, _, _, max_loc) = cv2.minMaxLoc(gray)

    # Overlay the detected LED position
    image = orig.copy()
    cv2.circle(image, max_loc, 2, (255, 0, 0), 2)

    debug_image_path = os.path.join(OUTPUT_DIRECTORY, f"led_{led_id}_angle_{angle}_debug.jpg")
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    cv2.imwrite(debug_image_path, image)
    print(f"Debug overlay saved at: {debug_image_path}")

    return max_loc


def calculate_3d_coordinates(positions_2d):
    """Estimate the 3D coordinates of an LED based on its 2D positions at multiple angles."""
    # Extract positions for each angle
    angle0_pos = positions_2d[0]
    angle90_pos = positions_2d[90]
    angle180_pos = positions_2d[180]
    angle270_pos = positions_2d[270]

    # Convert positions to 3D coordinates
    points_3d = np.array([
        [0, angle0_pos[0], angle0_pos[1]],
        [angle90_pos[0], 0, angle90_pos[1]],
        [0, angle180_pos[0], angle180_pos[1]],
        [angle270_pos[0], 0, angle270_pos[1]]
    ])

    # Compute intermediate coordinates
    first_coord = np.array([
        points_3d[1, 0],  # angle90_x
        points_3d[0, 1],  # angle0_y
        (points_3d[0, 2] + points_3d[1, 2]) / 2  # Average of z-coordinates (angle0_z, angle90_z)
    ])

    second_coord_raw = np.array([
        points_3d[3, 0],  # angle270_x
        points_3d[2, 1],  # angle180_y
        (points_3d[3, 2] + points_3d[2, 2]) / 2  # Average of z-coordinates (angle270_z, angle180_z)
    ])

    # Apply correction matrix
    correction_matrix = np.array([-1, -1, 1])
    second_coord = second_coord_raw * correction_matrix

    # Compute average of the two coordinates
    avg_coord = (first_coord + second_coord) / 2

    print(f"Calculated 3D coord at {tuple(avg_coord)}")
    return tuple(avg_coord)


def process_led_images(led_id):
    """Process the 'on' and 'off' images for a specific LED and return its 3D coordinates."""
    if ROTATION_POINT is None:
        raise ValueError("Rotation point must be selected before processing images.")

    positions_2d = {}
    # for angle in ANGLES:
    #     on_image_path = os.path.join(INPUT_DIRECTORY, f"angle_{angle}", f"led_on_{led_id}.jpg")
    #
    #     led_coordinates = image_bp(on_image_path, led_id, angle)
    #     ax, ay = led_coordinates
    #     rx = ax - ROTATION_POINT[0]
    #     ry = ay - ROTATION_POINT[1]  # Adjust for bottom-left coordinate system
    #
    #     positions_2d[angle] = (rx, ry)
    #     print(f"LED detected at: {(rx, ry)}")
    positions_2d = mock_positions_2d()
    return calculate_3d_coordinates(positions_2d)

def mock_all_positions_2d():
    """Generate hardcoded test mock for positions_2d."""
    angel0 = [
        [ 0, 0],
        [ 0, 0],
        [ 2, 0],
        [ 1, 2],
        [ 1, 0],
        [ 1, 0],
        [ -2, 0],
        [ -1, 0],
        [ -1, 0],
        [ -1, 2]
    ]

    angel90 = [
        [0,  0],
        [0,  0],
        [0,  2],
        [1,  0],
        [-1, 0],
        [0,  0],
        [-1, 0],
        [1,  0],
        [0,  2]
    ]

    angel180 = [
        [ 0, 0],
        [ -2, 0],
        [ -1, 2],
        [ -1, 0],
        [ -1, 0],
        [ 2, 0],
        [ 1, 0],
        [ 1, 0],
        [ 1, 2]
    ]

    angel270 = [
        [0,  0],
        [0,  0],
        [0,  2],
        [-1, 0],
        [1,  0],
        [0,  0],
        [1,  0],
        [-1, 0],
        [0,  2]
    ]

    result = [
        {
            0: np.array(angel0[i]),
            90: np.array(angel90[i]),
            180:  np.array(angel180[i]),
            270:np.array( angel270[i])
        }
        for i in range(len(angel0))
    ]
    return result

def mock_positions_2d():
    """Generate hardcoded test mock for positions_2d."""
    return {
        0: np.array([0, 2]),
        90: np.array([1, 0]),
        180: np.array([0, -2]),
        270: np.array([-1, 0])
    }

def main():
    global ROTATION_POINT

    # Allow user to select the rotation point
    sample_image_path = os.path.join(INPUT_DIRECTORY, f"angle_0", f"led_on_0.jpg")

    print("Select the rotation point from the displayed image.")
    try:
        ROTATION_POINT = select_rotation_point(sample_image_path)
    except Exception as e:
        print(f"Error during rotation point selection: {e}")
        return
    mocks=mock_all_positions_2d()

    led_positions_3d = []
    try:
        for led_id in range(len(mocks)):
            print(f"Processing LED {led_id}...")
            # led_3d_coords = process_led_images(led_id)
            led_3d_coords = calculate_3d_coordinates(mocks[led_id])

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
