import cv2
import mediapipe as mp
import threading
import os
from gtts import gTTS
import pygame

mpHands = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils
hands = mpHands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

is_speaking = False

def speak(text):
    def _play():
        global is_speaking
        if is_speaking:
            return
        is_speaking = True
        try:
            tts = gTTS(text=text, lang='id')
            file = "voice.mp3"
            tts.save(file)

            pygame.mixer.init()
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pass
            pygame.mixer.quit()
            os.remove(file)
        except Exception as e:
            print("Error suara:", e)
        is_speaking = False

    threading.Thread(target=_play, daemon=True).start()

def count_fingers(hand_landmarks):
    tipIds = [4, 8, 12, 16, 20]
    fingers = []

    if hand_landmarks.landmark[tipIds[0]].x < hand_landmarks.landmark[tipIds[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    for id in range(1, 5):
        if hand_landmarks.landmark[tipIds[id]].y < hand_landmarks.landmark[tipIds[id] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers.count(1)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

prev_gesture = None

while True:
    success, img = cap.read()
    if not success:
        break
    img = cv2.flip(img, 1)  
    results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    gesture_text = ""

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            finger_count = count_fingers(handLms)

            if finger_count == 1:
                gesture_text = "Halo!"
                if prev_gesture != gesture_text:
                    speak("Halo")
            elif finger_count == 2:
                gesture_text = "Perkenalkan, nama saya Fazril."
                if prev_gesture != gesture_text:
                    speak("Perkenalkan, nama saya Fazril.")
            elif finger_count == 3:
                gesture_text = "Terima kasih!"
                if prev_gesture != gesture_text:
                    speak("Terima kasih!")
            elif finger_count == 5:
                gesture_text = "Senang bertemu denganmu!"
                if prev_gesture != gesture_text:
                    speak("Senang bertemu denganmu!")

            prev_gesture = gesture_text

    cv2.putText(img, gesture_text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    cv2.imshow("Hand Gesture Voice - Fazril", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
