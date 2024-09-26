import sounddevice as sd
import numpy as np
import whisper
import scipy.io.wavfile as wav

# Function to record audio
def record_audio(duration=5, fs=16000):
    print("Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    print("Recording finished.")
    wav.write("audio.wav", fs, audio)  # Save as WAV file
    return "audio.wav"  # Return the file name

# Function to convert speech to text using Whisper
def speech_to_text_whisper(audio_file):
    model = whisper.load_model("base")  # Load the Whisper model
    result = model.transcribe(audio_file)  # Transcribe the audio file
    return result['text']  # Return the transcribed text