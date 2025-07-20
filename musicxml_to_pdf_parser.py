#!/usr/bin/env python3
"""
MusicXML to PDF Parser

This module converts MusicXML files to traditional visual music sheet PDFs
using music21 and various rendering backends.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
import xml.etree.ElementTree as ET

from music21 import converter, stream, metadata, tempo, key, meter
from music21 import layout, style, bar, clef, instrument
from music21.musicxml import xmlToM21
from music21.common import pathTools


class MusicXMLToPDFParser:
    """
    A comprehensive parser for converting MusicXML files to PDF sheet music
    """
    
    def __init__(self):
        """Initialize the parser with default settings"""
        self.supported_input_formats = ['.xml', '.musicxml', '.mxl']
        self.rendering_backends = ['musescore', 'lilypond', 'music21']
        self.default_backend = 'music21'
        
        # PDF generation settings
        self.pdf_settings = {
            'page_size': 'A4',
            'orientation': 'portrait',
            'margins': {'top': 20, 'bottom': 20, 'left': 15, 'right': 15},
            'staff_size': 20,
            'title_font_size': 16,
            'composer_font_size': 12,
            'lyric_font_size': 10
        }
        
        # Check available backends
        self.available_backends = self._check_available_backends()
        print(f"Available rendering backends: {self.available_backends}")
    
    def _check_available_backends(self) -> List[str]:
        """Check which rendering backends are available on the system"""
        available = ['music21']  # music21 is always available
        
        # Check for MuseScore
        try:
            result = subprocess.run(['mscore', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                available.append('musescore')
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            try:
                # Try alternative MuseScore command names
                result = subprocess.run(['musescore', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    available.append('musescore')
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                pass
        
        # Check for LilyPond
        try:
            result = subprocess.run(['lilypond', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                available.append('lilypond')
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass
        
        return available
    
    def validate_musicxml(self, xml_path: str) -> Dict[str, Any]:
        """
        Validate and analyze a MusicXML file
        
        Args:
            xml_path (str): Path to the MusicXML file
            
        Returns:
            Dict[str, Any]: Validation results and file information
        """
        if not os.path.exists(xml_path):
            raise FileNotFoundError(f"MusicXML file not found: {xml_path}")
        
        file_extension = Path(xml_path).suffix.lower()
        if file_extension not in self.supported_input_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        validation_result = {
            'valid': False,
            'file_path': xml_path,
            'file_size': os.path.getsize(xml_path),
            'format': file_extension,
            'errors': [],
            'warnings': [],
            'metadata': {}
        }
        
        try:
            # Basic XML validation
            if file_extension in ['.xml', '.musicxml']:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                
                # Check if it's a valid MusicXML file
                if root.tag not in ['score-partwise', 'score-timewise']:
                    validation_result['errors'].append("Not a valid MusicXML file (missing score root element)")
                    return validation_result
                
                # Extract basic metadata from XML
                work_title = root.find('.//work-title')
                if work_title is not None:
                    validation_result['metadata']['title'] = work_title.text
                
                creator = root.find('.//creator[@type="composer"]')
                if creator is not None:
                    validation_result['metadata']['composer'] = creator.text
                
                # Count parts
                parts = root.findall('.//score-part')
                validation_result['metadata']['num_parts'] = len(parts)
                
                # Get part names
                part_names = []
                for part in parts:
                    part_name = part.find('part-name')
                    if part_name is not None:
                        part_names.append(part_name.text)
                validation_result['metadata']['part_names'] = part_names
            
            # Try to load with music21 for deeper validation
            try:
                score = converter.parse(xml_path)
                validation_result['metadata']['duration'] = float(score.duration.quarterLength)
                validation_result['metadata']['num_measures'] = len(score.parts[0].getElementsByClass('Measure')) if score.parts else 0
                
                # Check for time signatures
                time_sigs = score.flat.getElementsByClass(meter.TimeSignature)
                if time_sigs:
                    validation_result['metadata']['time_signature'] = str(time_sigs[0])
                
                # Check for key signatures
                key_sigs = score.flat.getElementsByClass(key.KeySignature)
                if key_sigs:
                    validation_result['metadata']['key_signature'] = str(key_sigs[0])
                
                validation_result['valid'] = True
                
            except Exception as e:
                validation_result['errors'].append(f"music21 parsing error: {str(e)}")
        
        except ET.ParseError as e:
            validation_result['errors'].append(f"XML parsing error: {str(e)}")
        except Exception as e:
            validation_result['errors'].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    def load_musicxml(self, xml_path: str) -> stream.Score:
        """
        Load a MusicXML file into a music21 Score object
        
        Args:
            xml_path (str): Path to the MusicXML file
            
        Returns:
            stream.Score: The loaded musical score
        """
        print(f"Loading MusicXML file: {xml_path}")
        
        # Validate file first
        validation = self.validate_musicxml(xml_path)
        if not validation['valid']:
            raise ValueError(f"Invalid MusicXML file: {', '.join(validation['errors'])}")
        
        try:
            # Load the file using music21
            score = converter.parse(xml_path)
            
            print(f"✓ MusicXML loaded successfully")
            print(f"  - Title: {validation['metadata'].get('title', 'Unknown')}")
            print(f"  - Composer: {validation['metadata'].get('composer', 'Unknown')}")
            print(f"  - Parts: {validation['metadata'].get('num_parts', 0)}")
            print(f"  - Duration: {validation['metadata'].get('duration', 0)} quarter notes")
            
            return score
            
        except Exception as e:
            raise Exception(f"Failed to load MusicXML file: {str(e)}")
    
    def enhance_score_for_pdf(self, score: stream.Score, title: Optional[str] = None) -> stream.Score:
        """
        Enhance the score with better formatting for PDF output
        
        Args:
            score (stream.Score): The musical score
            title (str, optional): Custom title for the score
            
        Returns:
            stream.Score: Enhanced score
        """
        print("Enhancing score for PDF output...")
        
        try:
            # Ensure metadata exists
            if not score.metadata:
                score.metadata = metadata.Metadata()
            
            # Set title
            if title:
                score.metadata.title = title
            elif not score.metadata.title:
                score.metadata.title = 'Music Sheet'
            
            # Set composer if not present
            if not score.metadata.composer:
                score.metadata.composer = 'Unknown'
            
            # Add layout and style information
            score.insert(0, layout.PageLayout(
                pageHeight=297,  # A4 height in mm
                pageWidth=210,   # A4 width in mm
                leftMargin=self.pdf_settings['margins']['left'],
                rightMargin=self.pdf_settings['margins']['right'],
                topMargin=self.pdf_settings['margins']['top'],
                bottomMargin=self.pdf_settings['margins']['bottom']
            ))
            
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
            
            # Ensure all parts have proper clefs
            for part in score.parts:
                if not part.getElementsByClass(clef.Clef):
                    # Analyze the part to determine appropriate clef
                    notes = part.flat.notes
                    if notes:
                        pitches = []
                        for element in notes:
                            if hasattr(element, 'pitch'):
                                pitches.append(element.pitch.midi)
                            elif hasattr(element, 'pitches'):
                                pitches.extend([p.midi for p in element.pitches])
                        
                        if pitches:
                            avg_pitch = sum(pitches) / len(pitches)
                            if avg_pitch < 60:  # Below middle C
                                part.insert(0, clef.BassClef())
                            else:
                                part.insert(0, clef.TrebleClef())
                        else:
                            part.insert(0, clef.TrebleClef())
                
                # Ensure measures exist
                if not part.getElementsByClass('Measure'):
                    part.makeMeasures(inPlace=True)
            
            # Add system breaks for better page layout
            measures = score.parts[0].getElementsByClass('Measure')
            for i, measure in enumerate(measures):
                if (i + 1) % 4 == 0:  # Add system break every 4 measures
                    measure.insert(0, layout.SystemLayout(isNew=True))
            
            print("✓ Score enhanced for PDF output")
            return score
            
        except Exception as e:
            print(f"⚠ Warning: Score enhancement failed: {str(e)}")
            return score
    
    def convert_to_pdf_music21(self, score: stream.Score, output_path: str) -> str:
        """
        Convert score to PDF using music21's built-in capabilities
        
        Args:
            score (stream.Score): The musical score
            output_path (str): Path for the output PDF file
            
        Returns:
            str: Path to the generated PDF file
        """
        print("Converting to PDF using music21...")
        
        try:
            # Try multiple music21 output formats
            formats_to_try = ['musicxml.pdf', 'midi.pdf', 'png']
            
            for fmt in formats_to_try:
                try:
                    if fmt == 'png':
                        # For PNG, we'll create multiple images for each page
                        png_path = output_path.replace('.pdf', '.png')
                        score.write(fmt, fp=png_path)
                        if os.path.exists(png_path):
                            print(f"✓ PNG generated successfully using music21: {png_path}")
                            return png_path
                    else:
                        score.write(fmt, fp=output_path)
                        if os.path.exists(output_path):
                            print(f"✓ PDF generated successfully using music21 ({fmt})")
                            return output_path
                except Exception as format_error:
                    print(f"⚠ Format {fmt} failed: {str(format_error)}")
                    continue
            
            raise Exception("All music21 formats failed")
                
        except Exception as e:
            print(f"⚠ music21 PDF generation failed: {str(e)}")
            
            # Fallback: create enhanced MusicXML
            temp_xml = output_path.replace('.pdf', '_temp.musicxml')
            try:
                score.write('musicxml', fp=temp_xml)
                print(f"✓ Created temporary MusicXML: {temp_xml}")
                
                # Try to use external tools to convert XML to PDF
                if 'musescore' in self.available_backends:
                    return self._convert_with_musescore(temp_xml, output_path)
                elif 'lilypond' in self.available_backends:
                    return self._convert_with_lilypond(temp_xml, output_path)
                else:
                    print("⚠ No external converters available, keeping MusicXML format")
                    print("💡 To get PDF output, install MuseScore (https://musescore.org) or LilyPond (https://lilypond.org)")
                    final_path = output_path.replace('.pdf', '.musicxml')
                    if temp_xml != final_path:
                        os.rename(temp_xml, final_path)
                    return final_path
                    
            except Exception as e2:
                raise Exception(f"All conversion methods failed. music21: {str(e)}, fallback: {str(e2)}")
    
    def _convert_with_musescore(self, xml_path: str, pdf_path: str) -> str:
        """Convert MusicXML to PDF using MuseScore"""
        print("Converting with MuseScore...")
        
        try:
            # Try different MuseScore command names
            for cmd in ['mscore', 'musescore', 'musescore3', 'musescore4']:
                try:
                    result = subprocess.run([
                        cmd, xml_path, '-o', pdf_path
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0 and os.path.exists(pdf_path):
                        print(f"✓ PDF generated successfully using {cmd}")
                        # Clean up temporary XML
                        if xml_path.endswith('_temp.musicxml'):
                            os.remove(xml_path)
                        return pdf_path
                    
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            raise Exception("MuseScore conversion failed")
            
        except Exception as e:
            raise Exception(f"MuseScore conversion error: {str(e)}")
    
    def _convert_with_lilypond(self, xml_path: str, pdf_path: str) -> str:
        """Convert MusicXML to PDF using LilyPond"""
        print("Converting with LilyPond...")
        
        try:
            # LilyPond requires conversion from MusicXML to LY format first
            ly_path = xml_path.replace('.musicxml', '.ly')
            
            # Convert XML to LY
            result1 = subprocess.run([
                'musicxml2ly', xml_path, '-o', ly_path
            ], capture_output=True, text=True, timeout=30)
            
            if result1.returncode != 0:
                raise Exception(f"musicxml2ly failed: {result1.stderr}")
            
            # Convert LY to PDF
            result2 = subprocess.run([
                'lilypond', '--pdf', f'--output={Path(pdf_path).parent}', ly_path
            ], capture_output=True, text=True, timeout=60)
            
            if result2.returncode == 0 and os.path.exists(pdf_path):
                print("✓ PDF generated successfully using LilyPond")
                # Clean up temporary files
                if xml_path.endswith('_temp.musicxml'):
                    os.remove(xml_path)
                if os.path.exists(ly_path):
                    os.remove(ly_path)
                return pdf_path
            else:
                raise Exception(f"LilyPond failed: {result2.stderr}")
                
        except Exception as e:
            raise Exception(f"LilyPond conversion error: {str(e)}")
    
    def parse_musicxml_to_pdf(self, xml_path: str, output_path: Optional[str] = None, 
                             title: Optional[str] = None, backend: Optional[str] = None) -> str:
        """
        Main method to parse MusicXML and convert to PDF
        
        Args:
            xml_path (str): Path to the input MusicXML file
            output_path (str, optional): Path for the output PDF file
            title (str, optional): Custom title for the sheet music
            backend (str, optional): Rendering backend to use
            
        Returns:
            str: Path to the generated PDF file
        """
        # Generate output path if not provided
        if output_path is None:
            xml_stem = Path(xml_path).stem
            output_path = f"{xml_stem}_sheet.pdf"
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Select backend
        if backend is None:
            backend = self.default_backend
        
        if backend not in self.available_backends:
            print(f"⚠ Backend '{backend}' not available, using '{self.available_backends[0]}'")
            backend = self.available_backends[0]
        
        try:
            print(f"Converting MusicXML to PDF")
            print(f"Input: {xml_path}")
            print(f"Output: {output_path}")
            print(f"Backend: {backend}")
            
            # Load MusicXML file
            score = self.load_musicxml(xml_path)
            
            # Enhance score for PDF output
            enhanced_score = self.enhance_score_for_pdf(score, title)
            
            # Convert to PDF based on selected backend
            if backend == 'music21':
                result_path = self.convert_to_pdf_music21(enhanced_score, output_path)
            else:
                # For external backends, create temporary MusicXML first
                temp_xml = output_path.replace('.pdf', '_temp.musicxml')
                enhanced_score.write('musicxml', fp=temp_xml)
                
                if backend == 'musescore':
                    result_path = self._convert_with_musescore(temp_xml, output_path)
                elif backend == 'lilypond':
                    result_path = self._convert_with_lilypond(temp_xml, output_path)
                else:
                    raise ValueError(f"Unknown backend: {backend}")
            
            print(f"✓ PDF sheet music generated successfully!")
            print(f"  - Output file: {result_path}")
            
            return result_path
            
        except Exception as e:
            print(f"✗ PDF generation failed: {str(e)}")
            raise
    
    def batch_convert(self, input_dir: str, output_dir: str, 
                     backend: Optional[str] = None) -> List[str]:
        """
        Convert multiple MusicXML files to PDF
        
        Args:
            input_dir (str): Directory containing MusicXML files
            output_dir (str): Directory for output PDF files
            backend (str, optional): Rendering backend to use
            
        Returns:
            List[str]: List of generated PDF file paths
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all MusicXML files
        xml_files = []
        for ext in self.supported_input_formats:
            xml_files.extend(input_path.glob(f"*{ext}"))
        
        if not xml_files:
            print(f"No MusicXML files found in {input_dir}")
            return []
        
        print(f"Found {len(xml_files)} MusicXML files to convert")
        
        generated_files = []
        for xml_file in xml_files:
            try:
                output_file = output_path / f"{xml_file.stem}_sheet.pdf"
                result_path = self.parse_musicxml_to_pdf(
                    str(xml_file), str(output_file), backend=backend
                )
                generated_files.append(result_path)
                print(f"✓ Converted: {xml_file.name}")
                
            except Exception as e:
                print(f"✗ Failed to convert {xml_file.name}: {str(e)}")
        
        print(f"\nBatch conversion complete: {len(generated_files)}/{len(xml_files)} files converted")
        return generated_files


def main():
    """Command-line interface for the MusicXML to PDF parser"""
    if len(sys.argv) < 2:
        print("MusicXML to PDF Parser")
        print("Usage: python3 musicxml_to_pdf_parser.py <musicxml_file> [output_file] [title] [backend]")
        print("       python3 musicxml_to_pdf_parser.py --batch <input_dir> <output_dir> [backend]")
        print("")
        print("Backends: music21, musescore, lilypond")
        print("Examples:")
        print("  python3 musicxml_to_pdf_parser.py song.musicxml")
        print("  python3 musicxml_to_pdf_parser.py song.xml sheet.pdf 'My Song' musescore")
        print("  python3 musicxml_to_pdf_parser.py --batch ./xml_files ./pdf_output")
        sys.exit(1)
    
    parser = MusicXMLToPDFParser()
    
    try:
        if sys.argv[1] == '--batch':
            # Batch conversion mode
            if len(sys.argv) < 4:
                print("Batch mode requires input and output directories")
                sys.exit(1)
            
            input_dir = sys.argv[2]
            output_dir = sys.argv[3]
            backend = sys.argv[4] if len(sys.argv) > 4 else None
            
            generated_files = parser.batch_convert(input_dir, output_dir, backend)
            print(f"\n✓ Batch conversion complete! Generated {len(generated_files)} PDF files")
            
        else:
            # Single file conversion mode
            xml_file = sys.argv[1]
            output_file = sys.argv[2] if len(sys.argv) > 2 else None
            title = sys.argv[3] if len(sys.argv) > 3 else None
            backend = sys.argv[4] if len(sys.argv) > 4 else None
            
            output_path = parser.parse_musicxml_to_pdf(xml_file, output_file, title, backend)
            print(f"\n✓ Success! PDF generated: {output_path}")
    
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
