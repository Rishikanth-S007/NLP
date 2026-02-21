from faster_whisper import WhisperModel
import numpy as np

class HelixTranscriber:
    def __init__(self, model_size="base.en"):
        # 'base.en' is more accurate than tiny.en but still fast.
        print(f"--- Loading Helix Brain ({model_size}) ---")
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe_audio(self, audio_data):
        """Converts raw audio bytes (as a numpy array) into text."""
        # Transcription starts here
        segments, info = self.model.transcribe(audio_data, beam_size=5)
        
        # Combine all spoken segments into one string
        full_text = " ".join([segment.text for segment in segments])
        return full_text.strip().lower()