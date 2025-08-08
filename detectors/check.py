import cv2
import mediapipe as mp
import numpy as np

# Initialize Mediapipe Face Mesh with iris detection
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1, refine_landmarks=True,
    min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)

# Constants (adjust to your setup)
KNOWN_EYE_DISTANCE = 6.3  # cm, average interpupillary distance
FOCAL_LENGTH = 840        # pixels, calibrate for your camera

# Iris landmark indices in Mediapipe Face Mesh
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

def get_iris_center(landmarks, img_w, img_h, iris_indices):
    x = int(np.mean([landmarks[i].x for i in iris_indices]) * img_w)
    y = int(np.mean([landmarks[i].y for i in iris_indices]) * img_h)
    return (x, y)

def estimate_distance(pixel_dist):
    if pixel_dist == 0:
        return 0
    return (KNOWN_EYE_DISTANCE * FOCAL_LENGTH) / pixel_dist

def pixel_to_3d(u, v, d, f, cx, cy):
    X = (u - cx) * d / f
    Y = (v - cy) * d / f
    Z = d
    return np.array([X, Y, Z])

def project_3d_to_2d(X, Y, Z, f, cx, cy):
    u = int((X * f) / Z + cx)
    v = int((Y * f) / Z + cy)
    return (u, v)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    img_h, img_w = frame.shape[:2]
    cx, cy = img_w / 2, img_h / 2

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            left_center = get_iris_center(face_landmarks.landmark, img_w, img_h, LEFT_IRIS)
            right_center = get_iris_center(face_landmarks.landmark, img_w, img_h, RIGHT_IRIS)

            # Draw iris centers
            cv2.circle(frame, left_center, 5, (255, 0, 0), -1)   # Blue for left eye
            cv2.circle(frame, right_center, 5, (0, 255, 0), -1)  # Green for right eye

            # Pixel distance between eyes in image
            pixel_distance_eyes = np.linalg.norm(np.array(left_center) - np.array(right_center))

            # Estimate overall distance to face (both eyes)
            distance_face = estimate_distance(pixel_distance_eyes)

            # Now calculate individual eye distances (For demo, we approximate both equal to face distance)
            # In real setup, you might calculate distances to other features or use stereo vision
            dist_left = distance_face
            dist_right = distance_face

            # Convert pixel coords + distances to 3D points
            P_left = pixel_to_3d(left_center[0], left_center[1], dist_left, FOCAL_LENGTH, cx, cy)
            P_right = pixel_to_3d(right_center[0], right_center[1], dist_right, FOCAL_LENGTH, cx, cy)

            # Project 3D points back to 2D for drawing
            p1_2d = project_3d_to_2d(*P_left, FOCAL_LENGTH, cx, cy)
            p2_2d = project_3d_to_2d(*P_right, FOCAL_LENGTH, cx, cy)

            # Draw line between the projected points
            cv2.line(frame, p1_2d, p2_2d, (0, 255, 255), 3)  # Yellow line

            # Show estimated distance on frame
            cv2.putText(frame, f"Distance: {distance_face:.2f} cm", (30, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow('3D Distance Line between Eyes', frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
