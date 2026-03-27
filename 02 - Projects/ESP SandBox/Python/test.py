import serial
import numpy as np
import sounddevice as sd

ser = serial.Serial('COM6', 921600)  # CHANGE THIS

def audio_callback(outdata, frames, time, status):
    data = ser.read(frames * 4)
    audio = np.frombuffer(data, dtype=np.int32)

    # Convert to float
    audio = audio.astype(np.float32) / 2147483648.0

    outdata[:] = audio.reshape(-1, 1)

with sd.OutputStream(samplerate=16000, channels=1, blocksize=256, callback=audio_callback):
    print("🎤 LIVE MIC STARTED...")
    while True:
        pass