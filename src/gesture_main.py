import cv2, requests, time, os
import pyautogui
from engine.gesture_engine import AetherGestureEngine
from logic.gestures import GestureRecognizer

def main():
    engine = AetherGestureEngine()
    recognizer = GestureRecognizer()
    cap = cv2.VideoCapture(0)
    last_stream_time = 0

    print("\n--- GESTURE SYSTEM ACTIVE ---")

    while True:
        success, frame = cap.read()
        if not success: break
        
        frame = cv2.flip(frame, 1)
        lms = engine.process_frame(frame)
        current_action = "IDLE"

        if lms:
            for hand in lms:
                engine.draw_landmarks(frame, hand)
                current_action = recognizer.detect_gesture(hand)
                
                if current_action != "IDLE":
                    try:
                        # Unified Bridge Endpoint
                        payload = {
                            "action": current_action,
                            "text": "",
                            "source": "gesture"
                        }
                        requests.post("http://localhost:8000/command", json=payload, timeout=0.05)
                        
                        # Save screenshot if Capture gesture detected
                        if current_action == "ACTION_CAPTURE":
                            if not os.path.exists("captures"):
                                os.makedirs("captures")
                            timestamp = time.strftime("%H%M%S")
                            filename = f"captures/nova_{timestamp}.jpg"
                            
                            # Taking a system-wide screenshot instead of camera frame
                            pyautogui.screenshot(filename)
                            print(f"📸 Screen captured: {filename}")
                    except Exception as e:
                        print(f"Capture error: {e}")

        cv2.putText(frame, f"HUD ACTION: {current_action}", (20, 40), 2, 0.8, (0,255,0), 2)
        cv2.imshow("Nova Gesture Engine", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()