# MusicXML to PDF Parser

A comprehensive Python parser that converts MusicXML files to traditional visual music sheet PDFs using music21 and various rendering backends.

## Features

- **Multiple Input Formats**: Supports `.xml`, `.musicxml`, and `.mxl` files
- **Multiple Rendering Backends**: music21, MuseScore, LilyPond
- **Comprehensive Validation**: Validates MusicXML files and extracts metadata
- **Enhanced Formatting**: Automatically enhances scores for better PDF output
- **Batch Processing**: Convert multiple files at once
- **Customizable Settings**: Configurable PDF layout, margins, fonts
- **Error Handling**: Robust error handling with fallback options
- **Command Line Interface**: Easy-to-use CLI
- **Programmatic API**: Use as a Python library

## Installation

Ensure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

The parser uses music21 as the core library, which is already included in your requirements.txt.

### Optional External Renderers

For better PDF output quality, you can install:

- **MuseScore**: Download from [musescore.org](https://musescore.org)
- **LilyPond**: Download from [lilypond.org](https://lilypond.org)

The parser will automatically detect and use available renderers.

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Convert MusicXML to PDF (or enhanced MusicXML if PDF rendering unavailable)
python3 musicxml_to_pdf_parser.py song.musicxml

# Specify output file
python3 musicxml_to_pdf_parser.py song.musicxml my_sheet.pdf

# Add custom title
python3 musicxml_to_pdf_parser.py song.musicxml sheet.pdf "My Beautiful Song"

# Use specific backend (if available)
python3 musicxml_to_pdf_parser.py song.musicxml sheet.pdf "My Song" musescore
```

#### Batch Processing
```bash
# Convert all MusicXML files in a directory
python3 musicxml_to_pdf_parser.py --batch ./xml_files ./pdf_output

# With specific backend
python3 musicxml_to_pdf_parser.py --batch ./xml_files ./pdf_output lilypond
```

### Programmatic Usage

```python
from musicxml_to_pdf_parser import MusicXMLToPDFParser

# Initialize parser
parser = MusicXMLToPDFParser()

# Basic conversion
output_path = parser.parse_musicxml_to_pdf('song.musicxml', 'sheet.pdf')

# With custom title and backend
output_path = parser.parse_musicxml_to_pdf(
    xml_path='song.musicxml',
    output_path='sheet.pdf',
    title='My Custom Title',
    backend='musescore'
)

# Validate a MusicXML file
validation = parser.validate_musicxml('song.musicxml')
print(f"Valid: {validation['valid']}")
print(f"Metadata: {validation['metadata']}")

# Batch conversion
generated_files = parser.batch_convert('./xml_files', './pdf_output')
```

### Customizing PDF Settings

```python
parser = MusicXMLToPDFParser()

# Modify PDF settings
parser.pdf_settings['margins']['top'] = 30
parser.pdf_settings['title_font_size'] = 18
parser.pdf_settings['page_size'] = 'A4'

# Convert with custom settings
output_path = parser.parse_musicxml_to_pdf('song.musicxml', 'custom_sheet.pdf')
```

## File Structure

```
musicxml_to_pdf_parser.py    # Main parser class
demo_parser.py               # Demo script showing all features
test_complete.musicxml       # Sample MusicXML file for testing
README_MusicXML_Parser.md    # This documentation
```

## Parser Features

### 1. MusicXML Validation
- Validates XML structure
- Checks MusicXML-specific elements
- Extracts metadata (title, composer, parts, etc.)
- Provides detailed error reporting

### 2. Score Enhancement
- Adds proper page layout for PDF output
- Ensures time and key signatures
- Adds appropriate clefs based on pitch analysis
- Inserts system breaks for better formatting
- Enhances metadata

### 3. Multiple Rendering Backends

#### music21 (Default)
- Always available
- Good for basic conversion
- Falls back to enhanced MusicXML if PDF generation fails

#### MuseScore (Optional)
- High-quality PDF output
- Professional music notation
- Requires MuseScore installation

#### LilyPond (Optional)
- Excellent typography
- Publication-quality output
- Requires LilyPond installation

### 4. Error Handling
- Graceful fallbacks when PDF generation fails
- Detailed error messages
- Validation before processing
- Cleanup of temporary files

## Configuration

### PDF Settings
```python
pdf_settings = {
    'page_size': 'A4',
    'orientation': 'portrait',
    'margins': {'top': 20, 'bottom': 20, 'left': 15, 'right': 15},
    'staff_size': 20,
    'title_font_size': 16,
    'composer_font_size': 12,
    'lyric_font_size': 10
}
```

### Supported Input Formats
- `.xml` - Standard MusicXML
- `.musicxml` - MusicXML with explicit extension
- `.mxl` - Compressed MusicXML

## Examples

### Example 1: Basic Conversion
```bash
python3 musicxml_to_pdf_parser.py test_complete.musicxml
```

### Example 2: Custom Title and Output
```bash
python3 musicxml_to_pdf_parser.py test_complete.musicxml "My Sheet.pdf" "Beautiful Music"
```

### Example 3: Batch Processing
```bash
mkdir xml_files pdf_output
cp test_complete.musicxml xml_files/
python3 musicxml_to_pdf_parser.py --batch xml_files pdf_output
```

### Example 4: Programmatic Usage
```python
# Run the demo to see all features
python3 demo_parser.py
```

## Output

The parser generates:
- PDF files (when external renderers are available)
- Enhanced MusicXML files (as fallback)
- Detailed console output with processing information
- Error messages and warnings

## Troubleshooting

### Common Issues

1. **"Cannot find mscore" error**
   - Install MuseScore from musescore.org
   - Or use music21 backend (default fallback)

2. **"Invalid MusicXML file" error**
   - Check if the XML file is complete and valid
   - Use the validation feature to diagnose issues

3. **"Unsupported file format" error**
   - Ensure file has .xml, .musicxml, or .mxl extension
   - Check file content is valid MusicXML

### Getting Better PDF Output

1. Install MuseScore for high-quality PDFs
2. Install LilyPond for publication-quality output
3. Customize PDF settings for your needs

## Integration

This parser integrates well with the existing music sheet generation project:
- Uses the same music21 library
- Compatible with existing MIDI to MusicXML workflows
- Can be used as the final step in audio → MIDI → MusicXML → PDF pipeline

## License

This parser is part of the Music Sheet Generation project and follows the same licensing terms.
