from processor import DocProcessor
import os
import sys

def test_processor():
    processor = DocProcessor()
    # Create a dummy PDF if none exists or just test the logic
    print("Testing DocProcessor...")
    try:
        # Check if we can even import it and initialize
        print("Processor initialized.")
        
        # Test language detection on a string
        lang = processor.detect_language("Hello, this is a test document in English.")
        print(f"Detected language: {lang}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == "__main__":
    test_processor()
