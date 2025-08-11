from .base import BaseDetector
import cv2
import mediapipe as mp
import time
from collections import deque


class GazeDetector(BaseDetector):
    """Gaze detector for cheating behavior detection based on iris tracking."""
    
    # Class attributes
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    
    # Iris and eye landmark indices
    LEFT_IRIS = [474, 475, 476, 477]
    RIGHT_IRIS = [469, 470, 471, 472]
    LEFT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
    RIGHT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
    
    def __init__(self):
        """Initialize the GazeDetector."""
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
        
        # Calibration variables
        self.calibration_data = []
        self.is_calibrated = False
        self.baseline_x = 0
        self.baseline_y = 0
        
        # Smoothing
        self.gaze_history = deque(maxlen=5)
        
        # Cheating detection variables (matching FaceDetector pattern)
        self.cheating_start_time = None
        self.cheating_end_time = None
        self.cheating_count = 0
        self.cheating_duration = 0
        self.cheating_duration_total = 0
        self.cheating = False
        self.cheating_direction = None
        self.cheating_status = False
        
        # Thresholds
        self.NORMAL_THRESHOLD = 3
        self.SUSPICIOUS_THRESHOLD = 6
        self.CHEATING_THRESHOLD = 10
    
    def detect(self, frame) -> dict:
        """Main detection method following FaceDetector pattern."""
        image, results = self.preprocess(frame)
        diff_x, diff_y = self.get_gaze_direction(results, image)
        
        if diff_x is None or diff_y is None:
            print("No face detected")
            return {
                "cheating": False,
                "direction": None,
                "cheating_count": self.cheating_count,
                "cheating_duration": self.cheating_duration,
                "cheating_duration_total": self.cheating_duration_total
            }
        
        print(f"Gaze - X: {diff_x:.1f}, Y: {diff_y:.1f}")
        
        direction = self.check_cheating_behavior(diff_x, diff_y)
        cheating_status, direction, duration, count, _ = self.update_cheating_count(direction)
        
        return {
            "cheating": cheating_status,
            "direction": direction,
            "cheating_count": count,
            "cheating_duration": duration,
            "cheating_duration_total": self.cheating_duration_total
        }
    def preprocess(self, frame):
        """Preprocess frame for gaze detection."""
        # Flip the image horizontally for a later selfie-view display
        # Also convert the color space from BGR to RGB for mediapipe
        image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        
        # To improve performance
        image.flags.writeable = False
        
        # Get the result
        results = self.face_mesh.process(image)
        
        # To improve performance
        image.flags.writeable = True
        
        # Convert the color space from RGB to BGR for OpenCV
        cv_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return cv_image, results
    
    def get_eye_center(self, landmarks, eye_indices, img_w, img_h):
        """Calculate the center of an eye region."""
        x_coords = [landmarks[i].x * img_w for i in eye_indices]
        y_coords = [landmarks[i].y * img_h for i in eye_indices]
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        return int(center_x), int(center_y)
    
    def get_iris_center(self, landmarks, iris_indices, img_w, img_h):
        """Calculate the center of iris."""
        x_coords = [landmarks[i].x * img_w for i in iris_indices]
        y_coords = [landmarks[i].y * img_h for i in iris_indices]
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        return int(center_x), int(center_y)
    
    def calibrate(self, landmarks, img_w, img_h):
        """Calibrate the system with forward-looking gaze."""
        # Get eye and iris centers
        left_eye_center = self.get_eye_center(landmarks, self.LEFT_EYE, img_w, img_h)
        right_eye_center = self.get_eye_center(landmarks, self.RIGHT_EYE, img_w, img_h)
        left_iris_center = self.get_iris_center(landmarks, self.LEFT_IRIS, img_w, img_h)
        right_iris_center = self.get_iris_center(landmarks, self.RIGHT_IRIS, img_w, img_h)
        
        # Calculate differences
        left_diff_x = left_iris_center[0] - left_eye_center[0]
        left_diff_y = left_iris_center[1] - left_eye_center[1]
        right_diff_x = right_iris_center[0] - right_eye_center[0]
        right_diff_y = right_iris_center[1] - right_eye_center[1]
        
        # Average
        avg_diff_x = (left_diff_x + right_diff_x) / 2
        avg_diff_y = (left_diff_y + right_diff_y) / 2
        
        self.calibration_data.append((avg_diff_x, avg_diff_y))
        
        # If we have enough calibration data, calculate baseline
        if len(self.calibration_data) >= 30:  # 30 frames for calibration
            x_vals = [d[0] for d in self.calibration_data]
            y_vals = [d[1] for d in self.calibration_data]
            
            self.baseline_x = sum(x_vals) / len(x_vals)
            self.baseline_y = sum(y_vals) / len(y_vals)
            self.is_calibrated = True
            
            print(f"Calibration complete! Baseline: X={self.baseline_x:.2f}, Y={self.baseline_y:.2f}")
    
    def get_gaze_direction(self, results, image):
        """Extract gaze direction from face landmarks."""
        img_h, img_w, _ = image.shape
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                
                # Calibration phase
                if not self.is_calibrated:
                    self.calibrate(landmarks, img_w, img_h)
                    return 0, 0  # Return neutral during calibration
                
                # Get eye and iris centers
                left_eye_center = self.get_eye_center(landmarks, self.LEFT_EYE, img_w, img_h)
                right_eye_center = self.get_eye_center(landmarks, self.RIGHT_EYE, img_w, img_h)
                left_iris_center = self.get_iris_center(landmarks, self.LEFT_IRIS, img_w, img_h)
                right_iris_center = self.get_iris_center(landmarks, self.RIGHT_IRIS, img_w, img_h)
                
                # Calculate differences
                left_diff_x = left_iris_center[0] - left_eye_center[0]
                left_diff_y = left_iris_center[1] - left_eye_center[1]
                right_diff_x = right_iris_center[0] - right_eye_center[0]
                right_diff_y = right_iris_center[1] - right_eye_center[1]
                
                # Average and normalize with baseline
                raw_diff_x = (left_diff_x + right_diff_x) / 2
                raw_diff_y = (left_diff_y + right_diff_y) / 2
                
                norm_diff_x = raw_diff_x - self.baseline_x
                norm_diff_y = raw_diff_y - self.baseline_y
                
                # Smooth the values
                self.gaze_history.append((norm_diff_x, norm_diff_y))
                if len(self.gaze_history) > 1:
                    avg_x = sum([g[0] for g in self.gaze_history]) / len(self.gaze_history)
                    avg_y = sum([g[1] for g in self.gaze_history]) / len(self.gaze_history)
                else:
                    avg_x, avg_y = norm_diff_x, norm_diff_y
                
                return avg_x, avg_y
        
        return None, None
    
    def check_cheating_behavior(self, diff_x, diff_y):
        """Check for suspicious gaze behavior."""
        abs_x = abs(diff_x)
        abs_y = abs(diff_y)
        
        # Direction determination with smaller thresholds
        if abs_x < 2 and abs_y < 2:
            return "Forward"
        
        # Determine primary direction
        if abs_x > abs_y:
            if diff_x > 2:
                direction = "Right"
            elif diff_x < -2:
                direction = "Left"
            else:
                direction = "Center"
        else:
            if diff_y > 2:
                direction = "Down"
            elif diff_y < -2:
                direction = "Up"
            else:
                direction = "Center"
        
        # Handle center cases
        if direction == "Center":
            if abs_y > 2:
                direction = "Up" if diff_y < 0 else "Down"
            elif abs_x > 2:
                direction = "Left" if diff_x < 0 else "Right"
            else:
                direction = "Forward"
        
        return direction
    
    def update_cheating_count(self, direction):
        """Update cheating count and duration (matching FaceDetector pattern)."""
        current_time = time.time()
        
        # Cheating logic
        if direction != "Forward":
            if self.cheating_start_time is None:
                self.cheating_start_time = current_time
                self.cheating_direction = direction
            else:
                if current_time - self.cheating_start_time > 3 and not self.cheating:
                    self.cheating = True
        else:
            if self.cheating:
                self.cheating_end_time = current_time
                self.cheating_duration = self.cheating_end_time - self.cheating_start_time
                self.cheating_duration_total += self.cheating_duration
                self.cheating_count += 1
                
                self.cheating = False
                self.cheating_start_time = None
                self.cheating_end_time = None
                self.cheating_direction = None
        
        return self.cheating, self.cheating_direction, self.cheating_duration, self.cheating_count, self.cheating_duration_total
