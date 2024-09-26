import sounddevice as sd
import numpy as np
import whisper
import scipy.io.wavfile as wav

import pyaudio
import wave
import webrtcvad
import time

def record_audio():
    sample_rate = 16000  # Sample rate for webrtcvad
    frame_duration = 30   # Frame duration in ms
    frame_size = int(sample_rate * frame_duration / 1000)  # Frame size in samples

    # Initialize VAD
    vad = webrtcvad.Vad(2)  # Set aggressiveness mode (1 is low, 3 is high)

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open the audio stream
    stream = audio.open(format=pyaudio.paInt16,
                        channels=1,  # Mono audio
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=frame_size)

    frames = []
    is_recording = False
    silence_counter = 0
    silence_threshold = 5  # Number of consecutive silent frames to stop recording

    print("Recording... Speak now!")

    # Allow a short delay before starting the speech detection
    time.sleep(0.5)  # Wait for 1 second before checking for speech

    try:
        while True:
            data = stream.read(frame_size, exception_on_overflow=False)

            # Use VAD to detect speech
            if vad.is_speech(data, sample_rate):
                if not is_recording:
                    print("Speech detected, starting recording...")
                    is_recording = True
                frames.append(data)
                silence_counter = 0  # Reset silence counter when speech is detected
            else:
                if is_recording:
                    silence_counter += 1  # Increment silence counter
                    print("Silence detected...")

                    # Only stop recording after enough silence frames
                    if silence_counter >= silence_threshold:
                        print("Silence confirmed, stopping recording...")
                        break

    except Exception as e:
        print(f"An error occurred: {e}")

    # Close the stream and terminate PyAudio
    stream.stop_stream()
    stream.close()
    audio.terminate()

    if frames:
        # Save the recorded frames as a WAV file
        output_filename = "output.wav"
        with wave.open(output_filename, 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 2 bytes for int16
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))  # Write the audio data

        print(f"Recording saved as {output_filename}")
        return output_filename
    else:
        print("No audio recorded.")
        return None  # Return None if no audio is recorded

# Example usage
if __name__ == "__main__":
    output_file = record_audio()  # Call the function to test
    if output_file:
        print(f"Audio recorded and saved as: {output_file}")
    else:
        print("Recording was not successful.")
        
# Function to convert speech to text using Whisper
def speech_to_text_whisper(audio_file):
    model = whisper.load_model("base")  # Load the Whisper model
    result = model.transcribe(audio_file)  # Transcribe the audio file
    return result['text']  # Return the transcribed text