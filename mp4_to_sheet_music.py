#!/usr/bin/env python3
"""
MP4 to Sheet Music Generator

A complete solution for generating sheet music from MP4 video files.
This application integrates audio extraction, music transcription, and 
sheet music generation into a single workflow.

Author: Music Sheet Generator
Version: 1.0.0
"""

import os
import sys
import argparse
import time
from pathlib import Path

# Import our custom modules
from audio_extractor import AudioExtractor
from music_transcriber_fixed import MusicTranscriber
from sheet_music_generator import SheetMusicGenerator


class MP4ToSheetMusicConverter:
    """
    Main class that orchestrates the complete conversion pipeline
    Supports both video files (MP4, AVI, MOV, etc.) and audio files (MP3, WAV, FLAC, etc.)
    """
    
    def __init__(self):
        """Initialize the converter with all required modules"""
        self.audio_extractor = AudioExtractor()
        self.music_transcriber = MusicTranscriber()
        self.sheet_generator = SheetMusicGenerator()
        
        # Supported file formats
        self.video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
        self.audio_formats = ['.wav', '.mp3', '.flac', '.aac', '.m4a', '.ogg', '.wma']
        
        # Temporary file tracking for cleanup
        self.temp_files = []
    
    def detect_file_type(self, file_path):
        """
        Detect whether the input file is a video or audio file
        
        Args:
            file_path (str): Path to the input file
            
        Returns:
            str: 'video', 'audio', or 'unknown'
        """
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension in self.video_formats:
            return 'video'
        elif file_extension in self.audio_formats:
            return 'audio'
        else:
            return 'unknown'
    
    def convert_to_sheet_music(self, input_path, output_dir=None, 
                             audio_format='wav', sheet_format='musicxml',
                             onset_threshold=0.5, frame_threshold=0.3,
                             title=None, keep_intermediate=False):
        """
        Complete pipeline: Video/Audio -> Audio -> MIDI -> Sheet Music
        
        Args:
            input_path (str): Path to the input file (video or audio)
            output_dir (str, optional): Output directory for all files
            audio_format (str): Audio format for extraction ('wav', 'mp3')
            sheet_format (str): Sheet music format ('musicxml', 'png', 'pdf')
            onset_threshold (float): Note onset detection threshold
            frame_threshold (float): Note frame detection threshold
            title (str, optional): Title for the sheet music
            keep_intermediate (bool): Whether to keep intermediate files
            
        Returns:
            dict: Paths to all generated files
        """
        
        start_time = time.time()
        
        try:
            # Detect file type
            file_type = self.detect_file_type(input_path)
            
            print("=" * 60)
            print("MUSIC TO SHEET MUSIC CONVERTER")
            print("=" * 60)
            print(f"Input file: {input_path}")
            print(f"File type: {file_type.upper()}")
            print(f"Audio format: {audio_format}")
            print(f"Sheet format: {sheet_format}")
            print(f"Onset threshold: {onset_threshold}")
            print(f"Frame threshold: {frame_threshold}")
            print()
            
            if file_type == 'unknown':
                raise ValueError(f"Unsupported file format: {Path(input_path).suffix}")
            
            # Setup output directory
            if output_dir is None:
                output_dir = Path(input_path).parent / f"{Path(input_path).stem}_output"
            
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # File paths
            input_stem = Path(input_path).stem
            midi_path = output_dir / f"{input_stem}.mid"
            sheet_path = output_dir / f"{input_stem}_sheet.{sheet_format}"
            
            results = {
                'input_file': str(input_path),
                'file_type': file_type,
                'output_directory': str(output_dir),
                'audio_file': None,
                'midi_file': None,
                'sheet_music': None,
                'processing_time': 0,
                'success': False
            }
            
            # Step 1: Handle audio extraction/preparation
            if file_type == 'video':
                print("STEP 1: EXTRACTING AUDIO FROM VIDEO")
                print("-" * 40)
                
                audio_info = self.audio_extractor.get_audio_info(input_path)
                if not audio_info["has_audio"]:
                    raise ValueError("Video file contains no audio track")
                
                print(f"Video audio info:")
                print(f"  - Duration: {audio_info['duration']:.2f} seconds")
                print(f"  - Sample rate: {audio_info['sample_rate']} Hz")
                print(f"  - Channels: {audio_info['channels']}")
                print()
                
                audio_path = output_dir / f"{input_stem}.{audio_format}"
                extracted_audio = self.audio_extractor.extract_audio_from_video(
                    input_path, str(audio_path), audio_format
                )
                results['audio_file'] = extracted_audio
                if not keep_intermediate:
                    self.temp_files.append(extracted_audio)
                
                print(f"✓ Audio extraction completed: {extracted_audio}")
                print()
                
            elif file_type == 'audio':
                print("STEP 1: USING DIRECT AUDIO INPUT")
                print("-" * 40)
                
                # Check if the audio file is in the desired format
                input_format = Path(input_path).suffix.lower().lstrip('.')
                
                if input_format == audio_format:
                    # Use the file directly
                    extracted_audio = str(input_path)
                    print(f"Using audio file directly: {extracted_audio}")
                else:
                    # Convert to desired format if needed
                    audio_path = output_dir / f"{input_stem}.{audio_format}"
                    print(f"Converting audio format from {input_format} to {audio_format}...")
                    
                    # Use librosa to load and save in the desired format
                    import librosa
                    import soundfile as sf
                    
                    audio_data, sr = librosa.load(input_path, sr=None)
                    sf.write(str(audio_path), audio_data, sr)
                    
                    extracted_audio = str(audio_path)
                    if not keep_intermediate:
                        self.temp_files.append(extracted_audio)
                
                results['audio_file'] = extracted_audio
                
                # Get audio info for display
                try:
                    import librosa
                    audio_data, sr = librosa.load(extracted_audio, sr=None)
                    duration = len(audio_data) / sr
                    
                    print(f"Audio file info:")
                    print(f"  - Duration: {duration:.2f} seconds")
                    print(f"  - Sample rate: {sr} Hz")
                    print(f"  - Channels: {1 if len(audio_data.shape) == 1 else audio_data.shape[1]}")
                except Exception as e:
                    print(f"  - Could not analyze audio: {str(e)}")
                
                print(f"✓ Audio preparation completed: {extracted_audio}")
                print()
            
            # Step 2: Transcribe audio to MIDI
            print("STEP 2: TRANSCRIBING AUDIO TO MIDI")
            print("-" * 40)
            
            # Analyze audio features first
            features = self.music_transcriber.analyze_audio_features(extracted_audio)
            print(f"Audio analysis:")
            print(f"  - Estimated tempo: {features['tempo']:.1f} BPM")
            print(f"  - Spectral centroid: {features['spectral_centroid_mean']:.1f} Hz")
            print(f"  - RMS energy: {features['rms_energy_mean']:.4f}")
            print()
            
            # Perform transcription
            transcribed_midi = self.music_transcriber.transcribe_audio_to_midi(
                extracted_audio, str(midi_path), onset_threshold, frame_threshold
            )
            results['midi_file'] = transcribed_midi
            if not keep_intermediate:
                self.temp_files.append(transcribed_midi)
            
            # Get MIDI info
            midi_info = self.music_transcriber.get_midi_info(transcribed_midi)
            print(f"MIDI transcription results:")
            print(f"  - Total notes: {midi_info['total_notes']}")
            print(f"  - Duration: {midi_info['duration']:.2f} seconds")
            print(f"  - Instruments: {midi_info['num_instruments']}")
            print()
            
            # Step 3: Generate sheet music
            print("STEP 3: GENERATING SHEET MUSIC")
            print("-" * 40)
            
            # Set title if not provided
            if title is None:
                title = f"Transcribed from {Path(input_path).name}"
            
            generated_sheet = self.sheet_generator.generate_sheet_music(
                transcribed_midi, str(sheet_path), sheet_format, title
            )
            results['sheet_music'] = generated_sheet
            
            # Also generate a simplified version
            simple_sheet_path = output_dir / f"{input_stem}_simple.musicxml"
            simple_sheet = self.sheet_generator.create_simple_notation(
                transcribed_midi, str(simple_sheet_path)
            )
            results['simple_sheet_music'] = str(simple_sheet)
            
            print()
            
            # Calculate processing time
            end_time = time.time()
            processing_time = end_time - start_time
            results['processing_time'] = processing_time
            results['success'] = True
            
            # Summary
            print("CONVERSION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"Processing time: {processing_time:.2f} seconds")
            print(f"Output directory: {output_dir}")
            print(f"Generated files:")
            if results['audio_file'] != str(input_path):  # Only show if we created a new audio file
                print(f"  - Audio: {results['audio_file']}")
            print(f"  - MIDI: {results['midi_file']}")
            print(f"  - Sheet music: {results['sheet_music']}")
            print(f"  - Simple notation: {results['simple_sheet_music']}")
            print()
            
            if not keep_intermediate:
                print("Cleaning up intermediate files...")
                self.cleanup_temp_files()
                print("✓ Cleanup completed")
            
            return results
            
        except Exception as e:
            print(f"\n✗ CONVERSION FAILED: {str(e)}")
            
            # Cleanup on failure
            if not keep_intermediate:
                self.cleanup_temp_files()
            
            results['success'] = False
            results['error'] = str(e)
            return results
    
    def convert_mp4_to_sheet_music(self, video_path, output_dir=None, **kwargs):
        """
        Backward compatibility method for video files
        
        Args:
            video_path (str): Path to the input video file
            output_dir (str, optional): Output directory
            **kwargs: Additional arguments for conversion
            
        Returns:
            dict: Conversion results
        """
        return self.convert_to_sheet_music(video_path, output_dir, **kwargs)
    
    def convert_audio_segment(self, input_path, start_time, end_time, 
                            output_dir=None, **kwargs):
        """
        Convert a specific segment of a video/audio file to sheet music
        
        Args:
            input_path (str): Path to the input file (video or audio)
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            output_dir (str, optional): Output directory
            **kwargs: Additional arguments for conversion
            
        Returns:
            dict: Conversion results
        """
        
        try:
            file_type = self.detect_file_type(input_path)
            print(f"Converting {file_type} segment: {start_time}s - {end_time}s")
            
            # Setup output directory
            if output_dir is None:
                output_dir = Path(input_path).parent / f"{Path(input_path).stem}_segment_{start_time}_{end_time}"
            
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract segment based on file type
            input_stem = Path(input_path).stem
            
            if file_type == 'video':
                # Extract audio segment from video
                audio_path = output_dir / f"{input_stem}_segment.wav"
                extracted_audio = self.audio_extractor.extract_audio_segment(
                    input_path, start_time, end_time, str(audio_path)
                )
            elif file_type == 'audio':
                # Extract audio segment from audio file
                import librosa
                import soundfile as sf
                
                # Load the full audio file
                audio_data, sr = librosa.load(input_path, sr=None)
                
                # Calculate sample indices
                start_sample = int(start_time * sr)
                end_sample = int(end_time * sr)
                
                # Extract segment
                segment_data = audio_data[start_sample:end_sample]
                
                # Save segment
                audio_path = output_dir / f"{input_stem}_segment.wav"
                sf.write(str(audio_path), segment_data, sr)
                extracted_audio = str(audio_path)
                
                print(f"✓ Audio segment extracted: {extracted_audio}")
            else:
                raise ValueError(f"Unsupported file format: {Path(input_path).suffix}")
            
            # Continue with normal conversion pipeline using the extracted segment
            return self.convert_to_sheet_music(
                extracted_audio, output_dir, **kwargs
            )
            
        except Exception as e:
            print(f"✗ Segment conversion failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def batch_convert(self, input_files, output_base_dir=None, **kwargs):
        """
        Convert multiple video/audio files to sheet music
        
        Args:
            input_files (list): List of video/audio file paths
            output_base_dir (str, optional): Base output directory
            **kwargs: Additional arguments for conversion
            
        Returns:
            list: List of conversion results
        """
        
        results = []
        
        print(f"BATCH CONVERSION: {len(input_files)} files")
        print("=" * 60)
        
        for i, input_file in enumerate(input_files, 1):
            file_type = self.detect_file_type(input_file)
            print(f"\nProcessing file {i}/{len(input_files)}: {input_file} ({file_type.upper()})")
            
            # Setup individual output directory
            if output_base_dir:
                output_dir = Path(output_base_dir) / f"{Path(input_file).stem}_output"
            else:
                output_dir = None
            
            # Convert file
            result = self.convert_to_sheet_music(
                input_file, output_dir, **kwargs
            )
            results.append(result)
            
            # Print summary for this file
            if result['success']:
                print(f"✓ File {i} completed successfully")
            else:
                print(f"✗ File {i} failed: {result.get('error', 'Unknown error')}")
        
        # Overall summary
        successful = sum(1 for r in results if r['success'])
        print(f"\nBATCH CONVERSION SUMMARY:")
        print(f"  - Total files: {len(input_files)}")
        print(f"  - Successful: {successful}")
        print(f"  - Failed: {len(input_files) - successful}")
        
        return results
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Warning: Could not remove {temp_file}: {e}")
        
        self.temp_files.clear()


def main():
    """
    Command-line interface for the Music to Sheet Music converter
    """
    
    parser = argparse.ArgumentParser(
        description="Convert video and audio files to sheet music notation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert video file
  python3 mp4_to_sheet_music.py video.mp4
  
  # Convert audio file
  python3 mp4_to_sheet_music.py song.mp3
  
  # Specify output directory and formats
  python3 mp4_to_sheet_music.py audio.wav -o output/ -af wav -sf musicxml
  
  # Convert with custom title and keep intermediate files
  python3 mp4_to_sheet_music.py music.flac -t "My Song" -k
  
  # Convert a specific segment (30s to 60s)
  python3 mp4_to_sheet_music.py video.mp4 -s 30 -e 60
  
  # Batch convert multiple files (mixed video and audio)
  python3 mp4_to_sheet_music.py video1.mp4 song1.mp3 audio.wav -o batch_output/

Supported formats:
  Video: MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V
  Audio: WAV, MP3, FLAC, AAC, M4A, OGG, WMA
        """
    )
    
    # Input files
    parser.add_argument('input_files', nargs='+', 
                       help='Input video or audio file(s)')
    
    # Output options
    parser.add_argument('-o', '--output', 
                       help='Output directory')
    parser.add_argument('-af', '--audio-format', default='wav',
                       choices=['wav', 'mp3', 'flac'],
                       help='Audio format for processing (default: wav)')
    parser.add_argument('-sf', '--sheet-format', default='musicxml',
                       choices=['musicxml', 'xml', 'png', 'pdf', 'svg'],
                       help='Sheet music format (default: musicxml)')
    
    # Transcription options
    parser.add_argument('-ot', '--onset-threshold', type=float, default=0.5,
                       help='Note onset detection threshold (0.0-1.0, default: 0.5)')
    parser.add_argument('-ft', '--frame-threshold', type=float, default=0.3,
                       help='Note frame detection threshold (0.0-1.0, default: 0.3)')
    
    # Segment options
    parser.add_argument('-s', '--start-time', type=float,
                       help='Start time for segment extraction (seconds)')
    parser.add_argument('-e', '--end-time', type=float,
                       help='End time for segment extraction (seconds)')
    
    # Other options
    parser.add_argument('-t', '--title',
                       help='Title for the sheet music')
    parser.add_argument('-k', '--keep-intermediate', action='store_true',
                       help='Keep intermediate audio and MIDI files')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.start_time is not None and args.end_time is None:
        parser.error("--end-time is required when --start-time is specified")
    
    if args.end_time is not None and args.start_time is None:
        parser.error("--start-time is required when --end-time is specified")
    
    if args.start_time is not None and args.end_time is not None:
        if args.start_time >= args.end_time:
            parser.error("--start-time must be less than --end-time")
    
    # Check input files exist and detect types
    converter = MP4ToSheetMusicConverter()
    
    for input_file in args.input_files:
        if not os.path.exists(input_file):
            print(f"Error: Input file not found: {input_file}")
            sys.exit(1)
        
        file_type = converter.detect_file_type(input_file)
        if file_type == 'unknown':
            print(f"Error: Unsupported file format: {input_file}")
            print("Supported formats:")
            print("  Video:", ', '.join(converter.video_formats))
            print("  Audio:", ', '.join(converter.audio_formats))
            sys.exit(1)
    
    try:
        # Single file with segment
        if len(args.input_files) == 1 and args.start_time is not None:
            result = converter.convert_audio_segment(
                args.input_files[0],
                args.start_time,
                args.end_time,
                args.output,
                audio_format=args.audio_format,
                sheet_format=args.sheet_format,
                onset_threshold=args.onset_threshold,
                frame_threshold=args.frame_threshold,
                title=args.title,
                keep_intermediate=args.keep_intermediate
            )
            
            if not result['success']:
                sys.exit(1)
        
        # Single file conversion
        elif len(args.input_files) == 1:
            result = converter.convert_to_sheet_music(
                args.input_files[0],
                args.output,
                args.audio_format,
                args.sheet_format,
                args.onset_threshold,
                args.frame_threshold,
                args.title,
                args.keep_intermediate
            )
            
            if not result['success']:
                sys.exit(1)
        
        # Batch conversion
        else:
            results = converter.batch_convert(
                args.input_files,
                args.output,
                audio_format=args.audio_format,
                sheet_format=args.sheet_format,
                onset_threshold=args.onset_threshold,
                frame_threshold=args.frame_threshold,
                title=args.title,
                keep_intermediate=args.keep_intermediate
            )
            
            # Exit with error if any conversion failed
            if not all(r['success'] for r in results):
                sys.exit(1)
        
        print("\n🎵 All conversions completed successfully! 🎵")
        
    except KeyboardInterrupt:
        print("\n\nConversion interrupted by user")
        converter.cleanup_temp_files()
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        converter.cleanup_temp_files()
        sys.exit(1)


if __name__ == "__main__":
    main()
