from faster_whisper import WhisperModel
import numpy as np

class AetherTranscriber:
    def __init__(self, model_size="tiny.en"):
        # 'tiny.en' is chosen for speed. 'int8' makes it run fast on any CPU.
        print(f"--- Loading Aether Brain ({model_size}) ---")
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe_audio(self, audio_data):
        """Converts raw audio bytes (as a numpy array) into text."""
        # Transcription starts here
        segments, info = self.model.transcribe(audio_data, beam_size=5)
        
        # Combine all spoken segments into one string
        full_text = " ".join([segment.text for segment in segments])
        return full_text.strip().lower()