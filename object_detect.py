from ultralytics import YOLO
import cv2 
import time



model = YOLO('yolo11s.pt')

# #LOAD IMAGE 
# image = cv2.imread(r"E:\Projects\Cheating Detection System\c7.PNG")

cheating_elements = {
    0: 'person',
    63: 'laptop',
    64: 'mouse',
    65: 'remote',
    66: 'keyboard',
    67: 'cell phone',
    73: 'book'
}


webcam = cv2.VideoCapture(0)

# Time tracking
no_person_start_time = None
ALERT_THRESHOLD_SECONDS = 5
no_object_start_time = 0
# object_present = False


while True :
    success , frame = webcam.read()
    if not success :
        print("Can't receive frame (stream end?). Exiting ...")
        break
    object_present = False
    # run detection 
    results = model(frame)
    person_count = 0 

    # for result in results : 
    #     boxes = result.boxes
    #     for box in boxes :
    #         if int(box.cls[0]) in cheating_elements.keys() : 
    #             annotated = results[0].plot()
    for box in results[0].boxes :
        cls = int(box.cls[0])
        if cls in cheating_elements.keys() :
            conf = float(box.conf[0])
            x1,y1,x2,y2 = map(int,box.xyxy[0])            
            if conf > 0.6 :  
                cv2.rectangle(frame , (x1, y1), (x2, y2),(0,255,0),2)
                label = f"{model.names[int(cls)]} ({conf:.2f})"
                cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        if cls == 0 : 
            person_count = person_count + 1

        current_time = time.time()

        
        if cls in [63,64,65,66,67,73]:
            object_present = True


    if object_present:
        if no_object_start_time is None:
            no_object_start_time = current_time
        elif (current_time - no_object_start_time) >= ALERT_THRESHOLD_SECONDS:
            cv2.putText(frame, "ALERT: Cheating object detected for 5 seconds!", (30, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        no_object_start_time = None

            

    # Alert Logic
    current_time = time.time()

    if person_count == 0:
        if no_person_start_time is None:
            no_person_start_time = current_time

        elif (current_time - no_person_start_time) >= ALERT_THRESHOLD_SECONDS:
            cv2.putText(frame, "ALERT: No person detected for 5 seconds!",(30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        no_person_start_time = None  # Reset when person is detected


    if person_count > 1:
        cv2.putText(frame, f"ALERT: {person_count} people detected!",(30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


    

    # annotated = results[0].plot()
    # # Disply results
    # cv2.imshow('Detection' , annotated)
    # print(results[0])

    # Show the frame
    cv2.imshow("Cheating Detection", frame)
        


    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

webcam.release()
cv2.destroyAllWindows()




