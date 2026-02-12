import requests 
import os
import struct
import numpy as np
from dotenv import load_dotenv
import pvporcupine
from pvrecorder import PvRecorder

# Updated imports to match the 'src' sub-folder structure
from engine.transcriber import AetherTranscriber
from logic.commands import CommandLogic

# Suppress warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["PYTHONWARNINGS"] = "ignore"

# Load API Key
load_dotenv()
PICO_KEY = os.getenv("PICOVOICE_API_KEY")

def send_action_to_team(action, transcript):
    """Sends the command to the unified Bridge Server."""
    # This now talks to the single bridge_server.py you just created
    url = "http://localhost:8000/command"
    data = {"action": action, "text": transcript}
    try:
        requests.post(url, json=data, timeout=0.2)
    except:
        # Hub is likely not running
        pass

def main():
    # 1. Initialize System Components
    logic = CommandLogic()
    transcriber = AetherTranscriber()
    
    # 2. Setup Wake Word - Updated path to match NEWPRJ/src/models/
    model_path = os.path.join(os.path.dirname(__file__), "models", "nova.ppn") 
    
    try:
        keyword_name = "NOVA"
        handle = pvporcupine.create(
            access_key=PICO_KEY, 
            keyword_paths=[model_path],
            sensitivities=[0.7]
        )
    except Exception as e:
        print(f"❌ Error loading wake word model at {model_path}: {e}")
        return

    # 3. Setup Audio Recorder
    recorder = PvRecorder(device_index=-1, frame_length=handle.frame_length)
    
    print(f"\n--- NOVA SURGICAL SYSTEM ACTIVE ---")
    print(f"Connected to Bridge: http://localhost:8000")
    print(f"Say '{keyword_name}'...")

    try:
        recorder.start()
        while True:
            pcm = recorder.read()
            result = handle.process(pcm)
            
            if result >= 0:
                print(f"\n✨ Wake Word Detected!")
                recorder.stop()
                
                # Capture 3 seconds of command audio
                command_frames = []
                temp_recorder = PvRecorder(device_index=-1, frame_length=512)
                temp_recorder.start()
                for _ in range(0, int(16000 / 512 * 3)): 
                    command_frames.extend(temp_recorder.read())
                temp_recorder.stop()
                temp_recorder.delete()
                
                # Process Audio
                audio_np = np.array(command_frames).astype(np.float32) / 32768.0
                text = transcriber.transcribe_audio(audio_np)
                
                if len(text.strip()) < 2:
                    print("🔇 (Silence detected)")
                else:
                    action = logic.get_action(text)
                    print(f"🗣️ Transcribed: '{text}'")
                    print(f"🚀 SYSTEM ACTION: {action}")
                    
                    # Send to the unified Bridge Server
                    send_action_to_team(action, text)
                    print(f"📡 Sent to Bridge!")

                recorder.start()

    except KeyboardInterrupt:
        print("\nStopping Nova System...")
    finally:
        if 'recorder' in locals():
            recorder.stop()
            recorder.delete()
        if 'handle' in locals():
            handle.delete()

if __name__ == "__main__":
    main()