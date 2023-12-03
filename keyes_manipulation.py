import librosa
import pyrubberband
import soundfile as sf
from pydub import AudioSegment
import numpy as np


def process_audio(sound, start, stop, octave_value):
    sound_chunk = sound[start:stop]
    sound_shifted = pitch_shift(sound_chunk, octave_value)
    return sound_shifted


def pitch_shift(sound, n_steps):
    sound_buffer = np.frombuffer(sound._data, dtype=np.int16).astype(np.float32)/2**15
    sound_buffer = librosa.effects.pitch_shift(sound_buffer, sr=sound.frame_rate, n_steps=n_steps)
    sound_segment = AudioSegment(np.array(sound_buffer * (1 << 15),
                                          dtype=np.int16).tobytes(),
                                 frame_rate=sound.frame_rate,
                                 sample_width=2,
                                 channels=1)
    return sound_segment


# First slow down the song
filepath = "raw-audio/keyes.mp3"
filepath_stretched = "processed-audio/keyes-processed.wav"
sound, sample_rate = librosa.load(filepath, sr=None)
slowdown = 0.55
sound_stretched = pyrubberband.time_stretch(sound, sample_rate, slowdown)
sf.write(filepath_stretched, sound_stretched, sample_rate, format="wav")

# Then add pitch modulation to the song
sound = AudioSegment.from_file(filepath_stretched, format="wav")
song_length = len(sound)
spacing = 10
song_chunks = np.linspace(0, song_length, spacing)
starts = song_chunks[0:-1]
ends = song_chunks[1:]
possible_octaves = [0, -1, -2, -3, -4, -5, -4, -3, -2, -1, 0., 1, 2, 3, 4, 5, 4, 3, 2, 1]
reps = int(np.ceil(len(ends) / len(possible_octaves)))
octaves = possible_octaves * reps
octaves = octaves[0:len(ends)]
sound_pitch_shifted = process_audio(sound, starts[0], ends[0], octaves[0])
for i in range(1, len(starts)):
    next_sound_pitch_shifted = process_audio(sound, starts[i], ends[i], octaves[i])
    sound_pitch_shifted = sound_pitch_shifted.append(next_sound_pitch_shifted)
sound_pitch_shifted.export(filepath_stretched, format="wav")