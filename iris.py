import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Face Mesh with iris detection
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,  # Important for iris detection
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Drawing specifications
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

# Start video capture
cap = cv2.VideoCapture(1)  # Change to 0 if using default camera

print("Starting iris detection...")
print("Press ESC to exit")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame")
        continue
    
    # Start timer for FPS
    start = time.time()
    
    # Flip frame horizontally for selfie view
    frame = cv2.flip(frame, 1)
    
    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame
    results = face_mesh.process(rgb_frame)
    
    # Convert back to BGR for display
    frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
    
    # Get image dimensions
    img_h, img_w, _ = frame.shape
    
    # Process face landmarks
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            
            # TODO: Add your iris detection logic here
            # Landmark indices:
            # Left Eye Center: 159
            # Left Iris Center: 468
            # Right Eye Center: 386
            # Right Iris Center: 473
            
            # Example: Extract landmark points
            landmarks = face_landmarks.landmark
            
            # Left eye and iris points
            left_eye = landmarks[159]
            left_iris = landmarks[468]
            
            # Right eye and iris points  
            right_eye = landmarks[386]
            right_iris = landmarks[473]
            
            # Convert to pixel coordinates
            left_eye_x, left_eye_y = int(left_eye.x * img_w), int(left_eye.y * img_h)
            left_iris_x, left_iris_y = int(left_iris.x * img_w), int(left_iris.y * img_h)
            
            right_eye_x, right_eye_y = int(right_eye.x * img_w), int(right_eye.y * img_h)
            right_iris_x, right_iris_y = int(right_iris.x * img_w), int(right_iris.y * img_h)
            
            # Draw eye and iris points (for visualization)
            cv2.circle(frame, (left_eye_x, left_eye_y), 3, (0, 255, 0), -1)  # Green - Eye center
            cv2.circle(frame, (left_iris_x, left_iris_y), 2, (255, 0, 0), -1)  # Blue - Iris center
            
            cv2.circle(frame, (right_eye_x, right_eye_y), 3, (0, 255, 0), -1)  # Green - Eye center
            cv2.circle(frame, (right_iris_x, right_iris_y), 2, (255, 0, 0), -1)  # Blue - Iris center
            
            # TODO: Calculate differences and implement gaze detection
            # left_diff_x = left_iris_x - left_eye_x
            # left_diff_y = left_iris_y - left_eye_y
            # ... your logic here
            
            # Draw face mesh (optional - you can comment this out)
            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
            )
            
            # Draw iris connections
            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_IRISES,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_iris_connections_style()
            )
    
    # Calculate and display FPS
    end = time.time()
    fps = 1 / (end - start)
    cv2.putText(frame, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Display instructions
    cv2.putText(frame, 'Green: Eye Center, Blue: Iris Center', (20, img_h - 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Show the frame
    cv2.imshow('Iris Detection - Basic Template', frame)
    
    # Exit on ESC key
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
print("Iris detection stopped.")