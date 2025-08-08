import cv2
from detectors.face_detector import FaceDetector
from detectors.object_detector import ObjectDetector

class CombinedDetector:
    def __init__(self):
        self.face_detector = FaceDetector()
        self.object_detector = ObjectDetector()
        self.all_labels = []  # Persistent labels for whole session

    def detect(self, frame):
        result_face = {}
        result_object = {}

        # Face detector try
        try:
            result_face = self.face_detector.detect(frame)
        except Exception as e:
            print(f"⚠ FaceDetector error: {e}")

        # Object detector try
        try:
            result_object = self.object_detector.detect(frame)
            # Persistent label logic
            if result_object.get("label"):
                for lbl in result_object["label"]:
                    if lbl not in self.all_labels:
                        self.all_labels.append(lbl)
        except Exception as e:
            print(f"⚠ ObjectDetector error: {e}")

        # Merge results
        return {
            "face": result_face,
            "object": result_object,
            "session_labels": self.all_labels
        }


# --- MAIN LOOP ---
cap = cv2.VideoCapture(0)
detector = CombinedDetector()

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    results = detector.detect(frame)

    # Window setup
    cv2.namedWindow("Detection", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Detection", 1200, 800)

    # Face detector info
    if results["face"]:
        f = results["face"]
        line1 = f"Cheating: {f.get('cheating')} | Direction: {f.get('direction')}"
        line2 = f"Count: {f.get('cheating_count')} | Duration: {f.get('cheating_duration', 0):.2f}s"
    else:
        line1 = "FaceDetector: No data"
        line2 = ""

    # Object detector info
    if results["object"]:
        o = results["object"]
        line3 = f"Persons: {o.get('person_count')} | Person Available: {o.get('person_avaliable')}"
        line4 = f"Object Present: {o.get('object_present')}"
    else:
        line3 = "ObjectDetector: No data"
        line4 = ""

    # Session labels
    line5 = f"Session Labels: {', '.join(results['session_labels']) if results['session_labels'] else 'None'}"

    # Draw text
    color = (0, 0, 255) if (results["object"].get("object_present") or results["face"].get("cheating")) else (0, 255, 0)
    y = 30
    for line in [line1, line2, line3, line4, line5]:
        cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        y += 35

    # Show frame
    cv2.imshow("Detection", frame)

    # Exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
