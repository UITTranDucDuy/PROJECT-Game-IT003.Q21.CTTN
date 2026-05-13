import math
import wave
import struct
import os

def make_sound(file, freq, duration, vol=0.5):
    f = wave.open(file, 'w')
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(44100)
    frames = int(duration * 44100)
    data = [int(vol * 32767 * math.sin(2 * math.pi * freq * (i / 44100.0))) for i in range(frames)]
    f.writeframes(struct.pack('<' + 'h' * len(data), *data))
    f.close()

if not os.path.exists('assets'):
    os.makedirs('assets')

make_sound('assets/click.wav', 880, 0.1)
make_sound('assets/connect.wav', 1320, 0.2)
make_sound('assets/wrong.wav', 220, 0.3)
make_sound('assets/win.wav', 1760, 0.5)

print("Sounds generated successfully!")
