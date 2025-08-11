from .base import BaseDetector
import cv2
import mediapipe as mp
import numpy as np
import time


class FaceDetector(BaseDetector):

    """Face detector for cheating behavior detection based on head pose estimation."""

    # class attributes
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    # Important facial landmarks for pose estimation
    IMPORTANT_LANDMARKS = {33, 263, 1, 61, 291, 199}  # Eyes, nose, mouth corners, chin

    # constructor 
    def __init__(self):  
        self.face_mesh = self.mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5,refine_landmarks=True)
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
        self.cheating_start_time = None
        self.cheating_end_time = None
        self.cheating_count = 0
        self.cheating_duration = 0
        self.cheating_duration_total = 0
        self.cheating = False
        self.cheating_direction = None
        self.cheating_status = False

    # detection method
    def detect( self, frame) -> dict:
        image,results = self.preprocess(frame)
        pitch,yaw,roll = self.get_head_pose(results,image)
        print(f"Pitch : {pitch} Yaw : {yaw} Roll : {roll}")
        
        if pitch is None or yaw is None or roll is None:
            return {
                "cheating": False,
                "direction": None,
                "cheating_count": self.cheating_count,
                "cheating_duration": self.cheating_duration,
                "cheating_duration_total": self.cheating_duration_total 
            }
        directions = self.check_cheating_behavior(pitch,yaw,roll) 
        cheating_status , direction , duration  ,count,_= self.update_cheating_count(directions)  
        return {
            "cheating": cheating_status,
            "direction": direction,
            "cheating_count": count,
            "cheating_duration": duration,
            "cheating_duration_total": self.cheating_duration_total 
        }

    def preprocess(self,frame):
        # Flip the image horizontally for a later selfie-view display
        # Also convert the color space from BGR to RGB for mediapipe
        image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)

        # To improve performance
        image.flags.writeable = False
    
        # Get the result
        results = self.face_mesh.process(image)
    
        # To improve performance
        image.flags.writeable = True
    
        # Convert the color space from RGB to BGR for Open cv conversion
        cv_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return cv_image,results


    def get_head_pose (self,results,image):
        # extract the landmarks of face
        img_h, img_w, _ = image.shape
        face_2d = []
        face_3d = []
        

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for idx, lm in enumerate(face_landmarks.landmark):
                    important_landmarks = {33, 263, 1, 61, 291, 199}
                    if idx in important_landmarks:
                        x, y = int(lm.x * img_w), int(lm.y * img_h)
                        face_2d.append([x, y])
                        face_3d.append([x, y, lm.z ])        
            if len(face_2d) < 6 :
                return None, None, None

            # Convert it to the NumPy array
            face_2d = np.array(face_2d, dtype=np.float64)

            # Convert it to the NumPy array
            face_3d = np.array(face_3d, dtype=np.float64)

            # The camera matrix
            focal_length = 1 * img_w
            cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                                    [0, focal_length, img_w / 2],
                                    [0, 0, 1]])

            # The distortion parameters
            dist_matrix = np.zeros((4, 1), dtype=np.float64)

            # Solve PnP
            success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
            if not success:
                return None, None, None

            # Get rotational matrix
            rmat, _ = cv2.Rodrigues(rot_vec)

            # Get angles
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

            # Get the y rotation degree
            x_angles = angles[0] * 360
            y_angles = angles[1] * 360
            z_angles = angles[2] * 360

            pitch, yaw, roll = x_angles, y_angles, z_angles
            return pitch, yaw, roll

        return None, None, None

    def check_cheating_behavior(self,pitch,yaw,roll):
        if yaw < -10:
            direction = "Left"
        elif yaw > 10:
            direction = "Right"
        elif pitch < -10:
            direction = "Down"
        elif pitch > 10:
            direction = "Up"
        else:
            direction = "Forward"
        return direction 


    def update_cheating_count(self , directions):
        current_time = time.time()
        
        # Cheating logic
        if directions != "Forward":
            if self.cheating_start_time is None:
                self.cheating_start_time = current_time  # 10 
                self.cheating_direction = directions #left 
            else:
                if current_time - self.cheating_start_time > 3 and not self.cheating:
                    self.cheating = True
                    # text = f"Alert: Cheating - Looking {self.cheating_direction}"
                    # print("Cheating Detected!")
        else:
            if self.cheating:
                self.cheating_end_time = current_time 
                self.cheating_duration = self.cheating_end_time - self.cheating_start_time
                self.cheating_duration_total += self.cheating_duration
                self.cheating_count += 1
                # print(f"Cheating #{self.cheating_count}: {self.cheating_direction} for {self.cheating_duration:.2f} sec")

                self.cheating = False
                self.cheating_start_time = None
                self.cheating_end_time = None
                self.cheating_direction = None
                # text = "Forward"

        return self.cheating , self.cheating_direction,self.cheating_duration,self.cheating_count,self.cheating_duration_total

        