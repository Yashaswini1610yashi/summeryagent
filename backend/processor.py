import fitz  # PyMuPDF
from langdetect import detect
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict
import os

class DocProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len
        )

    def extract_text(self, pdf_path: str) -> str:
        """Extract all text from a PDF file."""
        print(f"Extracting text from: {pdf_path}")
        text = ""
        try:
            doc = fitz.open(pdf_path)
            print(f"PDF opened. Pages: {len(doc)}")
            for i, page in enumerate(doc):
                text += page.get_text()
                if (i+1) % 10 == 0:
                    print(f"Processed {i+1} pages...")
            doc.close()
            print("Extraction complete.")
        except Exception as e:
            print(f"Error extracting text: {e}")
            raise e
        return text

    def detect_language(self, text: str) -> str:
        """Detect the language of the document."""
        if not text.strip():
            return "unknown"
        try:
            return detect(text)
        except:
            return "en" # Fallback to English

    def chunk_text(self, text: str) -> List[str]:
        """Split large text into manageable chunks."""
        return self.text_splitter.split_text(text)

    def process_document(self, pdf_path: str) -> Dict:
        """Complete pipeline: extract, detect language, and chunk."""
        text = self.extract_text(pdf_path)
        lang = self.detect_language(text[:2000]) # Sample first 2k chars for detection
        chunks = self.chunk_text(text)
        
        return {
            "text": text,
            "language": lang,
            "chunks": chunks,
            "num_chunks": len(chunks)
        }
