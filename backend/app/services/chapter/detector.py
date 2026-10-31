import re
from typing import List, Dict, Any
import fitz

class ChapterDetector:
    CHAPTER_PATTERNS_EN = [
        re.compile(r"^(?:chapter|unit|lesson)\s*(\d+|[ivxlcdm]+)[:\.\-\s]+(.*)$", re.IGNORECASE),
        re.compile(r"^(?:chapter|unit|lesson)\s*(\d+|[ivxlcdm]+)$", re.IGNORECASE),
    ]

    CHAPTER_PATTERNS_UR = [
        re.compile(r"^(?:باب|سبق|یونٹ)\s*(?:نمبر)?\s*([۰-۹\d]+)[:\.\-\s]*(.*)$"),
        re.compile(r"^(?:باب|سبق|یونٹ)\s*(?:نمبر)?\s*([۰-۹\d]+)$"),
    ]

    @classmethod
    def detect_chapters(cls, file_path: str, pages_cache: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detects chapters using TOC bookmarks first, then text regex heuristics,
        and finally fallback partitioning.
        """
        total_pages = len(pages_cache)
        if total_pages == 0:
            return []

        # 1. Attempt PDF Table of Contents bookmarks
        toc_chapters = cls._detect_from_pdf_toc(file_path, total_pages)
        if toc_chapters and len(toc_chapters) >= 1:
            return toc_chapters

        # 2. Attempt Text Regex scanning on page headers
        text_chapters = cls._detect_from_page_text(pages_cache, total_pages)
        if text_chapters and len(text_chapters) >= 1:
            return text_chapters

        # 3. Fallback: create reasonable chunks (e.g. 10-15 pages per chapter)
        return cls._fallback_chapters(total_pages)

    @classmethod
    def _detect_from_pdf_toc(cls, file_path: str, total_pages: int) -> List[Dict[str, Any]]:
        try:
            doc = fitz.open(file_path)
            toc = doc.get_toc()  # returns [[lvl, title, page, ...], ...]
            doc.close()
            
            if not toc:
                return []

            # Filter top-level or level-1 entries
            top_entries = [entry for entry in toc if entry[0] <= 2 and entry[2] > 0]
            if not top_entries:
                return []

            detected = []
            for i, entry in enumerate(top_entries):
                title = entry[1].strip()
                start_p = max(1, entry[2])
                # end page is either next chapter's start - 1, or total_pages
                if i + 1 < len(top_entries):
                    next_start = max(start_p, top_entries[i + 1][2])
                    end_p = max(start_p, next_start - 1)
                else:
                    end_p = total_pages

                detected.append({
                    "chapter_number": i + 1,
                    "title": title or f"Chapter {i + 1}",
                    "start_page": start_p,
                    "end_page": min(end_p, total_pages),
                    "is_detected": True,
                    "confidence": 0.9,
                    "detection_method": "pdf_toc_bookmarks",
                })
            return detected
        except Exception:
            return []

    @classmethod
    def _detect_from_page_text(cls, pages_cache: List[Dict[str, Any]], total_pages: int) -> List[Dict[str, Any]]:
        found_markers = []

        for p in pages_cache:
            p_num = p["page_number"]
            lines = p["text"].split("\n")[:10]  # Check top 10 lines of page

            for line in lines:
                line_clean = line.strip()
                # Check English
                for pat in cls.CHAPTER_PATTERNS_EN:
                    m = pat.match(line_clean)
                    if m:
                        num_str = m.group(1)
                        title_str = m.group(2).strip() if len(m.groups()) > 1 and m.group(2) else f"Chapter {num_str}"
                        found_markers.append((p_num, title_str))
                        break
                
                # Check Urdu
                for pat in cls.CHAPTER_PATTERNS_UR:
                    m = pat.match(line_clean)
                    if m:
                        num_str = m.group(1)
                        title_str = m.group(2).strip() if len(m.groups()) > 1 and m.group(2) else f"باب {num_str}"
                        found_markers.append((p_num, title_str))
                        break

        if not found_markers:
            return []

        # Deduplicate and sort
        detected = []
        for i, (start_p, title) in enumerate(found_markers):
            if i + 1 < len(found_markers):
                next_p = found_markers[i + 1][0]
                end_p = max(start_p, next_p - 1)
            else:
                end_p = total_pages

            detected.append({
                "chapter_number": i + 1,
                "title": title,
                "start_page": start_p,
                "end_page": min(end_p, total_pages),
                "is_detected": True,
                "confidence": 0.8,
                "detection_method": "heading_heuristics",
            })
        return detected

    @classmethod
    def _fallback_chapters(cls, total_pages: int) -> List[Dict[str, Any]]:
        chunk_size = 15
        chapters = []
        chap_num = 1
        curr_page = 1
        
        while curr_page <= total_pages:
            end_page = min(curr_page + chunk_size - 1, total_pages)
            chapters.append({
                "chapter_number": chap_num,
                "title": f"Chapter {chap_num} (Pages {curr_page}-{end_page})",
                "start_page": curr_page,
                "end_page": end_page,
                "is_detected": False,
                "confidence": 0.5,
                "detection_method": "fallback_partition",
            })
            curr_page = end_page + 1
            chap_num += 1

        return chapters
