import cv2
import pyttsx3
import threading
import time
import numpy as np
from scipy.spatial import distance
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import mediapipe as mp

# Text-to-Speech setup
engine = pyttsx3.init()

# MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)

# Camera setup
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FPS, 30)

# EAR & MAR calculation
def get_EAR(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def get_MAR(mouth):
    A = distance.euclidean(mouth[3], mouth[7])
    B = distance.euclidean(mouth[2], mouth[6])
    C = distance.euclidean(mouth[0], mouth[4])
    return (A + B) / (2.0 * C)

# Alert function
def alert_loop():
    while alarm_on_flag[0]:
        engine.say("Alert! Wake up!")
        engine.runAndWait()
        time.sleep(1.5)

# State variables
COUNTER = 0
ALARM_FRAME_THRESHOLD = 15
alarm_on_flag = [False]
alarm_thread = None

# Indexes for face landmarks from MediaPipe
LEFT_EYE_IDX = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_IDX = [33, 160, 158, 133, 153, 144]
MOUTH_IDX = [78, 81, 13, 311, 308, 402, 14, 178]  # Approximate inner mouth

# Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        print("Không lấy được khung hình.")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w, _ = frame.shape

            # Extract eye landmarks
            leftEye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in LEFT_EYE_IDX]
            rightEye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in RIGHT_EYE_IDX]
            mouth = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in MOUTH_IDX]

            cv2.polylines(frame, [np.array(leftEye)], True, (255, 255, 0), 1)
            cv2.polylines(frame, [np.array(rightEye)], True, (0, 255, 0), 1)
            cv2.polylines(frame, [np.array(mouth)], True, (0, 0, 255), 1)

            EAR = round((get_EAR(leftEye) + get_EAR(rightEye)) / 2.0, 2)
            MAR = round(get_MAR(mouth), 2)

            drowsy_detected = False

            # Buồn ngủ
            if EAR < 0.25:
                COUNTER += 1
                if COUNTER >= ALARM_FRAME_THRESHOLD:
                    cv2.putText(frame, "DROWSINESS DETECTED", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    drowsy_detected = True
            else:
                COUNTER = 0

            # Ngáp
            if MAR > 0.6:
                cv2.putText(frame, "YAWNING DETECTED", (50, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                drowsy_detected = True

            # Cảnh báo
            if drowsy_detected and not alarm_on_flag[0]:
                alarm_on_flag[0] = True
                alarm_thread = threading.Thread(target=alert_loop)
                alarm_thread.daemon = True
                alarm_thread.start()
            elif not drowsy_detected:
                alarm_on_flag[0] = False

    cv2.imshow("Driver Monitor (MediaPipe)", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        alarm_on_flag[0] = False
        break

cap.release()
cv2.destroyAllWindows()
