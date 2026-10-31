# ExamForge AI — REST API Documentation (v1)

> **Architect**: **Muhammad Ali** (Frontend Developer & Web Developer | [alibuild.site](https://alibuild.site))  
> **Base URL**: `http://localhost:8000/api/v1`  
> **Interactive Swagger UI**: `http://localhost:8000/api/v1/docs`  
> **OpenAPI JSON**: `http://localhost:8000/api/v1/openapi.json`

---

## 1. Authentication Endpoints (`/auth`)

### 1.1 Register School & Admin Account
- **Endpoint**: `POST /auth/register`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "school_name": "Peshawar Model Degree College",
    "contact_email": "principal@pmdc.edu.pk",
    "admin_full_name": "Principal Khan",
    "admin_password": "SecurePassword@123"
  }
  ```
- **Response**: `201 Created` with School and Admin User object.

### 1.2 User Login (Get JWT Token)
- **Endpoint**: `POST /auth/login`
- **Access**: Public
- **Request Body**: `OAuth2PasswordRequestForm` (`username` = email, `password` = password)
- **Response**: `200 OK`
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "c623be87-5c24-4f40-a17f-e224e756c9a3",
      "email": "teacher@lgs.edu.pk",
      "full_name": "Teacher Account",
      "role": "teacher",
      "school_id": "01c9b360-ff8f-4318-ae71-d686f0d9c495",
      "school_name": "Lahore Grammar School"
    }
  }
  ```

### 1.3 Get Authenticated User Profile
- **Endpoint**: `GET /auth/me`
- **Access**: Bearer Token required
- **Response**: `200 OK` with user details.

---

## 2. Books & Syllabus Management (`/books`)

### 2.1 List School Books
- **Endpoint**: `GET /books/`
- **Access**: Authenticated School Members
- **Query Params**: `skip` (default 0), `limit` (default 20), `subject`, `grade`

### 2.2 Upload Textbook PDF
- **Endpoint**: `POST /books/upload`
- **Access**: Teachers / School Admins
- **Content-Type**: `multipart/form-data`
- **Form Fields**: `file` (PDF file), `title`, `grade`, `subject`, `medium` (`english` or `urdu`)

### 2.3 Get Book Details & Chapters
- **Endpoint**: `GET /books/{id}`
- **Access**: School Members
- **Response**: Book metadata and detected chapter boundaries (`start_page`, `end_page`).

### 2.4 Update Chapter Boundaries
- **Endpoint**: `PUT /books/{book_id}/chapters/{chapter_id}`
- **Access**: Teachers / School Admins
- **Request Body**:
  ```json
  {
    "title": "Kinematics",
    "start_page": 14,
    "end_page": 38
  }
  ```
- **Validation**: Enforces `start_page >= 1`, `end_page >= start_page`, `end_page <= total_pages`.

---

## 3. Examination Papers (`/papers`)

### 3.1 Generate Examination Blueprint (Cognitive Balancer)
- **Endpoint**: `POST /papers/generate-blueprint`
- **Access**: School Members
- **Request Body**:
  ```json
  {
    "book_id": "9618b761-04e8-4b71-b27e-3ba34a6549f0",
    "total_marks": 75,
    "mcq_count": 12,
    "short_count": 11,
    "long_count": 3
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "total_marks": 75,
    "sections": [
      {"name": "Section A", "type": "mcq", "count": 12, "marks_per_question": 1},
      {"name": "Section B", "type": "short", "count": 11, "attempt_count": 8, "marks_per_question": 4},
      {"name": "Section C", "type": "long", "count": 3, "attempt_count": 2, "marks_per_question": 9}
    ],
    "blooms_distribution": {
      "Remember": 20,
      "Understand": 35,
      "Apply": 25,
      "Analyze": 15,
      "Evaluate": 5
    }
  }
  ```

### 3.2 Create & Generate Paper
- **Endpoint**: `POST /papers/`
- **Access**: Teachers / Admins (Checks and locks quota reservation)
- **Request Body**:
  ```json
  {
    "title": "Physics Midterm Exam 2026",
    "grade": "10",
    "subject": "Physics",
    "medium": "english",
    "duration_minutes": 180,
    "total_marks": 75,
    "sections": [...],
    "chapter_ids": ["..."]
  }
  ```

### 3.3 Public Anti-Tamper Paper Verification
- **Endpoint**: `GET /papers/verify/{verification_code}`
- **Access**: Public
- **Response**: `200 OK`
  ```json
  {
    "verification_code": "EF-77D5-6CB2",
    "paper_title": "Physics Midterm Exam 2026",
    "grade": "10",
    "subject": "Physics",
    "school_name": "Lahore Grammar School",
    "total_marks": 75,
    "question_count": 26,
    "created_at": "2026-10-28T16:21:40"
  }
  ```

### 3.4 Regenerate Individual Question
- **Endpoint**: `POST /papers/{paper_id}/questions/{question_id}/regenerate`
- **Access**: Teachers / Admins
- **Description**: Atomically regenerates a single question with fresh textbook provenance without altering any other question on the examination paper.

---

## 4. Document Export Endpoints

### 4.1 Export Student Examination Paper (.docx)
- **Endpoint**: `GET /papers/{id}/download-docx`
- **Access**: School Members
- **Output**: Professional Word document formatted in BISEP layout with bubble options, institutional headers, and zero answer leaks.

### 4.2 Export Confidential Marking Scheme (.docx)
- **Endpoint**: `GET /papers/{id}/download-answer-key`
- **Access**: School Members
- **Output**: Secure Word document containing official teacher answers, marking schemes, and Bloom's Taxonomy classification matrix.

---

## 5. School Administration & Analytics (`/schools`)

### 5.1 Get School Billing & Usage Analytics
- **Endpoint**: `GET /schools/{id}/billing-analytics`
- **Access**: School Admins & Super Admins
- **Response**: Monthly usage trends, quota utilization percentage, storage consumed, and teacher count.

### 5.2 Reset Monthly Paper Quota
- **Endpoint**: `POST /schools/{id}/reset-monthly-quota`
- **Access**: School Admins & Super Admins
- **Description**: Resets `used_monthly_papers` to zero and logs audit event.

### 5.3 Retrieve Institutional Audit Logs
- **Endpoint**: `GET /schools/{id}/audit-logs`
- **Access**: School Admins & Super Admins
- **Description**: Returns immutable chronological log of actions, role switches, and quota events.

---

## 6. Developer Attribution

Authored by:  
**Muhammad Ali**  
Frontend Developer & Web Developer | Founder of **AliBuild**  
Portfolio: [https://alibuild.site](https://alibuild.site)  
Email: [alikhanwebdeveloper@gmail.com](mailto:alikhanwebdeveloper@gmail.com)
