# ExamForge AI — System Architecture & Engineering Blueprint

> **Author & Architect**: **Muhammad Ali** (Frontend Developer & Web Developer | [alibuild.site](https://alibuild.site))  
> **System**: ExamForge AI (Multi-Tenant Bilingual Examination Generation SaaS)  
> **Target Boards**: KPK BISE Peshawar, Federal Board of Intermediate & Secondary Education, Punjab Boards

---

## 1. Architectural Philosophy & Overview

ExamForge AI is engineered from the ground up to solve the critical challenges of educational assessments in Pakistan:
1. **Curriculum Grounding**: Eliminating LLM hallucinations by enforcing strict page-level and paragraph-level citation to uploaded textbook chapters.
2. **Cognitive Balance**: Applying Bloom's Revised Taxonomy (Remember, Understand, Apply, Analyze, Evaluate, Create) to ensure examinations assess higher-order thinking rather than pure rote memorization.
3. **Board-Compliant Formatting**: Generating standardized, ready-to-print Microsoft Word (`.docx`) examinations conforming to KPK BISEP standards, complete with bubble answer sheets, institutional headers, and digital signature blocks.
4. **Tenant Security**: Protecting intellectual property and exam papers with row-level multi-tenant isolation, cryptographically hashed passwords, and token expiration handling.

```
+-----------------------------------------------------------------------------------+
|                                Client Applications                                |
|  - Next.js 16 Web Portal (Claymorphic UI / Tailwind CSS / React 19)                |
|  - Desktop Wrapper (WebView2 / PowerShell Launcher)                               |
+-----------------------------------------+-----------------------------------------+
                                          | REST / JSON / Dual-Encoded File Streams
                                          v
+-----------------------------------------------------------------------------------+
|                            FastAPI Application Gateway                            |
|  - JWT Bearer Authentication & Claims Derivation (User, Role, School ID)           |
|  - Tenant Boundary Middleware & Rate Limiting                                      |
|  - Pydantic v2 Schema Validation                                                   |
+-------------------+---------------------+--------------------+--------------------+
                    |                     |                    |
                    v                     v                    v
+-----------------------+ +-----------------------+ +-------------------------------+
|  Document Processing  | |  AI Generation Engine | |  Examination & DOCX Engine    |
| - PyMuPDF Extraction  | | - Gemini 2.5 Flash    | | - OpenXML Word Generator      |
| - NFC Normalization   | | - Claude 3.5 Sonnet   | | - BISEP Layout Engine         |
| - Chapter Detection   | | - Grounded Mock Engine| | - RTL Nastaliq Typography     |
| - Chunker & Scorer    | | - Bloom's Blueprinter | | - Verification Code Generator |
+-----------------------+ +-----------------------+ +-------------------------------+
                    |                     |                    |
                    +---------------------+--------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                         Database Layer (SQLAlchemy 2.x)                           |
|  - 24 Normalized Models across Core, Document, Paper, and Quota Domains           |
|  - SQLite (Local Development) / PostgreSQL 15+ (Production)                       |
+-----------------------------------------------------------------------------------+
```

---

## 2. Relational Domain Models (24 Entities)

The data architecture is partitioned into four decoupled modules:

### 2.1 Core Entities (`app/models/core_entities.py`)
- **`School`**: Root tenant containing subscription plan, status (`active`, `suspended`), max limits (`max_teachers`, `max_monthly_papers`, `storage_limit_mb`), and monthly usage counters.
- **`User`**: Institutional accounts containing hashed passwords (`bcrypt`), role (`super_admin`, `school_admin`, `teacher`), and school relationship.
- **`UsageReservation`**: Atomic quota reservation token locking paper units during generation. Features expiration timestamps and automated reconciliation to prevent ghost locks.
- **`SubscriptionPlan`**: Tier metadata (Free, Standard, Pro, Enterprise).
- **`AuditLog`**: Tamper-evident ledger recording administrative actions, quota adjustments, and role switches.

### 2.2 Document Processing Entities (`app/models/document_entities.py`)
- **`Book`**: Uploaded textbook entity containing subject, grade, medium (`english`, `urdu`), file path, and total page count.
- **`DocumentPage`**: Page-level extraction entity with raw text, NFC normalized text, and extraction quality score.
- **`TextChunk`**: Fine-grained passage chunks (500–1000 characters) indexed with character offsets for verbatim AI context injection.
- **`Chapter`**: Detected or manually configured chapter boundaries (`start_page`, `end_page`, title).
- **`ProcessingJob`**: Async job tracking for PDF parsing with state (`queued`, `processing`, `completed`, `failed`), progress percentage, and retry count.
- **`ExtractionLog`**: Diagnostic records detailing PyMuPDF font extraction warnings or fallback triggers.

### 2.3 Paper & Examination Entities (`app/models/paper_entities.py`)
- **`Paper`**: Complete exam specification containing title, grade, subject, duration, total marks, status (`draft`, `generated`, `finalized`, `archived`), verification code (`EF-XXXX-YYYY`), and watermark.
- **`Section`**: Paper partition (e.g. Section A - Objective, Section B - Short, Section C - Long) with required question counts, sub-choices, and marks per question.
- **`Question`**: Individual assessment item storing:
  - `question_text` & `urdu_text`
  - `question_type` (`mcq`, `short`, `long`, `fill_blanks`, `true_false`)
  - `options` (JSON array for MCQs)
  - `correct_answer` & `marking_guide`
  - **Grounding Fields**: `blooms_level`, `source_page`, `source_excerpt`, `confidence_score`, `quality_score`, `duplicate_risk`.
- **`PaperVersion`**: Immutable snapshot of the paper before regeneration or bulk edits.
- **`QuestionVersion`**: Granular question change history tracking teacher edits.

---

## 3. Multi-Tenant Isolation & Security Boundary

Every tenant-owned table features a non-nullable `school_id` foreign key.

### Strict Server-Side Claims Derivation
1. The frontend never passes `school_id` in request payloads to access or modify data.
2. FastAPI's `get_current_active_user` extracts the authenticated user's `school_id` directly from the server-validated JWT payload.
3. Every database query enforces:
   ```python
   query = db.query(Model).filter(Model.school_id == current_user.school_id)
   ```
4. Super Admins bypass tenant filtering only when explicitly invoking superadmin management routes.
5. School Admins attempting to patch subscription parameters (`max_monthly_papers`, `is_active`) have their requests silently sanitized or rejected with `403 Forbidden`.

---

## 4. Textbook Ingestion & Grounding Pipeline

```
+------------------+     +-------------------+     +--------------------+
|  PDF Textbook    | --> |  PyMuPDF Parser   | --> | NFC Normalization  |
|  (Urdu/English)  |     |  (Extract Text)   |     | (Urdu Ligatures)   |
+------------------+     +-------------------+     +--------------------+
                                                             |
                                                             v
+------------------+     +-------------------+     +--------------------+
|  TextChunk Store | <-- | Chapter Boundary  | <-- | Quality Scoring    |
|  (Page/Offsets)  |     | Detection Engine  |     | (Garbage Detect)   |
+------------------+     +-------------------+     +--------------------+
```

### Chapter Detection Heuristics
1. **PDF Table of Contents / Bookmarks**: PyMuPDF reads embedded PDF bookmarks.
2. **Regex Heading Matching**: Scans page text for patterns such as `Chapter \d+`, `Unit \d+`, `باب نمبر \d+`, or `سبق \d+`.
3. **Teacher Manual Override**: If PDF bookmarks are missing or malformed, teachers can adjust `start_page` and `end_page` via the UI with backend boundary validation (`1 <= start_page <= end_page <= total_pages`).

---

## 5. Bloom's Taxonomy Cognitive Engine

ExamForge AI ensures assessments follow modern pedagogical standards rather than testing only low-level recall:

| Level | Cognitive Domain | Action Verbs | Typical Exam Section |
|---|---|---|---|
| **L1: Remember** | Factual recall | Define, list, name, state | Section A (MCQs) |
| **L2: Understand** | Conceptual grasp | Explain, summarize, classify | Section B (Short) |
| **L3: Apply** | Rule/Formula use | Solve, calculate, demonstrate | Section B / Section C |
| **L4: Analyze** | Component breakdown | Compare, contrast, differentiate | Section B / Section C |
| **L5: Evaluate** | Critical judgment | Justify, assess, critique | Section C (Long) |
| **L6: Create** | Synthesis & design | Formulate, compose, construct | Section C (Long) |

The blueprint engine (`POST /api/v1/papers/generate-blueprint`) calculates balanced mark distributions across these tiers before questions are generated.

---

## 6. OpenXML Word (.docx) Generation & BISEP Formatting

ExamForge AI utilizes `python-docx` augmented with direct OpenXML manipulation to render high-fidelity examination papers:

1. **Urdu Nastaliq RTL Support**:
   - Paragraph properties receive `<w:bidi w:val="1"/>`.
   - Text runs receive `<w:rtl w:val="1"/>`.
   - Font hierarchy specifies `Noto Nastaliq Urdu` and `Jameel Noori Nastaleeq` with fallback to `Calibri`.
2. **BISEP Bubble Answer Grids**:
   - Section A MCQs format with circular fill choices (`◯ A  ◯ B  ◯ C  ◯ D`).
3. **Confidential Marking Scheme Isolation**:
   - Student papers completely omit answer indicators and marking keys.
   - Separate endpoint (`/export-answer-key`) generates confidential teacher keys with question solutions and Bloom's classifications.
4. **Anti-Tamper Signature Block**:
   - Institutional header with school name and roll number boxes.
   - Verification code badge (`EF-XXXX-YYYY`) and invigilator signature lines at document footer.

---

## 7. Developer Attribution

Designed and engineered by:  
**Muhammad Ali**  
*Frontend Developer & Web Developer*  
Founder of **AliBuild** ([https://alibuild.site](https://alibuild.site))  
Contact: [alikhanwebdeveloper@gmail.com](mailto:alikhanwebdeveloper@gmail.com)
