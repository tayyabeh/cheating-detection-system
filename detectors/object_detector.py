from .base import BaseDetector
from ultralytics import YOLO
import cv2 
import time


class ObjectDetector(BaseDetector):
    
    model = None
    
    def __init__(self,alert_threshold_seconds = 5,conf_threshold=0.6):
        if ObjectDetector.model is None :
            ObjectDetector.model = YOLO(r'models\yolo11n.pt')
        self.no_person_start_time = None        
        self.no_object_start_time = None
        self.object_present = False
        self.person_count = 0 
        self.alert_threshold_seconds = alert_threshold_seconds
        self.conf_threshold = conf_threshold
        self.cheating_elements = [63,64,65,66,67,73]
        self.person_avaliable = False

    def detect(self , frame):
        results = ObjectDetector.model(frame)
        person_count, object_present,labels = self._process_detections(frame, results)
        status = self._check_alerts(person_count, object_present)
        # Return combined result
        return {
        "person_count": person_count,
        "person_avaliable": status["person_avaliable"],
        "object_present": status["object_present"],
        "label": labels,
        "no_person_start_time": status["no_person_start_time"],
        "no_object_start_time": status["no_object_start_time"],
        "alert_threshold_seconds": self.alert_threshold_seconds,
        "conf_threshold": self.conf_threshold,
        "cheating_elements": self.cheating_elements
        }

    def _process_detections(self,frame, results):
        # Loop YOLO results and update counts, draw boxes
        self.person_count = 0  
        self.object_present = False
        labels = []
        for box in results[0].boxes :
            cls = int(box.cls[0])
            if cls in self.cheating_elements :
                conf = float(box.conf[0])
                # x1,y1,x2,y2 = map(int,box.xyxy[0])            
                if conf > self.conf_threshold :  
                    # cv2.rectangle(frame , (x1, y1), (x2, y2),(0,255,0),2)
                    labels.append(f"{ObjectDetector.model.names[int(cls)]} ({conf:.2f})")
                    # cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            if cls == 0 : 
                self.person_count = self.person_count + 1

            # self.current_time = time.time()

            
            if cls in self.cheating_elements:
                self.object_present = True

        return self.person_count , self.object_present ,labels

    def _check_alerts(self,person_count, object_present):
        # Timer logic for alerts
         # Alert Logic
        current_time = time.time()
        self.person_avaliable = False

        # Person check
        if person_count > 0:
            # At least one person detected
            self.person_avaliable = True
            self.no_person_start_time = None
        else:
            # No person detected
            if self.no_person_start_time is None:
                self.no_person_start_time = current_time
            elif (current_time - self.no_person_start_time) >= self.alert_threshold_seconds:
                # 5 sec se zyada koi banda nahi
                self.person_avaliable = False


        # Object check
        # self.object_present = False
        if object_present:
            if self.no_object_start_time is None:
                self.no_object_start_time = current_time

            elif (current_time - self.no_object_start_time) >= self.alert_threshold_seconds:
                # cv2.putText(frame, "ALERT: Cheating object detected for 5 seconds!", (30, 90),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                self.object_present = True
        else:
            self.no_object_start_time = None    

        return {
        "person_count": person_count,
        "person_avaliable": self.person_avaliable,
        "object_present": self.object_present,
        "no_person_start_time": self.no_person_start_time,
        "no_object_start_time": self.no_object_start_time
    }