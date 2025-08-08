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
cap = cv2.VideoCapture(0)  # Change to 0 if using default camera
suspicious_start_time = None
cheating_detected = False
alert_message = "Normal - Forward Looking"

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
            cv2.circle(frame, (left_iris_x, left_iris_y), 2, (0, 0, 255), -1)  # Blue - Iris center
            
            cv2.circle(frame, (right_eye_x, right_eye_y), 3, (0, 255, 0), -1)  # Green - Eye center
            cv2.circle(frame, (right_iris_x, right_iris_y), 2, (0, 0, 255), -1)  # Blue - Iris center
            
            # TODO: Calculate differences and implement gaze detection

            # Left eye differences
            left_diff_x = left_iris_x - left_eye_x
            left_diff_y = left_iris_y - left_eye_y

            # Right eye differences  
            right_diff_x = right_iris_x - right_eye_x
            right_diff_y = right_iris_y - right_eye_y

            # Average differences (both eyes combined)
            avg_diff_x = (left_diff_x + right_diff_x) / 2
            avg_diff_y = (left_diff_y + right_diff_y) / 2

            # Print for debugging
            print(f"Avg Diff - X: {avg_diff_x:.1f}, Y: {avg_diff_y:.1f}")

            # Threshold for detection
            THRESHOLD = 6

            # Direction detection
            if avg_diff_x > THRESHOLD:
                horizontal = "Right"
            elif avg_diff_x < -THRESHOLD:
                horizontal = "Left"
            else:
                horizontal = "Center"

            if avg_diff_y > THRESHOLD:
                vertical = "Down"
            elif avg_diff_y < -THRESHOLD:
                vertical = "Up"
            else:
                vertical = "Center"

            # Final direction
            if horizontal == "Center" and vertical == "Center":
                direction = "Forward"
            else:
                direction = f"{vertical} {horizontal}".strip()

            print(f"Direction: {direction}")



            # # Different sensitivity levels
            # NORMAL_THRESHOLD = 8      # Below this = normal behavior
            # SUSPICIOUS_THRESHOLD = 12 # Medium suspicion level  
            # CHEATING_THRESHOLD = 18   # High cheating probability

            # # Corner detection (diagonal movement)
            # CORNER_THRESHOLD = 6      # Lower because corners are more suspicious
            NORMAL_THRESHOLD = 6      # Values ≤6 = Normal
            SUSPICIOUS_THRESHOLD = 8  # Values 7-8 = Suspicious  
            CHEATING_THRESHOLD = 10   # Values >10 = Cheating
            CORNER_THRESHOLD = 7      # Values 6-7 = Corner

            # Classification system
            def classify_behavior(avg_diff_x, avg_diff_y):
                abs_x = abs(avg_diff_x)
                abs_y = abs(avg_diff_y)
                
                # Normal behavior
                if abs_x <= NORMAL_THRESHOLD and abs_y <= NORMAL_THRESHOLD:
                    return "NORMAL", "Forward"
                
                # Corner looking (most suspicious)
                elif abs_x > CORNER_THRESHOLD and abs_y > CORNER_THRESHOLD:
                    return "HIGH_RISK", "Corner Looking"
                
                # High movement (clear cheating)
                elif abs_x > CHEATING_THRESHOLD or abs_y > CHEATING_THRESHOLD:
                    return "HIGH_RISK", "Clear Cheating"
                
                # Medium suspicion
                elif abs_x > SUSPICIOUS_THRESHOLD or abs_y > SUSPICIOUS_THRESHOLD:
                    return "MEDIUM_RISK", "Suspicious"
                
                # Low suspicion
                else:
                    return "LOW_RISK", "Slight Movement"

                
            # Different time thresholds based on risk level
            def get_time_threshold(risk_level):
                if risk_level == "HIGH_RISK":
                    return 1.5  # 1.5 seconds for high risk
                elif risk_level == "MEDIUM_RISK":
                    return 3.0  # 3 seconds for medium risk  
                elif risk_level == "LOW_RISK":
                    return 5.0  # 5 seconds for low risk
                else:
                    return float('inf')  # Normal behavior - no time limit

            # After calculating avg_diff_x and avg_diff_y

            # Classify behavior
            risk_level, behavior_type = classify_behavior(avg_diff_x, avg_diff_y)

            # Get appropriate time threshold
            time_threshold = get_time_threshold(risk_level)

            # Timing logic
            current_time = time.time()


            if risk_level != "NORMAL":
                if suspicious_start_time is None:
                    suspicious_start_time = current_time
                    current_risk_level = risk_level
                    current_behavior = behavior_type
                else:
                    # Check if threshold time exceeded
                    if current_time - suspicious_start_time > time_threshold:
                        if not cheating_detected:
                            cheating_detected = True
                            alert_message = f"ALERT: {risk_level} - {behavior_type}"
                            print(f"Cheating detected: {behavior_type}")
            else:
                # Reset when looking forward
                suspicious_start_time = None
                cheating_detected = False
                alert_message = "Normal - Forward Looking"

            # Visual feedback based on risk level
            if cheating_detected:
                if risk_level == "HIGH_RISK":
                    rect_color = (0, 0, 255)    # Red
                    text_color = (0, 0, 255)    # Red
                    thickness = 5
                elif risk_level == "MEDIUM_RISK":
                    rect_color = (0, 165, 255)  # Orange
                    text_color = (0, 165, 255)  # Orange
                    thickness = 3
                else:
                    rect_color = (0, 255, 255)  # Yellow
                    text_color = (0, 255, 255)  # Yellow
                    thickness = 2
                
                # Draw warning
                cv2.rectangle(frame, (50, 50), (300, 150), rect_color, thickness)
                cv2.putText(frame, alert_message, (20, 200), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)

            # Display current values (for tuning)
            cv2.putText(frame, f'Risk: {risk_level}', (20, 250), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, f'Behavior: {behavior_type}', (20, 270), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)


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
    
    # FPS Calculation with ZeroDivisionError protection
            end = time.time()
            totalTime = end - start

            # Prevent division by zero
            if totalTime > 0:
                fps = 1 / totalTime
            else:
                fps = 0  # or use a default value like 30

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






# OBJECT Oriented of this class 


