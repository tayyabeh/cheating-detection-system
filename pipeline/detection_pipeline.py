class DetectionPipeline:
    def __init__(self, detectors, frame_skip=2):
        """
        detectors: list of detector objects [FaceDetector(), HandDetector(), EyeDetector()]
        frame_skip: how many frames to skip (2 = process every 2nd frame)
        """
        self.detectors = detectors
        self.frame_skip = frame_skip
        self.frame_counter = 0

    def run(self, frame):
        """Run all detectors on a given frame"""
        self.frame_counter += 1

        # Frame skipping for performance
        if self.frame_counter % self.frame_skip != 0:
            return None  # Skip this frame

        results = {}
        for detector in self.detectors:
            try:
                results[type(detector).__name__] = detector.detect(frame)
            except Exception as e:
                results[type(detector).__name__] = {"error": str(e)}

        return results
