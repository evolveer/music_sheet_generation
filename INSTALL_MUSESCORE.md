# Installing MuseScore for PDF Output

To get high-quality PDF output from the MusicXML parser, you can install MuseScore, which is a free and open-source music notation software.

## Installation Instructions

### Ubuntu/Debian Linux
```bash
# Update package list
sudo apt update

# Install MuseScore
sudo apt install musescore3

# Or for newer versions
sudo apt install musescore
```

### Alternative: AppImage (Recommended for Linux)
```bash
# Download the latest MuseScore AppImage
wget https://github.com/musescore/MuseScore/releases/download/v4.2.1/MuseScore-4.2.1.232071203-x86_64.AppImage

# Make it executable
chmod +x MuseScore-4.2.1.232071203-x86_64.AppImage

# Create a symlink for easy access
sudo ln -s $(pwd)/MuseScore-4.2.1.232071203-x86_64.AppImage /usr/local/bin/musescore
```

### Snap Package
```bash
sudo snap install musescore
```

### Flatpak
```bash
flatpak install flathub org.musescore.MuseScore
```

## Verification

After installation, verify MuseScore is available:

```bash
# Check if MuseScore is installed
musescore --version

# Or try alternative command names
mscore --version
musescore3 --version
musescore4 --version
```

## Testing with the Parser

Once MuseScore is installed, test the parser:

```bash
# The parser should now detect MuseScore
python3 musicxml_to_pdf_parser.py test_complete.musicxml test_output.pdf

# You should see output like:
# Available rendering backends: ['music21', 'musescore']
# ✓ PDF generated successfully using musescore
```

## Troubleshooting

### Command Not Found
If you get "command not found" errors:

1. **Check installation path**: MuseScore might be installed with a different name
2. **Add to PATH**: Make sure MuseScore is in your system PATH
3. **Use full path**: You can modify the parser to use the full path to MuseScore

### Permission Issues
If you get permission errors:
```bash
# Make sure MuseScore is executable
chmod +x /path/to/musescore
```

### Alternative: Manual Path Configuration
If MuseScore is installed but not detected, you can modify the parser to use a specific path:

```python
# In musicxml_to_pdf_parser.py, modify the _check_available_backends method
def _check_available_backends(self) -> List[str]:
    available = ['music21']
    
    # Add custom MuseScore paths
    musescore_paths = [
        '/usr/bin/musescore',
        '/usr/bin/mscore',
        '/snap/bin/musescore',
        '/usr/local/bin/musescore',
        # Add your custom path here
    ]
    
    for path in musescore_paths:
        if os.path.exists(path):
            available.append('musescore')
            break
    
    return available
```

## Benefits of MuseScore

With MuseScore installed, you'll get:
- High-quality PDF output
- Professional music notation
- Better layout and formatting
- Support for complex musical elements
- Faster rendering than fallback methods

## Alternative: LilyPond

For even higher quality output, you can also install LilyPond:

```bash
sudo apt install lilypond
```

LilyPond provides publication-quality music typesetting but has a steeper learning curve.
