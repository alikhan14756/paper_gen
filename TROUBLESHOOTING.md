# ExamForge AI — Developer Troubleshooting & FAQ Guide

> **Author**: **Muhammad Ali** (Frontend Developer & Web Developer | [alibuild.site](https://alibuild.site))  
> **Repository**: ExamForge AI

---

## 1. Database & SQLite Schema Evolution

### Issue: `sqlite3.OperationalError: no such column: verification_code`
- **Cause**: SQLite `Base.metadata.create_all()` creates missing tables but does not alter existing tables to add newly declared columns when models evolve.
- **Resolution**: ExamForge AI includes an automatic SQLite introspection routine in `app/core/init_db.py`. If you add new columns to SQLAlchemy models in development, simply run:
  ```powershell
  $env:PYTHONPATH='backend'
  .\backend\venv\Scripts\python.exe -c "from app.core.init_db import init_db; init_db()"
  ```
  In production with PostgreSQL, use standard Alembic migrations (`alembic upgrade head`).

---

## 2. Urdu Nastaliq Typography in Word (.docx)

### Issue: Urdu text displays in system fallback font instead of authentic Nastaliq
- **Cause**: Microsoft Word requires the target font to be installed locally to render complex Arabic/Urdu ligatures.
- **Resolution**:
  1. Download and install **Noto Nastaliq Urdu** from Google Fonts:
     `https://fonts.google.com/specimen/Noto+Nastaliq+Urdu`
  2. Or install **Jameel Noori Nastaleeq**.
  3. ExamForge AI embeds OpenXML `<w:rFonts w:cs="Noto Nastaliq Urdu" w:ascii="Noto Nastaliq Urdu"/>` into all Urdu runs, with automated fallback to `Calibri` if the font is not installed on the client machine.

---

## 3. Starlette File Download Header Encoding

### Issue: `UnicodeEncodeError: 'latin-1' codec can't encode characters in position ...: ordinal not in range(256)`
- **Cause**: Starlette `FileResponse` headers default to RFC 2616 (Latin-1). Sending Urdu characters directly in the `filename` parameter causes a runtime exception.
- **Resolution**: Dual-encode the `Content-Disposition` header using an ASCII fallback alongside the RFC 5987 UTF-8 encoded filename:
  ```python
  ascii_filename = f"ExamForge_Paper_{paper.id}.docx"
  encoded_filename = urllib.parse.quote(f"{paper.title}.docx")
  response.headers["Content-Disposition"] = (
      f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}'
  )
  ```

---

## 4. Next.js 16 Suspense Boundary Constraints

### Issue: `useSearchParams() should be wrapped in a suspense boundary at page "/..."`
- **Cause**: Next.js 16 App Router requires any client component reading query parameters (`useSearchParams()`) during static generation to be enveloped in a `<Suspense>` boundary to prevent de-optimizing the entire page tree.
- **Resolution**:
  ```tsx
  export default function MyPage() {
    return (
      <Suspense fallback={<LoadingSpinner />}>
        <PageContent />
      </Suspense>
    );
  }
  ```

---

## 5. Windows PowerShell Environment

### Issue: `ModuleNotFoundError: No module named 'app'`
- **Cause**: PowerShell runs commands from the root directory; Python needs `backend` in its `sys.path`.
- **Resolution**: Always prefix Python invocations with `$env:PYTHONPATH='backend'`:
  ```powershell
  $env:PYTHONPATH='backend'; .\backend\venv\Scripts\python.exe -m pytest backend/tests -v
  ```

---

## 6. PyMuPDF Import Deprecation

### Issue: `FutureWarning: The fitz API is deprecated and will be removed in future. Use import pymupdf instead.`
- **Cause**: PyMuPDF is phasing out the legacy `fitz` module alias in favor of the top-level `pymupdf` package.
- **Resolution**: All extraction modules in ExamForge AI import both safely:
  ```python
  try:
      import pymupdf as fitz
  except ImportError:
      import fitz
  ```

---

## 7. Creator Attribution & Support

Need assistance or custom board layout integrations?

**Muhammad Ali**  
Frontend Developer & Web Developer  
Founder & Principal at **AliBuild**  
Portfolio: [https://alibuild.site](https://alibuild.site)  
Email: [alikhanwebdeveloper@gmail.com](mailto:alikhanwebdeveloper@gmail.com)
