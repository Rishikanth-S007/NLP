import requests, os, sys, numpy as np
from dotenv import load_dotenv
import pvporcupine
from pvrecorder import PvRecorder
import traceback
import msvcrt

# Ensure Python finds the subfolders
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from engine.transcriber import AetherTranscriber
from logic.commands import CommandLogic

load_dotenv()
PICO_KEY = os.getenv("PICOVOICE_API_KEY")

def send_to_bridge(action, transcript):
    try:
        payload = {
            "action": action, 
            "text": transcript,
            "source": "voice"
        }
        requests.post("http://localhost:8000/command", json=payload, timeout=0.2)
        print(f"📡 Sent to HUD: {action}")
    except: pass

def main():
    if not PICO_KEY:
        print("ERROR: PICOVOICE_API_KEY is missing in .env")
        return

    logic = CommandLogic()
    transcriber = AetherTranscriber()
    model_path = os.path.join(os.path.dirname(__file__), "models", "helix.ppn") 
    
    if not os.path.exists(model_path):
        print(f"ERROR: Model not found at {model_path}")
        return

    try:
        # Reverting to 'NOVA'
        handle = pvporcupine.create(access_key=PICO_KEY, keyword_paths=[model_path], sensitivities=[0.8])
        # handle = pvporcupine.create(access_key=PICO_KEY, keywords=['jarvis'], sensitivities=[0.6])
    except Exception as e:
        print(f"ERROR: Failed to create Porcupine handle: {e}")
        raise

    recorder = PvRecorder(device_index=-1, frame_length=handle.frame_length)
    
    print("\n--- VOICE SYSTEM ACTIVE (Say 'HELIX' or press SPACEBAR) ---")
    print(f"Using Audio Device: {recorder.selected_device}")
    print("Listening... (Volume Bar: | means silent, # means loud)")

    recorder.start()

    try:
        while True:
            pcm = recorder.read()
            
            # --- DEBUG: Audio Level Meter ---
            # Calculate RMS (Root Mean Square) amplitude
            rms = np.sqrt(np.mean(np.array(pcm)**2))
            bar_len = int(rms / 100)
            
            if bar_len > 100:
                print(f"[{'#' * 20}] ⚠️ MAX VOLUME / CLIPPING DETECTED!", end='\r')
            else:
                print(f"[{'#' * bar_len:<20}]", end='\r')
            # --------------------------------

            # Check for Spacebar Manual Trigger
            manual_trigger = False
            if msvcrt.kbhit():
                if msvcrt.getch() == b' ':
                    manual_trigger = True

            if handle.process(pcm) >= 0 or manual_trigger:
                print("\n✨ Wake Word Detected (or Manual Trigger)!")
                recorder.stop()
                
                # Simple 3-second capture
                frames = []
                temp = PvRecorder(device_index=-1, frame_length=512)
                temp.start()
                for _ in range(93): frames.extend(temp.read())
                temp.stop(); temp.delete()
                
                text = transcriber.transcribe_audio(np.array(frames).astype(np.float32) / 32768.0)
                print(f"\n📝 Heard: '{text}'")
                
                if len(text.strip()) > 1:
                    action = logic.get_action(text)
                    print(f"🧠 Logic: {action}")
                    send_to_bridge(action, text)
                else:
                    print("❌ No speech detected.")
                
                recorder.start()
    except KeyboardInterrupt:
        recorder.stop()
    except Exception as e:
        print(f"ERROR inside loop: {e}")
        raise

if __name__ == "__main__":
    try:
        print("Available Audio Devices:")
        for i, device in enumerate(PvRecorder.get_available_devices()):
            print(f"[{i}] {device}")
        main()
    except Exception as e:
        print("CRITICAL ERROR:")
        traceback.print_exc()
        # Keep window open if crashed
        while True:
            pass