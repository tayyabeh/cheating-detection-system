import cv2
from detectors.face_detector import FaceDetector
from detectors.object_detector import ObjectDetector
from detectors.gaze_detector import GazeDetector
from pipeline.detection_pipeline import DetectionPipeline

def run_app():
    # Initialize detectors
    face_detector = FaceDetector()
    object_detector = ObjectDetector()
    gaze_detector = GazeDetector()

    # Create pipeline
    pipeline = DetectionPipeline(
        detectors=[face_detector, object_detector, gaze_detector],
        frame_skip=3  # Process every 3rd frame
    )

    # Open camera
    cap = cv2.VideoCapture(1)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        output = pipeline.run(frame)
        if output:
            print(output)  # Or display results on frame

        cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
