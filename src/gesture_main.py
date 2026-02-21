import cv2, requests, time, os
import pyautogui
from engine.gesture_engine import HelixGestureEngine
from logic.gestures import GestureRecognizer

def main():
    engine = HelixGestureEngine()
    recognizer = GestureRecognizer()
    cap = cv2.VideoCapture(0)
    last_stream_time = 0

    last_voice_timestamp = 0
    print("\n--- GESTURE SYSTEM ACTIVE ---")

    while True:
        # 1. Poll Bridge for Voice-Triggered Capture
        try:
            r = requests.get("http://localhost:8000/status", timeout=0.05)
            if r.status_code == 200:
                data = r.json()
                # If voice sent a capture command and we haven't processed it yet
                if data["action"] == "ACTION_CAPTURE" and data["source"] == "voice" and data["timestamp"] > last_voice_timestamp:
                    last_voice_timestamp = data["timestamp"]
                    
                    if not os.path.exists("captures"):
                        os.makedirs("captures")
                    timestamp = time.strftime("%H%M%S")
                    filename = f"captures/helix_{timestamp}.jpg"
                    pyautogui.screenshot(filename)
                    print(f"📸 Voice-Triggered Screen captured: {filename}")
        except: pass

        # 2. Process Camera Frame for Gesture Logic
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
                            filename = f"captures/helix_{timestamp}.jpg"
                            
                            # Taking a system-wide screenshot instead of camera frame
                            pyautogui.screenshot(filename)
                            print(f"📸 Screen captured: {filename}")
                    except Exception as e:
                        print(f"Capture error: {e}")

        cv2.putText(frame, f"HUD ACTION: {current_action}", (20, 40), 2, 0.8, (0,255,0), 2)
        cv2.imshow("Helix Gesture Engine", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()