# local main class

import cv2
from detectors.face_detector import FaceDetector  # Adjust this import if path is different

# Initialize your detector
detector = FaceDetector()

# Start video capture
cap = cv2.VideoCapture(0)  # Use 0 for default webcam

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Detect cheating
    result = detector.detect(frame)

    # Draw info
    # info = f"Cheating: {result['cheating']} | Direction: {result['direction']} | Count: {result['cheating_count']} | Duration: {result['cheating_duration']:.2f}s, |  Duration: {result['cheating_duration_total']:.2f}s"
    # cv2.putText(frame, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255) if result["cheating"] else (0, 255, 0), 2)

    # # Show frame
    # cv2.imshow("Cheating Detection", frame)

    # Draw info
    cv2.namedWindow("Cheating Detection", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Cheating Detection", 1200, 800)

    line1 = f"Cheating: {result['cheating']} | Direction: {result['direction']}"
    line2 = f"Count: {result['cheating_count']} | Duration: {result['cheating_duration']:.2f}s"
    line3 = f"Total Duration: {result['cheating_duration_total']:.2f}s"

    color = (0, 0, 255) if result["cheating"] else (0, 255, 0)
    cv2.putText(frame, line1, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.putText(frame, line2, (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.putText(frame, line3, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    # Show frame
    cv2.imshow("Cheating Detection", frame)

    # Break on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
