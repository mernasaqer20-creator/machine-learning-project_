import cv2
import mediapipe as mp
import math
import serial
import time

# الاتصال بالأردوينو (غيّر COM3 حسب جهازك)
arduino = serial.Serial('COM3', 9600)
time.sleep(2)

# إعداد Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# الكاميرا
cap = cv2.VideoCapture(0)

def calculate_distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # نقاط الإبهام والسبابة
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]

            # تحويل الإحداثيات إلى بكسلات
            h, w, _ = frame.shape
            x1, y1 = int(thumb_tip.x * w), int(thumb_tip.y * h)
            x2, y2 = int(index_tip.x * w), int(index_tip.y * h)

            # رسم خط ودائرة
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.circle(frame, (x1, y1), 5, (0, 255, 0), -1)
            cv2.circle(frame, (x2, y2), 5, (0, 255, 0), -1)

            # حساب المسافة
            distance = calculate_distance(x1, y1, x2, y2)

            # تحويل المسافة إلى قيمة PWM (0 - 255)
            # نحدد مدى منطقي مثلاً: المسافة بين 30 إلى 200 بكسل
            pwm_value = int((distance - 30) / (200 - 30) * 255)
            pwm_value = max(0, min(pwm_value, 255))  # تقييد القيمة بين 0 و 255

            # إرسال القيمة للأردوينو
            arduino.write(f"{pwm_value}\n".encode())

            # عرض المسافة على الشاشة
            cv2.putText(frame, f'Distance: {int(distance)}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2)
            cv2.putText(frame, f'PWM: {pwm_value}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2)

    cv2.imshow("التحكم في اضاءة LED باليد", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()
