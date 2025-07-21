#!/usr/bin/env python3
"""
MusicXML to PDF Converter

A standalone tool for converting MusicXML files to visual music score PDFs.
This tool uses MuseScore for high-quality rendering and supports batch processing.

Author: Music Sheet Generator Project
Version: 1.0.0
"""

import os
import sys
import argparse
from pathlib import Path
import subprocess
import glob


class MusicXMLToPDFConverter:
    """
    Standalone converter for MusicXML files to PDF format
    """
    
    def __init__(self):
        self.temp_files = []
    
    def convert_to_pdf(self, musicxml_path, pdf_path=None, use_musescore=True):
        """
        Convert a MusicXML file to PDF
        
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
                    print(f"✓ PDF generated successfully: {pdf_path}")
                    return pdf_path
                else:
                    print("⚠ MuseScore conversion failed")
                    raise Exception("MuseScore conversion failed")
            else:
                raise Exception("Only MuseScore conversion is supported")
                
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
            print("Using MuseScore for PDF conversion...")
            
            # Check if MuseScore is available
            if not self._check_musescore():
                raise Exception("MuseScore not found. Please install MuseScore 3.")
            
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
                timeout=120  # 2 minute timeout
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
    
    def _check_musescore(self):
        """
        Check if MuseScore is available (tries musescore3, musescore, musescore4, mscore)
        
        Returns:
            bool: True if MuseScore is available, False otherwise
        """
        self.musescore_cmd = None
        candidates = ['musescore3', 'musescore', 'musescore4']
        for cmd in candidates:
            try:
                result = subprocess.run(['which', cmd], capture_output=True, text=True)
                if result.returncode == 0:
                    self.musescore_cmd = cmd
                    return True
            except Exception:
                continue
        return False
    
    def convert_to_png(self, musicxml_path, png_path=None, resolution=300):
        """
        Convert a MusicXML file to PNG image
        
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
            
            # Check if MuseScore is available
            if not self._check_musescore():
                raise Exception("MuseScore not found. Please install MuseScore 3.")
            
            # Use MuseScore to convert to PNG
            cmd = [
                'xvfb-run', '-a',
                getattr(self, 'musescore_cmd', 'mscore'),
                '-r', str(resolution),
                '-o', png_path,
                musicxml_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                # MuseScore adds page numbers to PNG files (e.g., file-1.png)
                # Check for the actual generated file
                png_stem = Path(png_path).stem
                png_dir = Path(png_path).parent
                
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
    
    def batch_convert(self, input_files, output_dir=None, output_format='pdf', resolution=300):
        """
        Convert multiple MusicXML files
        
        Args:
            input_files (list): List of MusicXML file paths
            output_dir (str, optional): Output directory
            output_format (str): Output format ('pdf' or 'png')
            resolution (int): DPI resolution for PNG output
            
        Returns:
            list: List of conversion results
        """
        
        results = []
        
        print(f"Batch converting {len(input_files)} MusicXML files to {output_format.upper()}...")
        print("=" * 60)
        
        for i, input_file in enumerate(input_files, 1):
            print(f"\nProcessing file {i}/{len(input_files)}: {input_file}")
            
            try:
                # Setup output path
                if output_dir:
                    output_dir_path = Path(output_dir)
                    output_dir_path.mkdir(parents=True, exist_ok=True)
                    output_path = output_dir_path / f"{Path(input_file).stem}_score.{output_format}"
                else:
                    output_path = None
                
                # Convert file
                if output_format.lower() == 'pdf':
                    result_path = self.convert_to_pdf(input_file, str(output_path) if output_path else None)
                elif output_format.lower() == 'png':
                    result_path = self.convert_to_png(input_file, str(output_path) if output_path else None, resolution)
                else:
                    raise ValueError(f"Unsupported output format: {output_format}")
                
                results.append({'file': input_file, 'output': result_path, 'success': True})
                print(f"✓ File {i} converted successfully")
                
            except Exception as e:
                print(f"✗ File {i} conversion failed: {str(e)}")
                results.append({'file': input_file, 'output': None, 'success': False, 'error': str(e)})
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        print(f"\nBatch conversion summary:")
        print(f"  - Total files: {len(input_files)}")
        print(f"  - Successful: {successful}")
        print(f"  - Failed: {len(input_files) - successful}")
        
        return results


def main():
    """
    Command-line interface for the MusicXML to PDF converter
    """
    
    parser = argparse.ArgumentParser(
        description="Convert MusicXML files to visual music score PDFs or PNGs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single MusicXML to PDF
  python3 musicxml_to_pdf.py score.musicxml
  
  # Convert to PNG with high resolution
  python3 musicxml_to_pdf.py score.musicxml -f png -r 600
  
  # Batch convert multiple files
  python3 musicxml_to_pdf.py *.musicxml -o output_pdfs/
  
  # Convert with custom output name
  python3 musicxml_to_pdf.py score.musicxml -o my_score.pdf
        """
    )
    
    # Input files
    parser.add_argument('input_files', nargs='+', 
                       help='Input MusicXML file(s)')
    
    # Output options
    parser.add_argument('-o', '--output', 
                       help='Output file or directory')
    parser.add_argument('-f', '--format', default='pdf',
                       choices=['pdf', 'png'],
                       help='Output format (default: pdf)')
    parser.add_argument('-r', '--resolution', type=int, default=300,
                       help='Resolution for PNG output (default: 300 DPI)')
    
    # Processing options
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Expand glob patterns
    input_files = []
    for pattern in args.input_files:
        if '*' in pattern or '?' in pattern:
            expanded = glob.glob(pattern)
            if expanded:
                input_files.extend(expanded)
            else:
                print(f"Warning: No files found matching pattern: {pattern}")
        else:
            input_files.append(pattern)
    
    if not input_files:
        print("Error: No input files specified")
        sys.exit(1)
    
    # Check input files exist
    for input_file in input_files:
        if not os.path.exists(input_file):
            print(f"Error: Input file not found: {input_file}")
            sys.exit(1)
        
        # Check if it's a MusicXML file
        if not input_file.lower().endswith(('.musicxml', '.xml')):
            print(f"Warning: File may not be MusicXML: {input_file}")
    
    # Create converter
    converter = MusicXMLToPDFConverter()
    
    try:
        # Single file conversion
        if len(input_files) == 1:
            input_file = input_files[0]
            
            if args.format == 'pdf':
                result = converter.convert_to_pdf(input_file, args.output)
            else:  # png
                result = converter.convert_to_png(input_file, args.output, args.resolution)
            
            print(f"\n✓ Conversion completed successfully!")
            print(f"Output file: {result}")
        
        # Batch conversion
        else:
            # For batch conversion, output should be a directory
            if args.output and not args.output.endswith('/'):
                output_dir = args.output
            else:
                output_dir = args.output
            
            results = converter.batch_convert(
                input_files,
                output_dir,
                args.format,
                args.resolution
            )
            
            # Exit with error if any conversion failed
            if not all(r['success'] for r in results):
                print(f"\nSome conversions failed. Check the output above for details.")
                sys.exit(1)
            else:
                print(f"\n✓ All conversions completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\nConversion interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
# This script is intended to be run as a standalone tool
