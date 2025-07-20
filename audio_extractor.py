#!/usr/bin/env python3
"""
Audio Extraction Module for Music Sheet Generator

This module handles extracting audio from video files (MP4, AVI, MOV, etc.)
and converting them to audio formats suitable for music transcription.
"""

import os
import sys
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip


class AudioExtractor:
    """
    A class to handle audio extraction from video files
    """
    
    def __init__(self):
        """Initialize the AudioExtractor"""
        self.supported_video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        self.supported_audio_formats = ['.wav', '.mp3', '.flac', '.aac']
    
    def is_supported_video_format(self, file_path):
        """
        Check if the video file format is supported
        
        Args:
            file_path (str): Path to the video file
            
        Returns:
            bool: True if format is supported, False otherwise
        """
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_video_formats
    
    def extract_audio_from_video(self, video_path, output_path=None, audio_format='wav'):
        """
        Extract audio from a video file
        
        Args:
            video_path (str): Path to the input video file
            output_path (str, optional): Path for the output audio file. 
                                       If None, uses video filename with audio extension
            audio_format (str): Output audio format ('wav', 'mp3', 'flac')
            
        Returns:
            str: Path to the extracted audio file
            
        Raises:
            FileNotFoundError: If video file doesn't exist
            ValueError: If video format is not supported
            Exception: If extraction fails
        """
        
        # Validate input file
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if not self.is_supported_video_format(video_path):
            raise ValueError(f"Unsupported video format: {Path(video_path).suffix}")
        
        # Generate output path if not provided
        if output_path is None:
            video_stem = Path(video_path).stem
            output_path = f"{video_stem}.{audio_format}"
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"Loading video file: {video_path}")
            
            # Load video file
            video_clip = VideoFileClip(video_path)
            
            # Check if video has audio
            if video_clip.audio is None:
                video_clip.close()
                raise ValueError("Video file contains no audio track")
            
            # Extract audio
            audio_clip = video_clip.audio
            
            print(f"Extracting audio to: {output_path}")
            print(f"Audio duration: {audio_clip.duration:.2f} seconds")
            print(f"Audio sample rate: {audio_clip.fps} Hz")
            
            # Write audio file
            audio_clip.write_audiofile(output_path)
            
            # Clean up
            audio_clip.close()
            video_clip.close()
            
            print(f"✓ Audio extraction completed: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"✗ Audio extraction failed: {str(e)}")
            raise
    
    def get_audio_info(self, video_path):
        """
        Get audio information from a video file without extracting
        
        Args:
            video_path (str): Path to the video file
            
        Returns:
            dict: Audio information including duration, sample rate, channels
        """
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        try:
            video_clip = VideoFileClip(video_path)
            
            if video_clip.audio is None:
                video_clip.close()
                return {"has_audio": False}
            
            audio_info = {
                "has_audio": True,
                "duration": video_clip.audio.duration,
                "sample_rate": video_clip.audio.fps,
                "channels": video_clip.audio.nchannels if hasattr(video_clip.audio, 'nchannels') else 'unknown'
            }
            
            video_clip.close()
            return audio_info
            
        except Exception as e:
            raise Exception(f"Failed to get audio info: {str(e)}")
    
    def extract_audio_segment(self, video_path, start_time, end_time, output_path=None, audio_format='wav'):
        """
        Extract a specific segment of audio from a video file
        
        Args:
            video_path (str): Path to the input video file
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            output_path (str, optional): Path for the output audio file
            audio_format (str): Output audio format
            
        Returns:
            str: Path to the extracted audio segment
        """
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if start_time >= end_time:
            raise ValueError("Start time must be less than end time")
        
        # Generate output path if not provided
        if output_path is None:
            video_stem = Path(video_path).stem
            output_path = f"{video_stem}_segment_{start_time}_{end_time}.{audio_format}"
        
        try:
            print(f"Loading video file: {video_path}")
            
            # Load video file and extract segment
            video_clip = VideoFileClip(video_path).subclip(start_time, end_time)
            
            if video_clip.audio is None:
                video_clip.close()
                raise ValueError("Video file contains no audio track")
            
            # Extract audio segment
            audio_clip = video_clip.audio
            
            print(f"Extracting audio segment ({start_time}s - {end_time}s) to: {output_path}")
            
            # Write audio file
            audio_clip.write_audiofile(output_path)
            
            # Clean up
            audio_clip.close()
            video_clip.close()
            
            print(f"✓ Audio segment extraction completed: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"✗ Audio segment extraction failed: {str(e)}")
            raise


    def get_audio_file_info(self, audio_path):
        """
        Get information about an audio file
        
        Args:
            audio_path (str): Path to the audio file
            
        Returns:
            dict: Audio file information
        """
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            import librosa
            
            print(f"Analyzing audio file: {audio_path}")
            
            # Load audio to get basic info
            audio_data, sample_rate = librosa.load(audio_path, sr=None)
            duration = len(audio_data) / sample_rate
            
            # Determine number of channels
            if len(audio_data.shape) == 1:
                channels = 1  # Mono
            else:
                channels = audio_data.shape[1]  # Stereo or multi-channel
            
            info = {
                "has_audio": True,
                "duration": duration,
                "sample_rate": sample_rate,
                "channels": channels,
                "format": Path(audio_path).suffix.lower().lstrip('.'),
                "file_size": os.path.getsize(audio_path)
            }
            
            print(f"Audio file analysis completed:")
            print(f"  - Duration: {duration:.2f} seconds")
            print(f"  - Sample rate: {sample_rate} Hz")
            print(f"  - Channels: {channels}")
            print(f"  - Format: {info['format'].upper()}")
            print(f"  - File size: {info['file_size'] / (1024*1024):.2f} MB")
            
            return info
            
        except Exception as e:
            raise Exception(f"Failed to analyze audio file: {str(e)}")
    
    def convert_audio_format(self, input_path, output_path, target_format='wav'):
        """
        Convert audio file from one format to another
        
        Args:
            input_path (str): Path to the input audio file
            output_path (str): Path for the output audio file
            target_format (str): Target audio format ('wav', 'mp3', 'flac')
            
        Returns:
            str: Path to the converted audio file
        """
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input audio file not found: {input_path}")
        
        try:
            import librosa
            import soundfile as sf
            
            print(f"Converting audio format...")
            print(f"  - Input: {input_path}")
            print(f"  - Output: {output_path}")
            print(f"  - Target format: {target_format.upper()}")
            
            # Load audio data
            audio_data, sample_rate = librosa.load(input_path, sr=None)
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save in target format
            if target_format.lower() == 'wav':
                sf.write(output_path, audio_data, sample_rate, format='WAV')
            elif target_format.lower() == 'flac':
                sf.write(output_path, audio_data, sample_rate, format='FLAC')
            elif target_format.lower() == 'mp3':
                # For MP3, we need to use a different approach
                # soundfile doesn't support MP3 writing, so we'll use moviepy
                from moviepy.audio.io.AudioFileClip import AudioFileClip
                
                # Create a temporary WAV file first
                temp_wav = output_path.replace('.mp3', '_temp.wav')
                sf.write(temp_wav, audio_data, sample_rate, format='WAV')
                
                # Convert to MP3 using moviepy
                audio_clip = AudioFileClip(temp_wav)
                audio_clip.write_audiofile(output_path, verbose=False, logger=None)
                audio_clip.close()
                
                # Clean up temporary file
                os.remove(temp_wav)
            else:
                raise ValueError(f"Unsupported target format: {target_format}")
            
            print(f"✓ Audio format conversion completed: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Audio format conversion failed: {str(e)}")
    
    def extract_audio_segment_from_audio(self, audio_path, start_time, end_time, output_path):
        """
        Extract a segment from an audio file
        
        Args:
            audio_path (str): Path to the input audio file
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            output_path (str): Path for the output audio segment
            
        Returns:
            str: Path to the extracted audio segment
        """
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            import librosa
            import soundfile as sf
            
            print(f"Extracting audio segment from audio file...")
            print(f"  - Input: {audio_path}")
            print(f"  - Segment: {start_time}s - {end_time}s")
            print(f"  - Output: {output_path}")
            
            # Load the full audio file
            audio_data, sample_rate = librosa.load(audio_path, sr=None)
            duration = len(audio_data) / sample_rate
            
            # Validate time range
            if start_time < 0:
                start_time = 0
            if end_time > duration:
                end_time = duration
            if start_time >= end_time:
                raise ValueError(f"Invalid time range: {start_time}s - {end_time}s")
            
            # Calculate sample indices
            start_sample = int(start_time * sample_rate)
            end_sample = int(end_time * sample_rate)
            
            # Extract segment
            segment_data = audio_data[start_sample:end_sample]
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save segment
            sf.write(output_path, segment_data, sample_rate)
            
            segment_duration = len(segment_data) / sample_rate
            print(f"✓ Audio segment extracted successfully")
            print(f"  - Segment duration: {segment_duration:.2f} seconds")
            print(f"  - Output file: {output_path}")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Audio segment extraction failed: {str(e)}")


def main():
    """
    Command-line interface for the audio extractor
    """
    if len(sys.argv) < 2:
        print("Usage: python3 audio_extractor.py <video_file> [output_file] [format]")
        print("Example: python3 audio_extractor.py video.mp4 audio.wav wav")
        sys.exit(1)
    
    video_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    audio_format = sys.argv[3] if len(sys.argv) > 3 else 'wav'
    
    extractor = AudioExtractor()
    
    try:
        # Get audio info first
        print("Getting audio information...")
        audio_info = extractor.get_audio_info(video_file)
        
        if not audio_info["has_audio"]:
            print("✗ Video file contains no audio track")
            sys.exit(1)
        
        print(f"Audio duration: {audio_info['duration']:.2f} seconds")
        print(f"Sample rate: {audio_info['sample_rate']} Hz")
        print(f"Channels: {audio_info['channels']}")
        print()
        
        # Extract audio
        output_path = extractor.extract_audio_from_video(
            video_file, 
            output_file, 
            audio_format
        )
        
        print(f"\n✓ Success! Audio extracted to: {output_path}")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

