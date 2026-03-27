import serial
import numpy as np
import sounddevice as sd

ser = serial.Serial('COM6', 921600)  # CHANGE THIS

def audio_callback(outdata, frames, time, status):
    data = ser.read(frames * 2)

    audio = np.frombuffer(data, dtype=np.int16)

    # remove DC offset (BIG improvement)
    audio = audio - np.mean(audio)

    # normalize
    audio = audio.astype(np.float32) / 32768.0

    outdata[:] = audio.reshape(-1, 1)

with sd.OutputStream(samplerate=8000, channels=1, blocksize=128, callback=audio_callback):
    print("🎤 LIVE MIC STARTED...")
    while True:
        pass