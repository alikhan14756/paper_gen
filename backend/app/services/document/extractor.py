import os
import json
import hashlib
import unicodedata
from typing import Dict, List, Any, Tuple
import pymupdf as fitz  # PyMuPDF modern import

class DocumentExtractor:
    @staticmethod
    def calculate_file_hash(file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalizes Unicode text preserving English & Urdu characters."""
        if not text:
            return ""
        # Normal Form C preserves combined Arabic/Urdu letters
        normalized = unicodedata.normalize("NFC", text)
        # Clean extra whitespace while preserving line breaks
        lines = [line.strip() for line in normalized.split("\n")]
        return "\n".join([line for line in lines if line])

    @staticmethod
    def evaluate_page_quality(page_text: str, page_number: int) -> Tuple[float, str]:
        """
        Calculates quality score (0.0 to 1.0) and status.
        Flags pages with negligible text as candidates for OCR.
        """
        char_count = len(page_text.strip())
        word_count = len(page_text.split())
        
        if char_count < 40 or word_count < 6:
            return 0.1, "ocr_needed"
        elif char_count < 150:
            return 0.6, "moderate_quality"
        else:
            return 0.95, "high_quality"

    @classmethod
    def extract_pdf_pages(cls, file_path: str, cache_path: str) -> Dict[str, Any]:
        """
        Extracts all pages from PDF file using PyMuPDF and saves JSON cache.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        doc = fitz.open(file_path)
        total_pages = len(doc)
        pages_data: List[Dict[str, Any]] = []

        for page_idx in range(total_pages):
            page = doc[page_idx]
            raw_text = page.get_text("text")
            cleaned_text = cls.normalize_text(raw_text)
            page_num = page_idx + 1
            quality_score, quality_flag = cls.evaluate_page_quality(cleaned_text, page_num)

            pages_data.append({
                "page_number": page_num,
                "text": cleaned_text,
                "char_count": len(cleaned_text),
                "quality_score": quality_score,
                "quality_flag": quality_flag,
            })

        # Save cache
        result = {
            "file_path": file_path,
            "total_pages": total_pages,
            "pages": pages_data,
        }

        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        doc.close()
        return result

    @classmethod
    def get_text_for_page_range(cls, cache_path: str, start_page: int, end_page: int) -> str:
        """Reads cached pages from start_page to end_page (inclusive, 1-based)."""
        if not os.path.exists(cache_path):
            return ""
        
        with open(cache_path, "r", encoding="utf-8") as f:
            cache = json.load(f)
            
        selected_texts = []
        for p in cache.get("pages", []):
            if start_page <= p["page_number"] <= end_page:
                selected_texts.append(f"--- PAGE {p['page_number']} ---\n" + p.get("text", ""))
                
        return "\n\n".join(selected_texts)
