const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "super_admin" | "school_admin" | "teacher";
  school_id: string | null;
  school_name: string | null;
  is_active: boolean;
}

export interface Chapter {
  id: string;
  book_id: string;
  chapter_number: number;
  title: string;
  start_page: number;
  end_page: number;
  is_detected: boolean;
  confidence: number;
  detection_method: string;
}

export interface Book {
  id: string;
  school_id: string | null;
  is_global?: boolean;
  title: string;
  subject: string;
  grade: string;
  language: string;
  file_path: string;
  file_size_bytes: number;
  total_pages: number;
  processing_status: string;
  failure_reason: string | null;
  created_at: string;
  chapters: Chapter[];
}

export interface Question {
  id: string;
  section_id: string;
  question_number: number;
  question_type: string;
  question_text: string;
  options: string[];
  correct_answer: string | null;
  marks: number;
  difficulty: string;
  blooms_level?: string; // Remember, Understand, Apply, Analyze, Evaluate, Create
  source_reference: string | null;
  source_page?: number | null;
  source_excerpt?: string | null; // Exact textbook excerpt
  confidence_score?: number;
  quality_score?: number;
  duplicate_risk?: number;
  explanation: string | null;
  sort_order: number;
  review_status: string;
}

export interface Section {
  id: string;
  paper_id: string;
  title: string;
  section_type: string;
  sort_order: number;
  total_questions: number;
  questions_to_attempt: number;
  marks_per_question: number;
  total_section_marks: number;
  instructions: string | null;
  questions: Question[];
}

export interface Paper {
  id: string;
  school_id: string;
  book_id: string | null;
  title: string;
  exam_type: string;
  academic_session: string;
  grade: string;
  subject: string;
  language: string;
  time_allowed_minutes: number;
  total_marks: number;
  instructions: string | null;
  status: string;
  selected_chapters: string[];
  docx_path: string | null;
  answer_key_docx_path?: string | null;
  verification_code?: string | null;
  watermark_text?: string | null;
  created_at: string;
  updated_at: string;
  sections: Section[];
}

export interface ChapterBlueprint {
  chapter_id: string;
  chapter_title: string;
  weightage_pct: number;
  marks_allocated: number;
  mcq_count: number;
  short_count: number;
  long_count: number;
  blooms_focus: string;
}

export interface BlueprintResponse {
  total_marks: number;
  subject: string;
  grade: string;
  chapters: ChapterBlueprint[];
  blooms_summary: Record<string, number>;
  difficulty_summary: Record<string, number>;
}

export interface MarksValidationResult {
  is_valid: boolean;
  configured_total_marks: number;
  calculated_total_marks: number;
  difference: number;
  breakdown: Array<{
    section_title: string;
    total_questions: number;
    questions_to_attempt: number;
    marks_per_question: number;
    calculated_section_marks: number;
  }>;
  warnings: string[];
}

export class ApiClient {
  private static getToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("examforge_token");
    }
    return null;
  }

  static async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorDetail = "An unexpected error occurred";
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || errorDetail;
      } catch {
        // fallback
      }
      throw new Error(errorDetail);
    }

    return response.json();
  }

  // Auth
  static async login(email: string, password: string) {
    return this.request<{ access_token: string; user: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  static async getMe() {
    return this.request<User>("/auth/me");
  }

  static async listSchools(): Promise<Array<{ id: string; name: string; slug: string; logo_url: string | null; address: string | null }>> {
    return this.request("/auth/schools");
  }

  static async registerSchool(data: {
    school_name: string;
    slug: string;
    logo_url?: string;
    address?: string;
    admin_name: string;
    admin_email: string;
    admin_password: string;
  }) {
    return this.request<{
      message: string;
      email: string;
      school_id: string;
      school_name: string;
    }>("/auth/register-school", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  static async verifyEmail(email: string, code: string) {
    return this.request<{ access_token: string; user: User }>("/auth/verify-email", {
      method: "POST",
      body: JSON.stringify({ email, code }),
    });
  }

  static async resendVerificationCode(email: string) {
    return this.request<{ message: string; email: string }>("/auth/resend-code", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  }

  static async registerTeacher(data: {
    school_id: string;
    full_name: string;
    email: string;
    password: string;
  }) {
    return this.request<{ access_token: string; user: User }>("/auth/register-teacher", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Quota & Subscriptions
  static async getSubjectQuota(subject: string): Promise<{
    subject: string;
    school_id: string;
    school_name: string;
    subscription_tier: string;
    is_paid: boolean;
    papers_used: number;
    max_free_papers: number;
    remaining_free_papers: number;
    can_generate: boolean;
    owner_name: string;
    owner_email: string;
    owner_portfolio: string;
  }> {
    return this.request(`/papers/subject-quota?subject=${encodeURIComponent(subject)}`);
  }

  static async upgradeSubscription(schoolId: string, tier = "paid") {
    return this.request<{
      message: string;
      school_id: string;
      subscription_tier: string;
      is_paid: boolean;
      max_monthly_papers: number;
    }>(`/schools/${schoolId}/upgrade-subscription?tier=${encodeURIComponent(tier)}`, {
      method: "POST",
    });
  }

  static async downloadBookPdf(bookId: string, filename: string) {
    const token = this.getToken();
    const response = await fetch(`${API_BASE_URL}/books/${bookId}/download-pdf`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!response.ok) {
      throw new Error("Failed to download PDF textbook.");
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename.endsWith(".pdf") ? filename : `${filename}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  // Books
  static async listBooks() {
    return this.request<Book[]>("/books");
  }

  static async getBook(id: string) {
    return this.request<Book>(`/books/${id}`);
  }

  static async uploadBook(formData: FormData) {
    return this.request<Book>("/books/upload", {
      method: "POST",
      body: formData,
    });
  }

  static async updateChapter(bookId: string, chapterId: string, data: Partial<Chapter>) {
    return this.request<Chapter>(`/books/${bookId}/chapters/${chapterId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  static async addChapter(bookId: string, data: { chapter_number: number; title: string; start_page: number; end_page: number }) {
    return this.request<Chapter>(`/books/${bookId}/chapters`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Papers
  static async validateMarks(data: any) {
    return this.request<MarksValidationResult>("/papers/validate-marks", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  static async generatePaper(data: any) {
    return this.request<Paper>("/papers/generate", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  static async listPapers() {
    return this.request<Paper[]>("/papers");
  }

  static async getPaper(id: string) {
    return this.request<Paper>(`/papers/${id}`);
  }

  static async updateQuestion(paperId: string, questionId: string, data: Partial<Question>) {
    return this.request<Question>(`/papers/${paperId}/questions/${questionId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  static async regenerateQuestion(paperId: string, questionId: string) {
    return this.request<Question>(`/papers/${paperId}/questions/${questionId}/regenerate`, {
      method: "POST",
    });
  }

  static async deleteQuestion(paperId: string, questionId: string) {
    return this.request<void>(`/papers/${paperId}/questions/${questionId}`, {
      method: "DELETE",
    });
  }

  static async exportDocx(paperId: string, includeAnswerKey: boolean = false): Promise<{ message: string; download_url: string }> {
    return this.request<{ message: string; download_url: string }>(`/papers/${paperId}/export-docx?include_answer_key=${includeAnswerKey}`, {
      method: "POST",
    });
  }

  static async exportAnswerKey(paperId: string): Promise<{ message: string; download_url: string }> {
    return this.request<{ message: string; download_url: string }>(`/papers/${paperId}/export-answer-key`, {
      method: "POST",
    });
  }

  static getDocxDownloadUrl(paperId: string): string {
    const token = this.getToken();
    return `${API_BASE_URL}/papers/${paperId}/download-docx${token ? `?token=${encodeURIComponent(token)}` : ""}`;
  }

  static async downloadDocx(paperId: string, filename?: string): Promise<void> {
    const token = this.getToken();
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/papers/${paperId}/download-docx`, {
      method: "GET",
      headers,
    });

    if (!response.ok) {
      let errorDetail = "Failed to download paper file.";
      try {
        const data = await response.json();
        errorDetail = data.detail || errorDetail;
      } catch {
        // Fallback
      }
      throw new Error(errorDetail);
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    
    // Extract filename from Content-Disposition header if available
    let resolvedFilename = filename;
    const disposition = response.headers.get("Content-Disposition");
    if (!resolvedFilename && disposition && disposition.includes("filename=")) {
      const match = disposition.match(/filename="?([^"]+)"?/);
      if (match && match[1]) {
        resolvedFilename = match[1];
      }
    }
    link.download = resolvedFilename || `ExamPaper_${paperId}.docx`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => window.URL.revokeObjectURL(downloadUrl), 1000);
  }

  static async downloadAnswerKey(paperId: string, filename?: string): Promise<void> {
    const token = this.getToken();
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/papers/${paperId}/download-answer-key`, {
      method: "GET",
      headers,
    });

    if (!response.ok) {
      let errorDetail = "Failed to download confidential answer key.";
      try {
        const data = await response.json();
        errorDetail = data.detail || errorDetail;
      } catch {
        // Fallback
      }
      throw new Error(errorDetail);
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;

    let resolvedFilename = filename;
    const disposition = response.headers.get("Content-Disposition");
    if (!resolvedFilename && disposition && disposition.includes("filename=")) {
      const match = disposition.match(/filename="?([^"]+)"?/);
      if (match && match[1]) {
        resolvedFilename = match[1];
      }
    }
    link.download = resolvedFilename || `CONFIDENTIAL_AnswerKey_${paperId}.docx`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => window.URL.revokeObjectURL(downloadUrl), 1000);
  }

  // Enterprise Blueprint & Verification
  static async generateBlueprint(data: { grade: string; subject: string; total_marks: number; selected_chapter_ids: string[] }): Promise<BlueprintResponse> {
    return this.request<BlueprintResponse>("/papers/generate-blueprint", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  static async verifyPaper(code: string): Promise<any> {
    return this.request<any>(`/papers/verify/${encodeURIComponent(code)}`);
  }

  // School Billing & Audit Logs
  static async getBillingAnalytics(schoolId: string): Promise<any> {
    return this.request<any>(`/schools/${schoolId}/billing-analytics`);
  }

  static async getAuditLogs(schoolId: string, limit: number = 25): Promise<any[]> {
    return this.request<any[]>(`/schools/${schoolId}/audit-logs?limit=${limit}`);
  }
}
