import math
import wave
import struct

def make_chord(file, freqs, duration, vol=0.2):
    f = wave.open(file, 'w')
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(44100)
    frames = int(duration * 44100)
    
    # Generate a slow fading chord
    data = []
    for i in range(frames):
        sample = 0
        t = i / 44100.0
        # Envelope: slow attack and release
        env = math.sin(math.pi * (i / frames))
        
        for freq in freqs:
            sample += math.sin(2 * math.pi * freq * t)
        
        sample = sample / len(freqs)
        val = int(vol * env * 32767 * sample)
        data.append(val)
        
    f.writeframes(struct.pack('<' + 'h' * len(data), *data))
    f.close()

# C Major 7 chord (soft and chill)
make_chord('assets/bgm.wav', [261.63, 329.63, 392.00, 493.88], 8.0, 0.3)
print("BGM generated!")
