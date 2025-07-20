#!/usr/bin/env python3
"""
Example Usage Scripts for MP4 to Sheet Music Generator

This file contains various examples showing how to use the different
modules and the main application programmatically.
"""

import os
from pathlib import Path

# Import our modules
from audio_extractor import AudioExtractor
from music_transcriber import MusicTranscriber
from sheet_music_generator import SheetMusicGenerator
from mp4_to_sheet_music import MP4ToSheetMusicConverter


def example_1_basic_conversion():
    """
    Example 1: Basic conversion using the main converter class
    """
    print("Example 1: Basic MP4 to Sheet Music Conversion")
    print("=" * 50)
    
    # Create converter instance
    converter = MP4ToSheetMusicConverter()
    
    # Convert a video file (replace with your actual file)
    video_file = "test_video.mp4"
    
    if os.path.exists(video_file):
        result = converter.convert_mp4_to_sheet_music(
            video_path=video_file,
            output_dir="example1_output",
            title="Example Song",
            keep_intermediate=True
        )
        
        if result['success']:
            print(f"✓ Conversion successful!")
            print(f"Sheet music: {result['sheet_music']}")
        else:
            print(f"✗ Conversion failed: {result.get('error')}")
    else:
        print(f"Video file not found: {video_file}")


def example_2_step_by_step():
    """
    Example 2: Step-by-step conversion using individual modules
    """
    print("\nExample 2: Step-by-Step Conversion")
    print("=" * 50)
    
    video_file = "test_video.mp4"
    
    if not os.path.exists(video_file):
        print(f"Video file not found: {video_file}")
        return
    
    try:
        # Step 1: Extract audio
        print("Step 1: Extracting audio...")
        extractor = AudioExtractor()
        audio_path = extractor.extract_audio_from_video(
            video_file, 
            "example2_audio.wav"
        )
        print(f"✓ Audio extracted: {audio_path}")
        
        # Step 2: Transcribe to MIDI
        print("\nStep 2: Transcribing to MIDI...")
        transcriber = MusicTranscriber()
        
        # Analyze audio first
        features = transcriber.analyze_audio_features(audio_path)
        print(f"Tempo: {features['tempo']:.1f} BPM")
        
        # Transcribe
        midi_path = transcriber.transcribe_audio_to_midi(
            audio_path, 
            "example2_music.mid",
            onset_threshold=0.4,
            frame_threshold=0.2
        )
        print(f"✓ MIDI created: {midi_path}")
        
        # Step 3: Generate sheet music
        print("\nStep 3: Generating sheet music...")
        generator = SheetMusicGenerator()
        
        sheet_path = generator.generate_sheet_music(
            midi_path,
            "example2_sheet.musicxml",
            title="Step-by-Step Example"
        )
        print(f"✓ Sheet music created: {sheet_path}")
        
        # Also create simplified version
        simple_path = generator.create_simple_notation(
            midi_path,
            "example2_simple.musicxml"
        )
        print(f"✓ Simple notation: {simple_path}")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def example_3_audio_analysis():
    """
    Example 3: Detailed audio analysis
    """
    print("\nExample 3: Audio Analysis")
    print("=" * 50)
    
    audio_file = "test_video.wav"
    
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        print("Run example 1 or 2 first to create an audio file")
        return
    
    try:
        transcriber = MusicTranscriber()
        
        # Perform detailed analysis
        print("Analyzing audio features...")
        features = transcriber.analyze_audio_features(audio_file)
        
        print(f"\nAudio Analysis Results:")
        print(f"  - Tempo: {features['tempo']:.1f} BPM")
        print(f"  - Beats detected: {features['num_beats']}")
        print(f"  - Spectral centroid: {features['spectral_centroid_mean']:.1f} Hz")
        print(f"  - RMS energy: {features['rms_energy_mean']:.4f}")
        print(f"  - Zero crossing rate: {features['zero_crossing_rate_mean']:.4f}")
        
        print(f"\nChroma features (pitch classes):")
        chroma_labels = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        for i, value in enumerate(features['chroma_mean']):
            print(f"  - {chroma_labels[i]}: {value:.3f}")
        
        print(f"\nMFCC features (first 5):")
        for i, value in enumerate(features['mfcc_mean'][:5]):
            print(f"  - MFCC {i+1}: {value:.3f}")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def example_4_midi_analysis():
    """
    Example 4: MIDI file analysis
    """
    print("\nExample 4: MIDI Analysis")
    print("=" * 50)
    
    midi_file = "test_video.mid"
    
    if not os.path.exists(midi_file):
        print(f"MIDI file not found: {midi_file}")
        print("Run example 1 or 2 first to create a MIDI file")
        return
    
    try:
        transcriber = MusicTranscriber()
        generator = SheetMusicGenerator()
        
        # Analyze MIDI file
        print("Analyzing MIDI file...")
        midi_info = transcriber.get_midi_info(midi_file)
        
        print(f"\nMIDI Analysis Results:")
        print(f"  - Duration: {midi_info['duration']:.2f} seconds")
        print(f"  - Total notes: {midi_info['total_notes']}")
        print(f"  - Number of instruments: {midi_info['num_instruments']}")
        print(f"  - Estimated tempo: {midi_info['initial_tempo']:.1f} BPM")
        
        print(f"\nInstrument details:")
        for inst in midi_info['instruments']:
            print(f"  - Instrument {inst['index']}: {inst['num_notes']} notes")
            print(f"    Range: {inst['note_range'][0]} - {inst['note_range'][1]}")
            print(f"    MIDI range: {inst['pitch_range'][0]} - {inst['pitch_range'][1]}")
        
        # Load as music21 score for detailed analysis
        print(f"\nLoading as music21 score...")
        score = generator.load_midi_to_music21(midi_file)
        analysis = generator.analyze_musical_content(score)
        
        print(f"Musical Analysis:")
        print(f"  - Key signature: {analysis['key_signature']}")
        print(f"  - Time signature: {analysis['time_signature']}")
        print(f"  - Duration: {analysis['duration_quarters']} quarter notes")
        print(f"  - Number of measures: {analysis['num_measures']}")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def example_5_batch_processing():
    """
    Example 5: Batch processing multiple files
    """
    print("\nExample 5: Batch Processing")
    print("=" * 50)
    
    # Create some test files (in practice, you'd have real video files)
    test_files = ["test_video.mp4"]  # Add more files as needed
    
    # Filter to existing files
    existing_files = [f for f in test_files if os.path.exists(f)]
    
    if not existing_files:
        print("No test files found for batch processing")
        return
    
    try:
        converter = MP4ToSheetMusicConverter()
        
        print(f"Processing {len(existing_files)} files...")
        
        results = converter.batch_convert(
            existing_files,
            output_base_dir="batch_output",
            audio_format="wav",
            sheet_format="musicxml",
            onset_threshold=0.5,
            frame_threshold=0.3,
            keep_intermediate=False
        )
        
        print(f"\nBatch processing completed!")
        successful = sum(1 for r in results if r['success'])
        print(f"Successful conversions: {successful}/{len(results)}")
        
        for i, result in enumerate(results):
            if result['success']:
                print(f"  ✓ File {i+1}: {result['sheet_music']}")
            else:
                print(f"  ✗ File {i+1}: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def example_6_custom_parameters():
    """
    Example 6: Using custom transcription parameters
    """
    print("\nExample 6: Custom Transcription Parameters")
    print("=" * 50)
    
    audio_file = "test_video.wav"
    
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        print("Run example 1 or 2 first to create an audio file")
        return
    
    try:
        transcriber = MusicTranscriber()
        
        # Test different parameter combinations
        parameter_sets = [
            {"onset": 0.3, "frame": 0.2, "name": "High Sensitivity"},
            {"onset": 0.5, "frame": 0.3, "name": "Medium Sensitivity"},
            {"onset": 0.7, "frame": 0.4, "name": "Low Sensitivity"}
        ]
        
        for i, params in enumerate(parameter_sets):
            print(f"\nTesting {params['name']} (onset={params['onset']}, frame={params['frame']})...")
            
            midi_path = f"example6_test_{i+1}.mid"
            
            transcriber.transcribe_audio_to_midi(
                audio_file,
                midi_path,
                onset_threshold=params['onset'],
                frame_threshold=params['frame']
            )
            
            # Analyze results
            midi_info = transcriber.get_midi_info(midi_path)
            print(f"  - Notes detected: {midi_info['total_notes']}")
            print(f"  - Duration: {midi_info['duration']:.2f}s")
        
        print(f"\nParameter comparison completed!")
        print(f"Check the generated MIDI files to compare results.")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def example_7_segment_extraction():
    """
    Example 7: Extract and convert specific segments
    """
    print("\nExample 7: Segment Extraction")
    print("=" * 50)
    
    video_file = "test_video.mp4"
    
    if not os.path.exists(video_file):
        print(f"Video file not found: {video_file}")
        return
    
    try:
        converter = MP4ToSheetMusicConverter()
        
        # Get video info first
        extractor = AudioExtractor()
        audio_info = extractor.get_audio_info(video_file)
        
        print(f"Video duration: {audio_info['duration']:.2f} seconds")
        
        # Extract different segments
        segments = [
            {"start": 0, "end": 2, "name": "Beginning"},
            {"start": 1, "end": 3, "name": "Middle"},
            {"start": 2, "end": 4, "name": "End"}
        ]
        
        for segment in segments:
            if segment["end"] <= audio_info['duration']:
                print(f"\nExtracting {segment['name']} segment ({segment['start']}s - {segment['end']}s)...")
                
                result = converter.convert_audio_segment(
                    video_file,
                    segment["start"],
                    segment["end"],
                    f"example7_{segment['name'].lower()}_output",
                    title=f"{segment['name']} Segment",
                    keep_intermediate=True
                )
                
                if result['success']:
                    print(f"✓ Segment converted: {result['sheet_music']}")
                else:
                    print(f"✗ Segment failed: {result.get('error')}")
            else:
                print(f"Skipping {segment['name']} segment (beyond video duration)")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def main():
    """
    Run all examples
    """
    print("MP4 to Sheet Music Generator - Examples")
    print("=" * 60)
    
    # Check if we have a test video file
    if not os.path.exists("test_video.mp4"):
        print("Creating test video file...")
        os.system('ffmpeg -f lavfi -i "sine=frequency=440:duration=5" -f lavfi -i "color=c=blue:size=320x240:duration=5" -c:v libx264 -c:a aac -shortest test_video.mp4 -y')
    
    # Run examples
    examples = [
        example_1_basic_conversion,
        example_2_step_by_step,
        example_3_audio_analysis,
        example_4_midi_analysis,
        example_5_batch_processing,
        example_6_custom_parameters,
        example_7_segment_extraction
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"Example failed: {str(e)}")
        
        print("\n" + "=" * 60)
    
    print("All examples completed!")


if __name__ == "__main__":
    main()

