#!/usr/bin/env python3
"""
Sheet Music Generation Module for Music Sheet Generator

This module handles converting MIDI files to visual sheet music notation
using music21 and other music notation libraries.
"""

import os
import sys
from pathlib import Path
import pretty_midi
from music21 import stream, note, duration, meter, key, tempo, bar, pitch, interval
from music21 import converter, midi as music21_midi
from music21.musicxml import m21ToXml
from music21.midi import translate as midi_translate


class SheetMusicGenerator:
    """
    A class to handle sheet music generation from MIDI files
    """
    
    def __init__(self):
        """Initialize the SheetMusicGenerator"""
        self.supported_input_formats = ['.mid', '.midi']
        self.supported_output_formats = ['.png', '.pdf', '.svg', '.musicxml', '.xml']
    
    def is_supported_input_format(self, file_path):
        """
        Check if the input MIDI file format is supported
        
        Args:
            file_path (str): Path to the MIDI file
            
        Returns:
            bool: True if format is supported, False otherwise
        """
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_input_formats
    
    def load_midi_to_music21(self, midi_path):
        """
        Load a MIDI file and convert it to a music21 stream
        
        Args:
            midi_path (str): Path to the MIDI file
            
        Returns:
            music21.stream.Stream: The loaded musical score
        """
        
        if not os.path.exists(midi_path):
            raise FileNotFoundError(f"MIDI file not found: {midi_path}")
        
        if not self.is_supported_input_format(midi_path):
            raise ValueError(f"Unsupported MIDI format: {Path(midi_path).suffix}")
        
        try:
            print(f"Loading MIDI file: {midi_path}")
            
            # Load MIDI file using music21
            score = converter.parse(midi_path)
            
            print(f"✓ MIDI loaded successfully")
            print(f"  - Duration: {score.duration.quarterLength} quarter notes")
            print(f"  - Number of parts: {len(score.parts)}")
            
            return score
            
        except Exception as e:
            raise Exception(f"Failed to load MIDI file: {str(e)}")
    
    def analyze_musical_content(self, score):
        """
        Analyze the musical content of a score
        
        Args:
            score (music21.stream.Stream): The musical score
            
        Returns:
            dict: Analysis results
        """
        
        try:
            analysis = {}
            
            # Basic information
            analysis['duration_quarters'] = float(score.duration.quarterLength)
            analysis['num_parts'] = len(score.parts)
            analysis['num_measures'] = len(score.parts[0].getElementsByClass('Measure')) if score.parts else 0
            
            # Key signature analysis
            key_signatures = score.flat.getElementsByClass(key.KeySignature)
            if key_signatures:
                analysis['key_signature'] = str(key_signatures[0])
            else:
                # Try to analyze key
                try:
                    analyzed_key = score.analyze('key')
                    analysis['key_signature'] = str(analyzed_key)
                except:
                    analysis['key_signature'] = 'C major'
            
            # Time signature analysis
            time_signatures = score.flat.getElementsByClass(meter.TimeSignature)
            if time_signatures:
                analysis['time_signature'] = str(time_signatures[0])
            else:
                analysis['time_signature'] = '4/4'
            
            # Tempo analysis
            tempo_markings = score.flat.getElementsByClass(tempo.TempoIndication)
            if tempo_markings:
                analysis['tempo'] = tempo_markings[0].number
            else:
                analysis['tempo'] = 120  # Default tempo
            
            # Note analysis for each part
            analysis['parts'] = []
            for i, part in enumerate(score.parts):
                part_notes = part.flat.notes
                if part_notes:
                    pitches = []
                    for element in part_notes:
                        if hasattr(element, 'pitch'):
                            pitches.append(element.pitch.midi)
                        elif hasattr(element, 'pitches'):  # Chord
                            pitches.extend([p.midi for p in element.pitches])
                    
                    if pitches:
                        part_analysis = {
                            'index': i,
                            'num_notes': len(part_notes),
                            'pitch_range': [min(pitches), max(pitches)],
                            'note_range': [pitch.Pitch(midi=min(pitches)).name,
                                         pitch.Pitch(midi=max(pitches)).name]
                        }
                        analysis['parts'].append(part_analysis)
            
            return analysis
            
        except Exception as e:
            raise Exception(f"Musical analysis failed: {str(e)}")
    
    def enhance_score_formatting(self, score):
        """
        Enhance the score with better formatting and metadata
        
        Args:
            score (music21.stream.Stream): The musical score
            
        Returns:
            music21.stream.Stream: Enhanced score
        """
        
        try:
            # Add title if not present
            if not score.metadata:
                score.append(stream.Metadata())
            
            if not score.metadata.title:
                score.metadata.title = 'Transcribed Music'
            
            if not score.metadata.composer:
                score.metadata.composer = 'Generated by Music Sheet Generator'
            
            # Ensure proper time signature
            if not score.flat.getElementsByClass(meter.TimeSignature):
                score.insert(0, meter.TimeSignature('4/4'))
            
            # Ensure proper key signature
            if not score.flat.getElementsByClass(key.KeySignature):
                try:
                    analyzed_key = score.analyze('key')
                    score.insert(0, analyzed_key)
                except:
                    score.insert(0, key.Key('C', 'major'))
            
            # Add tempo marking if not present
            if not score.flat.getElementsByClass(tempo.TempoIndication):
                score.insert(0, tempo.TempoIndication(number=120))
            
            # Add bar lines and measures if needed
            for part in score.parts:
                if not part.getElementsByClass('Measure'):
                    part.makeMeasures(inPlace=True)
            
            print("✓ Score formatting enhanced")
            return score
            
        except Exception as e:
            print(f"⚠ Warning: Score enhancement failed: {str(e)}")
            return score
    
    def generate_sheet_music(self, midi_path, output_path=None, output_format='png', 
                           title=None, enhance_formatting=True):
        """
        Generate sheet music from a MIDI file
        
        Args:
            midi_path (str): Path to the input MIDI file
            output_path (str, optional): Path for the output file
            output_format (str): Output format ('png', 'pdf', 'svg', 'musicxml')
            title (str, optional): Title for the sheet music
            enhance_formatting (bool): Whether to enhance score formatting
            
        Returns:
            str: Path to the generated sheet music file
        """
        
        # Generate output path if not provided
        if output_path is None:
            midi_stem = Path(midi_path).stem
            output_path = f"{midi_stem}_sheet.{output_format}"
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"Generating sheet music from: {midi_path}")
            print(f"Output format: {output_format}")
            print(f"Output file: {output_path}")
            
            # Load MIDI file
            score = self.load_midi_to_music21(midi_path)
            
            # Analyze musical content
            print("\nAnalyzing musical content...")
            analysis = self.analyze_musical_content(score)
            
            print(f"Musical Analysis:")
            print(f"  - Key: {analysis['key_signature']}")
            print(f"  - Time signature: {analysis['time_signature']}")
            print(f"  - Tempo: {analysis['tempo']} BPM")
            print(f"  - Duration: {analysis['duration_quarters']} quarter notes")
            print(f"  - Number of parts: {analysis['num_parts']}")
            
            # Enhance formatting if requested
            if enhance_formatting:
                print("\nEnhancing score formatting...")
                score = self.enhance_score_formatting(score)
                
                # Set custom title if provided
                if title:
                    score.metadata.title = title
            
            # Generate output based on format
            print(f"\nGenerating {output_format.upper()} output...")
            
            if output_format.lower() in ['png', 'pdf', 'svg']:
                # For image formats, we need to use music21's show method
                # Note: This requires additional software like MuseScore or LilyPond
                try:
                    if output_format.lower() == 'png':
                        score.write('musicxml.png', fp=output_path)
                    elif output_format.lower() == 'pdf':
                        score.write('musicxml.pdf', fp=output_path)
                    elif output_format.lower() == 'svg':
                        score.write('musicxml.svg', fp=output_path)
                except Exception as e:
                    print(f"⚠ Warning: Direct {output_format} generation failed: {str(e)}")
                    print("Falling back to MusicXML format...")
                    musicxml_path = output_path.replace(f'.{output_format}', '.musicxml')
                    score.write('musicxml', fp=musicxml_path)
                    output_path = musicxml_path
                    
            elif output_format.lower() in ['musicxml', 'xml']:
                score.write('musicxml', fp=output_path)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
            
            print(f"✓ Sheet music generated successfully!")
            print(f"  - Output file: {output_path}")
            
            return output_path
            
        except Exception as e:
            print(f"✗ Sheet music generation failed: {str(e)}")
            raise
    
    def create_simple_notation(self, midi_path, output_path=None):
        """
        Create a simplified notation focusing on melody
        
        Args:
            midi_path (str): Path to the input MIDI file
            output_path (str, optional): Path for the output file
            
        Returns:
            str: Path to the generated notation file
        """
        
        if output_path is None:
            midi_stem = Path(midi_path).stem
            output_path = f"{midi_stem}_simple.musicxml"
        
        try:
            print(f"Creating simple notation from: {midi_path}")
            
            # Load MIDI
            score = self.load_midi_to_music21(midi_path)
            
            # Create a simplified version
            simple_score = stream.Score()
            simple_score.append(meter.TimeSignature('4/4'))
            simple_score.append(key.Key('C', 'major'))
            simple_score.append(tempo.TempoIndication(number=120))
            
            # Extract melody (highest notes) from all parts
            all_notes = []
            for part in score.parts:
                for element in part.flat.notes:
                    if hasattr(element, 'pitch'):
                        all_notes.append((element.offset, element.pitch.midi, element.duration.quarterLength))
                    elif hasattr(element, 'pitches'):  # Chord - take highest note
                        highest_pitch = max(p.midi for p in element.pitches)
                        all_notes.append((element.offset, highest_pitch, element.duration.quarterLength))
            
            # Sort by time and create melody line
            all_notes.sort(key=lambda x: x[0])
            
            melody_part = stream.Part()
            for offset, midi_pitch, dur in all_notes:
                n = note.Note(midi=midi_pitch)
                n.duration = duration.Duration(quarterLength=dur)
                melody_part.insert(offset, n)
            
            simple_score.append(melody_part)
            
            # Add measures
            simple_score.makeMeasures(inPlace=True)
            
            # Write output
            simple_score.write('musicxml', fp=output_path)
            
            print(f"✓ Simple notation created: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"✗ Simple notation creation failed: {str(e)}")
            raise


def main():
    """
    Command-line interface for the sheet music generator
    """
    if len(sys.argv) < 2:
        print("Usage: python3 sheet_music_generator.py <midi_file> [output_file] [format] [title]")
        print("Formats: png, pdf, svg, musicxml, xml")
        print("Example: python3 sheet_music_generator.py song.mid sheet.png png 'My Song'")
        sys.exit(1)
    
    midi_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    output_format = sys.argv[3] if len(sys.argv) > 3 else 'musicxml'
    title = sys.argv[4] if len(sys.argv) > 4 else None
    
    generator = SheetMusicGenerator()
    
    try:
        # Generate sheet music
        output_path = generator.generate_sheet_music(
            midi_file, 
            output_file, 
            output_format,
            title
        )
        
        print(f"\n✓ Success! Sheet music generated: {output_path}")
        
        # Also create a simple version
        print("\nCreating simplified version...")
        simple_path = generator.create_simple_notation(midi_file)
        print(f"✓ Simplified notation: {simple_path}")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

