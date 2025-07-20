#!/usr/bin/env python3
"""
Music Transcription Module for Music Sheet Generator (Fixed for Python 3.12)

This module handles converting audio files to MIDI using Basic Pitch
with ONNX model support for Python 3.12 compatibility.
"""

import os
import sys
import numpy as np
from pathlib import Path
import librosa
import pretty_midi
from basic_pitch.inference import Model
import basic_pitch


class MusicTranscriber:
    """
    A class to handle music transcription from audio to MIDI
    """
    
    def __init__(self):
        """Initialize the MusicTranscriber"""
        self.supported_audio_formats = ['.wav', '.mp3', '.flac', '.aac', '.m4a']
        self.sample_rate = 22050  # Basic Pitch default sample rate
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the ONNX model for Basic Pitch"""
        try:
            # Use ONNX model which is compatible with Python 3.12
            onnx_model_path = os.path.join(
                os.path.dirname(basic_pitch.__file__), 
                'saved_models', 'icassp_2022', 'nmp.onnx'
            )
            
            if os.path.exists(onnx_model_path):
                print("Loading ONNX model for Basic Pitch...")
                self.model = Model(onnx_model_path)
                print("✓ ONNX model loaded successfully!")
            else:
                raise FileNotFoundError(f"ONNX model not found at {onnx_model_path}")
                
        except Exception as e:
            print(f"✗ Failed to load ONNX model: {e}")
            raise
    
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
    
    def _predict_with_onnx_model(self, audio_data):
        """
        Predict using ONNX model with proper chunking
        
        Args:
            audio_data (np.ndarray): Audio data
            
        Returns:
            dict: Model predictions
        """
        # ONNX model expects chunks of 43844 samples (about 1.99 seconds)
        chunk_size = 43844
        hop_size = chunk_size // 2  # 50% overlap
        
        # Pad audio if necessary
        if len(audio_data) < chunk_size:
            audio_data = np.pad(audio_data, (0, chunk_size - len(audio_data)))
        
        # Process audio in chunks
        all_predictions = {'note': [], 'onset': [], 'contour': []}
        
        for start in range(0, len(audio_data) - chunk_size + 1, hop_size):
            chunk = audio_data[start:start + chunk_size]
            
            # Reshape for model input: (batch, time, channels)
            chunk_input = chunk.reshape(1, chunk_size, 1).astype(np.float32)
            
            # Get prediction
            prediction = self.model.predict(chunk_input)
            
            # Store predictions
            for key in all_predictions:
                all_predictions[key].append(prediction[key])
        
        # Concatenate all predictions
        final_predictions = {}
        for key in all_predictions:
            if all_predictions[key]:
                final_predictions[key] = np.concatenate(all_predictions[key], axis=1)
            else:
                # Fallback for very short audio
                chunk_input = np.pad(audio_data, (0, chunk_size - len(audio_data))).reshape(1, chunk_size, 1).astype(np.float32)
                prediction = self.model.predict(chunk_input)
                final_predictions[key] = prediction[key]
        
        return final_predictions
    
    def _predictions_to_midi(self, predictions, onset_threshold=0.5, frame_threshold=0.3):
        """
        Convert model predictions to MIDI
        
        Args:
            predictions (dict): Model predictions
            onset_threshold (float): Onset threshold
            frame_threshold (float): Frame threshold
            
        Returns:
            tuple: (midi_data, note_events)
        """
        from basic_pitch.constants import AUDIO_SAMPLE_RATE, ANNOTATIONS_FPS
        
        # Extract predictions
        note_predictions = predictions['note'][0]  # Remove batch dimension
        onset_predictions = predictions['onset'][0]
        
        # Apply thresholds
        note_activations = note_predictions > frame_threshold
        onset_activations = onset_predictions > onset_threshold
        
        # Create MIDI
        midi_data = pretty_midi.PrettyMIDI()
        instrument = pretty_midi.Instrument(program=0)  # Piano
        
        # Convert to note events
        note_events = []
        
        # Time resolution
        time_per_frame = 1.0 / ANNOTATIONS_FPS  # Basic Pitch uses ~86.13 FPS
        
        # Find notes
        for pitch_idx in range(note_activations.shape[1]):  # 88 piano keys
            # Find note segments
            note_active = note_activations[:, pitch_idx]
            onset_active = onset_activations[:, pitch_idx]
            
            # Find note starts and ends
            note_starts = []
            note_ends = []
            
            in_note = False
            note_start = 0
            
            for frame_idx in range(len(note_active)):
                if not in_note and (onset_active[frame_idx] or note_active[frame_idx]):
                    # Start of note
                    in_note = True
                    note_start = frame_idx
                elif in_note and not note_active[frame_idx]:
                    # End of note
                    in_note = False
                    note_starts.append(note_start)
                    note_ends.append(frame_idx)
            
            # Handle note that extends to end
            if in_note:
                note_starts.append(note_start)
                note_ends.append(len(note_active) - 1)
            
            # Create MIDI notes
            for start_frame, end_frame in zip(note_starts, note_ends):
                start_time = start_frame * time_per_frame
                end_time = end_frame * time_per_frame
                
                # Convert pitch index to MIDI note number (A0 = 21)
                midi_note = pitch_idx + 21
                
                # Minimum note length
                if end_time - start_time >= 0.05:  # 50ms minimum
                    note = pretty_midi.Note(
                        velocity=80,
                        pitch=midi_note,
                        start=start_time,
                        end=end_time
                    )
                    instrument.notes.append(note)
                    
                    note_events.append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'pitch': midi_note,
                        'velocity': 80
                    })
        
        midi_data.instruments.append(instrument)
        return midi_data, note_events
    
    def transcribe_audio_to_midi(self, audio_path, output_path=None, onset_threshold=0.5, frame_threshold=0.3):
        """
        Transcribe audio to MIDI using Basic Pitch ONNX model
        
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
            
            # Perform transcription using ONNX model
            print("Running Basic Pitch transcription with ONNX model...")
            predictions = self._predict_with_onnx_model(audio_data)
            
            # Convert predictions to MIDI
            print("Converting predictions to MIDI...")
            midi_data, note_events = self._predictions_to_midi(
                predictions, onset_threshold, frame_threshold
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
            
            print(f"Audio analysis completed for: {audio_path}")
            print(f"Estimated tempo: {features['tempo']:.1f} BPM")
            print(f"Number of beats: {features['num_beats']}")
            print("Audio analysis:")
            print(f"  - Estimated tempo: {features['tempo']:.1f} BPM")
            print(f"  - Spectral centroid: {features['spectral_centroid_mean']:.1f} Hz")
            print(f"  - RMS energy: {features['rms_energy_mean']:.4f}")
            
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


def main():
    """
    Command-line interface for the music transcriber
    """
    if len(sys.argv) < 2:
        print("Usage: python3 music_transcriber_fixed.py <audio_file> [output_file] [onset_threshold] [frame_threshold]")
        print("Example: python3 music_transcriber_fixed.py audio.wav output.mid 0.5 0.3")
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
