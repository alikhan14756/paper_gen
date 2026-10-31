import os
import json
import uuid
import fitz
from app.core.database import SessionLocal
from app.core.config import settings
from app.core.init_db import init_db
from app.models import (
    School,
    User,
    Book,
    Chapter,
    Paper,
    Section,
    Question,
)
from app.services.document.extractor import DocumentExtractor
from app.services.chapter.detector import ChapterDetector
from app.services.export.docx_generator import DocxGenerator

def seed_sample_textbooks():
    init_db()
    db = SessionLocal()
    try:
        school = db.query(School).filter(School.slug == "lgs").first()
        teacher = db.query(User).filter(User.email == "teacher@lgs.edu.pk").first()

        if not school or not teacher:
            print("School or teacher not found. Run init_db first.")
            return

        # Check if books already exist
        existing_book = db.query(Book).filter(Book.school_id == school.id).first()
        if existing_book:
            print("Sample textbooks already seeded.")
            return

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(settings.EXPORT_DIR, exist_ok=True)

        # -------------------------------------------------------------------------
        # 1. Create English Physics Textbook PDF
        # -------------------------------------------------------------------------
        physics_pdf_path = os.path.join(settings.UPLOAD_DIR, "matric_physics_class10.pdf")
        physics_cache_path = os.path.join(settings.UPLOAD_DIR, "matric_physics_class10_cache.json")

        doc_en = fitz.open()

        # Page 1: Chapter 10
        p1 = doc_en.new_page()
        p1.insert_text((50, 50), """Chapter 10: Simple Harmonic Motion and Waves

Simple harmonic motion (SHM) occurs when the net force is directly proportional to the displacement from the mean position and is always directed towards the mean position.
Examples of SHM include the motion of a simple pendulum, the ball and bowl system, and a mass attached to a spring.
Restoring force always pushes or pulls the object performing oscillatory motion towards the mean position.
Hooke's Law states that within elastic limits, the force applied to a spring is directly proportional to the extension produced: F = -kx.
The time period of a simple pendulum depends upon its length and the acceleration due to gravity: T = 2 * pi * sqrt(l / g).
Frequency is defined as the number of cycles or vibrations completed in one second. Its SI unit is Hertz (Hz).
Damped oscillations are oscillations in which the amplitude of the vibrating body decreases gradually with time due to friction or air resistance.""")

        # Page 2: Chapter 10 Waves
        p2 = doc_en.new_page()
        p2.insert_text((50, 50), """Chapter 10 continued: Wave Motion and Sound

A wave is a disturbance in the medium which causes the particles of the medium to undergo vibratory motion about their mean position in equal intervals of time.
Mechanical waves require a physical material medium for their propagation, such as water waves, sound waves, and seismic waves.
Electromagnetic waves do not require any medium and can propagate through a vacuum, such as light waves, X-rays, and radio waves.
Transverse waves have particle oscillations perpendicular to the direction of wave travel.
Longitudinal waves consist of compressions and rarefactions where particle motion is parallel to wave direction.
The wave equation relates speed (v), frequency (f), and wavelength (lambda): v = f * lambda.""")

        # Page 3: Chapter 14 Current Electricity
        p3 = doc_en.new_page()
        p3.insert_text((50, 50), """Chapter 14: Current Electricity

Electric current is defined as the rate of flow of electric charges through any cross-sectional area of a conductor: I = Q / t.
The SI unit of current is Ampere (A). One ampere represents one coulomb of charge passing in one second.
Potential difference between two points is the work done in moving a unit positive charge from one point to another: V = W / Q.
Ohm's Law states that the current passing through a conductor is directly proportional to the potential difference across its ends, provided temperature remains constant: V = I * R.
Resistance is the opposition offered by the atoms of a conductor to the flow of free electrons. Its SI unit is Ohm.
Factors affecting resistance include length of the conductor, cross-sectional area, material resistivity, and temperature.""")

        # Page 4: Chapter 14 cont
        p4 = doc_en.new_page()
        p4.insert_text((50, 50), """Chapter 14 continued: Electric Power and Circuits

Joule's Law states that the heat produced in a resistor is proportional to the square of current, resistance, and time: H = I^2 * R * t.
Electric power is the rate at which electrical energy is converted into other forms of energy: P = V * I = I^2 * R.
In series circuits, current remains identical across all components, while voltage divides: R_eq = R1 + R2 + R3.
In parallel circuits, voltage is identical across each branch, while current divides: 1/R_eq = 1/R1 + 1/R2 + 1/R3.""")

        doc_en.set_toc([
            [1, "Chapter 10: Simple Harmonic Motion and Waves", 1],
            [1, "Chapter 14: Current Electricity", 3]
        ])
        doc_en.save(physics_pdf_path)
        doc_en.close()

        # Extract & Detect for Physics
        DocumentExtractor.extract_pdf_pages(physics_pdf_path, physics_cache_path)
        physics_book = Book(
            id=str(uuid.uuid4()),
            school_id=school.id,
            uploaded_by_id=teacher.id,
            title="Matric Physics (Punjab Curriculum)",
            subject="Physics",
            grade="10",
            language="en",
            file_path=physics_pdf_path,
            file_hash=DocumentExtractor.calculate_file_hash(open(physics_pdf_path, "rb").read()),
            file_size_bytes=os.path.getsize(physics_pdf_path),
            total_pages=4,
            processing_status="ready",
        )
        db.add(physics_book)
        db.commit()
        db.refresh(physics_book)

        ch10 = Chapter(
            book_id=physics_book.id,
            school_id=school.id,
            chapter_number=10,
            title="Simple Harmonic Motion and Waves",
            start_page=1,
            end_page=2,
            is_detected=True,
            confidence=0.95,
            detection_method="pdf_toc_bookmarks"
        )
        ch14 = Chapter(
            book_id=physics_book.id,
            school_id=school.id,
            chapter_number=14,
            title="Current Electricity and Circuits",
            start_page=3,
            end_page=4,
            is_detected=True,
            confidence=0.95,
            detection_method="pdf_toc_bookmarks"
        )
        db.add_all([ch10, ch14])
        db.commit()

        # -------------------------------------------------------------------------
        # 2. Create Urdu Textbook PDF (مطالعہ پاکستان جماعت نہم)
        # -------------------------------------------------------------------------
        urdu_pdf_path = os.path.join(settings.UPLOAD_DIR, "pakistan_studies_class9.pdf")
        urdu_cache_path = os.path.join(settings.UPLOAD_DIR, "pakistan_studies_class9_cache.json")

        doc_ur = fitz.open()

        # Page 1: باب 1
        up1 = doc_ur.new_page()
        up1.insert_text((50, 50), """باب 1: نظریہ پاکستان کی اساس

نظریہ سے مراد ایسا ضابطہ یا پروگرام ہے جس کی بنیاد فلسفہ اور تفکر پر رکھی گئی ہو۔
اسلامی نظریہ حیات ہی نظریہ پاکستان کی بنیاد ہے۔
قائد اعظم محمد علی جناح نے فرمایا کہ پاکستان تو اسی روز وجود میں آ گیا تھا جب پہلا مسلمان ہندوستان میں ہوا تھا۔
علامہ محمد اقبال نے 1930ء کے خطبہ الہ آباد میں مسلمانوں کے لیے ایک الگ آزاد ریاست کا تصور پیش کیا۔
دو قومی نظریے سے مراد یہ ہے کہ برصغیر پاک و ہند میں دو بڑی قومیں ہندو اور مسلمان آباد ہیں جن کی تہذیب و ثقافت اور مذہب بالکل جداگانہ ہیں۔""")

        # Page 2: باب 2
        up2 = doc_ur.new_page()
        up2.insert_text((50, 50), """باب 2: تحریک پاکستان اور قیام پاکستان

23 مارچ 1940ء کو لاہور کے منٹو پارک (موجودہ اقبال پارک) میں تاریخی قرارداد پاکستان منظور ہوئی۔
اس قرارداد کی صدارت قائد اعظم محمد علی جناح نے کی جبکہ قرارداد اے کے فضل الحق نے پیش کی۔
شملہ وفد 1906ء میں وائسرائے لارڈ منٹو سے سر آغا خان کی قیادت میں ملا۔
3 جون 1947ء کو تقسیم ہند کا منصوبہ پیش کیا گیا جس کے تحت 14 اگست 1947ء کو پاکستان معرض وجود میں آیا۔""")

        doc_ur.set_toc([
            [1, "باب 1: نظریہ پاکستان کی اساس", 1],
            [1, "باب 2: تحریک پاکستان اور قیام پاکستان", 2]
        ])
        doc_ur.save(urdu_pdf_path)
        doc_ur.close()

        DocumentExtractor.extract_pdf_pages(urdu_pdf_path, urdu_cache_path)
        urdu_book = Book(
            id=str(uuid.uuid4()),
            school_id=school.id,
            uploaded_by_id=teacher.id,
            title="مطالعہ پاکستان (جماعت نہم)",
            subject="مطالعہ پاکستان",
            grade="9",
            language="ur",
            file_path=urdu_pdf_path,
            file_hash=DocumentExtractor.calculate_file_hash(open(urdu_pdf_path, "rb").read()),
            file_size_bytes=os.path.getsize(urdu_pdf_path),
            total_pages=2,
            processing_status="ready",
        )
        db.add(urdu_book)
        db.commit()
        db.refresh(urdu_book)

        uch1 = Chapter(
            book_id=urdu_book.id,
            school_id=school.id,
            chapter_number=1,
            title="نظریہ پاکستان کی اساس",
            start_page=1,
            end_page=1,
            is_detected=True,
            confidence=0.95,
            detection_method="pdf_toc_bookmarks"
        )
        uch2 = Chapter(
            book_id=urdu_book.id,
            school_id=school.id,
            chapter_number=2,
            title="تحریک پاکستان اور قیام پاکستان",
            start_page=2,
            end_page=2,
            is_detected=True,
            confidence=0.95,
            detection_method="pdf_toc_bookmarks"
        )
        db.add_all([uch1, uch2])
        db.commit()

        # -------------------------------------------------------------------------
        # 3. Create Sample English Paper with Questions & Export DOCX
        # -------------------------------------------------------------------------
        eng_paper = Paper(
            id=str(uuid.uuid4()),
            school_id=school.id,
            created_by_id=teacher.id,
            book_id=physics_book.id,
            title="Matric Physics Midterm Examination 2026",
            exam_type="Midterm Examination",
            academic_session="2025-2026",
            grade="10",
            subject="Physics",
            language="en",
            time_allowed_minutes=120,
            total_marks=50,
            instructions="Section A MCQs are compulsory. Section B attempt any 5 questions. Section C attempt any 2 questions.",
            status="generated",
            selected_chapters_json=json.dumps([ch10.id, ch14.id]),
        )
        db.add(eng_paper)
        db.commit()
        db.refresh(eng_paper)

        # Sec A: MCQs (10 * 1 = 10)
        sec_a = Section(
            paper_id=eng_paper.id,
            school_id=school.id,
            title="Section A — Multiple Choice Questions",
            section_type="mcq",
            sort_order=1,
            total_questions=10,
            questions_to_attempt=10,
            marks_per_question=1.0,
            total_section_marks=10.0,
            instructions="Select the single correct option for each question.",
        )
        db.add(sec_a)
        db.commit()
        db.refresh(sec_a)

        physics_mcqs = [
            ("Which of the following is an example of simple harmonic motion?", ["A. Spinning top", "B. Simple pendulum", "C. Train moving on straight tracks", "D. Falling apple"], "B. Simple pendulum", "Chapter 10, Page 1"),
            ("What is the SI unit of frequency?", ["A. Second", "B. Meter", "C. Hertz (Hz)", "D. Joule"], "C. Hertz (Hz)", "Chapter 10, Page 1"),
            ("Waves that do not require any medium for propagation are called:", ["A. Mechanical waves", "B. Sound waves", "C. Water waves", "D. Electromagnetic waves"], "D. Electromagnetic waves", "Chapter 10, Page 2"),
            ("The relationship between velocity, frequency, and wavelength is expressed as:", ["A. v = f / lambda", "B. v = f * lambda", "C. f = v * lambda", "D. lambda = v * f"], "B. v = f * lambda", "Chapter 10, Page 2"),
            ("The rate of flow of electric charges through a conductor is known as:", ["A. Electric potential", "B. Electric current", "C. Resistance", "D. Capacitance"], "B. Electric current", "Chapter 14, Page 3"),
            ("Ohm's Law is mathematically stated as:", ["A. V = I / R", "B. V = I * R", "C. I = V * R", "D. R = V * I"], "B. V = I * R", "Chapter 14, Page 3"),
            ("The SI unit of electric resistance is:", ["A. Volt", "B. Ampere", "C. Ohm", "D. Coulomb"], "C. Ohm", "Chapter 14, Page 3"),
            ("In a series circuit, which physical quantity remains identical across all resistors?", ["A. Current", "B. Voltage", "C. Resistance", "D. Power"], "A. Current", "Chapter 14, Page 4"),
            ("According to Hooke's Law, restoring force in a spring is given by:", ["A. F = ma", "B. F = -kx", "C. F = qE", "D. F = GmM/r^2"], "B. F = -kx", "Chapter 10, Page 1"),
            ("The formula for heat produced in a conductor according to Joule's Law is:", ["A. H = I * R * t", "B. H = I^2 * R * t", "C. H = V * R * t", "D. H = I / (R * t)"], "B. H = I^2 * R * t", "Chapter 14, Page 4")
        ]

        for idx, (q_txt, opts, ans, ref) in enumerate(physics_mcqs):
            db.add(Question(
                section_id=sec_a.id,
                paper_id=eng_paper.id,
                school_id=school.id,
                question_number=idx + 1,
                question_type="mcq",
                question_text=q_txt,
                options_json=json.dumps(opts),
                correct_answer=ans,
                marks=1.0,
                difficulty="medium",
                source_reference=ref,
                explanation=f"Textbook Reference: {ref}",
                sort_order=idx + 1,
                review_status="reviewed",
            ))

        # Sec B: Short (Attempt 5 of 8, 4 marks each = 20)
        sec_b = Section(
            paper_id=eng_paper.id,
            school_id=school.id,
            title="Section B — Short Questions",
            section_type="short",
            sort_order=2,
            total_questions=8,
            questions_to_attempt=5,
            marks_per_question=4.0,
            total_section_marks=20.0,
            instructions="Attempt any FIVE questions. Each question carries 4 marks.",
        )
        db.add(sec_b)
        db.commit()
        db.refresh(sec_b)

        physics_shorts = [
            ("Define Simple Harmonic Motion (SHM) and state two necessary conditions for a body to execute SHM.", "Definition (2 marks): Acceleration is proportional to displacement and directed towards mean position. Conditions (2 marks): Elastic restoring force and system inertia.", "Chapter 10, Page 1"),
            ("Differentiate between mechanical waves and electromagnetic waves with one example of each.", "Mechanical waves require material medium (e.g. sound/water waves). Electromagnetic waves propagate in vacuum (e.g. light/radio waves). (2+2 marks)", "Chapter 10, Page 2"),
            ("State Ohm's Law and specify the conditions under which it remains valid.", "Statement: Current is directly proportional to potential difference (2 marks). Condition: Temperature and physical state of conductor must remain constant (2 marks).", "Chapter 14, Page 3"),
            ("Derive the wave equation v = f * lambda from basic definitions.", "Speed v = d/t. For one cycle, d = lambda and t = T. Thus v = lambda / T = f * lambda. (4 marks)", "Chapter 10, Page 2"),
            ("Define electric potential and write its SI unit and mathematical formula.", "Definition: Work done per unit positive charge (2 marks). Formula V = W/Q and unit Volt (2 marks).", "Chapter 14, Page 3"),
            ("What are damped oscillations? How does damping affect the amplitude of vibration?", "Oscillations whose amplitude decreases over time due to resistive forces like friction/air resistance. (4 marks)", "Chapter 10, Page 1"),
            ("Compare the characteristics of series and parallel combination of resistors.", "Series: Same current, voltages add (2 marks). Parallel: Same voltage, currents add (2 marks).", "Chapter 14, Page 4"),
            ("State Joule's Law of heating and write its formula.", "Heat produced in resistor is directly proportional to square of current, resistance, and time: H = I^2 * R * t. (4 marks)", "Chapter 14, Page 4")
        ]

        for idx, (q_txt, ans, ref) in enumerate(physics_shorts):
            db.add(Question(
                section_id=sec_b.id,
                paper_id=eng_paper.id,
                school_id=school.id,
                question_number=idx + 1,
                question_type="short",
                question_text=q_txt,
                options_json="[]",
                correct_answer=ans,
                marks=4.0,
                difficulty="medium",
                source_reference=ref,
                explanation=ans,
                sort_order=idx + 1,
                review_status="reviewed",
            ))

        # Sec C: Long (Attempt 2 of 3, 10 marks each = 20)
        sec_c = Section(
            paper_id=eng_paper.id,
            school_id=school.id,
            title="Section C — Long Questions",
            section_type="long",
            sort_order=3,
            total_questions=3,
            questions_to_attempt=2,
            marks_per_question=10.0,
            total_section_marks=20.0,
            instructions="Attempt any TWO questions in detail. Each question carries 10 marks.",
        )
        db.add(sec_c)
        db.commit()
        db.refresh(sec_c)

        physics_longs = [
            ("Prove that the motion of a mass attached to a spring executes Simple Harmonic Motion. Derive the formula for its time period.", "Proof using Hooke's Law F = -kx and Newton's Second Law F = ma => a = -(k/m)x (5 marks). Derivation of time period T = 2*pi*sqrt(m/k) with diagram (5 marks).", "Chapter 10, Page 1"),
            ("Explain the factors on which the resistance of a conductor depends. Derive the formula for specific resistance (resistivity).", "Detailed discussion of length (R proportional to L) and area (R inversely proportional to A) (5 marks). Formulation R = rho * L / A and units of resistivity (5 marks).", "Chapter 14, Page 3"),
            ("What are transverse and longitudinal waves? Explain how sound travels as a longitudinal mechanical wave with compressions and rarefactions.", "Definitions and differences with diagrams (5 marks). Detailed description of air pressure variations, compressions, and rarefactions in sound transmission (5 marks).", "Chapter 10, Page 2")
        ]

        for idx, (q_txt, ans, ref) in enumerate(physics_longs):
            db.add(Question(
                section_id=sec_c.id,
                paper_id=eng_paper.id,
                school_id=school.id,
                question_number=idx + 1,
                question_type="long",
                question_text=q_txt,
                options_json="[]",
                correct_answer=ans,
                marks=10.0,
                difficulty="hard",
                source_reference=ref,
                explanation=ans,
                sort_order=idx + 1,
                review_status="reviewed",
            ))

        db.commit()

        # Generate DOCX for English Paper
        eng_docx_path = os.path.join(settings.EXPORT_DIR, f"ExamPaper_{eng_paper.id}.docx")
        from app.api.v1.papers import _format_paper_dict
        DocxGenerator.generate_exam_docx(
            paper_data=_format_paper_dict(eng_paper),
            school_info={"name": school.name},
            output_path=eng_docx_path,
            include_answer_key=True
        )
        eng_paper.docx_path = eng_docx_path
        db.commit()

        # -------------------------------------------------------------------------
        # 4. Create Sample Urdu Paper with Questions & Export DOCX
        # -------------------------------------------------------------------------
        urdu_paper = Paper(
            id=str(uuid.uuid4()),
            school_id=school.id,
            created_by_id=teacher.id,
            book_id=urdu_book.id,
            title="سالانہ امتحان مطالعہ پاکستان (جماعت نہم)",
            exam_type="سالانہ امتحانات",
            academic_session="2025-2026",
            grade="9",
            subject="مطالعہ پاکستان",
            language="ur",
            time_allowed_minutes=120,
            total_marks=50,
            instructions="حصہ اول کثیر الانتخابی سوالات لازمی ہیں۔ حصہ دوم کے کوئی سے پانچ مختصر سوالات حل کریں۔",
            status="generated",
            selected_chapters_json=json.dumps([uch1.id, uch2.id]),
        )
        db.add(urdu_paper)
        db.commit()
        db.refresh(urdu_paper)

        # Urdu Sec A
        u_sec_a = Section(
            paper_id=urdu_paper.id,
            school_id=school.id,
            title="حصہ اول — کثیر الانتخابی سوالات",
            section_type="mcq",
            sort_order=1,
            total_questions=10,
            questions_to_attempt=10,
            marks_per_question=1.0,
            total_section_marks=10.0,
            instructions="درست جواب کا انتخاب کریں۔ ہر سوال کا ایک نمبر ہے۔",
        )
        db.add(u_sec_a)
        db.commit()
        db.refresh(u_sec_a)

        urdu_mcqs = [
            ("نظریہ پاکستان کی بنیادی اساس کیا ہے؟", ["الف) اسلامی نظریہ حیات", "ب) معاشی ترقی", "ج) لسانی بنیاد", "د) جغرافیائی اتحاد"], "الف) اسلامی نظریہ حیات", "باب 1"),
            ("علامہ محمد اقبال نے تاریخی خطبہ الہ آباد کس سال پیش کیا؟", ["الف) 1928ء", "ب) 1930ء", "ج) 1935ء", "د) 1940ء"], "ب) 1930ء", "باب 1"),
            ("قرارداد پاکستان 23 مارچ 1940ء کو کس شہر میں منظور ہوئی؟", ["الف) دہلی", "ب) کراچی", "ج) لاہور", "د) ڈھاکا"], "ج) لاہور", "باب 2"),
            ("قرارداد پاکستان کا تاریخی اجلاس کس پارک میں منعقد ہوا؟", ["الف) شالامار باغ", "ب) منٹو پارک (اقبال پارک)", "ج) جناح باغ", "د) لارڈز پارک"], "ب) منٹو پارک (اقبال پارک)", "باب 2"),
            ("قرارداد لاہور کس ممتاز رہنما نے پیش کی؟", ["الف) چوہدری رحمت علی", "ب) اے کے فضل الحق", "ج) لیاقت علی خان", "د) سر سید احمد خان"], "ب) اے کے فضل الحق", "باب 2"),
            ("شملہ وفد وائسرائے لارڈ منٹو سے کس سال ملا؟", ["الف) 1905ء", "ب) 1906ء", "ج) 1909ء", "د) 1913ء"], "ب) 1906ء", "باب 2"),
            ("تقسیم ہند کا تاریخی منصوبہ کس تاریخ کو جاری کیا گیا؟", ["الف) 3 جون 1947ء", "ب) 14 اگست 1947ء", "ج) 23 مارچ 1940ء", "د) 15 جولائی 1947ء"], "الف) 3 جون 1947ء", "باب 2"),
            ("دو قومی نظریے کی اصطلاح کس تاریخی حقیقت کی طرف اشارہ کرتی ہے؟", ["الف) ہندو اور سکھ", "ب) ہندو اور مسلمان دو الگ قومیں ہیں", "ج) تمام مذاہب یکساں ہیں", "د) برطانوی اور ہندوستانی"], "ب) ہندو اور مسلمان دو الگ قومیں ہیں", "باب 1"),
            ("شملہ وفد 1906ء کی قیادت کس نے کی؟", ["الف) نواب وقار الملک", "ب) سر آغا خان", "ج) مولانا محمد علی جوہر", "د) سر سلیم اللہ خان"], "ب) سر آغا خان", "باب 2"),
            ("پاکستان دنیا کے نقشے پر کس دن ابھرا؟", ["الف) 27 رمضان المبارک 1366ھ (14 اگست 1947ء)", "ب) 23 مارچ 1940ء", "ج) 15 اگست 1947ء", "د) 11 ستمبر 1948ء"], "الف) 27 رمضان المبارک 1366ھ (14 اگست 1947ء)", "باب 2")
        ]

        for idx, (q_txt, opts, ans, ref) in enumerate(urdu_mcqs):
            db.add(Question(
                section_id=u_sec_a.id,
                paper_id=urdu_paper.id,
                school_id=school.id,
                question_number=idx + 1,
                question_type="mcq",
                question_text=q_txt,
                options_json=json.dumps(opts, ensure_ascii=False),
                correct_answer=ans,
                marks=1.0,
                difficulty="medium",
                source_reference=ref,
                explanation=f"درسی کتاب کا حوالہ: {ref}",
                sort_order=idx + 1,
                review_status="reviewed",
            ))

        # Urdu Sec B
        u_sec_b = Section(
            paper_id=urdu_paper.id,
            school_id=school.id,
            title="حصہ دوم — مختصر سوالات",
            section_type="short",
            sort_order=2,
            total_questions=8,
            questions_to_attempt=5,
            marks_per_question=4.0,
            total_section_marks=20.0,
            instructions="کوئی سے پانچ سوالات کے مختصر جوابات تحریر کریں۔",
        )
        db.add(u_sec_b)
        db.commit()
        db.refresh(u_sec_b)

        urdu_shorts = [
            ("نظریہ سے کیا مراد ہے؟ مختصر تعریف بیان کریں۔", "نظریہ سے مراد ایسا ضابطہ یا پروگرام ہے جس کی بنیاد فلسفہ اور تفکر پر رکھی گئی ہو۔ (4 نمبر)", "باب 1"),
            ("دو قومی نظریے کی مختصر وضاحت کریں۔", "برصغیر میں دو بڑی قومیں ہندو اور مسلمان آباد ہیں جن کا مذہب، رہن سہن اور تہذیب مکمل مختلف ہے۔ (4 نمبر)", "باب 1"),
            ("قائد اعظم محمد علی جناح نے نظریہ پاکستان کے بارے میں کیا ارشاد فرمایا؟", "قائد اعظم نے فرمایا: پاکستان تو اسی روز وجود میں آ گیا تھا جب پہلا مسلمان ہندوستان میں ہوا تھا۔ (4 نمبر)", "باب 1"),
            ("علامہ محمد اقبال کے خطبہ الہ آباد 1930ء کا بنیادی نکتہ کیا تھا؟", "شمال مغربی ہندوستان کے مسلمانوں کے لیے ایک الگ خود مختار اسلامی ریاست کا تصور۔ (4 نمبر)", "باب 1"),
            ("قرارداد پاکستان 1940ء کا متن کیا تھا؟", "مسلم اکثریتی علاقوں کو ملا کر آزاد اور خود مختار ریاستیں تشکیل دی جائیں۔ (4 نمبر)", "باب 2"),
            ("شملہ وفد کے دو اہم مطالبات کیا تھے؟", "مسلمانوں کے لیے جداگانہ طریقہ انتخاب اور سرکاری ملازمتوں میں مناسب نمائندگی۔ (4 نمبر)", "باب 2"),
            ("منصوبہ 3 جون 1947ء کے اہم نکات تحریر کریں۔", "برصغیر کو دو آزاد ریاستوں پاکستان اور بھارت میں تقسیم کرنے کا برطانوی اعلان۔ (4 نمبر)", "باب 2"),
            ("قائد اعظم کے فرمودات کی روشنی میں نظریہ پاکستان کے مقاصد کیا تھے؟", "اسلامی اصولوں اور عدل و انصاف پر مبنی فلاحی ریاست کا قیام جہاں اقلیتوں کو مکمل حقوق حاصل ہوں۔ (4 نمبر)", "باب 1")
        ]

        for idx, (q_txt, ans, ref) in enumerate(urdu_shorts):
            db.add(Question(
                section_id=u_sec_b.id,
                paper_id=urdu_paper.id,
                school_id=school.id,
                question_number=idx + 1,
                question_type="short",
                question_text=q_txt,
                options_json="[]",
                correct_answer=ans,
                marks=4.0,
                difficulty="medium",
                source_reference=ref,
                explanation=ans,
                sort_order=idx + 1,
                review_status="reviewed",
            ))

        # Urdu Sec C
        u_sec_c = Section(
            paper_id=urdu_paper.id,
            school_id=school.id,
            title="حصہ سوم — تفصیلی سوالات",
            section_type="long",
            sort_order=3,
            total_questions=3,
            questions_to_attempt=2,
            marks_per_question=10.0,
            total_section_marks=20.0,
            instructions="کوئی سے دو سوالات کے جامع اور تفصیلی جوابات تحریر کریں۔",
        )
        db.add(u_sec_c)
        db.commit()
        db.refresh(u_sec_c)

        urdu_longs = [
            ("علامہ محمد اقبال اور قائد اعظم کے ارشادات کی روشنی میں نظریہ پاکستان کی وضاحت کریں۔", "علامہ اقبال کے خطبہ الہ آباد اور افکار کی وضاحت (5 نمبر)۔ قائد اعظم کے بیانات اور تقریروں کا تجزیہ (5 نمبر)۔", "باب 1"),
            ("قرارداد پاکستان 1940ء کے پس منظر، اہم نکات اور اس کے برصغیر کی سیاست پر اثرات کا جائزہ لیں۔", "قرارداد کا تاریخی پس منظر اور پیش کش (4 نمبر)، اہم نکات (3 نمبر)، اور تحریک پاکستان میں اس کی اہمیت (3 نمبر)۔", "باب 2"),
            ("تحریک پاکستان میں 1940ء سے 1947ء تک کے اہم تاریخی واقعات پر جامع نوٹ لکھیں۔", "کرپس مشن، شملہ کانفرنس، عام انتخابات 1945-46، کیبنٹ مشن اور 3 جون پلان کی تفصیلی بحث (10 نمبر)۔", "باب 2")
        ]

        for idx, (q_txt, ans, ref) in enumerate(urdu_longs):
            db.add(Question(
                section_id=u_sec_c.id,
                paper_id=urdu_paper.id,
                school_id=school.id,
                question_number=idx + 1,
                question_type="long",
                question_text=q_txt,
                options_json="[]",
                correct_answer=ans,
                marks=10.0,
                difficulty="hard",
                source_reference=ref,
                explanation=ans,
                sort_order=idx + 1,
                review_status="reviewed",
            ))

        db.commit()

        # Generate DOCX for Urdu Paper
        urdu_docx_path = os.path.join(settings.EXPORT_DIR, f"ExamPaper_{urdu_paper.id}.docx")
        DocxGenerator.generate_exam_docx(
            paper_data=_format_paper_dict(urdu_paper),
            school_info={"name": school.name},
            output_path=urdu_docx_path,
            include_answer_key=True
        )
        urdu_paper.docx_path = urdu_docx_path
        db.commit()

        print("Seeded sample textbooks, chapters, questions, and DOCX files successfully!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_textbooks()
