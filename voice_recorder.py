import sounddevice as sd
import scipy.io.wavfile as wav
import whisper
import numpy as np
import tempfile

# Function to detect silence
def is_silence(data, threshold=0.01):
    return np.abs(data).mean() < threshold

def record_audio(fs=44100, silence_threshold=0.01, silence_duration=1):
    silence_count = 0
    audio_data = []

    print("Recording... Press 'Stop' to finish.")

    # Open an input stream and listen for silence
    with sd.InputStream(samplerate=fs, channels=1) as stream:
        while True:
            # Record in chunks (buffer size)
            chunk = stream.read(int(fs * 0.2))  # 200ms chunks
            audio_chunk = chunk[0]  # Extract audio data

            audio_data.append(audio_chunk)

            # Check for silence
            if is_silence(audio_chunk, silence_threshold):
                silence_count += 0.2
            else:
                silence_count = 0  # Reset silence counter when sound is detected

            # Stop after a certain duration of silence
            if silence_count > silence_duration:
                break

    # Convert the list to a numpy array
    audio_data = np.concatenate(audio_data)

    # Save the audio data to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav_file:
        wav.write(tmp_wav_file.name, fs, audio_data)
        print(f"Recording saved: {tmp_wav_file.name}")
        return tmp_wav_file.name  # Return path to temp audio file

# Function to transcribe audio to text using Whisper
def speech_to_text_whisper(audio_file):
    model = whisper.load_model("base")  # Load the whisper model (use a smaller model if needed)
    result = model.transcribe(audio_file)
    return result['text']  # Return the transcribed text