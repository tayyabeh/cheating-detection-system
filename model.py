import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time



model_path = 'face_landmarker.task'

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh


BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode


# Create a face landmarker instance with the live stream mode:
# def print_result(result: FaceLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
#     print('face landmarker result: {}'.format(result))

# def draw_landmarks_on_frame(frame, landmarks):
#     h, w, _ = frame.shape
#     for landmark in landmarks:
#         x = int(landmark.x * w)
#         y = int(landmark.y * h)
#         cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

# def print_result(result: FaceLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
#     global current_frame  # Use global frame to draw on it
#     if result.face_landmarks:
#         for face_landmarks in result.face_landmarks:
#             draw_landmarks_on_frame(current_frame, face_landmarks)


# options = FaceLandmarkerOptions(
#     base_options=BaseOptions(model_asset_path=model_path),
#     running_mode=VisionRunningMode.LIVE_STREAM,
#     num_faces=2, 
#     output_face_blendshapes=True,     
#     result_callback=print_result)


# # Start webcam and process frames
# with FaceLandmarker.create_from_options(options) as landmarker:
#     cap = cv2.VideoCapture(1)
#     if not cap.isOpened():
#         print("Cannot open camera" )
#         exit()
#     while True:
#         # Capture frame-by-frame
#         ret, frame = cap.read()
 
#         # if frame is read correctly ret is True
#         if not ret:
#             print("Can't receive frame (stream end?). Exiting ...")
#             break

#         # current_frame = frame.copy()  # Save frame for drawing

#         # Convert frame to MediaPipe Image
#         mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

#         # Get timestamp
#         timestamp_ms = int(time.time() * 1000)

#         # Run face landmark detection
#         landmarker.detect_async(mp_image, timestamp_ms)

#         # Show frame
#         cv2.imshow("Webcam Feed", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

 
#     # When everything done, release the capture
#     cap.release()
#     cv2.destroyAllWindows()

# For webcam input:
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
cap = cv2.VideoCapture(1)
with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image)

    # Draw the face mesh annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_face_landmarks:
      for face_landmarks in results.multi_face_landmarks:
        mp_drawing.draw_landmarks(
            image=image,
            landmark_list=face_landmarks,
            connections=mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles
            .get_default_face_mesh_tesselation_style())
        mp_drawing.draw_landmarks(
            image=image,
            landmark_list=face_landmarks,
            connections=mp_face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles
            .get_default_face_mesh_contours_style())
        mp_drawing.draw_landmarks(
            image=image,
            landmark_list=face_landmarks,
            connections=mp_face_mesh.FACEMESH_IRISES,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_iris_connections_style())
    # Flip the image horizontally for a selfie-view display.
    cv2.imshow('MediaPipe Face Mesh', cv2.flip(image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()
cv2.destroyAllWindows()