# from ultralytics import YOLO
# import cv2 
# import time



# model = YOLO('yolo11s.pt') # class var

# # #LOAD IMAGE 
# # image = cv2.imread(r"E:\Projects\Cheating Detection System\c7.PNG")

# cheating_elements = {
#     0: 'person',
#     63: 'laptop',
#     64: 'mouse',
#     65: 'remote',
#     66: 'keyboard',
#     67: 'cell phone',
#     73: 'book'
# } # class var


# webcam = cv2.VideoCapture(0)

# # Time tracking  
# no_person_start_time = None # intance var
# ALERT_THRESHOLD_SECONDS = 5 # class var
# no_object_start_time = 0 # intance var
# object_present = False # intance var


# while True :
#     success , frame = webcam.read()
#     if not success :
#         print("Can't receive frame (stream end?). Exiting ...")
#         break
#     object_present = False
#     # run detection 
#     results = model(frame)
#     person_count = 0 # intance var

#     # for result in results : 
#     #     boxes = result.boxes
#     #     for box in boxes :
#     #         if int(box.cls[0]) in cheating_elements.keys() : 
#     #             annotated = results[0].plot()
#     for box in results[0].boxes :
#         cls = int(box.cls[0])
#         if cls in cheating_elements.keys() :
#             conf = float(box.conf[0])
#             x1,y1,x2,y2 = map(int,box.xyxy[0])            
#             if conf > 0.6 :  
#                 cv2.rectangle(frame , (x1, y1), (x2, y2),(0,255,0),2)
#                 label = f"{model.names[int(cls)]} ({conf:.2f})"
#                 cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#         if cls == 0 : 
#             person_count = person_count + 1

#         current_time = time.time()

        
#         if cls in [63,64,65,66,67,73]:
#             object_present = True


#     if object_present:
#         if no_object_start_time is None:
#             no_object_start_time = current_time
#         elif (current_time - no_object_start_time) >= ALERT_THRESHOLD_SECONDS:
#             cv2.putText(frame, "ALERT: Cheating object detected for 5 seconds!", (30, 90),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
#     else:
#         no_object_start_time = None

            

#     # Alert Logic
#     current_time = time.time()

#     if person_count == 0:
#         if no_person_start_time is None:
#             no_person_start_time = current_time

#         elif (current_time - no_person_start_time) >= ALERT_THRESHOLD_SECONDS:
#             cv2.putText(frame, "ALERT: No person detected for 5 seconds!",(30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
#     else:
#         no_person_start_time = None  # Reset when person is detected


#     if person_count > 1:
#         cv2.putText(frame, f"ALERT: {person_count} people detected!",(30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


    

#     # annotated = results[0].plot()
#     # # Disply results
#     # cv2.imshow('Detection' , annotated)
#     # print(results[0])

#     # Show the frame
#     cv2.imshow("Cheating Detection", frame)
        


#     key = cv2.waitKey(1) & 0xFF
#     if key == ord('q'):
#         break

# webcam.release()
# cv2.destroyAllWindows()




## Modular code 

from .base import BaseDetector
from ultralytics import YOLO
import cv2 
import time


class ObjectDetector(BaseDetector):
    
    model = None
    
    def __init__(self,alert_threshold_seconds = 5,conf_threshold=0.6):
        if ObjectDetector.model is None :
            ObjectDetector.model = YOLO(r'models\yolo11s.pt')
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