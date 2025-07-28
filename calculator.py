import cv2
import mediapipe as mp
import time
import threading
import math
from playsound import playsound
from button import Button   # your existing class

# ───────── MediaPipe setup ─────────
mp_hands = mp.solutions.hands
hands     = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.85)
mp_draw   = mp.solutions.drawing_utils

# ───────── helper: non‑blocking sound ─────────
def play_click():
    threading.Thread(target=playsound, args=('click.wav',), daemon=True).start()

# ───────── build calculator buttons ─────────
labels = [
    ['7', '8', '9', '/'],
    ['4', '5', '6', '*'],
    ['1', '2', '3', '-'],
    ['C', '0', '=', '+'],
    ['←']
]

button_list = []
start_x, start_y = 50, 200          # top‑left corner of keypad
btn_w = btn_h = 100

for row_i, row in enumerate(labels):
    for col_i, text in enumerate(row):
        x = start_x + col_i * btn_w
        y = start_y + row_i * btn_h
        button_list.append(Button((x, y), btn_w, btn_h, text))

# ───────── state variables ─────────
expression        = ""
last_click_time   = 0
clicking_previous = False            # for state‑change detection

# ───────── camera / window ─────────
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  720)

win_name = "Hand‑Gesture Calculator"
cv2.namedWindow(win_name, cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# ───────── main loop ─────────
while True:
    ok, frame = cap.read()
    if not ok:
        break
    frame = cv2.flip(frame, 1)
    overlay = frame.copy()           # for transparent buttons

    # detect hands
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    # ─── draw buttons on overlay ───
    for b in button_list:
        x, y = b.pos
        cv2.rectangle(overlay, (x, y), (x+btn_w, y+btn_h), (0, 0, 0), cv2.FILLED)
        cv2.putText(overlay, b.text, (x+30, y+65),
                    cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 255, 255), 2)

    # blend overlay for transparency
    frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

    # ─── right‑side expression panel ───
    panel_top_left  = (950, 120)
    panel_bot_right = (1250, 200)
    cv2.rectangle(frame, panel_top_left, panel_bot_right, (0, 0, 0), cv2.FILLED)
    cv2.putText(frame, expression[-20:], (panel_top_left[0]+10, panel_top_left[1]+60),
                cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255), 3)

    # ─── gesture processing ───
    if result.multi_hand_landmarks:
        for hand_lms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)

            h, w, _ = frame.shape
            coords = [(int(lm.x*w), int(lm.y*h)) for lm in hand_lms.landmark]

            # need at least thumb‑tip (4) and index‑tip (8)
            if len(coords) >= 9:
                ix, iy = coords[8]   # index tip
                tx, ty = coords[4]   # thumb tip

                # visual helpers
                cv2.circle(frame, (ix, iy), 8, (255, 0, 0), -1)
                cv2.circle(frame, (tx, ty), 8, (255, 0, 0), -1)
                cv2.line(frame, (ix, iy), (tx, ty), (255, 0, 0), 2)

                touching = math.hypot(ix - tx, iy - ty) < 30
                # state‑change → click
                if touching and not clicking_previous and time.time() - last_click_time > 1:
                    last_click_time = time.time()
                    for b in button_list:
                        if b.is_clicked(ix, iy):
                            val = b.text
                            play_click()

                            if val == 'C':
                                expression = ''
                            elif val == '=':
                                try:
                                    expression = str(eval(expression))
                                except Exception:
                                    expression = 'Error'
                            elif val == '←':
                                expression = expression[:-1]
                            else:
                                expression += val

                            # instant visual feedback
                            cv2.rectangle(frame, b.pos, (b.pos[0]+btn_w, b.pos[1]+btn_h),
                                          (0, 255, 0), cv2.FILLED)
                            cv2.putText(frame, val, (b.pos[0]+30, b.pos[1]+65),
                                        cv2.FONT_HERSHEY_PLAIN, 2.5, (255, 255, 255), 2)
                            break
                clicking_previous = touching

    # ─── display ───
    cv2.imshow(win_name, frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ───────── cleanup ─────────
cap.release()
cv2.destroyAllWindows()
