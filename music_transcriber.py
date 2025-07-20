#!/usr/bin/env python3
"""
Music Transcription Module for Music Sheet Generator

This module handles converting audio files to MIDI using Basic Pitch
and other music transcription techniques.
"""

import os
import sys
import numpy as np
from pathlib import Path
import librosa
import pretty_midi
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


class MusicTranscriber:
    """
    A class to handle music transcription from audio to MIDI
    """
    
    def __init__(self):
        """Initialize the MusicTranscriber"""
        self.supported_audio_formats = ['.wav', '.mp3', '.flac', '.aac', '.m4a']
        self.sample_rate = 22050  # Basic Pitch default sample rate
    
    def is_supported_audio_format(self, file_path):
        """
        Check if the audio file format is supported
        
        Args:
            file_path (str): Path to the audio file
            
        Returns:
            bool: True if format is supported, False otherwise
        """
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_audio_formats
    
    def load_audio(self, audio_path):
        """
        Load audio file and prepare it for transcription
        
        Args:
            audio_path (str): Path to the audio file
            
        Returns:
            tuple: (audio_data, sample_rate)
        """
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if not self.is_supported_audio_format(audio_path):
            raise ValueError(f"Unsupported audio format: {Path(audio_path).suffix}")
        
        try:
            # Load audio using librosa
            audio_data, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            print(f"Loaded audio: {audio_path}")
            print(f"Duration: {len(audio_data) / sr:.2f} seconds")
            print(f"Sample rate: {sr} Hz")
            print(f"Audio shape: {audio_data.shape}")
            
            return audio_data, sr
            
        except Exception as e:
            raise Exception(f"Failed to load audio: {str(e)}")
    
    def transcribe_audio_to_midi(self, audio_path, output_path=None, onset_threshold=0.5, frame_threshold=0.3):
        """
        Transcribe audio to MIDI using Basic Pitch
        
        Args:
            audio_path (str): Path to the input audio file
            output_path (str, optional): Path for the output MIDI file
            onset_threshold (float): Threshold for note onset detection (0.0-1.0)
            frame_threshold (float): Threshold for note frame detection (0.0-1.0)
            
        Returns:
            str: Path to the generated MIDI file
        """
        
        # Generate output path if not provided
        if output_path is None:
            audio_stem = Path(audio_path).stem
            output_path = f"{audio_stem}.mid"
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"Starting transcription of: {audio_path}")
            print(f"Using onset threshold: {onset_threshold}")
            print(f"Using frame threshold: {frame_threshold}")
            
            # Load audio
            audio_data, sr = self.load_audio(audio_path)
            
            # Perform transcription using Basic Pitch
            print("Running Basic Pitch transcription...")
            
            model_output, midi_data, note_events = predict(
                audio_path,
                model_or_model_path=ICASSP_2022_MODEL_PATH,
                onset_threshold=onset_threshold,
                frame_threshold=frame_threshold
            )
            
            # Save MIDI file
            print(f"Saving MIDI to: {output_path}")
            midi_data.write(output_path)
            
            # Get transcription statistics
            num_notes = len(note_events)
            duration = midi_data.get_end_time()
            
            print(f"✓ Transcription completed!")
            print(f"  - Output file: {output_path}")
            print(f"  - Number of notes detected: {num_notes}")
            print(f"  - MIDI duration: {duration:.2f} seconds")
            
            return output_path
            
        except Exception as e:
            print(f"✗ Transcription failed: {str(e)}")
            raise
    
    def analyze_audio_features(self, audio_path):
        """
        Analyze audio features for better transcription understanding
        
        Args:
            audio_path (str): Path to the audio file
            
        Returns:
            dict: Audio analysis results
        """
        
        try:
            # Load audio
            audio_data, sr = self.load_audio(audio_path)
            
            # Extract features
            features = {}
            
            # Tempo estimation
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sr)
            features['tempo'] = float(tempo)
            features['num_beats'] = len(beats)
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)[0]
            features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            features['spectral_centroid_std'] = float(np.std(spectral_centroids))
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
            features['zero_crossing_rate_mean'] = float(np.mean(zcr))
            
            # RMS energy
            rms = librosa.feature.rms(y=audio_data)[0]
            features['rms_energy_mean'] = float(np.mean(rms))
            features['rms_energy_std'] = float(np.std(rms))
            
            # Chroma features (pitch class profiles)
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
            features['chroma_mean'] = np.mean(chroma, axis=1).tolist()
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            features['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
            
            print(f"Audio analysis completed for: {audio_path}")
            print(f"Estimated tempo: {features['tempo']:.1f} BPM")
            print(f"Number of beats: {features['num_beats']}")
            
            return features
            
        except Exception as e:
            raise Exception(f"Audio analysis failed: {str(e)}")
    
    def get_midi_info(self, midi_path):
        """
        Get information about a MIDI file
        
        Args:
            midi_path (str): Path to the MIDI file
            
        Returns:
            dict: MIDI file information
        """
        
        if not os.path.exists(midi_path):
            raise FileNotFoundError(f"MIDI file not found: {midi_path}")
        
        try:
            midi_data = pretty_midi.PrettyMIDI(midi_path)
            
            # Get initial tempo safely
            try:
                initial_tempo = midi_data.estimate_tempo()
            except:
                initial_tempo = 120.0  # Default tempo
            
            info = {
                'duration': midi_data.get_end_time(),
                'num_instruments': len(midi_data.instruments),
                'total_notes': sum(len(instrument.notes) for instrument in midi_data.instruments),
                'initial_tempo': initial_tempo
            }
            
            # Get note range for each instrument
            info['instruments'] = []
            for i, instrument in enumerate(midi_data.instruments):
                if len(instrument.notes) > 0:
                    pitches = [note.pitch for note in instrument.notes]
                    inst_info = {
                        'index': i,
                        'name': instrument.name,
                        'program': instrument.program,
                        'is_drum': instrument.is_drum,
                        'num_notes': len(instrument.notes),
                        'pitch_range': [min(pitches), max(pitches)],
                        'note_range': [pretty_midi.note_number_to_name(min(pitches)),
                                     pretty_midi.note_number_to_name(max(pitches))]
                    }
                    info['instruments'].append(inst_info)
            
            return info
            
        except Exception as e:
            raise Exception(f"Failed to analyze MIDI file: {str(e)}")
    
    def transcribe_with_custom_settings(self, audio_path, output_path=None, 
                                      onset_threshold=0.5, frame_threshold=0.3,
                                      minimum_note_length=0.1, minimum_frequency=80.0,
                                      maximum_frequency=2000.0):
        """
        Transcribe audio with custom settings for better results
        
        Args:
            audio_path (str): Path to the input audio file
            output_path (str, optional): Path for the output MIDI file
            onset_threshold (float): Threshold for note onset detection
            frame_threshold (float): Threshold for note frame detection
            minimum_note_length (float): Minimum note length in seconds
            minimum_frequency (float): Minimum frequency to transcribe (Hz)
            maximum_frequency (float): Maximum frequency to transcribe (Hz)
            
        Returns:
            str: Path to the generated MIDI file
        """
        
        # Generate output path if not provided
        if output_path is None:
            audio_stem = Path(audio_path).stem
            output_path = f"{audio_stem}_custom.mid"
        
        try:
            print(f"Starting custom transcription of: {audio_path}")
            print(f"Settings:")
            print(f"  - Onset threshold: {onset_threshold}")
            print(f"  - Frame threshold: {frame_threshold}")
            print(f"  - Min note length: {minimum_note_length}s")
            print(f"  - Frequency range: {minimum_frequency}-{maximum_frequency} Hz")
            
            # Perform transcription
            model_output, midi_data, note_events = predict(
                audio_path,
                model_or_model_path=ICASSP_2022_MODEL_PATH,
                onset_threshold=onset_threshold,
                frame_threshold=frame_threshold,
                minimum_note_length=minimum_note_length,
                minimum_frequency=minimum_frequency,
                maximum_frequency=maximum_frequency
            )
            
            # Save MIDI file
            midi_data.write(output_path)
            
            print(f"✓ Custom transcription completed: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"✗ Custom transcription failed: {str(e)}")
            raise


def main():
    """
    Command-line interface for the music transcriber
    """
    if len(sys.argv) < 2:
        print("Usage: python3 music_transcriber.py <audio_file> [output_file] [onset_threshold] [frame_threshold]")
        print("Example: python3 music_transcriber.py audio.wav output.mid 0.5 0.3")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    onset_threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    frame_threshold = float(sys.argv[4]) if len(sys.argv) > 4 else 0.3
    
    transcriber = MusicTranscriber()
    
    try:
        # Analyze audio features first
        print("Analyzing audio features...")
        features = transcriber.analyze_audio_features(audio_file)
        print()
        
        # Perform transcription
        output_path = transcriber.transcribe_audio_to_midi(
            audio_file, 
            output_file, 
            onset_threshold, 
            frame_threshold
        )
        
        print()
        
        # Analyze the resulting MIDI
        print("Analyzing generated MIDI...")
        midi_info = transcriber.get_midi_info(output_path)
        
        print(f"MIDI Information:")
        print(f"  - Duration: {midi_info['duration']:.2f} seconds")
        print(f"  - Total notes: {midi_info['total_notes']}")
        print(f"  - Number of instruments: {midi_info['num_instruments']}")
        
        for inst in midi_info['instruments']:
            print(f"  - Instrument {inst['index']}: {inst['num_notes']} notes, "
                  f"range {inst['note_range'][0]}-{inst['note_range'][1]}")
        
        print(f"\n✓ Success! MIDI file created: {output_path}")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

