import math
import wave
import struct

def generate_arcade_bgm(file_path):
    f = wave.open(file_path, 'w')
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(44100)
    
    # 120 BPM -> 2 beats per second -> 0.5s per beat
    # We want 16th notes -> 4 notes per beat -> 0.125s per note
    note_duration = 0.125
    frames_per_note = int(note_duration * 44100)
    vol = 0.15 # Arcade sounds can be loud, keep volume moderate
    
    # Frequencies for A minor, F Major, C Major, G Major
    # A3=220, C4=261.63, E4=329.63, A4=440
    am = [220.0, 261.63, 329.63, 440.0]
    # F3=174.61, A3=220, C4=261.63, F4=349.23
    fm = [174.61, 220.0, 261.63, 349.23]
    # C3=130.81, E3=164.81, G3=196, C4=261.63
    cm = [130.81, 164.81, 196.0, 261.63]
    # G3=196, B3=246.94, D4=293.66, G4=392
    gm = [196.0, 246.94, 293.66, 392.0]
    
    progression = [am, fm, cm, gm]
    
    data = []
    
    # Repeat the progression 4 times to make a longer loop
    for _ in range(4):
        for chord in progression:
            # Play the chord as an arpeggio (up and down)
            # Pattern: 0 1 2 3 2 1 0 1 (8 notes) -> 1 second per chord
            pattern = [0, 1, 2, 3, 2, 1, 0, 1]
            for p in pattern:
                freq = chord[p]
                
                for i in range(frames_per_note):
                    t = i / 44100.0
                    # Square wave for arcade feel
                    # math.sin(2 * math.pi * freq * t) > 0 -> 1 else -1
                    if math.sin(2 * math.pi * freq * t) > 0:
                        sample = 1.0
                    else:
                        sample = -1.0
                        
                    # Add a very simple envelope (percussive hit)
                    env = max(0, 1.0 - (i / frames_per_note))
                    
                    val = int(vol * env * 32767 * sample)
                    data.append(val)
                    
    f.writeframes(struct.pack('<' + 'h' * len(data), *data))
    f.close()

generate_arcade_bgm('assets/bgm.wav')
print("Energetic arcade BGM generated!")
