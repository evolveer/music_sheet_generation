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


    def convert_musicxml_to_pdf(self, musicxml_path, pdf_path=None, use_musescore=True):
        """
        Convert a MusicXML file to a visual PDF score
        
        Args:
            musicxml_path (str): Path to the input MusicXML file
            pdf_path (str, optional): Path for the output PDF file
            use_musescore (bool): Whether to use MuseScore for conversion
            
        Returns:
            str: Path to the generated PDF file
        """
        
        if not os.path.exists(musicxml_path):
            raise FileNotFoundError(f"MusicXML file not found: {musicxml_path}")
        
        # Generate output path if not provided
        if pdf_path is None:
            musicxml_stem = Path(musicxml_path).stem
            pdf_path = f"{musicxml_stem}_score.pdf"
        
        # Ensure output directory exists
        output_dir = Path(pdf_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"Converting MusicXML to PDF...")
            print(f"  - Input: {musicxml_path}")
            print(f"  - Output: {pdf_path}")
            
            if use_musescore:
                success = self._convert_with_musescore(musicxml_path, pdf_path)
                if success:
                    print(f"✓ PDF generated successfully with MuseScore: {pdf_path}")
                    return pdf_path
                else:
                    print("⚠ MuseScore conversion failed, trying alternative method...")
            
            # Fallback to music21 method
            success = self._convert_with_music21(musicxml_path, pdf_path)
            if success:
                print(f"✓ PDF generated successfully with music21: {pdf_path}")
                return pdf_path
            else:
                raise Exception("All PDF conversion methods failed")
                
        except Exception as e:
            print(f"✗ PDF conversion failed: {str(e)}")
            raise
    
    def _convert_with_musescore(self, musicxml_path, pdf_path):
        """
        Convert MusicXML to PDF using MuseScore
        
        Args:
            musicxml_path (str): Path to the input MusicXML file
            pdf_path (str): Path for the output PDF file
            
        Returns:
            bool: True if successful, False otherwise
        """
        
        try:
            import subprocess
            
            print("Using MuseScore for PDF conversion...")
            
            # Use xvfb-run to provide virtual display for MuseScore
            cmd = [
                'xvfb-run', '-a',
                'musescore3',
                '-o', pdf_path,
                musicxml_path
            ]
            
            # Run MuseScore conversion
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            if result.returncode == 0 and os.path.exists(pdf_path):
                print("✓ MuseScore conversion successful")
                return True
            else:
                print(f"✗ MuseScore conversion failed:")
                print(f"  Return code: {result.returncode}")
                if result.stderr:
                    print(f"  Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("✗ MuseScore conversion timed out")
            return False
        except Exception as e:
            print(f"✗ MuseScore conversion error: {str(e)}")
            return False
    
    def _convert_with_music21(self, musicxml_path, pdf_path):
        """
        Convert MusicXML to PDF using music21 (fallback method)
        
        Args:
            musicxml_path (str): Path to the input MusicXML file
            pdf_path (str): Path for the output PDF file
            
        Returns:
            bool: True if successful, False otherwise
        """
        
        try:
            print("Using music21 for PDF conversion...")
            
            # Load the MusicXML file
            score = converter.parse(musicxml_path)
            
            # Try to write as PDF
            score.write('musicxml.pdf', fp=pdf_path)
            
            if os.path.exists(pdf_path):
                print("✓ music21 conversion successful")
                return True
            else:
                print("✗ music21 conversion failed - PDF not created")
                return False
                
        except Exception as e:
            print(f"✗ music21 conversion error: {str(e)}")
            return False
    
    def convert_musicxml_to_png(self, musicxml_path, png_path=None, resolution=300):
        """
        Convert a MusicXML file to a PNG image
        
        Args:
            musicxml_path (str): Path to the input MusicXML file
            png_path (str, optional): Path for the output PNG file
            resolution (int): DPI resolution for the image
            
        Returns:
            str: Path to the generated PNG file
        """
        
        if not os.path.exists(musicxml_path):
            raise FileNotFoundError(f"MusicXML file not found: {musicxml_path}")
        
        # Generate output path if not provided
        if png_path is None:
            musicxml_stem = Path(musicxml_path).stem
            png_path = f"{musicxml_stem}_score.png"
        
        # Ensure output directory exists
        output_dir = Path(png_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"Converting MusicXML to PNG...")
            print(f"  - Input: {musicxml_path}")
            print(f"  - Output: {png_path}")
            print(f"  - Resolution: {resolution} DPI")
            
            import subprocess
            
            # Use MuseScore to convert to PNG
            cmd = [
                'xvfb-run', '-a',
                'musescore3',
                '-r', str(resolution),
                '-o', png_path,
                musicxml_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # MuseScore adds page numbers to PNG files (e.g., file-1.png)
                # Check for the actual generated file
                png_stem = Path(png_path).stem
                png_dir = Path(png_path).parent
                png_ext = Path(png_path).suffix
                
                # Look for files with page numbers
                generated_files = list(png_dir.glob(f"{png_stem}-*.png"))
                
                if generated_files:
                    # If multiple pages, return the first one or rename it
                    actual_file = generated_files[0]
                    if str(actual_file) != png_path:
                        # Rename the first page to the requested filename
                        import shutil
                        shutil.move(str(actual_file), png_path)
                    
                    print(f"✓ PNG generated successfully: {png_path}")
                    if len(generated_files) > 1:
                        print(f"  Note: {len(generated_files)} pages generated, using first page")
                    return png_path
                elif os.path.exists(png_path):
                    print(f"✓ PNG generated successfully: {png_path}")
                    return png_path
                else:
                    print(f"✗ PNG conversion failed: No output file found")
                    raise Exception("PNG conversion failed - no output file")
            else:
                print(f"✗ PNG conversion failed:")
                print(f"  Return code: {result.returncode}")
                if result.stderr:
                    print(f"  Error: {result.stderr}")
                raise Exception("PNG conversion failed")
                
        except subprocess.TimeoutExpired:
            raise Exception("PNG conversion timed out")
        except Exception as e:
            print(f"✗ PNG conversion failed: {str(e)}")
            raise
    
    def batch_convert_to_pdf(self, musicxml_files, output_dir=None):
        """
        Convert multiple MusicXML files to PDF
        
        Args:
            musicxml_files (list): List of MusicXML file paths
            output_dir (str, optional): Output directory for PDF files
            
        Returns:
            list: List of generated PDF file paths
        """
        
        results = []
        
        print(f"Batch converting {len(musicxml_files)} MusicXML files to PDF...")
        print("=" * 60)
        
        for i, musicxml_file in enumerate(musicxml_files, 1):
            print(f"\nProcessing file {i}/{len(musicxml_files)}: {musicxml_file}")
            
            try:
                # Setup output path
                if output_dir:
                    output_dir_path = Path(output_dir)
                    output_dir_path.mkdir(parents=True, exist_ok=True)
                    pdf_path = output_dir_path / f"{Path(musicxml_file).stem}_score.pdf"
                else:
                    pdf_path = None
                
                # Convert to PDF
                result_path = self.convert_musicxml_to_pdf(musicxml_file, str(pdf_path) if pdf_path else None)
                results.append(result_path)
                
                print(f"✓ File {i} converted successfully")
                
            except Exception as e:
                print(f"✗ File {i} conversion failed: {str(e)}")
                results.append(None)
        
        # Summary
        successful = sum(1 for r in results if r is not None)
        print(f"\nBatch conversion summary:")
        print(f"  - Total files: {len(musicxml_files)}")
        print(f"  - Successful: {successful}")
        print(f"  - Failed: {len(musicxml_files) - successful}")
        
        return results

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

