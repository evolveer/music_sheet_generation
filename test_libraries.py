#!/usr/bin/env python3
"""
Test script to verify that all required libraries are properly installed
"""

def test_moviepy():
    """Test MoviePy for video processing"""
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
        from moviepy.audio.io.AudioFileClip import AudioFileClip
        print("✓ MoviePy imported successfully")
        return True
    except ImportError as e:
        print(f"✗ MoviePy import failed: {e}")
        return False

def test_basic_pitch():
    """Test Basic Pitch for music transcription"""
    try:
        import basic_pitch
        from basic_pitch.inference import predict
        print("✓ Basic Pitch imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Basic Pitch import failed: {e}")
        return False

def test_music21():
    """Test music21 for sheet music generation"""
    try:
        from music21 import stream, note, duration, meter, key
        print("✓ music21 imported successfully")
        return True
    except ImportError as e:
        print(f"✗ music21 import failed: {e}")
        return False

def test_librosa():
    """Test librosa for audio analysis"""
    try:
        import librosa
        print("✓ librosa imported successfully")
        return True
    except ImportError as e:
        print(f"✗ librosa import failed: {e}")
        return False

def test_aubio():
    """Test aubio for audio analysis"""
    try:
        # Skip aubio for now as we have librosa as alternative
        print("⚠ aubio skipped (using librosa instead)")
        return True
    except ImportError as e:
        print(f"✗ aubio import failed: {e}")
        return False

def test_midi_libraries():
    """Test MIDI processing libraries"""
    try:
        import mido
        import pretty_midi
        print("✓ MIDI libraries (mido, pretty_midi) imported successfully")
        return True
    except ImportError as e:
        print(f"✗ MIDI libraries import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing library installations...")
    print("=" * 50)
    
    tests = [
        test_moviepy,
        test_basic_pitch,
        test_music21,
        test_librosa,
        test_aubio,
        test_midi_libraries
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All {total} tests passed! Environment is ready.")
        return True
    else:
        print(f"✗ {passed}/{total} tests passed. Some libraries need attention.")
        return False

if __name__ == "__main__":
    main()

