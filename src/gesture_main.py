import cv2
import requests
import time
import os
from datetime import datetime
from engine.gesture_engine import AetherGestureEngine
from logic.gestures import GestureRecognizer

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def main():
    engine = AetherGestureEngine()
    recognizer = GestureRecognizer()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not os.path.exists("captures"): 
        os.makedirs("captures")

    last_action = "IDLE"
    last_stream_time = 0
    
    # Define the lists clearly
    TRIGGERS = ["ACTION_RESET", "ACTION_SELECT", "ACTION_CAPTURE", "ACTION_SWIPE_LEFT", "ACTION_SWIPE_RIGHT"]

    print("\n--- NOVA SPATIAL SYSTEM: FULLY SYNCED ---")

    try:
        while True:
            success, frame = cap.read()
            if not success: continue
            
            frame = cv2.flip(frame, 1)
            raw_frame = frame.copy() 
            
            # This is the variable name that caused the error - fixed to match below
            landmarks_list = engine.process_frame(frame)
            current_action = "IDLE"

            if landmarks_list:
                for hand_lms in landmarks_list:
                    engine.draw_landmarks(frame, hand_lms)
                    current_action = recognizer.detect_gesture(hand_lms)

                    if current_action != "IDLE":
                        now = time.time()
                        
                        # 1. TRIGGER LOGIC (Prints to terminal once)
                        if current_action in TRIGGERS:
                            if current_action != last_action:
                                print(f"🎯 TRIGGER: {current_action}")
                                if current_action == "ACTION_CAPTURE":
                                    fn = f"captures/nova_{datetime.now().strftime('%H%M%S')}.jpg"
                                    cv2.imwrite(fn, raw_frame)
                                    print(f"📸 Saved: {fn}")
                                try: 
                                    requests.post("http://localhost:8000/command", 
                                                 json={"action": current_action}, timeout=0.05)
                                except: pass
                        
                        # 2. STREAMING LOGIC (Prints to terminal continuously)
                        else:
                            if now - last_stream_time > 0.1:
                                print(f"🔄 STREAMING: {current_action}")
                                try: 
                                    requests.post("http://localhost:8000/command", 
                                                 json={"action": current_action}, timeout=0.05)
                                except: pass
                                last_stream_time = now

            # HUD Display
            color = (0, 255, 0) if current_action != "IDLE" else (255, 255, 255)
            cv2.putText(frame, f"ACTION: {current_action}", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            cv2.imshow("Nova Gesture Engine", frame)
            
            last_action = current_action
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()