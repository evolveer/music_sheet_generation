#!/usr/bin/env python3
"""
Demo script for the MusicXML to PDF Parser

This script demonstrates how to use the MusicXMLToPDFParser class
to convert MusicXML files to traditional visual music sheets.
"""

from musicxml_to_pdf_parser import MusicXMLToPDFParser
import os


def demo_basic_conversion():
    """Demonstrate basic MusicXML to PDF conversion"""
    print("=== MusicXML to PDF Parser Demo ===\n")
    
    # Initialize the parser
    parser = MusicXMLToPDFParser()
    
    # Check if we have a test file
    test_file = "test_complete.musicxml"
    if not os.path.exists(test_file):
        print(f"Test file {test_file} not found. Please run the parser first to create it.")
        return
    
    print("1. Basic conversion with default settings:")
    try:
        output_path = parser.parse_musicxml_to_pdf(
            xml_path=test_file,
            output_path="demo_output.pdf",
            title="Demo Music Sheet"
        )
        print(f"   ✓ Generated: {output_path}\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
    
    print("2. Validation and analysis:")
    try:
        validation = parser.validate_musicxml(test_file)
        print(f"   File valid: {validation['valid']}")
        print(f"   File size: {validation['file_size']} bytes")
        print(f"   Format: {validation['format']}")
        
        if validation['metadata']:
            print("   Metadata:")
            for key, value in validation['metadata'].items():
                print(f"     - {key}: {value}")
        print()
    except Exception as e:
        print(f"   ✗ Validation error: {e}\n")
    
    print("3. Available backends:")
    print(f"   {parser.available_backends}")
    print(f"   Default backend: {parser.default_backend}\n")
    
    print("4. PDF Settings:")
    for key, value in parser.pdf_settings.items():
        print(f"   - {key}: {value}")


def demo_custom_settings():
    """Demonstrate parser with custom settings"""
    print("\n=== Custom Settings Demo ===\n")
    
    parser = MusicXMLToPDFParser()
    
    # Modify PDF settings
    parser.pdf_settings['margins']['top'] = 30
    parser.pdf_settings['margins']['bottom'] = 30
    parser.pdf_settings['title_font_size'] = 18
    
    test_file = "test_complete.musicxml"
    if os.path.exists(test_file):
        try:
            output_path = parser.parse_musicxml_to_pdf(
                xml_path=test_file,
                output_path="demo_custom.pdf",
                title="Custom Settings Demo"
            )
            print(f"✓ Generated with custom settings: {output_path}")
        except Exception as e:
            print(f"✗ Error: {e}")


def demo_error_handling():
    """Demonstrate error handling"""
    print("\n=== Error Handling Demo ===\n")
    
    parser = MusicXMLToPDFParser()
    
    # Test with non-existent file
    print("1. Testing with non-existent file:")
    try:
        parser.parse_musicxml_to_pdf("nonexistent.musicxml")
    except Exception as e:
        print(f"   ✓ Correctly caught error: {e}")
    
    # Test with invalid file format
    print("\n2. Testing with invalid file format:")
    try:
        # Create a dummy text file
        with open("test.txt", "w") as f:
            f.write("This is not a MusicXML file")
        
        parser.parse_musicxml_to_pdf("test.txt")
    except Exception as e:
        print(f"   ✓ Correctly caught error: {e}")
        # Clean up
        if os.path.exists("test.txt"):
            os.remove("test.txt")


def show_usage_examples():
    """Show various usage examples"""
    print("\n=== Usage Examples ===\n")
    
    examples = [
        "# Basic usage:",
        "python3 musicxml_to_pdf_parser.py song.musicxml",
        "",
        "# With custom output file:",
        "python3 musicxml_to_pdf_parser.py song.musicxml my_sheet.pdf",
        "",
        "# With custom title:",
        "python3 musicxml_to_pdf_parser.py song.musicxml sheet.pdf 'My Beautiful Song'",
        "",
        "# With specific backend (if available):",
        "python3 musicxml_to_pdf_parser.py song.musicxml sheet.pdf 'My Song' musescore",
        "",
        "# Batch conversion:",
        "python3 musicxml_to_pdf_parser.py --batch ./xml_files ./pdf_output",
        "",
        "# Programmatic usage:",
        "from musicxml_to_pdf_parser import MusicXMLToPDFParser",
        "parser = MusicXMLToPDFParser()",
        "output = parser.parse_musicxml_to_pdf('song.musicxml', 'sheet.pdf')"
    ]
    
    for example in examples:
        print(example)


def main():
    """Run all demos"""
    demo_basic_conversion()
    demo_custom_settings()
    demo_error_handling()
    show_usage_examples()
    
    print("\n=== Demo Complete ===")
    print("The MusicXML to PDF Parser is ready to use!")
    print("Check the generated files in the current directory.")


if __name__ == "__main__":
    main()
