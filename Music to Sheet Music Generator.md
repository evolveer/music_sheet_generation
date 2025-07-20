# Music to Sheet Music Generator

A complete Python solution for generating sheet music notation from both **video files** (MP4, AVI, MOV, etc.) and **audio files** (MP3, WAV, FLAC, etc.). This application extracts audio from videos or processes audio files directly, transcribes the music using AI-powered analysis, and generates professional sheet music notation.

## Features

- **Universal Input Support**: Process both video files and audio files directly
- **Audio Extraction**: Extract high-quality audio from video formats when needed
- **Music Transcription**: AI-powered music transcription using Spotify's Basic Pitch
- **Sheet Music Generation**: Generate professional sheet music in multiple formats
- **Batch Processing**: Convert multiple files at once (mixed video and audio)
- **Segment Processing**: Extract and convert specific time segments
- **Multiple Output Formats**: Support for MusicXML, PNG, PDF, and SVG
- **Command-Line Interface**: Easy-to-use CLI with comprehensive options
- **Format Auto-Detection**: Automatically detects file type and handles accordingly

## Installation

### Prerequisites

- Python 3.11 or higher
- FFmpeg (for video processing)
- System audio libraries

### Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libaubio-dev libaubio5 aubio-tools ffmpeg \
    libavcodec-dev libavformat-dev libavutil-dev libswresample-dev \
    libsndfile1-dev libsamplerate0-dev build-essential pkg-config

# macOS (using Homebrew)
brew install aubio ffmpeg libsndfile libsamplerate

# Windows
# Install FFmpeg from https://ffmpeg.org/download.html
# Add FFmpeg to your system PATH
```

### Install Python Dependencies

```bash
pip install moviepy basic-pitch music21 librosa mido pretty_midi
```

## Quick Start

### Basic Usage

Convert a video file to sheet music:
```bash
python3 mp4_to_sheet_music.py video.mp4
```

Convert an audio file to sheet music:
```bash
python3 mp4_to_sheet_music.py song.mp3
```

Convert a WAV audio file:
```bash
python3 mp4_to_sheet_music.py audio.wav
```

This will create an output directory with:
- Extracted/converted audio file (if needed)
- Transcribed MIDI file
- Sheet music notation (MusicXML)
- Simplified notation (MusicXML)

### Advanced Usage

```bash
# Specify output directory and formats
python3 mp4_to_sheet_music.py audio.wav -o output/ -af wav -sf musicxml

# Convert with custom title and keep intermediate files
python3 mp4_to_sheet_music.py song.flac -t "My Song" -k

# Convert a specific segment (30s to 60s) from video or audio
python3 mp4_to_sheet_music.py video.mp4 -s 30 -e 60
python3 mp4_to_sheet_music.py audio.mp3 -s 30 -e 60

# Batch convert multiple files (mixed video and audio)
python3 mp4_to_sheet_music.py video1.mp4 song1.mp3 audio.wav -o batch_output/

# Fine-tune transcription parameters
python3 mp4_to_sheet_music.py music.flac -ot 0.3 -ft 0.2
```

## Command-Line Options

```
positional arguments:
  input_files           Input video or audio file(s)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory
  -af {wav,mp3,flac}, --audio-format {wav,mp3,flac}
                        Audio format for processing (default: wav)
  -sf {musicxml,xml,png,pdf,svg}, --sheet-format {musicxml,xml,png,pdf,svg}
                        Sheet music format (default: musicxml)
  -ot ONSET_THRESHOLD, --onset-threshold ONSET_THRESHOLD
                        Note onset detection threshold (0.0-1.0, default: 0.5)
  -ft FRAME_THRESHOLD, --frame-threshold FRAME_THRESHOLD
                        Note frame detection threshold (0.0-1.0, default: 0.3)
  -s START_TIME, --start-time START_TIME
                        Start time for segment extraction (seconds)
  -e END_TIME, --end-time END_TIME
                        End time for segment extraction (seconds)
  -t TITLE, --title TITLE
                        Title for the sheet music
  -k, --keep-intermediate
                        Keep intermediate audio and MIDI files
```

### Supported File Formats

**Video Formats:**
- MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V

**Audio Formats:**
- WAV, MP3, FLAC, AAC, M4A, OGG, WMA

## Module Documentation

### AudioExtractor

Handles audio extraction from video files using MoviePy.

```python
from audio_extractor import AudioExtractor

extractor = AudioExtractor()

# Extract full audio
audio_path = extractor.extract_audio_from_video("video.mp4", "audio.wav")

# Extract segment
segment_path = extractor.extract_audio_segment("video.mp4", 30, 60, "segment.wav")

# Get audio info
info = extractor.get_audio_info("video.mp4")
```

### MusicTranscriber

Converts audio to MIDI using Basic Pitch and librosa.

```python
from music_transcriber import MusicTranscriber

transcriber = MusicTranscriber()

# Transcribe audio to MIDI
midi_path = transcriber.transcribe_audio_to_midi("audio.wav", "output.mid")

# Analyze audio features
features = transcriber.analyze_audio_features("audio.wav")

# Get MIDI information
midi_info = transcriber.get_midi_info("output.mid")
```

### SheetMusicGenerator

Generates sheet music from MIDI files using music21.

```python
from sheet_music_generator import SheetMusicGenerator

generator = SheetMusicGenerator()

# Generate sheet music
sheet_path = generator.generate_sheet_music("input.mid", "output.musicxml")

# Create simplified notation
simple_path = generator.create_simple_notation("input.mid", "simple.musicxml")

# Analyze musical content
score = generator.load_midi_to_music21("input.mid")
analysis = generator.analyze_musical_content(score)
```

## Output Formats

### Audio Formats
- **WAV**: Uncompressed, high quality (recommended)
- **MP3**: Compressed, smaller file size
- **FLAC**: Lossless compression

### Sheet Music Formats
- **MusicXML**: Standard format, widely supported (recommended)
- **PNG**: Image format for viewing
- **PDF**: Printable format
- **SVG**: Scalable vector graphics

## Transcription Parameters

### Onset Threshold (0.0-1.0)
Controls sensitivity for detecting note beginnings:
- **Lower values (0.2-0.4)**: More sensitive, detects subtle notes
- **Higher values (0.6-0.8)**: Less sensitive, only strong notes

### Frame Threshold (0.0-1.0)
Controls sensitivity for note continuation:
- **Lower values (0.1-0.3)**: Longer notes, more sustained sounds
- **Higher values (0.4-0.6)**: Shorter notes, more staccato

## Examples

### Example 1: Piano Recording (Audio File)

```bash
# Convert piano MP3 with high sensitivity
python3 mp4_to_sheet_music.py piano_recording.mp3 \
    -t "Piano Piece" \
    -ot 0.3 -ft 0.2 \
    -sf pdf
```

### Example 2: Guitar Performance (Video File)

```bash
# Convert guitar video with medium sensitivity
python3 mp4_to_sheet_music.py guitar_song.mp4 \
    -t "Guitar Solo" \
    -ot 0.5 -ft 0.3 \
    -s 60 -e 120
```

### Example 3: Vocal Melody (Audio File)

```bash
# Extract vocal melody from FLAC with low sensitivity
python3 mp4_to_sheet_music.py vocal_performance.flac \
    -t "Vocal Melody" \
    -ot 0.7 -ft 0.4 \
    -af wav -sf musicxml
```

### Example 4: Mixed Batch Processing

```bash
# Process multiple files of different types
python3 mp4_to_sheet_music.py \
    concert_video.mp4 \
    studio_recording.wav \
    demo_track.mp3 \
    live_performance.flac \
    -o batch_results/ \
    -t "Concert Collection"
```

## Troubleshooting

### Common Issues

1. **"No audio track found"**
   - Ensure the video file contains audio
   - Check if the video file is corrupted

2. **"MoviePy import failed"**
   - Install MoviePy: `pip install moviepy`
   - Install FFmpeg system dependency

3. **"Basic Pitch import failed"**
   - Install Basic Pitch: `pip install basic-pitch`
   - Ensure TensorFlow is properly installed

4. **"Sheet music generation failed"**
   - Install music21: `pip install music21`
   - For PNG/PDF output, install MuseScore or LilyPond

### Performance Tips

1. **Use WAV format** for best transcription quality
2. **Adjust thresholds** based on your audio type:
   - Solo instruments: Lower thresholds (0.3, 0.2)
   - Complex music: Higher thresholds (0.6, 0.4)
3. **Process segments** for long videos to improve accuracy
4. **Keep intermediate files** (`-k`) for debugging

## Technical Details

### File Processing Pipeline
1. **File Type Detection**: Automatically detects whether input is video or audio
2. **Audio Preparation**: 
   - For video files: Extract audio track using MoviePy
   - For audio files: Use directly or convert format if needed
3. **Format Standardization**: Convert to optimal format for transcription
4. **Quality Validation**: Verify audio properties and compatibility

### Audio Processing Pipeline
1. **Audio Loading**: Librosa loads and preprocesses audio
2. **Format Conversion**: Convert between audio formats as needed
3. **Segment Extraction**: Extract specific time ranges from audio/video
4. **Quality Analysis**: Analyze audio characteristics and properties

### Music Transcription Pipeline
1. **Audio Loading**: Librosa loads and preprocesses audio
2. **Feature Extraction**: Spectral and temporal features are analyzed
3. **AI Transcription**: Basic Pitch neural network predicts notes
4. **MIDI Generation**: Note events are converted to MIDI format
5. **Post-processing**: MIDI is cleaned and validated

### Sheet Music Generation Pipeline
1. **MIDI Loading**: Music21 parses the MIDI file
2. **Musical Analysis**: Key, tempo, and structure are analyzed
3. **Score Enhancement**: Formatting and metadata are added
4. **Notation Generation**: Visual notation is created
5. **Export**: Final sheet music is saved in the chosen format

## Limitations

- **Polyphonic Music**: Complex polyphonic music may not transcribe perfectly
- **Audio Quality**: Poor audio quality affects transcription accuracy
- **Instrument Recognition**: All instruments are transcribed as piano by default
- **Rhythm Complexity**: Very complex rhythms may be simplified
- **Background Noise**: Noisy audio can introduce false notes

## Contributing

This is a demonstration project. For production use, consider:
- Adding more robust error handling
- Implementing instrument-specific transcription
- Adding support for more audio/video formats
- Improving rhythm detection accuracy
- Adding GUI interface

## License

This project is provided as-is for educational and demonstration purposes.

## Dependencies

- **MoviePy**: Video and audio processing
- **Basic Pitch**: AI-powered music transcription (Spotify)
- **music21**: Music notation and analysis (MIT)
- **librosa**: Audio analysis and feature extraction
- **pretty_midi**: MIDI file handling
- **NumPy**: Numerical computing
- **TensorFlow**: Machine learning backend for Basic Pitch

## Version History

- **v1.1.0**: Added support for direct audio file input (MP3, WAV, FLAC, etc.)
  - Universal file type detection
  - Audio format conversion capabilities
  - Enhanced batch processing for mixed file types
  - Improved segment extraction for audio files
- **v1.0.0**: Initial release with complete MP4 to sheet music pipeline

