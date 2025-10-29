"""
Creates earthquake warning sound effects
"""

from pydub import AudioSegment
from pydub.generators import Sine, Square
import os

def create_warning_sound(filename='earthquake_warning.wav', duration_ms=2000):
    """Create an attention-grabbing warning sound"""

    print("Creating earthquake warning sound...")

    # Create alarm-like sound with multiple frequencies
    # Frequency 1: High alert tone (like siren)
    tone1 = Sine(880).to_audio_segment(duration=300)
    tone2 = Sine(1200).to_audio_segment(duration=300)

    # Create alternating siren pattern
    siren = AudioSegment.empty()
    for _ in range(3):
        siren += tone1
        siren += tone2

    # Add some bass rumble (like earthquake rumble)
    rumble = Sine(120).to_audio_segment(duration=duration_ms)
    rumble = rumble - 15  # Make it quieter

    # Combine siren with rumble
    if len(siren) < duration_ms:
        # Extend siren to match duration
        repeats = (duration_ms // len(siren)) + 1
        siren = siren * repeats
        siren = siren[:duration_ms]

    # Overlay rumble on siren
    warning_sound = siren.overlay(rumble)

    # Fade in and out for smoother sound
    warning_sound = warning_sound.fade_in(100).fade_out(200)

    # Export
    warning_sound.export(filename, format='wav')
    print(f"✓ Created warning sound: {filename}")
    print(f"  Duration: {duration_ms}ms")
    print(f"  Format: WAV")

    return filename

def create_simple_beep(filename='earthquake_beep.wav'):
    """Create a simple but loud beep sound (fallback)"""

    print("Creating simple warning beep...")

    # Triple beep pattern
    beep = Sine(1000).to_audio_segment(duration=200)
    silence = AudioSegment.silent(duration=100)

    warning = beep + silence + beep + silence + beep

    # Make it louder
    warning = warning + 5

    warning.export(filename, format='wav')
    print(f"✓ Created warning beep: {filename}")

    return filename

if __name__ == '__main__':
    try:
        # Try to create the complex warning sound
        create_warning_sound()
        create_simple_beep()
        print("\n✓ All warning sounds created successfully!")
        print("\nNote: If you get FFmpeg errors, the app will use system beep instead.")
    except Exception as e:
        print(f"\n⚠ Error creating sounds: {e}")
        print("The app will use system beep as fallback.")
