from faster_whisper import WhisperModel

# Load lightweight local Whisper model (downloads once, runs 100% offline)
stt_model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_audio(audio_file_path: str) -> str:
    """Transcribes local audio files to text offline."""
    segments, info = stt_model.transcribe(audio_file_path, beam_size=5)
    full_text = " ".join([segment.text for segment in segments])
    return full_text.strip()