# ExamForge AI — Multi-Tenant Bilingual Examination Paper Generator SaaS
### KPK Peshawar Board (BISEP), Federal & Punjab Boards Edition

> **Lead Creator & Architect**: **Muhammad Ali**  
> **Role**: Frontend Developer & Web Developer | Founder of **AliBuild**  
> **Portfolio**: [https://alibuild.site](https://alibuild.site)  
> **Email**: [alikhanwebdeveloper@gmail.com](mailto:alikhanwebdeveloper@gmail.com)  
> **Attribution**: *ExamForge AI — Designed and developed by Muhammad Ali | Frontend Developer & Web Developer | Portfolio: alibuild.site*

---

## 🌟 Executive Overview

**ExamForge AI** is an enterprise-grade multi-tenant SaaS platform built for educational institutions, examination boards, and teachers in Pakistan and worldwide. It enables schools to upload English and Urdu PDF textbooks, extract text and chapters with page coordinates, configure standardized examination sections, generate factual curriculum-grounded questions with AI, edit questions interactively, and export professionally formatted Microsoft Word (`.docx`) examination papers and confidential marking schemes.

The platform is designed in accordance with **KPK BISE Peshawar** examination patterns, featuring authentic bubble answer grids, right-to-left (RTL) Urdu Nastaliq typography, Bloom's Taxonomy cognitive modeling, and anti-tamper public verification codes.

---

## 🚀 Key Architectural Pillars & Features

1. **Multi-Tenant Isolation & Role-Based Access Control (RBAC)**:
   - 24 normalized SQLAlchemy 2.x models with strict tenant isolation (`school_id`).
   - Hierarchical access: **Super Admin**, **School Admin**, and **Teacher**.
   - Concurrency-safe monthly quotas (`max_monthly_papers`, `max_teachers`, `storage_limit_mb`) protected by `UsageReservation` tokens with automated rollback and expiration reconciliation.
   - School admin quota escalation protection (only Super Admin can modify subscription limits).

2. **Verbatim AI Grounding & Provenance Engine**:
   - Zero-hallucination verification linking every generated question to exact textbook page coordinates and paragraph excerpts.
   - Per-question confidence scores and duplicate risk detection.
   - Interactive **"Inspect Source Evidence"** modal displaying exact verbatim textbook proof for teachers and invigilators.

3. **Bloom's Taxonomy Cognitive Modeling**:
   - Automated exam blueprinting balancing questions across six cognitive levels:
     - **Remember** (Knowledge retrieval)
     - **Understand** (Comprehension & translation)
     - **Apply** (Application in problem-solving)
     - **Analyze** (Breakdown & comparison)
     - **Evaluate** (Critique & judgment)
     - **Create** (Synthesis & formulation)
   - Real-time cognitive badges on paper preview and question editors.

4. **KPK Peshawar Board (BISEP) Standardized Layout**:
   - **Section A**: Objective Type / Multiple Choice Questions (with bubble fill circles `◯ A  ◯ B  ◯ C  ◯ D`).
   - **Section B**: Short Answer Questions (with optional sub-choices, e.g. "Attempt any 8 out of 11").
   - **Section C**: Long / Detailed Questions with comprehensive marking rubrics.
   - Official institutional header with School Name, Subject, Class, Roll Number boxes, Date, and Time Allowed.
   - Invigilator and Principal digital signature lines.

5. **True Native Bilingual Urdu & English DOCX Generation**:
   - Word OpenXML paragraph-level (`w:bidi`) and run-level (`w:rtl`) right-to-left formatting.
   - Professional font pairing: **Noto Nastaliq Urdu** / **Jameel Noori Nastaleeq** for Urdu, and **Times New Roman** / **Calibri** for English.
   - Separate generation of **Confidential Marking Guides / Answer Keys** ensuring students never receive answer hints on exam papers.

6. **Public Anti-Tamper Paper Verification**:
   - Unique cryptographic verification code embedded on every generated paper (`EF-XXXX-YYYY`).
   - Dedicated public endpoint (`GET /api/v1/papers/verify/{code}`) allowing invigilators and board officials to verify paper authenticity and question integrity.

7. **Claymorphic Tactile User Experience**:
   - Bespoke soft 3D inflated surfaces, tactile buttons, and organic pill navigation.
   - Dedicated **About ExamForge AI** page highlighting design philosophy and creator spotlight for **Muhammad Ali** (`https://alibuild.site`).

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4, Lucide Icons |
| **Backend** | Python 3.14, FastAPI, SQLAlchemy 2.x, Pydantic v2, PyMuPDF (fitz), python-docx, PyJWT, bcrypt |
| **Database** | SQLite (Zero-config local development) / PostgreSQL 15+ (Production) |
| **AI Providers** | Google Gemini 2.5 Flash, Anthropic Claude, and Grounded Deterministic Mock |
| **Design** | Modern Claymorphism (Soft 3D elevations, organic badges, tactile pills) |

---

## 🔑 Pre-Seeded Accounts

The database automatically initializes with a demonstration school (*Lahore Grammar School*) and three role accounts:

| Role | Email | Password | Scope |
|---|---|---|---|
| **Teacher** | `teacher@lgs.edu.pk` | `Teacher@1234` | Upload books, generate papers, inspect evidence, edit questions, export DOCX |
| **School Admin** | `admin@lgs.edu.pk` | `Admin@1234` | Manage school teachers, view billing analytics, quota usage, and audit logs |
| **Super Admin** | `superadmin@examforge.ai` | `Admin@1234` | Cross-tenant administration, adjust school subscription quotas, system monitoring |

*(In the frontend, click the role switch buttons in the navbar or log in via `/login`).*

---

## 🏃 Quick Start (Local Development)

### 1. Backend Setup

```powershell
# Navigate to project root
$env:PYTHONPATH='backend'

# Run database setup & SQLite column introspection
.\backend\venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'backend'); from app.core.init_db import init_db; init_db()"

# Seed KPK syllabus sample books
.\backend\venv\Scripts\python.exe scripts/seed_sample_books.py

# Start FastAPI server
.\backend\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API Base: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/api/v1/docs`

### 2. Frontend Setup

```powershell
cd frontend
npm install
npm run dev -- --port 3000
```

- Open `http://localhost:3000` in your web browser.

---

## 🧪 Automated Test Suite

ExamForge AI features 23 automated end-to-end tests validating multi-tenant isolation, token security, quota reservation lifecycles, single-question regeneration, DOCX formatting, and marks balance:

```powershell
$env:PYTHONPATH='backend'
.\backend\venv\Scripts\python.exe -m pytest backend/tests -v
```

All 23 tests execute in under 12 seconds with 100% pass rate.

---

## 👨‍💻 Creator Attribution

ExamForge AI was conceptualized, designed, and developed by:

**Muhammad Ali**  
*Frontend Developer & Web Developer*  
Founder & Principal at **AliBuild**  
Portfolio: [https://alibuild.site](https://alibuild.site)  
Email: [alikhanwebdeveloper@gmail.com](mailto:alikhanwebdeveloper@gmail.com)  

*Dedicated to empowering Pakistani schools, teachers, and students with modern, beautiful, and secure educational technology.*
