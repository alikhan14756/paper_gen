import os
import json
import pytest
import pymupdf as fitz
from app.services.document.extractor import DocumentExtractor
from app.services.chapter.detector import ChapterDetector
from app.services.ai.provider import GroundedMockProvider

def test_synthetic_pdf_extraction_and_chapters(tmp_path):
    pdf_path = str(tmp_path / "biology_grade10.pdf")
    cache_path = str(tmp_path / "biology_cache.json")

    # Create a 4-page synthetic textbook PDF with bookmarks and chapters
    doc = fitz.open()
    
    # Page 1: Chapter 1
    p1 = doc.new_page()
    p1.insert_text((50, 50), "Chapter 1: Cell Biology and Genetics\n\nCells are the fundamental units of all living organisms.\nEvery cell contains DNA inside the nucleus which encodes genetic instructions.\nMitosis is the process of cell division resulting in two identical daughter cells.")
    
    # Page 2: Chapter 1 cont.
    p2 = doc.new_page()
    p2.insert_text((50, 50), "Chapter 1 continued: Cellular Respiration\n\nMitochondria generate ATP through oxidative phosphorylation.\nGlucose is broken down during glycolysis to produce pyruvate.")

    # Page 3: Chapter 2
    p3 = doc.new_page()
    p3.insert_text((50, 50), "Chapter 2: Plant Physiology and Photosynthesis\n\nChloroplasts contain chlorophyll pigments that absorb sunlight.\nLight reactions convert water and carbon dioxide into glucose and oxygen.")

    # Page 4: Chapter 2 cont.
    p4 = doc.new_page()
    p4.insert_text((50, 50), "Chapter 2: Transpiration\n\nTranspiration is the evaporation of water from plant leaves through stomata.")

    # Add bookmarks TOC
    doc.set_toc([
        [1, "Chapter 1: Cell Biology", 1],
        [1, "Chapter 2: Plant Physiology", 3]
    ])
    doc.save(pdf_path)
    doc.close()

    # 1. Test Extraction
    extraction = DocumentExtractor.extract_pdf_pages(pdf_path, cache_path)
    assert extraction["total_pages"] == 4
    assert len(extraction["pages"]) == 4
    assert "Cell Biology" in extraction["pages"][0]["text"]
    assert os.path.exists(cache_path)

    # 2. Test Chapter Detection
    detected = ChapterDetector.detect_chapters(pdf_path, extraction["pages"])
    assert len(detected) == 2
    assert detected[0]["chapter_number"] == 1
    assert detected[0]["start_page"] == 1
    assert detected[0]["end_page"] == 2
    assert detected[1]["chapter_number"] == 2
    assert detected[1]["start_page"] == 3
    assert detected[1]["end_page"] == 4

    # 3. Test Grounded AI Generation
    source_ch1 = DocumentExtractor.get_text_for_page_range(cache_path, 1, 2)
    assert "Mitochondria" in source_ch1

    provider = GroundedMockProvider()
    import asyncio
    mcqs = asyncio.run(provider.generate_questions_for_section(
        section_title="Section A: MCQs",
        section_type="mcq",
        count=3,
        marks_per_question=1.0,
        language="en",
        subject="Biology",
        grade="Grade 10",
        source_text=source_ch1
    ))

    assert len(mcqs) == 3
    for q in mcqs:
        assert len(q["options"]) == 4
        assert q["correct_answer"] != ""
        assert q["marks"] == 1.0
