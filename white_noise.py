from pydub.generators import WhiteNoise, Pulse
from pydub import AudioSegment
import numpy as np

# Constants -----
filepath = "processed-audio/white-noise-1.wav"
noise_duration = 14000.
pulse_freq = 10.
cross_fade_duration = noise_duration * 0.2
fade_in_duration = 4000
volume_increase_duration = noise_duration * 0.4
# volume_increase_increments = 100.  # Every 100ms, for smoothing
# volume_num = int(np.ceil(volume_increase_duration / volume_increase_increments))
volume_increase = 50.0
# volume_baseline = 0.0  # No change
ending_silence_duration = 1000.
file_format = "wav"

# Create noise -----
white_noise = WhiteNoise().to_audio_segment(duration=noise_duration)

# Make cross-faded pulse -----
halves_plus_cross_fade_duration = (noise_duration + cross_fade_duration) / 2.
# We can't just divide by 2 because we lose time to the cross-fade, hence it's stretched
stretch_ratio = halves_plus_cross_fade_duration / noise_duration
pulse_duration = noise_duration * stretch_ratio  # Doubles as silence duration
pulse = Pulse(freq=pulse_freq).to_audio_segment(duration=pulse_duration)
pulse_silence = AudioSegment.silent(duration=pulse_duration)
silence_to_pulse = pulse_silence.append(pulse, crossfade=cross_fade_duration)

# Combine white noise and pulse -----
noise = white_noise.overlay(silence_to_pulse)

# Increase volume over last portion of the white noise -----
noise_end = white_noise[(noise_duration - volume_increase_duration):]
noise_end = noise_end + volume_increase
noise_end.overlay(silence_to_pulse[noise_duration - volume_increase_duration])
noise = noise.append(noise_end, crossfade=cross_fade_duration)

# Add silence -----
silence_end = AudioSegment.silent(duration=ending_silence_duration)

# Combine and fade in entire audio segment -----
noise = noise.append(silence_end, 0.0)
noise = noise.fade_in(fade_in_duration)

# Save -----
noise.export(filepath, format=file_format)
