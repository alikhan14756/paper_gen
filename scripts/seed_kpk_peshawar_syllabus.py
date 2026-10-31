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
)
from app.services.document.extractor import DocumentExtractor

def seed_kpk_syllabus():
    print("=" * 60)
    print("  Seeding KPK Textbook Board Peshawar & BISEP Board Syllabus")
    print("=" * 60)

    init_db()
    db = SessionLocal()
    try:
        # Find or create a KPK-oriented school
        school = db.query(School).filter((School.slug == "pms-peshawar") | (School.slug == "lgs")).first()
        if not school:
            print("No existing school found. Creating Peshawar Model School...")
            school = School(
                id=str(uuid.uuid4()),
                name="Peshawar Model School & College (Boys Campus)",
                slug="pms-peshawar",
                address="Warsak Road, Peshawar, Khyber Pakhtunkhwa",
                status="active"
            )
            db.add(school)
            db.commit()
            db.refresh(school)

        teacher = db.query(User).filter(User.school_id == school.id).first()
        if not teacher:
            teacher = db.query(User).first()

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        kpk_books = [
            {
                "title": "Physics Class 10 (KPK Textbook Board Peshawar)",
                "subject": "Physics",
                "grade": "10",
                "language": "en",
                "chapters": [
                    (10, "Simple Harmonic Motion and Waves", "Simple harmonic motion (SHM), restoring force, Hooke's Law F = -kx. Wave motion, transverse and longitudinal waves, wave equation v = f * lambda."),
                    (11, "Sound", "Characteristics of sound, pitch, loudness, quality. Speed of sound in various media. Reflection of sound (Echo) and ultrasound applications in medicine and industry."),
                    (12, "Geometrical Optics", "Reflection of light, spherical mirrors, mirror formula 1/f = 1/p + 1/q. Refraction of light, Snell's law, total internal reflection, lenses and optical instruments."),
                    (13, "Electrostatics", "Electric charges, Coulomb's Law F = k * q1 * q2 / r^2. Electric field intensity, electric potential, capacitors and capacitance C = Q / V."),
                    (14, "Current Electricity", "Electric current I = Q / t, Ohm's Law V = I * R. Series and parallel resistor circuits, Joule's Law H = I^2 * R * t, electrical safety."),
                    (15, "Electromagnetism", "Magnetic effect of steady current, force on a current-carrying conductor in a magnetic field. Electromagnetic induction, Faraday's Law, Lenz's law, transformer."),
                    (16, "Basic Electronics", "Thermionic emission, cathode rays, logic gates (AND, OR, NOT, NAND, NOR) and truth tables."),
                    (17, "Information and Communication Technology", "Components of computer-based ICT, transmission of electrical signals, optical fibers, internet and data storage."),
                    (18, "Atomic and Nuclear Physics", "Structure of atom, isotopes, natural radioactivity (alpha, beta, gamma decay), half-life and nuclear fission/fusion.")
                ]
            },
            {
                "title": "مطالعہ پاکستان جماعت نہم (خیبر پختونخوا ٹیکسٹ بک بورڈ پشاور)",
                "subject": "مطالعہ پاکستان",
                "grade": "9",
                "language": "ur",
                "chapters": [
                    (1, "باب 1: نظریہ پاکستان کی اساس اور تاریخی پس منظر", "نظریہ کی تعریف، اسلامی نظریہ حیات نظریہ پاکستان کی بنیاد ہے۔ قائد اعظم اور علامہ اقبال کے ارشادات اور دو قومی نظریہ۔"),
                    (2, "باب 2: تحریک پاکستان اور قیام پاکستان (1940ء تا 1947ء)", "قرارداد پاکستان 23 مارچ 1940ء، کرپس مشن، شملہ کانفرنس، عام انتخابات 1945-46، کیبنٹ مشن اور 14 اگست 1947ء کو پاکستان کا قیام۔"),
                    (3, "باب 3: پاکستان کا جغرافیہ اور خیبر پختونخوا کے قدرتی وسائل", "پاکستان کا محل وقوع، طبعی خدوخال، موسم اور آب و ہوا، خیبر پختونخوا کی وادیاں، دریا اور جنگلات و معدنیات۔"),
                    (4, "باب 4: پاکستان کی ابتدائی مشکلات اور آئینی ارتقاء", "مہاجرین کی آباد کاری، اثاثوں کی تقسیم، الحاق کشمیر کا تنازع، 1956ء اور 1973ء کے دساتیر کے اسلامی نکات۔"),
                    (5, "باب 5: خیبر پختونخوا کی تاریخ، ثقافت اور قبائلی اضلاع کی شمولیت", "خیبر پختونخوا کا تاریخی پس منظر، پشتون ثقافت و روایات، لوک ادب، اور سابق فاٹا قبائلی اضلاع کی خیبر پختونخوا میں تاریخی آئینی شمولیت۔")
                ]
            },
            {
                "title": "Chemistry Class 9 (KPK Textbook Board Peshawar)",
                "subject": "Chemistry",
                "grade": "9",
                "language": "en",
                "chapters": [
                    (1, "Fundamentals of Chemistry", "Branches of chemistry, basic definitions, matter, elements, compounds, mixtures, atomic number, mass number, mole and Avogadro's number."),
                    (2, "Structure of Atoms", "Rutherford and Bohr's atomic models, subatomic particles (electrons, protons, neutrons), electronic configurations and isotopes."),
                    (3, "Periodic Table and Periodicity", "Modern periodic law, periods and groups, periodic trends in physical properties: atomic radius, ionization energy, electron affinity, electronegativity."),
                    (4, "Structure of Molecules", "Chemical bonding, ionic bond, covalent bond (single, double, triple), coordinate covalent bond, metallic bond, intermolecular forces."),
                    (5, "Physical States of Matter", "Gaseous state, Boyle's Law P1V1 = P2V2, Charles's Law V1/T1 = V2/T2. Liquid state, evaporation, vapor pressure, boiling point. Solid state and allotropy."),
                    (6, "Solutions", "Solution, aqueous solution, solute, solvent, saturated/unsaturated solutions, concentration units (molarity, percentage), solubility factors."),
                    (7, "Electrochemistry", "Oxidation and reduction, oxidation state rules, oxidizing and reducing agents, electrochemical cells (electrolytic and galvanic), corrosion prevention.")
                ]
            },
            {
                "title": "Mathematics Class 10 (KPK Textbook Board Peshawar)",
                "subject": "Mathematics",
                "grade": "10",
                "language": "en",
                "chapters": [
                    (1, "Quadratic Equations", "Standard form ax^2 + bx + c = 0, solution by factorization, completing square, quadratic formula x = (-b +- sqrt(b^2 - 4ac)) / (2a)."),
                    (2, "Theory of Quadratic Equations", "Nature of roots using discriminant b^2 - 4ac, cube roots of unity, relations between roots and coefficients."),
                    (3, "Variations", "Ratio, proportion, direct variation, inverse variation, joint variation, K-method theorem on proportions."),
                    (4, "Partial Fractions", "Resolution of rational fractions into partial fractions for linear and quadratic irreducible factors."),
                    (5, "Sets and Functions", "Operations on sets, Venn diagrams, De Morgan's laws, binary relations, one-one, onto and bijective functions."),
                    (6, "Basic Statistics", "Frequency distribution, cumulative frequency, arithmetic mean, median, mode, variance and standard deviation."),
                    (7, "Introduction to Trigonometry", "Measurement of angles (degrees and radians), trigonometric ratios (sin, cos, tan), fundamental trigonometric identities.")
                ]
            },
            {
                "title": "اردو لازمی جماعت نہم (خیبر پختونخوا ٹیکسٹ بک بورڈ پشاور)",
                "subject": "اردو",
                "grade": "9",
                "language": "ur",
                "chapters": [
                    (1, "حصہ نثر: ہجرت نبوی (ص) اور کاہلی", "مولانا شبلی نعمانی کا اسلوب بیان، ہجرت مدینہ کا واقعہ۔ سر سید احمد خان کا مضمون کاہلی اور اس کا اخلاقی و عملی درس۔"),
                    (2, "حصہ نثر: آرام و سکون اور امتحان", "سید امتیاز علی تاج کا مزاحیہ ڈراما آرام و سکون۔ مرزا فرحت اللہ بیگ کا مضمون امتحان اور طلبہ کی نفسیات۔"),
                    (3, "حصہ نظم: حمد اور نعت", "مولانا الطاف حسین حالی کی مسدس اور حمدیہ شاعری۔ احسان دانش کی نعت رسول مقبول (ص) اور اس کے محاسن۔"),
                    (4, "حصہ غزل: میر تقی میر اور مرزا غالب", "میر تقی میر کی غزل سرہانے میر کے آہستہ بولو۔ مرزا اسد اللہ خان غالب کی شاہکار غزل دل ناداں تجھے ہوا کیا ہے۔")
                ]
            }
        ]

        for b_data in kpk_books:
            existing = db.query(Book).filter(Book.title == b_data["title"], Book.school_id == school.id).first()
            if existing:
                print(f"Book already exists: {b_data['title']}")
                continue

            pdf_filename = f"kpk_{b_data['subject'].lower().replace(' ', '_')}_grade{b_data['grade']}.pdf"
            pdf_path = os.path.join(settings.UPLOAD_DIR, pdf_filename)
            cache_path = os.path.join(settings.UPLOAD_DIR, f"{pdf_filename}_cache.json")

            # Create synthetic PDF
            doc = fitz.open()
            toc = []
            for ch_num, ch_title, ch_content in b_data["chapters"]:
                p = doc.new_page()
                p.insert_text((50, 60), f"{ch_title}\n\n{ch_content}\n\nOfficial Syllabus of KPK Textbook Board Peshawar.")
                toc.append([1, ch_title, len(doc)])

            doc.set_toc(toc)
            doc.save(pdf_path)
            doc.close()

            # Extract pages to cache
            DocumentExtractor.extract_pdf_pages(pdf_path, cache_path)

            book_id = str(uuid.uuid4())
            new_book = Book(
                id=book_id,
                school_id=school.id,
                uploaded_by_id=teacher.id if teacher else None,
                title=b_data["title"],
                subject=b_data["subject"],
                grade=b_data["grade"],
                language=b_data["language"],
                file_path=pdf_path,
                file_hash=DocumentExtractor.calculate_file_hash(open(pdf_path, "rb").read()),
                file_size_bytes=os.path.getsize(pdf_path),
                total_pages=len(b_data["chapters"]),
                processing_status="ready",
            )
            db.add(new_book)
            db.commit()
            db.refresh(new_book)

            # Add chapters
            for idx, (ch_num, ch_title, ch_content) in enumerate(b_data["chapters"]):
                ch = Chapter(
                    book_id=new_book.id,
                    school_id=school.id,
                    chapter_number=ch_num,
                    title=ch_title,
                    start_page=idx + 1,
                    end_page=idx + 1,
                    is_detected=True,
                    confidence=0.98,
                    detection_method="kpk_textbook_board_syllabus"
                )
                db.add(ch)

            db.commit()
            safe_title = b_data['title'].encode('ascii', 'replace').decode('ascii')
            print(f"Successfully added: {safe_title} with {len(b_data['chapters'])} chapters.")

        print("\nAll KPK Peshawar Board syllabus textbooks successfully seeded!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_kpk_syllabus()
