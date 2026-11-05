import os
import re
from typing import Dict, Any, List, Optional
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

class DocxGenerator:
    @staticmethod
    def set_paragraph_rtl(paragraph):
        """Applies Word OpenXML paragraph-level bidi/RTL property."""
        pPr = paragraph._element.get_or_add_pPr()
        bidi = OxmlElement('w:bidi')
        bidi.set(qn('w:val'), '1')
        pPr.append(bidi)

    @staticmethod
    def set_run_rtl(run, font_name="Arial"):
        """Applies Word OpenXML run-level RTL property and complex script font."""
        rPr = run._element.get_or_add_rPr()
        rtl = OxmlElement('w:rtl')
        rtl.set(qn('w:val'), '1')
        rPr.append(rtl)
        
        rFonts = rPr.find(qn('w:rFonts'))
        if rFonts is None:
            rFonts = OxmlElement('w:rFonts')
            rPr.append(rFonts)
        rFonts.set(qn('w:cs'), font_name)
        rFonts.set(qn('w:ascii'), font_name)
        rFonts.set(qn('w:hAnsi'), font_name)

    @staticmethod
    def set_table_rtl(table):
        """Sets table-level visual Right-to-Left order so columns visually flow RTL."""
        tblPr = table._element.xpath('w:tblPr')
        if tblPr:
            bidi = parse_xml(f'<w:bidiVisual {nsdecls("w")}/>')
            tblPr[0].append(bidi)

    @staticmethod
    def clean_text_references(text: str) -> str:
        """Removes textbook page numbers, chapter page references, and context markers."""
        if not text:
            return ""
        patterns = [
            r"\[\s*(?:Page|صفحہ|Book|Ref|Context)[^\]]*\]",
            r"\(\s*(?:Page|صفحہ|Book|Ref|Context)[^\)]*\)",
            r"(?:Page\s*context\s*#\s*\d+)",
            r"(?:Page\s*\d+(?:\s*[-–]\s*\d+)?)",
            r"(?:صفحہ\s*(?:نمبر)?\s*[:\s]*[\d\u0660-\u0669]+(?:\s*[-–]\s*[\d\u0660-\u0669]+)?)",
            r"(?:Source\s*reference\s*:[^\.\n]+)",
        ]
        cleaned = text
        for p in patterns:
            cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    @classmethod
    def format_mcq_options_with_bubbles(cls, raw_options: List[str], is_urdu: bool) -> List[str]:
        """
        Formats MCQ options with authentic BISEP board rounded fill circles (bubbles) ◯.
        English: (A) ◯ Option Text
        Urdu:    (الف) ◯ آپشن متن
        """
        formatted = []
        urdu_letters = ["الف", "ب", "ج", "د", "ہ"]
        eng_letters = ["A", "B", "C", "D", "E"]

        for idx, opt in enumerate(raw_options):
            cleaned_opt = cls.clean_text_references(str(opt))
            # Strip existing leading labels like 'A.', '(A)', 'الف)', 'الف -', '1.'
            cleaned_opt = re.sub(r"^(?:[A-Ea-e\d]|الف|ب|ج|د|ہ|[\u0627-\u064A])[\.\)\-\:\s]+\s*", "", cleaned_opt).strip()
            cleaned_opt = re.sub(r"^\((?:[A-Ea-e\d]|الف|ب|ج|د|ہ|[\u0627-\u064A])\)\s*", "", cleaned_opt).strip()
            cleaned_opt = re.sub(r"^\[(?:[A-Ea-e\d]|الف|ب|ج|د|ہ|[\u0627-\u064A])\]\s*", "", cleaned_opt).strip()
            cleaned_opt = re.sub(r"^[◯○●\s]+", "", cleaned_opt).strip()

            if is_urdu:
                letter = urdu_letters[idx] if idx < len(urdu_letters) else str(idx + 1)
                bubble_opt = f"({letter}) ◯  {cleaned_opt}"
            else:
                letter = eng_letters[idx] if idx < len(eng_letters) else str(idx + 1)
                bubble_opt = f"({letter}) ◯  {cleaned_opt}"

            formatted.append(bubble_opt)
        return formatted

    @classmethod
    def generate_exam_docx(
        cls,
        paper_data: Dict[str, Any],
        school_info: Dict[str, Any],
        output_path: str,
        include_answer_key: bool = True
    ) -> str:
        """
        Generates an authentic BISEP Board (Board of Intermediate & Secondary Education)
        pattern examination paper in editable Microsoft Word (.docx) format with full Urdu RTL support.
        """
        doc = Document()
        
        # Professional standard margins: 0.65 in
        for section in doc.sections:
            section.top_margin = Inches(0.65)
            section.bottom_margin = Inches(0.65)
            section.left_margin = Inches(0.65)
            section.right_margin = Inches(0.65)

        is_urdu = paper_data.get("language") == "ur"
        urdu_font = "Noto Nastaliq Urdu" if is_urdu else "Arial"
        base_font = urdu_font if is_urdu else "Times New Roman"

        # -------------------------------------------------------------
        # 1. School & BISEP Board Header
        # -------------------------------------------------------------
        school_name = school_info.get("name") or "PAKISTAN MODEL SCHOOL"
        
        # School Name Banner (Prominent Bold Header)
        p_school = doc.add_paragraph()
        p_school.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_school.paragraph_format.space_after = Pt(2)
        if is_urdu:
            cls.set_paragraph_rtl(p_school)

        r_school = p_school.add_run(school_name.upper())
        r_school.font.name = base_font
        r_school.font.size = Pt(17)
        r_school.font.bold = True
        r_school.font.color.rgb = RGBColor(15, 23, 42) # Deep slate navy
        if is_urdu:
            cls.set_run_rtl(r_school, urdu_font)

        # BISEP Board Subtitle
        p_board = doc.add_paragraph()
        p_board.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_board.paragraph_format.space_after = Pt(3)
        if is_urdu:
            cls.set_paragraph_rtl(p_board)

        board_title = (
            "بورڈ آف انٹرمیڈیٹ اینڈ سیکنڈری ایجوکیشن پیٹرن امتحانات"
            if is_urdu else
            "BOARD OF INTERMEDIATE & SECONDARY EDUCATION (BISE) PATTERN"
        )
        r_board = p_board.add_run(board_title)
        r_board.font.name = base_font
        r_board.font.size = Pt(10.5)
        r_board.font.bold = True
        r_board.font.color.rgb = RGBColor(71, 85, 105)
        if is_urdu:
            cls.set_run_rtl(r_board, urdu_font)

        # Exam Title & Academic Session
        p_exam = doc.add_paragraph()
        p_exam.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_exam.paragraph_format.space_after = Pt(8)
        if is_urdu:
            cls.set_paragraph_rtl(p_exam)

        exam_title = f"{paper_data.get('title', 'Examination')} — Session {paper_data.get('academic_session', '2025-2026')}"
        r_exam = p_exam.add_run(exam_title)
        r_exam.font.name = base_font
        r_exam.font.size = Pt(12)
        r_exam.font.bold = True
        r_exam.font.underline = True
        if is_urdu:
            cls.set_run_rtl(r_exam, urdu_font)

        # -------------------------------------------------------------
        # 2. Examination Meta Table (Subject, Class, Time, Marks)
        # -------------------------------------------------------------
        meta_table = doc.add_table(rows=2, cols=4)
        meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        meta_table.autofit = False

        if is_urdu:
            cls.set_table_rtl(meta_table)
            fields = [
                ("مضمون:", paper_data.get("subject", "")),
                ("جماعت:", f"جماعت {paper_data.get('grade', '')}"),
                ("کل وقت:", f"{paper_data.get('time_allowed_minutes', 120)} منٹ"),
                ("کل نمبر:", f"{paper_data.get('total_marks', 50)}"),
            ]
        else:
            fields = [
                ("SUBJECT:", paper_data.get("subject", "").upper()),
                ("CLASS / GRADE:", f"{paper_data.get('grade', '')}TH"),
                ("TIME ALLOWED:", f"{paper_data.get('time_allowed_minutes', 120)} Minutes"),
                ("MAXIMUM MARKS:", str(paper_data.get("total_marks", 50))),
            ]

        for i, (label, val) in enumerate(fields):
            r_idx = 0 if i < 2 else 1
            c_idx = (i % 2) * 2

            c_lbl = meta_table.cell(r_idx, c_idx)
            c_val = meta_table.cell(r_idx, c_idx + 1)
            
            p_l = c_lbl.paragraphs[0]
            p_v = c_val.paragraphs[0]
            p_l.paragraph_format.space_after = Pt(2)
            p_v.paragraph_format.space_after = Pt(2)

            if is_urdu:
                cls.set_paragraph_rtl(p_l)
                cls.set_paragraph_rtl(p_v)
                p_l.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                p_v.alignment = WD_ALIGN_PARAGRAPH.RIGHT

            run_l = p_l.add_run(label)
            run_l.font.name = base_font
            run_l.font.bold = True
            run_l.font.size = Pt(10)
            if is_urdu:
                cls.set_run_rtl(run_l, urdu_font)

            run_v = p_v.add_run(val)
            run_v.font.name = base_font
            run_v.font.size = Pt(10)
            if is_urdu:
                cls.set_run_rtl(run_v, urdu_font)

        # Style table borders
        for row in meta_table.rows:
            for cell in row.cells:
                tcPr = cell._element.get_or_add_tcPr()
                tcBorders = parse_xml(
                    f'<w:tcBorders {nsdecls("w")}>'
                    f'<w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
                    f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
                    f'<w:left w:val="none"/>'
                    f'<w:right w:val="none"/>'
                    f'</w:tcBorders>'
                )
                tcPr.append(tcBorders)

        # -------------------------------------------------------------
        # 3. BISEP Candidate Roll Number & Identification Block
        # -------------------------------------------------------------
        roll_table = doc.add_table(rows=2, cols=2)
        roll_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        roll_table.autofit = False

        if is_urdu:
            cls.set_table_rtl(roll_table)

        c00 = roll_table.cell(0, 0).paragraphs[0]
        c01 = roll_table.cell(0, 1).paragraphs[0]
        c10 = roll_table.cell(1, 0).paragraphs[0]
        c11 = roll_table.cell(1, 1).paragraphs[0]

        if is_urdu:
            cls.set_paragraph_rtl(c00)
            cls.set_paragraph_rtl(c01)
            cls.set_paragraph_rtl(c10)
            cls.set_paragraph_rtl(c11)
            c00.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            c01.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            c10.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            c11.alignment = WD_ALIGN_PARAGRAPH.RIGHT

            r_roll = c00.add_run("رول نمبر (ہندسوں میں): [  ][  ][  ][  ][  ][  ]")
            r_wrd = c01.add_run("رول نمبر (الفاظ میں): ______________________")
            r_name = c10.add_run("طالب علم کا نام: ___________________________")
            r_sig = c11.add_run("نگران کے دستخط: ___________________________")
        else:
            r_roll = c00.add_run("Roll No. (in Figures): [  ][  ][  ][  ][  ][  ]")
            r_wrd = c01.add_run("Roll No. (in Words): ______________________")
            r_name = c10.add_run("Candidate Name: __________________________")
            r_sig = c11.add_run("Invigilator Signature: ______________________")

        for r_item in [r_roll, r_wrd, r_name, r_sig]:
            r_item.font.name = base_font
            r_item.font.size = Pt(9.5)
            r_item.font.italic = True
            if is_urdu:
                cls.set_run_rtl(r_item, urdu_font)

        for row in roll_table.rows:
            for cell in row.cells:
                tcPr = cell._element.get_or_add_tcPr()
                tcBorders = parse_xml(
                    f'<w:tcBorders {nsdecls("w")}>'
                    f'<w:top w:val="single" w:sz="6" w:space="0" w:color="94A3B8"/>'
                    f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="94A3B8"/>'
                    f'<w:left w:val="single" w:sz="6" w:space="0" w:color="94A3B8"/>'
                    f'<w:right w:val="single" w:sz="6" w:space="0" w:color="94A3B8"/>'
                    f'</w:tcBorders>'
                )
                tcPr.append(tcBorders)

        # General Note
        raw_instructions = paper_data.get("instructions") or ""
        cleaned_instructions = cls.clean_text_references(raw_instructions) or (
            "تمام سوالات کے جوابات پرچہ سوالات کی ہدایات کے مطابق تحریر کریں۔"
            if is_urdu else
            "Read the questions carefully and answer according to the marks allocated in each section."
        )
        p_inst = doc.add_paragraph()
        p_inst.paragraph_format.space_before = Pt(8)
        p_inst.paragraph_format.space_after = Pt(8)
        if is_urdu:
            cls.set_paragraph_rtl(p_inst)
            p_inst.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            r_i = p_inst.add_run(f"عام ہدایات: {cleaned_instructions}")
        else:
            r_i = p_inst.add_run(f"GENERAL NOTE: {cleaned_instructions}")
        r_i.font.name = base_font
        r_i.font.size = Pt(9)
        r_i.font.italic = True
        r_i.font.color.rgb = RGBColor(71, 85, 105)
        if is_urdu:
            cls.set_run_rtl(r_i, urdu_font)

        # -------------------------------------------------------------
        # 4. Sections & Questions (BISEP Board Partitioning)
        # -------------------------------------------------------------
        sections = paper_data.get("sections", [])
        for s_idx, sec in enumerate(sections):
            if s_idx == 1:
                # Force Page Break between Objective (Section A) and Subjective (Section B & C)
                doc.add_page_break()
            sec_type = sec.get("section_type", "mcq")
            total_sec_m = sec.get("total_section_marks", 0)
            attempt = sec.get("questions_to_attempt", sec.get("total_questions", 0))
            sec_title = sec.get("title", f"Section {s_idx + 1}")

            # Section Header Bar
            p_sh = doc.add_paragraph()
            p_sh.paragraph_format.space_before = Pt(14)
            p_sh.paragraph_format.space_after = Pt(4)
            p_sh.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if is_urdu:
                cls.set_paragraph_rtl(p_sh)

            if is_urdu:
                s_header_text = f"― {sec_title} (کل نمبر: {total_sec_m}) ―"
            else:
                s_header_text = f"― {sec_title.upper()} (Marks: {total_sec_m}) ―"

            r_sh = p_sh.add_run(s_header_text)
            r_sh.font.name = base_font
            r_sh.font.size = Pt(12)
            r_sh.font.bold = True
            r_sh.font.color.rgb = RGBColor(15, 23, 42)
            if is_urdu:
                cls.set_run_rtl(r_sh, urdu_font)

            # Section Note / Attempt Rule
            p_sn = doc.add_paragraph()
            p_sn.paragraph_format.space_after = Pt(6)
            sec_instructions = cls.clean_text_references(sec.get("instructions") or "")

            if is_urdu:
                cls.set_paragraph_rtl(p_sn)
                p_sn.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                note_text = sec_instructions or f"نوٹ: اس حصے سے کوئی سے {attempt} سوالات حل کریں۔ تمام سوالات کے نمبر یکساں ہیں۔"
                r_sn = p_sn.add_run(note_text)
            else:
                note_text = sec_instructions or f"Note: Attempt any {attempt} questions from this section. All questions carry equal marks."
                r_sn = p_sn.add_run(note_text)

            r_sn.font.name = base_font
            r_sn.font.size = Pt(9.5)
            r_sn.font.italic = True
            r_sn.font.bold = True
            if is_urdu:
                cls.set_run_rtl(r_sn, urdu_font)

            # Questions inside Section
            questions = sec.get("questions", [])
            for q_idx, q in enumerate(questions):
                p_q = doc.add_paragraph()
                p_q.paragraph_format.space_before = Pt(6)
                p_q.paragraph_format.space_after = Pt(2)
                
                # CRITICAL: For Urdu papers, question paragraph MUST align to the RIGHT!
                if is_urdu:
                    cls.set_paragraph_rtl(p_q)
                    p_q.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                else:
                    p_q.alignment = WD_ALIGN_PARAGRAPH.LEFT

                q_num = q_idx + 1
                raw_q_text = q.get("question_text", "")
                q_text = cls.clean_text_references(raw_q_text)
                q_marks = q.get("marks", 1)

                if is_urdu:
                    prefix = f"سوال نمبر {q_num}: "
                    marks_str = f" [{q_marks} نمبر]"
                else:
                    prefix = f"Q.{q_num} "
                    marks_str = f" [{q_marks}]"

                r_pfx = p_q.add_run(prefix)
                r_pfx.font.name = base_font
                r_pfx.font.bold = True
                r_pfx.font.size = Pt(10.5)
                if is_urdu:
                    cls.set_run_rtl(r_pfx, urdu_font)

                r_body = p_q.add_run(q_text)
                r_body.font.name = base_font
                r_body.font.size = Pt(10)
                if is_urdu:
                    cls.set_run_rtl(r_body, urdu_font)

                r_mrk = p_q.add_run(marks_str)
                r_mrk.font.name = base_font
                r_mrk.font.bold = True
                r_mrk.font.size = Pt(9.5)
                r_mrk.font.color.rgb = RGBColor(100, 116, 139)
                if is_urdu:
                    cls.set_run_rtl(r_mrk, urdu_font)

                # MCQ Options Grid with Board Bubbles ◯
                raw_options = q.get("options", [])
                if sec_type == "mcq" and raw_options:
                    bubble_options = cls.format_mcq_options_with_bubbles(raw_options, is_urdu)
                    
                    opt_p = doc.add_paragraph()
                    opt_p.paragraph_format.space_after = Pt(5)
                    
                    if is_urdu:
                        cls.set_paragraph_rtl(opt_p)
                        opt_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                        opt_p.paragraph_format.right_indent = Inches(0.25)
                    else:
                        opt_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                        opt_p.paragraph_format.left_indent = Inches(0.25)

                    total_opts_len = sum(len(opt) for opt in bubble_options)
                    if total_opts_len < 75:
                        # Single line with wide spacing
                        opt_line = "      ".join(bubble_options)
                        r_opt = opt_p.add_run(opt_line)
                        r_opt.font.name = base_font
                        r_opt.font.size = Pt(9.5)
                        if is_urdu:
                            cls.set_run_rtl(r_opt, urdu_font)
                    elif len(bubble_options) == 4 and total_opts_len < 130:
                        # 2x2 lines
                        r_opt1 = opt_p.add_run(f"{bubble_options[0]}            {bubble_options[1]}\n")
                        r_opt2 = opt_p.add_run(f"{bubble_options[2]}            {bubble_options[3]}")
                        for r_item in [r_opt1, r_opt2]:
                            r_item.font.name = base_font
                            r_item.font.size = Pt(9.5)
                            if is_urdu:
                                cls.set_run_rtl(r_item, urdu_font)
                    else:
                        # Each option on a separate line
                        for o_idx, opt_text in enumerate(bubble_options):
                            suffix = "\n" if o_idx < len(bubble_options) - 1 else ""
                            r_o = opt_p.add_run(f"{opt_text}{suffix}")
                            r_o.font.name = base_font
                            r_o.font.size = Pt(9.5)
                            if is_urdu:
                                cls.set_run_rtl(r_o, urdu_font)

        # -------------------------------------------------------------
        # 5. Official Signature & Verification Block
        # -------------------------------------------------------------
        p_sig_space = doc.add_paragraph()
        p_sig_space.paragraph_format.space_before = Pt(16)

        p_sig = doc.add_paragraph()
        if is_urdu:
            cls.set_paragraph_rtl(p_sig)
            p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            r_sig1 = p_sig.add_run("دستخط نگرانِ امتحانات: ___________________          دستخط پرنسپل / کنٹرولر امتحانات: ___________________")
        else:
            p_sig.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r_sig1 = p_sig.add_run("Invigilator Signature: ___________________          Controller of Examinations / Principal: ___________________")
        r_sig1.font.name = base_font
        r_sig1.font.size = Pt(9.5)
        r_sig1.font.bold = True
        r_sig1.font.color.rgb = RGBColor(71, 85, 105)
        if is_urdu:
            cls.set_run_rtl(r_sig1, urdu_font)

        v_code = paper_data.get("verification_code") or "EXAM-VERIFIED-AUTH"
        p_v = doc.add_paragraph()
        p_v.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_v.paragraph_format.space_before = Pt(6)
        r_v = p_v.add_run(f"🔒 Official ExamForge Verification Code: [{v_code}] • Verify Authenticity at: https://examforge.ai/verify/{v_code}")
        r_v.font.name = "Calibri"
        r_v.font.size = Pt(8.5)
        r_v.font.italic = True
        r_v.font.color.rgb = RGBColor(148, 163, 184)

        # -------------------------------------------------------------
        # 6. Dedicated Answer Key (Zero Textbook Page References)
        # -------------------------------------------------------------
        if include_answer_key:
            doc.add_page_break()
            p_ak = doc.add_paragraph()
            p_ak.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if is_urdu:
                cls.set_paragraph_rtl(p_ak)

            r_akh = p_ak.add_run(
                "امتحانی جوابی پرچہ اور حل شدہ خاکہ (CONFIDENTIAL MARKING SCHEME)"
                if is_urdu else
                "CONFIDENTIAL MARKING SCHEME & OFFICIAL ANSWER KEY"
            )
            r_akh.font.name = base_font
            r_akh.font.size = Pt(14)
            r_akh.font.bold = True
            r_akh.font.color.rgb = RGBColor(185, 28, 28) # Red distinction
            if is_urdu:
                cls.set_run_rtl(r_akh, urdu_font)

            p_aks = doc.add_paragraph()
            p_aks.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_aks = p_aks.add_run(f"For Examiners & Evaluators Only | {paper_data.get('title')}")
            r_aks.font.name = base_font
            r_aks.font.size = Pt(9.5)
            r_aks.font.italic = True

            for sec in sections:
                p_s_ak = doc.add_paragraph()
                p_s_ak.paragraph_format.space_before = Pt(10)
                p_s_ak.paragraph_format.space_after = Pt(3)
                if is_urdu:
                    cls.set_paragraph_rtl(p_s_ak)
                    p_s_ak.alignment = WD_ALIGN_PARAGRAPH.RIGHT

                r_sak = p_s_ak.add_run(f"● {sec.get('title')} Marking Scheme:")
                r_sak.font.name = base_font
                r_sak.font.bold = True
                r_sak.font.size = Pt(11)
                r_sak.font.color.rgb = RGBColor(15, 23, 42)
                if is_urdu:
                    cls.set_run_rtl(r_sak, urdu_font)

                for q_idx, q in enumerate(sec.get("questions", [])):
                    p_k = doc.add_paragraph()
                    p_k.paragraph_format.space_after = Pt(3)
                    if is_urdu:
                        cls.set_paragraph_rtl(p_k)
                        p_k.alignment = WD_ALIGN_PARAGRAPH.RIGHT

                    q_num = q_idx + 1
                    raw_ans = q.get("correct_answer", "N/A")
                    ans = cls.clean_text_references(raw_ans)
                    raw_expl = q.get("explanation", "")
                    expl = cls.clean_text_references(raw_expl)

                    lbl = f"سوال {q_num}: " if is_urdu else f"Q.{q_num}: "
                    r_klbl = p_k.add_run(lbl)
                    r_klbl.font.name = base_font
                    r_klbl.font.bold = True
                    if is_urdu:
                        cls.set_run_rtl(r_klbl, urdu_font)

                    r_kans = p_k.add_run(f"{ans} ")
                    r_kans.font.name = base_font
                    r_kans.font.bold = True
                    r_kans.font.color.rgb = RGBColor(21, 128, 61) # Green
                    if is_urdu:
                        cls.set_run_rtl(r_kans, urdu_font)

                    # Only show conceptual explanation, strictly no textbook page references
                    if expl:
                        r_kdt = p_k.add_run(f"— {expl}")
                        r_kdt.font.name = base_font
                        r_kdt.font.size = Pt(9)
                        r_kdt.font.italic = True
                        if is_urdu:
                            cls.set_run_rtl(r_kdt, urdu_font)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
        return output_path

    @classmethod
    def generate_confidential_answer_key_docx(
        cls,
        paper_data: Dict[str, Any],
        school_info: Dict[str, Any],
        output_path: str
    ) -> str:
        """Generates an independent, strictly confidential Answer Key & Marking Scheme document."""
        doc = Document()
        is_urdu = paper_data.get("language") == "ur"
        base_font = "Calibri"
        urdu_font = "Arial"

        # Margins
        sections_doc = doc.sections
        for s in sections_doc:
            s.top_margin = Inches(0.7)
            s.bottom_margin = Inches(0.7)
            s.left_margin = Inches(0.75)
            s.right_margin = Inches(0.75)

        # Header Badge
        p_badge = doc.add_paragraph()
        p_badge.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_badge = p_badge.add_run("CONFIDENTIAL & STRICTLY RESTRICTED | EXAMINERS ONLY")
        r_badge.font.name = base_font
        r_badge.font.size = Pt(10)
        r_badge.font.bold = True
        r_badge.font.color.rgb = RGBColor(185, 28, 28)

        # Title
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if is_urdu:
            cls.set_paragraph_rtl(p_title)
        r_title = p_title.add_run(
            f"امتحانی جوابی پرچہ اور حل شدہ خاکہ (MARKING SCHEME)\n{paper_data.get('title', 'Examination Paper')}"
            if is_urdu else
            f"OFFICIAL MARKING SCHEME & ANSWER KEY\n{paper_data.get('title', 'Examination Paper')}"
        )
        r_title.font.name = base_font
        r_title.font.size = Pt(14)
        r_title.font.bold = True
        if is_urdu:
            cls.set_run_rtl(r_title, urdu_font)

        # Meta summary
        p_meta = doc.add_paragraph()
        p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
        school_name = school_info.get("name", "Pakistan Model School")
        r_meta = p_meta.add_run(
            f"School: {school_name} | Grade: {paper_data.get('grade')} | Subject: {paper_data.get('subject')} | Total Marks: {paper_data.get('total_marks')}"
        )
        r_meta.font.size = Pt(9.5)
        r_meta.font.italic = True
        r_meta.font.color.rgb = RGBColor(71, 85, 105)

        # Separator line
        p_div = doc.add_paragraph()
        r_div = p_div.add_run("―" * 55)
        r_div.font.color.rgb = RGBColor(203, 213, 225)
        p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Sections and answers
        sections = paper_data.get("sections", [])
        for sec in sections:
            p_s = doc.add_paragraph()
            p_s.paragraph_format.space_before = Pt(12)
            p_s.paragraph_format.space_after = Pt(4)
            if is_urdu:
                cls.set_paragraph_rtl(p_s)
                p_s.alignment = WD_ALIGN_PARAGRAPH.RIGHT

            r_sec = p_s.add_run(f"■ {sec.get('title')} ({sec.get('section_type', '').upper()}):")
            r_sec.font.name = base_font
            r_sec.font.bold = True
            r_sec.font.size = Pt(11.5)
            r_sec.font.color.rgb = RGBColor(15, 23, 42)
            if is_urdu:
                cls.set_run_rtl(r_sec, urdu_font)

            for q_idx, q in enumerate(sec.get("questions", [])):
                p_q = doc.add_paragraph()
                p_q.paragraph_format.space_after = Pt(4)
                if is_urdu:
                    cls.set_paragraph_rtl(p_q)
                    p_q.alignment = WD_ALIGN_PARAGRAPH.RIGHT

                q_num = q_idx + 1
                raw_ans = q.get("correct_answer", "N/A")
                ans = cls.clean_text_references(raw_ans)
                raw_expl = q.get("explanation", "")
                expl = cls.clean_text_references(raw_expl)

                q_prefix = f"سوال {q_num}: " if is_urdu else f"Question {q_num}: "
                rq = p_q.add_run(q_prefix)
                rq.font.name = base_font
                rq.font.bold = True
                if is_urdu:
                    cls.set_run_rtl(rq, urdu_font)

                ra = p_q.add_run(f"{ans}  ")
                ra.font.name = base_font
                ra.font.bold = True
                ra.font.color.rgb = RGBColor(22, 101, 52)  # Dark green
                if is_urdu:
                    cls.set_run_rtl(ra, urdu_font)

                if expl:
                    re = p_q.add_run(f"[{expl}]")
                    re.font.name = base_font
                    re.font.size = Pt(9.5)
                    re.font.italic = True
                    re.font.color.rgb = RGBColor(71, 85, 105)
                    if is_urdu:
                        cls.set_run_rtl(re, urdu_font)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
        return output_path
