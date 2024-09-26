import sounddevice as sd
import numpy as np
import whisper
import scipy.io.wavfile as wav

import pyaudio
import wave
import webrtcvad

def record_audio():
    sample_rate = 16000  # Sample rate for webrtcvad
    frame_duration = 30   # Frame duration in ms
    frame_size = int(sample_rate * frame_duration / 1000)  # Frame size in samples

    vad = webrtcvad.Vad(0)  # Set aggressiveness mode (1 is low, 3 is high)
    audio = pyaudio.PyAudio()

    stream = audio.open(format=pyaudio.paInt16,
                        channels=1,  # Mono audio
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=frame_size)

    frames = []
    is_recording = False

    print("Recording... Speak now!")

    while True:
        data = stream.read(frame_size, exception_on_overflow=False)

        # Use VAD to detect speech
        if vad.is_speech(data, sample_rate):
            if not is_recording:
                print("Speech detected, starting recording...")
                is_recording = True
            frames.append(data)
        else:
            if is_recording:
                print("Silence detected, stopping recording...")
                break

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded frames as a WAV file
    output_filename = "output.wav"
    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 2 bytes for int16
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))  # Write the audio data

    print(f"Recording saved as {output_filename}")
    
    return output_filename  # Return the output filename

# Function to convert speech to text using Whisper
def speech_to_text_whisper(audio_file):
    model = whisper.load_model("base")  # Load the Whisper model
    result = model.transcribe(audio_file)  # Transcribe the audio file
    return result['text']  # Return the transcribed text