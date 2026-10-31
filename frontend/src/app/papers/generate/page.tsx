"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ApiClient, Book, Chapter, MarksValidationResult } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { 
  Sparkles, 
  BookOpen, 
  CheckSquare, 
  Sliders, 
  CheckCircle2, 
  AlertTriangle, 
  Plus, 
  Trash2, 
  ArrowRight, 
  ArrowLeft, 
  Loader2,
  GraduationCap,
  Building2,
  Check,
  ShieldCheck,
  Calendar,
  Clock,
  Award,
  Mail,
  Globe,
  Lock,
  Gift,
  ExternalLink,
  X
} from "lucide-react";

interface SectionFormState {
  title: string;
  section_type: "mcq" | "short" | "long";
  total_questions: number;
  questions_to_attempt: number;
  marks_per_question: number;
  instructions: string;
}

function PaperGenerationWizardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialBookId = searchParams?.get("book_id") || "";
  const { user } = useAuth();

  const [currentStep, setCurrentStep] = useState(1);
  const [books, setBooks] = useState<Book[]>([]);
  const [loadingBooks, setLoadingBooks] = useState(true);

  // Board Selection
  const [selectedBoard, setSelectedBoard] = useState("BISE Peshawar (KPK Board)");

  // Step 1: Selected Book
  const [selectedBookId, setSelectedBookId] = useState<string>(initialBookId);
  const selectedBook = books.find((b) => b.id === selectedBookId);

  // Step 2: Selected Chapters
  const [selectedChapterIds, setSelectedChapterIds] = useState<string[]>([]);

  // Step 3: Exam Details
  const [title, setTitle] = useState("Annual Examination 2026");
  const [examType, setExamType] = useState("Annual Examination");
  const [academicSession, setAcademicSession] = useState("2025-2026");
  const [grade, setGrade] = useState("10");
  const [subject, setSubject] = useState("Physics");
  const [language, setLanguage] = useState("en");
  const [timeAllowed, setTimeAllowed] = useState(120);
  const [totalMarks, setTotalMarks] = useState(50);
  const [instructions, setInstructions] = useState(
    "All questions in Section A are compulsory. Answer any 5 short questions from Section B."
  );

  // Step 4: Sections Configuration
  const [sections, setSections] = useState<SectionFormState[]>([
    {
      title: "Section A — Multiple Choice Questions",
      section_type: "mcq",
      total_questions: 10,
      questions_to_attempt: 10,
      marks_per_question: 1,
      instructions: "Choose the correct answer from the given four options.",
    },
    {
      title: "Section B — Short Questions",
      section_type: "short",
      total_questions: 8,
      questions_to_attempt: 5,
      marks_per_question: 4,
      instructions: "Attempt any FIVE questions.",
    },
    {
      title: "Section C — Long Questions",
      section_type: "long",
      total_questions: 3,
      questions_to_attempt: 2,
      marks_per_question: 10,
      instructions: "Attempt any TWO questions in detail.",
    },
  ]);

  // Step 5: Validation Result
  const [validation, setValidation] = useState<MarksValidationResult | null>(null);
  const [validating, setValidating] = useState(false);

  // Step 6: Generation
  const [generating, setGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);

  // Subject Quota & Free Trial State
  interface QuotaState {
    subject: string;
    school_id?: string;
    school_name?: string;
    is_paid: boolean;
    subscription_tier: string;
    papers_used: number;
    max_free_papers: number;
    remaining_free_papers: number;
    can_generate: boolean;
    owner_name: string;
    owner_email: string;
    owner_portfolio: string;
  }
  const [quotaInfo, setQuotaInfo] = useState<QuotaState | null>(null);
  const [loadingQuota, setLoadingQuota] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [upgrading, setUpgrading] = useState(false);

  const refreshQuota = (subj: string) => {
    if (!subj) return;
    setLoadingQuota(true);
    ApiClient.getSubjectQuota(subj)
      .then((data) => setQuotaInfo(data))
      .catch(() => {})
      .finally(() => setLoadingQuota(false));
  };

  useEffect(() => {
    if (subject) {
      refreshQuota(subject);
    }
  }, [subject]);

  const handleUpgradeSubscription = async () => {
    if (!user?.school_id) return;
    setUpgrading(true);
    try {
      await ApiClient.upgradeSubscription(user.school_id, "paid");
      setShowUpgradeModal(false);
      refreshQuota(subject);
    } catch (err: any) {
      alert(err.message || "Failed to activate subscription.");
    } finally {
      setUpgrading(false);
    }
  };

  useEffect(() => {
    ApiClient.listBooks()
      .then((data) => {
        setBooks(data);
        if (data.length > 0) {
          const target = initialBookId ? data.find(b => b.id === initialBookId) || data[0] : data[0];
          setSelectedBookId(target.id);
          setSubject(target.subject);
          setGrade(target.grade);
          setLanguage(target.language);
          if (target.language === "ur") {
            setTitle("سالانہ امتحان 2026ء");
            setInstructions("حصہ اول کثیر الانتخابی سوالات لازمی ہیں۔ حصہ دوم کے کوئی سے پانچ مختصر سوالات حل کریں۔");
          }
          if (target.chapters?.length) {
            setSelectedChapterIds(target.chapters.map(c => c.id));
          }
        }
      })
      .finally(() => setLoadingBooks(false));
  }, [initialBookId]);

  const handleBookChange = (bookId: string) => {
    setSelectedBookId(bookId);
    const b = books.find((x) => x.id === bookId);
    if (b) {
      setSubject(b.subject);
      setGrade(b.grade);
      setLanguage(b.language);
      if (b.language === "ur") {
        setTitle("سالانہ امتحان 2026ء");
        setInstructions("تمام سوالات کے جوابات پرچہ سوالات کی ہدایات کے مطابق تحریر کریں۔");
      } else {
        setTitle(`Annual Examination — Grade ${b.grade} ${b.subject}`);
        setInstructions("All questions in Section A are compulsory. Answer any 5 short questions from Section B.");
      }
      if (b.chapters?.length) {
        setSelectedChapterIds(b.chapters.map(c => c.id));
      } else {
        setSelectedChapterIds([]);
      }
    }
  };

  const toggleChapter = (chapterId: string) => {
    if (selectedChapterIds.includes(chapterId)) {
      setSelectedChapterIds(selectedChapterIds.filter((id) => id !== chapterId));
    } else {
      setSelectedChapterIds([...selectedChapterIds, chapterId]);
    }
  };

  const selectAllChapters = () => {
    if (selectedBook?.chapters) {
      setSelectedChapterIds(selectedBook.chapters.map(c => c.id));
    }
  };

  const deselectAllChapters = () => {
    setSelectedChapterIds([]);
  };

  const addSection = () => {
    setSections([
      ...sections,
      {
        title: `Section ${String.fromCharCode(65 + sections.length)}`,
        section_type: "short",
        total_questions: 5,
        questions_to_attempt: 5,
        marks_per_question: 2,
        instructions: "Answer all questions.",
      },
    ]);
  };

  const removeSection = (index: number) => {
    setSections(sections.filter((_, i) => i !== index));
  };

  const updateSection = (index: number, field: keyof SectionFormState, val: any) => {
    const updated = [...sections];
    updated[index] = { ...updated[index], [field]: val };
    setSections(updated);
  };

  // Run validation
  const runValidation = async () => {
    setValidating(true);
    try {
      const payload = {
        book_id: selectedBookId,
        selected_chapter_ids: selectedChapterIds,
        title,
        grade,
        subject,
        language,
        total_marks: Number(totalMarks),
        sections: sections.map((s, idx) => ({
          title: s.title,
          section_type: s.section_type,
          sort_order: idx + 1,
          total_questions: Number(s.total_questions),
          questions_to_attempt: Number(s.questions_to_attempt),
          marks_per_question: Number(s.marks_per_question),
          total_section_marks: Number(s.questions_to_attempt) * Number(s.marks_per_question),
          instructions: s.instructions,
        })),
      };
      const res = await ApiClient.validateMarks(payload);
      setValidation(res);
    } catch (err: any) {
      alert("Validation failed: " + err.message);
    } finally {
      setValidating(false);
    }
  };

  const handleGenerate = async () => {
    if (!selectedBookId) {
      alert("Please select a textbook first.");
      return;
    }
    if (selectedChapterIds.length === 0) {
      alert("Please select at least one chapter.");
      return;
    }

    if (quotaInfo && !quotaInfo.can_generate) {
      setShowUpgradeModal(true);
      return;
    }

    setGenerating(true);
    setGenerationError(null);

    const payload = {
      book_id: selectedBookId,
      selected_chapter_ids: selectedChapterIds,
      title,
      exam_type: examType,
      academic_session: academicSession,
      grade,
      subject,
      language,
      time_allowed_minutes: Number(timeAllowed),
      total_marks: Number(totalMarks),
      instructions,
      sections: sections.map((s, idx) => ({
        title: s.title,
        section_type: s.section_type,
        sort_order: idx + 1,
        total_questions: Number(s.total_questions),
        questions_to_attempt: Number(s.questions_to_attempt),
        marks_per_question: Number(s.marks_per_question),
        total_section_marks: Number(s.questions_to_attempt) * Number(s.marks_per_question),
        instructions: s.instructions,
      })),
    };

    try {
      const createdPaper = await ApiClient.generatePaper(payload);
      router.push(`/papers/${createdPaper.id}`);
    } catch (err: any) {
      const msg = err.message || "Failed to generate examination paper.";
      setGenerationError(msg);
      if (msg.toLowerCase().includes("free trial limit") || msg.toLowerCase().includes("muhammad ali")) {
        setShowUpgradeModal(true);
      }
      setGenerating(false);
    }
  };

  // Step Calculation
  const totalCalculatedMarks = sections.reduce(
    (acc, s) => acc + Number(s.questions_to_attempt) * Number(s.marks_per_question),
    0
  );
  const marksMatch = totalCalculatedMarks === Number(totalMarks);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto space-y-2">
        <div className="inline-flex items-center px-3.5 py-1.5 rounded-full text-xs font-bold clay-badge-mint">
          <GraduationCap className="w-4 h-4 mr-1.5" />
          KPK Peshawar Board (BISEP) Pattern Generator
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
          Create Examination Paper
        </h1>
        <p className="text-sm text-slate-600">
          Configure syllabus chapters, question distribution, marks allocation, and generate a print-ready exam.
        </p>
      </div>

      {/* Subject Quota & Free Trial Status Pill */}
      {quotaInfo && (
        <div className="max-w-3xl mx-auto">
          <div className={`clay-card p-3.5 px-5 rounded-2xl flex items-center justify-between gap-4 border ${
            quotaInfo.is_paid
              ? "bg-emerald-50/50 border-emerald-200"
              : quotaInfo.remaining_free_papers > 0
              ? "bg-orange-50/50 border-orange-200"
              : "bg-red-50/60 border-red-200"
          }`}>
            <div className="flex items-center space-x-3">
              <div className={`h-9 w-9 rounded-xl flex items-center justify-center shrink-0 shadow-sm ${
                quotaInfo.is_paid 
                  ? "bg-emerald-600 text-white" 
                  : quotaInfo.remaining_free_papers > 0 
                  ? "bg-orange-600 text-white" 
                  : "bg-red-600 text-white"
              }`}>
                {quotaInfo.is_paid ? <Award className="w-4 h-4" /> : quotaInfo.remaining_free_papers > 0 ? <Gift className="w-4 h-4" /> : <Lock className="w-4 h-4" />}
              </div>
              <div className="text-left">
                <p className="text-xs font-black text-slate-900">
                  {quotaInfo.is_paid ? (
                    "Paid Subscription Active — Unlimited Generation"
                  ) : (
                    <span>Free Trial Quota: <strong className="text-orange-600">{quotaInfo.papers_used} of {quotaInfo.max_free_papers}</strong> Free Papers Used for {quotaInfo.subject}</span>
                  )}
                </p>
                <p className="text-[11px] text-slate-600">
                  {quotaInfo.is_paid ? (
                    "Your school has full access to all Class 9th and 10th subjects."
                  ) : quotaInfo.remaining_free_papers > 0 ? (
                    <span>You have <strong>{quotaInfo.remaining_free_papers} free paper{quotaInfo.remaining_free_papers > 1 ? "s" : ""}</strong> remaining for {quotaInfo.subject}.</span>
                  ) : (
                    <span className="text-red-600 font-bold">2/2 papers limit reached for this subject. Upgrade or contact owner Muhammad Ali to continue.</span>
                  )}
                </p>
              </div>
            </div>

            {!quotaInfo.is_paid && (
              <button
                type="button"
                onClick={() => setShowUpgradeModal(true)}
                className="clay-btn-light px-3.5 py-1.5 text-[11px] font-extrabold whitespace-nowrap shrink-0 flex items-center space-x-1"
              >
                <span>{quotaInfo.remaining_free_papers > 0 ? "Upgrade Plan" : "Unlock Subject"}</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* Stepper (Clay Pills) */}
      <div className="clay-card p-3 flex items-center justify-between overflow-x-auto max-w-3xl mx-auto gap-2">
        {[
          { num: 1, title: "1. Select Textbook" },
          { num: 2, title: "2. Pick Chapters" },
          { num: 3, title: "3. Exam Info" },
          { num: 4, title: "4. Sections & Marks" },
          { num: 5, title: "5. Review & Generate" },
        ].map((s) => {
          const isActive = currentStep === s.num;
          const isDone = currentStep > s.num;
          return (
            <button
              key={s.num}
              onClick={() => setCurrentStep(s.num)}
              className={`flex-1 min-w-[120px] py-2 px-3 rounded-2xl text-xs font-bold transition-all text-center ${
                isActive
                  ? "clay-btn-primary shadow-sm"
                  : isDone
                  ? "clay-btn-dark shadow-xs"
                  : "text-slate-500 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              {s.title}
            </button>
          );
        })}
      </div>

      {/* Main Wizard Form Card */}
      <div className="clay-card p-6 sm:p-10 space-y-6">

        {/* ----------------- STEP 1: SELECT TEXTBOOK ----------------- */}
        {currentStep === 1 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-black text-slate-900 flex items-center">
                <BookOpen className="w-5 h-5 mr-2 text-orange-600" />
                Step 1: Choose Textbook & Board
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Select from pre-loaded KPK Textbook Board Peshawar syllabus books or upload your custom book.
              </p>
            </div>

            {/* Target Board Selector */}
            <div className="clay-card-flat p-4 space-y-2">
              <label className="block text-xs font-bold text-slate-700">
                Examination Board Authority
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  "BISE Peshawar (KPK Board)",
                  "BISE Mardan / Malakand (KPK)",
                  "Federal Board Islamabad (FBISE)"
                ].map((bName) => (
                  <button
                    key={bName}
                    type="button"
                    onClick={() => setSelectedBoard(bName)}
                    className={`p-3 rounded-2xl text-xs font-bold text-left transition border ${
                      selectedBoard === bName
                        ? "clay-btn-primary text-white border-transparent"
                        : "bg-white text-slate-700 border-slate-200 hover:border-orange-400"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span>{bName}</span>
                      {selectedBoard === bName && <Check className="w-4 h-4 ml-1" />}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Book Selection Grid */}
            <div className="space-y-3">
              <label className="block text-xs font-bold text-slate-700">
                Select Available Syllabus Textbook *
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {books.map((b) => {
                  const isSelected = b.id === selectedBookId;
                  const isUrdu = b.language === "ur";
                  const isKPK = b.title.includes("KPK") || b.title.includes("خیبر");

                  return (
                    <div
                      key={b.id}
                      onClick={() => handleBookChange(b.id)}
                      className={`clay-card-interactive p-4 cursor-pointer relative ${
                        isSelected
                          ? "ring-3 ring-orange-500 bg-orange-50/20"
                          : ""
                      }`}
                    >
                      {isSelected && (
                        <div className="absolute top-3 right-3 w-6 h-6 rounded-full bg-orange-600 text-white flex items-center justify-center shadow-md">
                          <Check className="w-3.5 h-3.5" />
                        </div>
                      )}

                      <div className="flex items-center space-x-2 mb-2">
                        {isKPK && (
                          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full clay-badge-mint">
                            KPK Textbook Board
                          </span>
                        )}
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          isUrdu ? "clay-badge-peach" : "clay-badge-sky"
                        }`}>
                          {isUrdu ? "اردو" : "English"}
                        </span>
                      </div>

                      <h3 className={`font-black text-sm text-slate-900 ${isUrdu ? "urdu-text text-base" : ""}`}>
                        {b.title}
                      </h3>

                      <div className="flex items-center gap-3 text-xs text-slate-500 mt-2">
                        <span>Subject: <strong>{b.subject}</strong></span>
                        <span>•</span>
                        <span>Grade: <strong>{b.grade}</strong></span>
                        <span>•</span>
                        <span>{b.chapters?.length || 0} Chapters</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="flex justify-end pt-4">
              <button
                type="button"
                onClick={() => setCurrentStep(2)}
                className="clay-btn-primary px-6 py-3 text-xs flex items-center space-x-2"
              >
                <span>Proceed to Chapter Selection</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* ----------------- STEP 2: SELECT CHAPTERS ----------------- */}
        {currentStep === 2 && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-black text-slate-900 flex items-center">
                  <CheckSquare className="w-5 h-5 mr-2 text-orange-600" />
                  Step 2: Syllabus & Chapter Selection
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Selected Textbook: <strong className="text-slate-900">{selectedBook?.title}</strong>
                </p>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={selectAllChapters}
                  className="clay-btn-light px-3 py-1.5 text-xs text-slate-700"
                >
                  Select All
                </button>
                <button
                  type="button"
                  onClick={deselectAllChapters}
                  className="clay-btn-light px-3 py-1.5 text-xs text-slate-700"
                >
                  Deselect All
                </button>
              </div>
            </div>

            {/* Chapters Chip Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {selectedBook?.chapters?.map((ch) => {
                const isChecked = selectedChapterIds.includes(ch.id);
                const isUrdu = selectedBook.language === "ur";

                return (
                  <div
                    key={ch.id}
                    onClick={() => toggleChapter(ch.id)}
                    className={`clay-card-interactive p-4 cursor-pointer flex items-center justify-between ${
                      isChecked ? "ring-2 ring-orange-500 bg-orange-50/20" : ""
                    }`}
                  >
                    <div className="flex items-center space-x-3 min-w-0 pr-2">
                      <div className={`w-5 h-5 rounded-lg flex items-center justify-center border transition ${
                        isChecked ? "bg-orange-600 border-orange-600 text-white" : "border-slate-300 bg-white"
                      }`}>
                        {isChecked && <Check className="w-3.5 h-3.5" />}
                      </div>

                      <div className="min-w-0">
                        <p className={`font-bold text-xs text-slate-900 truncate ${isUrdu ? "urdu-text" : ""}`}>
                          {ch.title}
                        </p>
                        <p className="text-[11px] text-slate-500">
                          Pages {ch.start_page}–{ch.end_page}
                        </p>
                      </div>
                    </div>

                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full clay-badge-sky shrink-0">
                      Ch #{ch.chapter_number}
                    </span>
                  </div>
                );
              })}
            </div>

            <div className="flex justify-between items-center pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setCurrentStep(1)}
                className="clay-btn-light px-5 py-2.5 text-xs flex items-center space-x-1.5"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </button>

              <button
                type="button"
                onClick={() => setCurrentStep(3)}
                disabled={selectedChapterIds.length === 0}
                className="clay-btn-primary px-6 py-3 text-xs flex items-center space-x-2 disabled:opacity-50"
              >
                <span>Continue with {selectedChapterIds.length} Chapters</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* ----------------- STEP 3: EXAM INFORMATION ----------------- */}
        {currentStep === 3 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-black text-slate-900 flex items-center">
                <Sliders className="w-5 h-5 mr-2 text-orange-600" />
                Step 3: Examination Metadata & Rules
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Configure official examination title, class, duration, and general candidate instructions.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Examination Paper Title *
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full clay-input px-3.5 py-2.5 text-xs"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Examination Type
                </label>
                <select
                  value={examType}
                  onChange={(e) => setExamType(e.target.value)}
                  className="w-full clay-input px-3.5 py-2.5 text-xs"
                >
                  <option value="Annual Examination">Annual Examination (سالانہ امتحان)</option>
                  <option value="Midterm Examination">Midterm Examination (ششماہی امتحان)</option>
                  <option value="Pre-Board Assessment">Pre-Board Assessment (پری بورڈ)</option>
                  <option value="Class Test">Class Test / Monthly Test</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Academic Session
                </label>
                <input
                  type="text"
                  value={academicSession}
                  onChange={(e) => setAcademicSession(e.target.value)}
                  placeholder="2025-2026"
                  className="w-full clay-input px-3.5 py-2.5 text-xs"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Time Allowed (Minutes)
                </label>
                <input
                  type="number"
                  value={timeAllowed}
                  onChange={(e) => setTimeAllowed(Number(e.target.value))}
                  className="w-full clay-input px-3.5 py-2.5 text-xs"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Total Paper Marks *
                </label>
                <input
                  type="number"
                  value={totalMarks}
                  onChange={(e) => setTotalMarks(Number(e.target.value))}
                  className="w-full clay-input px-3.5 py-2.5 text-xs"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Examination Language
                </label>
                <div className="flex space-x-3 pt-1">
                  <label className="inline-flex items-center text-xs font-semibold">
                    <input
                      type="radio"
                      name="lang"
                      checked={language === "en"}
                      onChange={() => setLanguage("en")}
                      className="mr-1.5 text-orange-600"
                    />
                    English (LTR)
                  </label>
                  <label className="inline-flex items-center text-xs font-semibold">
                    <input
                      type="radio"
                      name="lang"
                      checked={language === "ur"}
                      onChange={() => setLanguage("ur")}
                      className="mr-1.5 text-orange-600"
                    />
                    اردو (Urdu RTL)
                  </label>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                General Instructions for Candidates
              </label>
              <textarea
                rows={2}
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                className={`w-full clay-input p-3 text-xs ${language === "ur" ? "urdu-text" : ""}`}
              />
            </div>

            <div className="flex justify-between items-center pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setCurrentStep(2)}
                className="clay-btn-light px-5 py-2.5 text-xs flex items-center space-x-1.5"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </button>

              <button
                type="button"
                onClick={() => setCurrentStep(4)}
                className="clay-btn-primary px-6 py-3 text-xs flex items-center space-x-2"
              >
                <span>Next: Configure Sections</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* ----------------- STEP 4: SECTIONS & MARKS ----------------- */}
        {currentStep === 4 && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-black text-slate-900 flex items-center">
                  <Award className="w-5 h-5 mr-2 text-orange-600" />
                  Step 4: BISEP Section Layout & Marks
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Configure Section A (MCQs with bubbles ◯), Section B (Short Questions with choice), and Section C.
                </p>
              </div>

              {/* Real-time Marks Counter Badge */}
              <div className={`px-4 py-2 rounded-2xl text-xs font-bold flex items-center space-x-2 ${
                marksMatch ? "clay-badge-mint" : "clay-badge-peach"
              }`}>
                <span>Total: {totalCalculatedMarks} / {totalMarks} Marks</span>
                {marksMatch ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <AlertTriangle className="w-4 h-4 text-orange-600" />}
              </div>
            </div>

            {/* Sections List */}
            <div className="space-y-4">
              {sections.map((sec, idx) => (
                <div key={idx} className="clay-card-flat p-4 sm:p-5 space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-black uppercase tracking-wider text-slate-700">
                      Section #{idx + 1}
                    </span>
                    {sections.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeSection(idx)}
                        className="text-red-500 hover:text-red-700 text-xs flex items-center"
                      >
                        <Trash2 className="w-3.5 h-3.5 mr-1" /> Remove
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="sm:col-span-2">
                      <label className="block text-[11px] font-bold text-slate-600 mb-1">
                        Section Title
                      </label>
                      <input
                        type="text"
                        value={sec.title}
                        onChange={(e) => updateSection(idx, "title", e.target.value)}
                        className="w-full clay-input px-3 py-2 text-xs"
                      />
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-slate-600 mb-1">
                        Question Type
                      </label>
                      <select
                        value={sec.section_type}
                        onChange={(e) => updateSection(idx, "section_type", e.target.value as any)}
                        className="w-full clay-input px-3 py-2 text-xs"
                      >
                        <option value="mcq">MCQs (Bubble Choices ◯)</option>
                        <option value="short">Short Questions (مختصر سوالات)</option>
                        <option value="long">Long Questions (تفصیلی سوالات)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-slate-600 mb-1">
                        Total Qs to Generate
                      </label>
                      <input
                        type="number"
                        min={1}
                        value={sec.total_questions}
                        onChange={(e) => updateSection(idx, "total_questions", Number(e.target.value))}
                        className="w-full clay-input px-3 py-2 text-xs"
                      />
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-slate-600 mb-1">
                        Questions to Attempt (Choice)
                      </label>
                      <input
                        type="number"
                        min={1}
                        value={sec.questions_to_attempt}
                        onChange={(e) => updateSection(idx, "questions_to_attempt", Number(e.target.value))}
                        className="w-full clay-input px-3 py-2 text-xs"
                      />
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-slate-600 mb-1">
                        Marks per Question
                      </label>
                      <input
                        type="number"
                        min={0.5}
                        step={0.5}
                        value={sec.marks_per_question}
                        onChange={(e) => updateSection(idx, "marks_per_question", Number(e.target.value))}
                        className="w-full clay-input px-3 py-2 text-xs"
                      />
                    </div>

                    <div className="sm:col-span-2">
                      <label className="block text-[11px] font-bold text-slate-600 mb-1">
                        Section Note / Attempt Rule
                      </label>
                      <input
                        type="text"
                        value={sec.instructions}
                        onChange={(e) => updateSection(idx, "instructions", e.target.value)}
                        placeholder="Attempt any 5 questions..."
                        className="w-full clay-input px-3 py-2 text-xs"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-between items-center pt-2">
              <button
                type="button"
                onClick={addSection}
                className="clay-btn-light px-4 py-2 text-xs flex items-center space-x-1.5"
              >
                <Plus className="w-4 h-4" />
                <span>Add Another Section</span>
              </button>

              <button
                type="button"
                onClick={runValidation}
                disabled={validating}
                className="clay-btn-dark px-4 py-2 text-xs flex items-center space-x-1.5"
              >
                {validating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                <span>Validate Total Marks</span>
              </button>
            </div>

            <div className="flex justify-between items-center pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setCurrentStep(3)}
                className="clay-btn-light px-5 py-2.5 text-xs flex items-center space-x-1.5"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </button>

              <button
                type="button"
                onClick={() => setCurrentStep(5)}
                className="clay-btn-primary px-6 py-3 text-xs flex items-center space-x-2"
              >
                <span>Review & Finalize</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* ----------------- STEP 5: REVIEW & GENERATE ----------------- */}
        {currentStep === 5 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-black text-slate-900 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-orange-600" />
                Step 5: Review & Generate Examination Paper
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Confirm your configuration before generating questions with AI.
              </p>
            </div>

            {generationError && (
              <div className="p-4 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-xs">
                {generationError}
              </div>
            )}

            {/* Summary Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="clay-card-flat p-4">
                <span className="text-[10px] uppercase font-bold text-slate-400">Board Authority</span>
                <p className="font-extrabold text-sm text-slate-900 mt-1">{selectedBoard}</p>
              </div>

              <div className="clay-card-flat p-4">
                <span className="text-[10px] uppercase font-bold text-slate-400">Target Class & Subject</span>
                <p className="font-extrabold text-sm text-slate-900 mt-1">{grade}th {subject}</p>
              </div>

              <div className="clay-card-flat p-4">
                <span className="text-[10px] uppercase font-bold text-slate-400">Total Marks</span>
                <p className="font-extrabold text-sm text-slate-900 mt-1">{totalMarks} Marks ({timeAllowed} Mins)</p>
              </div>

              <div className="clay-card-flat p-4">
                <span className="text-[10px] uppercase font-bold text-slate-400">Selected Chapters</span>
                <p className="font-extrabold text-sm text-slate-900 mt-1">{selectedChapterIds.length} Chapters</p>
              </div>
            </div>

            {/* Section Breakdown Summary */}
            <div className="clay-card-flat p-5 space-y-3">
              <h4 className="text-xs font-black uppercase tracking-wider text-slate-700">
                Examination Sections Summary
              </h4>
              <div className="divide-y divide-slate-200 text-xs">
                {sections.map((s, idx) => (
                  <div key={idx} className="py-2.5 flex items-center justify-between">
                    <div>
                      <span className="font-bold text-slate-900">{s.title}</span>
                      <span className="text-slate-500 ml-2">
                        ({s.questions_to_attempt} of {s.total_questions} Qs to attempt)
                      </span>
                    </div>
                    <span className="font-bold text-orange-600 bg-orange-50 px-2.5 py-1 rounded-xl">
                      {s.questions_to_attempt * s.marks_per_question} Marks
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Quota Limit Warning if Free Trial Exhausted for this Subject */}
            {quotaInfo && !quotaInfo.can_generate && (
              <div className="clay-card p-5 bg-gradient-to-r from-red-50 to-orange-50 border-2 border-red-300 rounded-3xl space-y-3">
                <div className="flex items-center space-x-2.5 text-red-700">
                  <Lock className="w-5 h-5 shrink-0" />
                  <h3 className="font-black text-sm">Free Trial Limit Reached (2/2 Papers Used for {quotaInfo.subject})</h3>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed">
                  Your school has used all <strong>2 free examination papers</strong> allocated for <strong>{quotaInfo.subject}</strong>. 
                  To generate additional papers for this subject, please upgrade to a paid subscription or contact the platform owner and developer <strong>Muhammad Ali</strong>.
                </p>
                <div className="flex flex-wrap items-center gap-3 pt-1">
                  <button
                    type="button"
                    onClick={() => setShowUpgradeModal(true)}
                    className="clay-btn-primary px-4 py-2 text-xs flex items-center space-x-1.5"
                  >
                    <span>Upgrade Subscription</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                  <a
                    href="mailto:alikhanwebdeveloper@gmail.com?subject=ExamForge%20AI%20Subscription%20Upgrade%20Request&body=Hello%20Muhammad%20Ali,%0A%0AWe%20would%20like%20to%20upgrade%20our%20school%20subscription%20on%20ExamForge%20AI%20to%20unlock%20unlimited%20paper%20generation.%0A%0AThank%20you!"
                    className="clay-btn-light px-3.5 py-2 text-xs flex items-center space-x-1.5 text-slate-700 hover:text-slate-900"
                  >
                    <Mail className="w-3.5 h-3.5 text-orange-600" />
                    <span>Contact Muhammad Ali (Owner)</span>
                  </a>
                  <a
                    href="https://alibuild.site"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-1 text-xs text-orange-600 font-bold hover:underline"
                  >
                    <Globe className="w-3.5 h-3.5" />
                    <span>alibuild.site</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            )}

            <div className="flex justify-between items-center pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setCurrentStep(4)}
                className="clay-btn-light px-5 py-2.5 text-xs flex items-center space-x-1.5"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </button>

              <button
                type="button"
                onClick={handleGenerate}
                disabled={generating || (quotaInfo !== null && !quotaInfo.can_generate)}
                className="clay-btn-primary px-8 py-3.5 text-sm flex items-center space-x-2 font-black shadow-lg disabled:opacity-50"
              >
                {generating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Generating BISEP Paper...</span>
                  </>
                ) : quotaInfo && !quotaInfo.can_generate ? (
                  <>
                    <Lock className="w-4 h-4" />
                    <span>Limit Reached — Upgrade to Generate</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Generate Official Paper Now</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

      </div>

      {/* Upgrade & Contact Owner Modal */}
      {showUpgradeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
          <div className="max-w-lg w-full clay-card p-6 sm:p-8 space-y-5 bg-white relative">
            <button
              onClick={() => setShowUpgradeModal(false)}
              className="absolute top-4 right-4 p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="flex items-center space-x-3">
              <div className="h-11 w-11 rounded-2xl bg-orange-500 text-white flex items-center justify-center shadow-md shadow-orange-500/30">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-lg font-black text-slate-900">
                  Upgrade to Paid Subscription
                </h3>
                <p className="text-xs text-orange-600 font-bold">
                  ExamForge AI — KPK Peshawar Board Edition
                </p>
              </div>
            </div>

            <div className="clay-card-flat p-4 rounded-2xl space-y-2 text-xs">
              <div className="flex justify-between text-slate-700">
                <span>Free Trial Allocation:</span>
                <span className="font-bold">2 Free Papers per Subject</span>
              </div>
              <div className="flex justify-between text-slate-700">
                <span>Subject:</span>
                <span className="font-bold">{quotaInfo?.subject || subject}</span>
              </div>
              <div className="flex justify-between text-slate-700">
                <span>Papers Used:</span>
                <span className="font-bold text-red-600">{quotaInfo?.papers_used || 2} of 2 (Limit Reached)</span>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              To unlock <strong>unlimited examination paper generation</strong> across all 18 authentic Class 9th & 10th KPK Textbook Board books, please contact the site creator and owner <strong>Muhammad Ali</strong> or activate paid access below.
            </p>

            {/* Owner Spotlight */}
            <div className="p-3.5 rounded-2xl bg-orange-50/70 border border-orange-200/80 space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-black text-slate-900">Muhammad Ali</p>
                  <p className="text-[11px] text-slate-500">Lead Architect & Developer • Founder of AliBuild</p>
                </div>
                <a
                  href="https://alibuild.site"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="clay-btn-light px-2.5 py-1 text-[11px] font-bold inline-flex items-center space-x-1"
                >
                  <Globe className="w-3 h-3 text-orange-600" />
                  <span>alibuild.site</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <div className="flex items-center space-x-2 text-xs text-slate-600">
                <Mail className="w-3.5 h-3.5 text-orange-600" />
                <a href="mailto:alikhanwebdeveloper@gmail.com" className="font-mono text-[11px] hover:underline">
                  alikhanwebdeveloper@gmail.com
                </a>
              </div>
            </div>

            <div className="space-y-2 pt-2">
              <a
                href={`mailto:alikhanwebdeveloper@gmail.com?subject=ExamForge%20AI%20Subscription%20Upgrade%20-%20${encodeURIComponent(quotaInfo?.school_name || "Our School")}&body=Hello%20Muhammad%20Ali,%0A%0AWe%20would%20like%20to%20upgrade%20our%20school%20subscription%20on%20ExamForge%20AI%20for%20our%20school:%20${encodeURIComponent(quotaInfo?.school_name || "")}.%0A%0AThank%20you!`}
                className="w-full clay-btn-primary py-3 px-4 text-xs font-bold flex items-center justify-center space-x-2"
              >
                <Mail className="w-4 h-4" />
                <span>Contact Muhammad Ali via Email to Allow Access</span>
              </a>

              <button
                type="button"
                onClick={handleUpgradeSubscription}
                disabled={upgrading}
                className="w-full clay-btn-dark py-2.5 px-4 text-xs font-bold flex items-center justify-center space-x-2 disabled:opacity-50"
              >
                {upgrading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Activating Paid Subscription...</span>
                  </>
                ) : (
                  <>
                    <Award className="w-3.5 h-3.5 text-amber-400" />
                    <span>Activate Paid Subscription (Demo / Self-Serve)</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

export default function PaperGenerationWizard() {
  return (
    <Suspense
      fallback={
        <div className="max-w-4xl mx-auto py-16 px-4">
          <div className="clay-card p-12 text-center text-slate-500">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-3 text-orange-500" />
            <p className="font-semibold text-slate-700">Loading Exam Paper Generator...</p>
          </div>
        </div>
      }
    >
      <PaperGenerationWizardContent />
    </Suspense>
  );
}
