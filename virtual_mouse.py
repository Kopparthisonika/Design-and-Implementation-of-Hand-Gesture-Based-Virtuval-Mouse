import cv2
import mediapipe as mp
import pyautogui
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils
cam = cv2.VideoCapture(0)
screen_width, screen_height = pyautogui.size()

last_click_time = 0
click_interval = 0.4
clicks = 0

prev_scroll_y = None

while True:
    success, frame = cam.read()
    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmark in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmark, mp_hands.HAND_CONNECTIONS)

            index_tip = hand_landmark.landmark[8]
            middle_tip = hand_landmark.landmark[12]
            thumb_tip = hand_landmark.landmark[4]

            x = int(index_tip.x * frame_width)
            y = int(index_tip.y * frame_height)
            thumb_x = int(thumb_tip.x * frame_width)
            thumb_y = int(thumb_tip.y * frame_height)
            middle_x = int(middle_tip.x * frame_width)
            middle_y = int(middle_tip.y * frame_height)

            screen_x = screen_width * index_tip.x
            screen_y = screen_height * index_tip.y
            pyautogui.moveTo(screen_x, screen_y)

            cv2.circle(frame, (x, y), 10, (0, 255, 255), -1)

            index_thumb_close = abs(x - thumb_x) < 40 and abs(y - thumb_y) < 40
            middle_thumb_close = abs(middle_x - thumb_x) < 40 and abs(middle_y - thumb_y) < 40

            if index_thumb_close and middle_thumb_close:
                print("Double Click Gesture Detected")
                pyautogui.doubleClick()
                time.sleep(1)

            elif index_thumb_close:
                print("Single Click Gesture Detected")
                pyautogui.click()
                time.sleep(1)

            elif middle_thumb_close:
                print("Right Click Gesture Detected")
                pyautogui.rightClick()
                time.sleep(1)

            if abs(index_x := x - middle_x) < 40:
                avg_y = (index_tip.y + middle_tip.y) / 2
                scroll_y = int(avg_y * frame_height)

                if prev_scroll_y is not None:
                    dy = scroll_y - prev_scroll_y
                    if abs(dy) > 5:
                        scroll_speed = int(dy * 3)
                        pyautogui.scroll(-scroll_speed)

                prev_scroll_y = scroll_y
            else:
                prev_scroll_y = None

    cv2.imshow("Virtual Mouse", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cam.release()
cv2.destroyAllWindows()
