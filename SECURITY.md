# ExamForge AI — Security Architecture & Threat Model

> **Author**: **Muhammad Ali** (Frontend Developer & Web Developer | [alibuild.site](https://alibuild.site))  
> **Classification**: Security Specification & Implementation Standards  
> **Application**: ExamForge AI Multi-Tenant SaaS

---

## 1. Threat Model & Security Posture

ExamForge AI operates in educational environments where academic integrity, student data privacy, and intellectual property (textbooks, proprietary exam questions) are critical. The system is designed against the following primary threat vectors:

1. **Cross-Tenant Data Leakage**: School A accessing School B's uploaded textbooks, draft exam papers, or confidential marking schemes.
2. **Quota Circumvention & Race Conditions**: Malicious users initiating concurrent paper generations to bypass school monthly paper limits.
3. **Privilege Escalation**: School Admins or Teachers modifying their account roles or school subscription limits.
4. **Malicious File Uploads**: Uploading executable binaries, shell scripts, or path-traversal payloads disguised as PDF textbooks.
5. **Exam Paper Tampering**: Unauthorized alteration of printed or exported examination papers before distribution to students.
6. **Confidential Answer Key Exposure**: Student examination papers inadvertently including answer keys or teacher solutions.

---

## 2. Authentication & Session Security

### 2.1 JWT Signature & Algorithm Enforcement
- **Algorithm**: Hardened to `HS256`. Token decoding strictly prohibits `none` algorithm or mismatched signing keys.
- **Expiry**: Access tokens expire after a configured duration (default: 60 minutes). Expired tokens immediately return `401 Unauthorized` with `Token has expired`.
- **Malformed Tokens**: Any signature mismatch, malformed base64 segment, or tampered payload returns `401 Unauthorized` with `Could not validate credentials`.
- **Claims Verification**:
  ```json
  {
    "sub": "user_id_uuid",
    "email": "teacher@lgs.edu.pk",
    "role": "teacher",
    "school_id": "school_id_uuid",
    "exp": 1793200000
  }
  ```

### 2.2 Password Security
- Passwords are encrypted using **bcrypt** with salted hashing.
- Raw passwords are never logged, serialized in API responses, or stored in plaintext.

### 2.3 Account & Tenant Invalidation
- When a user's `is_active` flag is set to `False`, all subsequent requests fail with `400 Inactive user`.
- When a school's status is set to `suspended`, requests by members of that school fail with `403 School account is suspended`.

---

## 3. Role-Based Access Control (RBAC) Matrix

| Operation / Resource | Super Admin | School Admin | Teacher | Public / Unauth |
|---|---|---|---|---|
| Register School & Admin Account | Yes | No | No | Yes (via `/register`) |
| Login / Refresh Token | Yes | Yes | Yes | Yes |
| View / Verify Public Paper Code | Yes | Yes | Yes | Yes (Read-only via `/verify/{code}`) |
| Modify School Subscription Limits | Yes | No (Stripped) | No | No |
| Invite / Manage School Teachers | Yes | Yes (Own school) | No | No |
| View School Billing & Audit Logs | Yes | Yes (Own school) | No | No |
| Upload PDF Textbooks | Yes | Yes (Own school) | Yes (Own school) | No |
| Generate Examination Papers | Yes | Yes (Own school) | Yes (Own school) | No |
| Edit & Regenerate Questions | Yes | Yes (Own school) | Yes (Own school) | No |
| Download Student DOCX Paper | Yes | Yes (Own school) | Yes (Own school) | No |
| Download Confidential Answer Key | Yes | Yes (Own school) | Yes (Own school) | No |

---

## 4. Multi-Tenant Isolation Controls

1. **Server-Side School ID Derivation**:
   All database queries filter by `current_user.school_id`. No client-supplied tenant ID is accepted for data access.
2. **Path Traversal & Foreign Key Verification**:
   When referencing sub-resources (such as `book_id`, `chapter_id`, `paper_id`), the API verifies that the foreign key also belongs to `current_user.school_id`:
   ```python
   book = db.query(Book).filter(Book.id == book_id, Book.school_id == current_user.school_id).first()
   if not book:
       raise HTTPException(status_code=404, detail="Book not found in your institution")
   ```
3. **Privilege Escalation Protection on School Profile**:
   The `PATCH /api/v1/schools/{id}` endpoint specifically strips `max_teachers`, `max_monthly_papers`, `subscription_plan`, `status`, and `is_active` unless the caller possesses the `super_admin` role.

---

## 5. Concurrency-Safe Quota Reservations

To prevent race conditions during paper generation, ExamForge AI employs atomic `UsageReservation` tokens:

```
[ Teacher clicks Generate ]
          |
          v
[ Lock School Row & Query Available Quota ]
          |
  [ Quota Exceeded? ] ---> YES ---> [ 403 HTTP Quota Exceeded ]
          | NO
          v
[ Create UsageReservation (status='reserved', expires_at=now + 15m) ]
          |
          v
[ Execute Async/Sync AI Question Generation ]
          |
    +-----+-----+
    |           |
[ Success ]  [ Failure ]
    |           |
    v           v
[ status='committed', increment used_papers ]  [ status='rolled_back', quota freed ]
```

### Auto-Reconciliation
A background reconciliation task (`reconcile_expired_reservations`) runs periodically to automatically roll back any reservations older than 15 minutes that were abandoned due to network or worker failure.

---

## 6. Upload & File System Security

1. **Filename Sanitization**:
   Incoming filenames are sanitized using `os.path.basename` and regex whitelisting (`[^a-zA-Z0-9_\-\.]`), preventing directory traversal attacks (`../../etc/passwd`).
2. **Isolated Storage Directories**:
   Files are stored in segregated school directories (`uploads/books/{school_id}/{book_id}.pdf`).
3. **MIME-Type & Magic Byte Validation**:
   Only valid PDF headers (`%PDF-`) are processed by PyMuPDF.

---

## 7. Anti-Tamper Paper Verification

1. **Unique Code Generation**:
   Every generated paper receives an immutable cryptographic code formatted as `EF-XXXX-YYYY` (e.g., `EF-4F2A-98BC`).
2. **Institutional Public Verification**:
   Invigilators, school principals, and board officers can verify the authenticity of a printed or digital paper by visiting `/api/v1/papers/verify/{code}` or scanning the paper QR code.
3. **Integrity Payload**:
   The verification response returns the exact title, grade, subject, question count, creation timestamp, and school identity without exposing the confidential answer key.

---

## 8. Developer Attribution & Reporting

For security disclosures or audit inquiries, please contact:

**Muhammad Ali**  
Lead Developer & Security Architect  
Portfolio: [https://alibuild.site](https://alibuild.site)  
Email: [alikhanwebdeveloper@gmail.com](mailto:alikhanwebdeveloper@gmail.com)
