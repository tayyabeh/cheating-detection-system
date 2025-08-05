import cv2
import mediapipe as mp
import numpy as np
import time
from mediapipe.python.solutions import drawing_styles as mp_drawing_styles
from mediapipe.python.solutions import face_mesh as mp_face_mesh


# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5,refine_landmarks=True)

# Initialize Drawing Utilities
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

# Start capturing video from the webcam
cap = cv2.VideoCapture(1)
# See where the user's head tilting
current_time = time.time()
cheating_start_time = None
cheating_end_time = None
cheating_count = 0
cheating_duration_total = 0
cheating = False
cheating_direction = None

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    start = time.time()

    # Flip the image horizontally for a later selfie-view display
    # Also convert the color space from BGR to RGB
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    # To improve performance
    image.flags.writeable = False
    
    # Get the result
    results = face_mesh.process(image)
    
    # To improve performance
    image.flags.writeable = True
    
    # Convert the color space from RGB to BGR
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    img_h, img_w, img_c = image.shape
    face_2d = []
    face_3d = []

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for idx, lm in enumerate(face_landmarks.landmark):
                # We are tracking specific landmarks on the face
                # 1: Nose tip, 33: Left eye, 263: Right eye, 61: Left mouth corner, 291: Right mouth corner, 199: Chin
                if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                    if idx == 1:
                        nose_2d = (lm.x * img_w, lm.y * img_h)
                        nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 3000)

                    x, y = int(lm.x * img_w), int(lm.y * img_h)

                    # Get the 2D Coordinates
                    face_2d.append([x, y])

                    # Get the 3D Coordinates
                    face_3d.append([x, y, lm.z])       
            
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

            # Get rotational matrix
            rmat, jac = cv2.Rodrigues(rot_vec)

            # Get angles
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

            # Get the y rotation degree
            x = angles[0] * 360
            y = angles[1] * 360
            z = angles[2] * 360
          
            

            # if y < -10:
            #     text = "Looking Left"
            # elif y > 10:
            #     text = "Looking Right"
            # elif x < -10:
            #     text = "Looking Down"
            # elif x > 10:
            #     text = "Looking Up"
            # else:
            #     text = "Forward"
            
            # Detect direction
            current_time = time.time()

            # Determine direction
            if y < -10:
                direction = "Left"
            elif y > 10:
                direction = "Right"
            elif x < -10:
                direction = "Down"
            elif x > 10:
                direction = "Up"
            else:
                direction = "Forward"

            # Cheating logic
            if direction != "Forward":
                if cheating_start_time is None:
                    cheating_start_time = current_time
                    cheating_direction = direction
                else:
                    if current_time - cheating_start_time > 3 and not cheating:
                        cheating = True
                        text = f"Alert: Cheating - Looking {cheating_direction}"
                        print("Cheating Detected!")
            else:
                if cheating:
                    cheating_end_time = current_time
                    cheating_duration = cheating_end_time - cheating_start_time
                    cheating_duration_total += cheating_duration
                    cheating_count += 1
                    print(f"Cheating #{cheating_count}: {cheating_direction} for {cheating_duration:.2f} sec")

                cheating = False
                cheating_start_time = None
                cheating_end_time = None
                cheating_direction = None
                text = "Forward"

            # Draw red rectangle if cheating
            if cheating:
                cv2.rectangle(image, (0, 0), (img_w-1, img_h-1), (0, 0, 255), 10)
                # x1, y1, x2, y2 = 50, 50, 300, 200
                # cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 5)
                # cv2.putText(image, "CHEATING ALERT!", (60, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


            # Display the nose direction
            nose_3d_projection, jacobian = cv2.projectPoints(nose_3d, rot_vec, trans_vec, cam_matrix, dist_matrix)

            p1 = (int(nose_2d[0]), int(nose_2d[1]))
            p2 = (int(nose_2d[0] + y * 10) , int(nose_2d[1] - x * 10))
            
            cv2.line(image, p1, p2, (255, 0, 0), 3)

            # Add the text on the image
            cv2.putText(image, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
            cv2.putText(image, "x: " + str(np.round(x,2)), (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(image, "y: " + str(np.round(y,2)), (500, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(image, "z: " + str(np.round(z,2)), (500, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


            # FPS
            end = time.time()
            totalTime = end - start
            fps = 1 / totalTime
            cv2.putText(image, f'FPS: {int(fps)}', (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)    

            mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=drawing_spec,
                        connection_drawing_spec=drawing_spec)

            mp_drawing.draw_landmarks(
            image=image,
            landmark_list=face_landmarks,
            connections=mp_face_mesh.FACEMESH_IRISES,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_iris_connections_style()
            )

            cv2.imshow('Head Pose Estimation', image)

    # Exit on pressing 'ESC'
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

print(f"\nTotal Cheating Events: {cheating_count}")
print(f"Total Cheating Time: {cheating_duration_total:.2f} seconds")
print()
