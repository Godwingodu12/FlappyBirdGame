import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Create a sound
def create_placeholder_sound(filename):
    sample_rate = 44100  # Sample rate
    duration = 1.0  # Duration in seconds
    frequency = 440  # Frequency of the beep (A4 note)

    # Generate the sound wave
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    sound_wave = 0.5 * np.sin(2 * np.pi * frequency * t)

    # Convert to 16-bit signed integers
    sound_wave = np.int16(sound_wave * 32767)

    # Save as a WAV file
    # Use the wave module to save the sound
    import wave
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono sound
        wf.setsampwidth(2)  # 2 bytes for 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(sound_wave.tobytes())

# Call the function to create the placeholder sound
create_placeholder_sound('sfx_boost.wav')

# Quit Pygame
pygame.quit()
