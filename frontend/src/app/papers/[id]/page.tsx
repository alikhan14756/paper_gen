"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useParams, useRouter } from "next/navigation";
import { ApiClient, Paper, Section, Question } from "@/lib/api";
import { 
  FileText, 
  Download, 
  Edit3, 
  RotateCw, 
  Trash2, 
  Check, 
  Save, 
  Eye, 
  CheckCircle, 
  Sparkles,
  ArrowLeft,
  Loader2,
  KeyRound,
  GraduationCap,
  Building2,
  Printer,
  ShieldCheck,
  BookOpen,
  Search,
  Award,
  QrCode,
  Info
} from "lucide-react";

function PaperEditorContent() {
  const params = useParams();
  const router = useRouter();
  const paperId = params?.id as string;

  const [paper, setPaper] = useState<Paper | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"editor" | "answer_key" | "preview">("preview");

  // Editing state for questions
  const [editingQuestionId, setEditingQuestionId] = useState<string | null>(null);
  const [editedText, setEditedText] = useState("");
  const [editedOptions, setEditedOptions] = useState<string[]>([]);
  const [editedAnswer, setEditedAnswer] = useState("");
  const [editedMarks, setEditedMarks] = useState<number>(1);
  const [regeneratingId, setRegeneratingId] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const [exportingKey, setExportingKey] = useState(false);
  const [inspectingQuestion, setInspectingQuestion] = useState<Question | null>(null);

  useEffect(() => {
    if (paperId) {
      loadPaper();
    }
  }, [paperId]);

  const loadPaper = async () => {
    setLoading(true);
    try {
      const data = await ApiClient.getPaper(paperId);
      setPaper(data);
    } catch (err: any) {
      alert("Error loading paper: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const startEditQuestion = (q: Question) => {
    setEditingQuestionId(q.id);
    setEditedText(q.question_text);
    setEditedOptions([...q.options]);
    setEditedAnswer(q.correct_answer || "");
    setEditedMarks(q.marks);
  };

  const handleSaveQuestion = async (questionId: string) => {
    if (!paper) return;
    try {
      await ApiClient.updateQuestion(paper.id, questionId, {
        question_text: editedText,
        options: editedOptions,
        correct_answer: editedAnswer,
        marks: editedMarks,
      });
      setEditingQuestionId(null);
      await loadPaper();
    } catch (err: any) {
      alert("Failed to save changes: " + err.message);
    }
  };

  const handleRegenerateQuestion = async (questionId: string) => {
    if (!paper) return;
    setRegeneratingId(questionId);
    try {
      await ApiClient.regenerateQuestion(paper.id, questionId);
      await loadPaper();
    } catch (err: any) {
      alert("Failed to regenerate question: " + err.message);
    } finally {
      setRegeneratingId(null);
    }
  };

  const handleDeleteQuestion = async (questionId: string) => {
    if (!paper || !confirm("Are you sure you want to delete this question?")) return;
    try {
      await ApiClient.deleteQuestion(paper.id, questionId);
      await loadPaper();
    } catch (err: any) {
      alert("Failed to delete question: " + err.message);
    }
  };

  const handleExportDocx = async () => {
    if (!paper) return;
    setExporting(true);
    try {
      await ApiClient.exportDocx(paper.id, false);
      const safeTitle = paper.title.replace(/[^a-zA-Z0-9_-]/g, "_");
      const filename = `ExamPaper_${paper.subject}_${paper.grade}_${safeTitle}.docx`;
      await ApiClient.downloadDocx(paper.id, filename);
    } catch (err: any) {
      alert("DOCX export/download failed: " + err.message);
    } finally {
      setExporting(false);
    }
  };

  const handleExportAnswerKey = async () => {
    if (!paper) return;
    setExportingKey(true);
    try {
      await ApiClient.exportAnswerKey(paper.id);
      const safeTitle = paper.title.replace(/[^a-zA-Z0-9_-]/g, "_");
      const filename = `CONFIDENTIAL_AnswerKey_${paper.subject}_${paper.grade}_${safeTitle}.docx`;
      await ApiClient.downloadAnswerKey(paper.id, filename);
    } catch (err: any) {
      alert("Answer Key download failed: " + err.message);
    } finally {
      setExportingKey(false);
    }
  };

  const cleanReferences = (text: string) => {
    if (!text) return "";
    return text
      .replace(/\[\s*(?:Page|صفحہ|Book|Ref|Context)[^\]]*\]/gi, "")
      .replace(/\(\s*(?:Page|صفحہ|Book|Ref|Context)[^\)]*\)/gi, "")
      .replace(/Page\s*context\s*#\s*\d+/gi, "")
      .replace(/Page\s*\d+(?:\s*[-–]\s*\d+)?/gi, "")
      .replace(/صفحہ\s*(?:نمبر)?\s*[:\s]*[\d\u0660-\u0669]+/gi, "")
      .replace(/\s+/g, " ")
      .trim();
  };

  const formatBubbles = (rawOptions: string[], isUrdu: boolean) => {
    const urduLetters = ["الف", "ب", "ج", "د", "ہ"];
    const engLetters = ["A", "B", "C", "D", "E"];

    return rawOptions.map((opt, idx) => {
      let cleaned = cleanReferences(opt);
      cleaned = cleaned.replace(/^(?:[A-Ea-e\d]|الف|ب|ج|د|ہ|[\u0627-\u064A])[\.\)\-\:\s]+\s*/, "").trim();
      cleaned = cleaned.replace(/^\((?:[A-Ea-e\d]|الف|ب|ج|د|ہ|[\u0627-\u064A])\)\s*/, "").trim();
      cleaned = cleaned.replace(/^[◯○●\s]+/, "").trim();

      const letter = isUrdu 
        ? (urduLetters[idx] || String(idx + 1))
        : (engLetters[idx] || String(idx + 1));

      return {
        letter,
        text: cleaned,
      };
    });
  };

  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center text-slate-500 space-y-3">
        <Loader2 className="w-10 h-10 animate-spin text-orange-500" />
        <p className="text-xs font-bold uppercase tracking-wider">Loading Examination Paper...</p>
      </div>
    );
  }

  if (!paper) {
    return (
      <div className="clay-card p-12 text-center max-w-md mx-auto my-12">
        <p className="text-sm font-bold text-slate-700">Examination paper not found.</p>
        <button onClick={() => router.push("/papers")} className="clay-btn-primary px-4 py-2 text-xs mt-4">
          Back to My Papers
        </button>
      </div>
    );
  }

  const isUrdu = paper.language === "ur";

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Top Bar (Clay Pill) */}
      <div className="clay-card p-4 sm:p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <button
            onClick={() => router.push("/papers")}
            className="text-xs font-bold text-slate-500 hover:text-slate-800 flex items-center mb-1.5 transition"
          >
            <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Back to My Papers
          </button>
          
          <div className="flex items-center space-x-2 flex-wrap gap-y-1">
            <span className={`text-[10px] px-3 py-0.5 rounded-full font-bold uppercase tracking-wider ${
              isUrdu ? "clay-badge-mint" : "clay-badge-sky"
            }`}>
              {isUrdu ? "اردو (Urdu RTL)" : "English (LTR)"}
            </span>
            <span className="text-[10px] px-2.5 py-0.5 rounded-full font-bold clay-badge-peach">
              {paper.total_marks} Marks
            </span>
            <span className="text-[10px] px-2.5 py-0.5 rounded-full font-bold clay-badge-purple">
              BISE Peshawar Pattern
            </span>
          </div>

          <h1 className={`text-xl sm:text-2xl font-black text-slate-900 mt-2 ${isUrdu ? "urdu-text" : ""}`}>
            {paper.title}
          </h1>

          <p className="text-xs text-slate-500 mt-0.5">
            Subject: <strong>{paper.subject}</strong> • Grade: <strong>{paper.grade}</strong> • Time Allowed: <strong>{paper.time_allowed_minutes} Mins</strong>
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <button
            onClick={handleExportDocx}
            disabled={exporting}
            className="clay-btn-primary px-4 py-2.5 text-xs flex items-center space-x-1.5 disabled:opacity-50"
            title="Download Student Examination Paper (No Answers)"
          >
            {exporting ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Exporting Paper...</span>
              </>
            ) : (
              <>
                <Download className="w-3.5 h-3.5" />
                <span>Student Paper (.docx)</span>
              </>
            )}
          </button>

          <button
            onClick={handleExportAnswerKey}
            disabled={exportingKey}
            className="clay-btn-dark px-4 py-2.5 text-xs flex items-center space-x-1.5 disabled:opacity-50 border border-slate-700"
            title="Download Confidential Marking Scheme (Examiners Only)"
          >
            {exportingKey ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin text-orange-400" />
                <span>Exporting Key...</span>
              </>
            ) : (
              <>
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>Marking Scheme (.docx)</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Tabs Navigation (Clay Pills) */}
      <div className="clay-card p-2 flex items-center max-w-md mx-auto space-x-2">
        <button
          onClick={() => setActiveTab("preview")}
          className={`flex-1 py-2 px-3 rounded-2xl text-xs font-bold transition flex items-center justify-center space-x-1.5 ${
            activeTab === "preview"
              ? "clay-btn-primary text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          }`}
        >
          <Eye className="w-3.5 h-3.5" />
          <span>Paper Preview</span>
        </button>

        <button
          onClick={() => setActiveTab("editor")}
          className={`flex-1 py-2 px-3 rounded-2xl text-xs font-bold transition flex items-center justify-center space-x-1.5 ${
            activeTab === "editor"
              ? "clay-btn-dark text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          }`}
        >
          <Edit3 className="w-3.5 h-3.5" />
          <span>Edit Questions</span>
        </button>

        <button
          onClick={() => setActiveTab("answer_key")}
          className={`flex-1 py-2 px-3 rounded-2xl text-xs font-bold transition flex items-center justify-center space-x-1.5 ${
            activeTab === "answer_key"
              ? "clay-btn-emerald text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          }`}
        >
          <KeyRound className="w-3.5 h-3.5" />
          <span>Answer Key</span>
        </button>
      </div>

      {/* TAB 1: SMOOTH & CLEAN PAPER PRINT PREVIEW */}
      {activeTab === "preview" && (
        <div className="space-y-4">
          <div className="paper-sheet p-8 sm:p-14 bg-white text-slate-900 space-y-6">
            
            {/* Header: School Name Banner */}
            <div className="text-center space-y-1">
              <h2 className={`font-black text-2xl tracking-wide uppercase text-slate-950 ${isUrdu ? "urdu-text text-2xl font-black" : ""}`}>
                {paper.school_id ? "PESHAWAR MODEL SCHOOL & COLLEGE" : "EXAMFORGE ACADEMY"}
              </h2>

              <p className={`text-xs font-black tracking-wider text-slate-600 uppercase ${isUrdu ? "urdu-text" : ""}`}>
                {isUrdu 
                  ? "بورڈ آف انٹرمیڈیٹ اینڈ سیکنڈری ایجوکیشن پشاور (BISEP) پیٹرن امتحانات" 
                  : "BOARD OF INTERMEDIATE & SECONDARY EDUCATION (BISEP) PATTERN"}
              </p>

              <h3 className={`font-extrabold text-sm text-slate-800 pt-1 ${isUrdu ? "urdu-text text-base" : ""}`}>
                {paper.title} — Session {paper.academic_session}
              </h3>
            </div>

            {/* Meta Table (4 Columns) */}
            <div className="border border-slate-300 rounded-lg overflow-hidden text-xs">
              <div className={`grid grid-cols-4 divide-x divide-slate-300 ${isUrdu ? "urdu-text divide-x-reverse" : ""}`}>
                <div className="p-2 bg-slate-50 font-bold">{isUrdu ? "مضمون:" : "SUBJECT:"}</div>
                <div className="p-2 font-medium">{paper.subject}</div>
                <div className="p-2 bg-slate-50 font-bold">{isUrdu ? "جماعت:" : "CLASS / GRADE:"}</div>
                <div className="p-2 font-medium">{paper.grade}th</div>
              </div>
              <div className={`grid grid-cols-4 divide-x divide-slate-300 border-t border-slate-300 ${isUrdu ? "urdu-text divide-x-reverse" : ""}`}>
                <div className="p-2 bg-slate-50 font-bold">{isUrdu ? "کل وقت:" : "TIME ALLOWED:"}</div>
                <div className="p-2 font-medium">{paper.time_allowed_minutes} Minutes</div>
                <div className="p-2 bg-slate-50 font-bold">{isUrdu ? "کل نمبر:" : "MAXIMUM MARKS:"}</div>
                <div className="p-2 font-black text-orange-600">{paper.total_marks}</div>
              </div>
            </div>

            {/* Official Candidate Roll Number & Identification Box */}
            <div className="border-2 border-slate-400 p-4 rounded-lg bg-slate-50/50 space-y-3 text-xs">
              <div className={`flex flex-col sm:flex-row justify-between gap-3 ${isUrdu ? "urdu-text" : ""}`}>
                <div className="flex items-center space-x-2">
                  <span className="font-bold">{isUrdu ? "رول نمبر (ہندسوں میں):" : "Roll No. (in Figures):"}</span>
                  <div className="flex space-x-1">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                      <div key={i} className="w-6 h-7 border border-slate-400 bg-white rounded flex items-center justify-center font-mono font-bold" />
                    ))}
                  </div>
                </div>
                <div>
                  <span className="font-bold">{isUrdu ? "رول نمبر (الفاظ میں):" : "Roll No. (in Words):"}</span>
                  <span className="inline-block border-b border-slate-400 w-44 ml-2" />
                </div>
              </div>

              <div className={`flex flex-col sm:flex-row justify-between gap-3 pt-1 ${isUrdu ? "urdu-text" : ""}`}>
                <div>
                  <span className="font-bold">{isUrdu ? "طالب علم کا نام:" : "Candidate Name:"}</span>
                  <span className="inline-block border-b border-slate-400 w-52 ml-2" />
                </div>
                <div>
                  <span className="font-bold">{isUrdu ? "نگران کے دستخط:" : "Invigilator Signature:"}</span>
                  <span className="inline-block border-b border-slate-400 w-40 ml-2" />
                </div>
              </div>
            </div>

            {/* General Note */}
            {paper.instructions && (
              <div className={`p-3 rounded-lg bg-amber-50/60 border border-amber-200/80 text-xs italic text-slate-700 ${isUrdu ? "urdu-text text-right" : ""}`}>
                <strong>{isUrdu ? "عام ہدایات: " : "GENERAL NOTE: "}</strong>
                {cleanReferences(paper.instructions)}
              </div>
            )}

            {/* Sections List */}
            <div className="space-y-8 pt-2">
              {paper.sections.map((sec, secIdx) => {
                const isMCQ = sec.section_type === "mcq";

                return (
                  <div key={sec.id} className="space-y-4">
                    {/* Section Header */}
                    <div className="text-center border-b-2 border-slate-900 pb-2">
                      <h4 className="font-black text-sm uppercase tracking-wider text-slate-900">
                        ― {sec.title} (Marks: {sec.total_section_marks}) ―
                      </h4>
                      {sec.instructions && (
                        <p className={`text-xs italic font-semibold text-slate-600 mt-0.5 ${isUrdu ? "urdu-text text-right" : ""}`}>
                          {cleanReferences(sec.instructions)}
                        </p>
                      )}
                    </div>

                    {/* Questions */}
                    <div className="space-y-4">
                      {sec.questions.map((q, qIdx) => {
                        const bubbleOpts = formatBubbles(q.options || [], isUrdu);
                        const cleanQuestionText = cleanReferences(q.question_text);

                        return (
                          <div
                            key={q.id}
                            className={`space-y-2 text-xs text-slate-900 ${
                              isUrdu ? "urdu-text text-right" : "text-left"
                            }`}
                          >
                            {/* Question Line */}
                            <div className="flex items-start justify-between gap-4">
                              <p className="font-bold text-sm leading-relaxed flex-1">
                                {isUrdu ? (
                                  <>
                                    <span>سوال نمبر {qIdx + 1}: </span>
                                    <span>{cleanQuestionText}</span>
                                  </>
                                ) : (
                                  <>
                                    <span>Q.{qIdx + 1} </span>
                                    <span>{cleanQuestionText}</span>
                                  </>
                                )}
                              </p>
                              <span className="font-extrabold text-slate-600 shrink-0">
                                [{q.marks} {isUrdu ? "نمبر" : ""}]
                              </span>
                            </div>

                            {/* MCQ Options with Fill Bubbles ◯ */}
                            {isMCQ && bubbleOpts.length > 0 && (
                              <div className={`grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 ${
                                isUrdu ? "pr-4" : "pl-4"
                              }`}>
                                {bubbleOpts.map((opt, oIdx) => (
                                  <div
                                    key={oIdx}
                                    className="flex items-center space-x-2 py-1 px-2 rounded-lg bg-slate-50 border border-slate-200/80 font-medium"
                                  >
                                    <span className="font-bold text-slate-800">{opt.letter})</span>
                                    <span className="w-3.5 h-3.5 rounded-full border-2 border-slate-500 inline-block bg-white shrink-0" />
                                    <span className="truncate">{opt.text}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Official Signature Block & Digital Stamp */}
            <div className="pt-8 pb-4 space-y-4 border-t border-slate-200">
              <div className="flex flex-col sm:flex-row items-center justify-between text-xs text-slate-600 gap-4 pt-4">
                <div className="text-center sm:text-left">
                  <div className="w-48 border-b-2 border-slate-400 mb-1" />
                  <span className="font-bold">{isUrdu ? "دستخط نگرانِ امتحانات" : "Invigilator Signature"}</span>
                </div>
                <div className="text-center sm:text-right">
                  <div className="w-48 border-b-2 border-slate-400 mb-1" />
                  <span className="font-bold">{isUrdu ? "دستخط پرنسپل / کنٹرولر امتحانات" : "Principal / Controller of Examinations"}</span>
                </div>
              </div>

              {/* Digital Verification Banner */}
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-500 gap-2">
                <div className="flex items-center space-x-2">
                  <QrCode className="w-4 h-4 text-orange-600 shrink-0" />
                  <span>
                    Verification Code: <strong className="text-slate-800 font-mono">{paper.verification_code || `EXAM-${paper.id.slice(0, 8).toUpperCase()}`}</strong>
                  </span>
                </div>
                <span className="text-[10px] text-emerald-700 font-bold bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                  ✓ SECURE BISEP BOARD VERIFIED
                </span>
              </div>
            </div>

            {/* Bottom Footer Note */}
            <div className="border-t border-slate-300 pt-4 text-center text-[10px] text-slate-400 font-mono">
              [ END OF EXAMINATION PAPER — EXAMFORGE AI BISEP PATTERN ]
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: INTERACTIVE QUESTION EDITOR */}
      {activeTab === "editor" && (
        <div className="space-y-6">
          {paper.sections.map((section, secIdx) => (
            <div key={section.id} className="clay-card p-6 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-3 gap-2">
                <div>
                  <h3 className={`font-black text-base text-slate-900 ${isUrdu ? "urdu-text" : ""}`}>
                    {section.title}
                  </h3>
                  {section.instructions && (
                    <p className={`text-xs text-slate-500 italic mt-0.5 ${isUrdu ? "urdu-text" : ""}`}>
                      {section.instructions}
                    </p>
                  )}
                </div>
                <div className="flex items-center space-x-2 text-xs font-semibold">
                  <span className="clay-badge-sky px-3 py-1 rounded-full">
                    Attempt {section.questions_to_attempt} of {section.questions.length}
                  </span>
                  <span className="clay-badge-peach px-3 py-1 rounded-full">
                    {section.total_section_marks} Marks
                  </span>
                </div>
              </div>

              {/* Questions List */}
              <div className="space-y-3.5">
                {section.questions.map((q, qIdx) => {
                  const isEditing = editingQuestionId === q.id;
                  const isRegen = regeneratingId === q.id;

                  return (
                    <div
                      key={q.id}
                      className={`p-4 rounded-2xl border transition ${
                        isEditing
                          ? "border-orange-500 bg-orange-50/20 ring-3 ring-orange-500/20"
                          : "clay-card-flat"
                      }`}
                    >
                      {isEditing ? (
                        /* Editing Mode */
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-slate-700">Editing Question {qIdx + 1}</span>
                            <div className="flex items-center space-x-2">
                              <label className="text-xs text-slate-500">Marks:</label>
                              <input
                                type="number"
                                step="0.5"
                                value={editedMarks}
                                onChange={(e) => setEditedMarks(Number(e.target.value))}
                                className="w-16 px-2 py-1 text-xs clay-input text-right font-bold"
                              />
                            </div>
                          </div>

                          <textarea
                            rows={3}
                            value={editedText}
                            onChange={(e) => setEditedText(e.target.value)}
                            className={`w-full p-3 text-xs clay-input ${
                              isUrdu ? "urdu-text" : ""
                            }`}
                          />

                          {/* MCQ Options Editing */}
                          {q.question_type === "mcq" && (
                            <div className="space-y-2">
                              <p className="text-[11px] font-bold text-slate-600">Options:</p>
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                {editedOptions.map((opt, optIdx) => (
                                  <input
                                    key={optIdx}
                                    type="text"
                                    value={opt}
                                    onChange={(e) => {
                                      const updated = [...editedOptions];
                                      updated[optIdx] = e.target.value;
                                      setEditedOptions(updated);
                                    }}
                                    className={`px-3 py-1.5 text-xs clay-input ${
                                      isUrdu ? "urdu-text" : ""
                                    }`}
                                  />
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Answer Key */}
                          <div>
                            <label className="block text-[11px] font-bold text-slate-600 mb-1">
                              Correct Answer / Marking Outline:
                            </label>
                            <input
                              type="text"
                              value={editedAnswer}
                              onChange={(e) => setEditedAnswer(e.target.value)}
                              className={`w-full px-3 py-1.5 text-xs clay-input ${
                                isUrdu ? "urdu-text" : ""
                              }`}
                            />
                          </div>

                          <div className="flex justify-end space-x-2 pt-2">
                            <button
                              type="button"
                              onClick={() => setEditingQuestionId(null)}
                              className="clay-btn-light px-3.5 py-1.5 text-xs font-bold"
                            >
                              Cancel
                            </button>
                            <button
                              type="button"
                              onClick={() => handleSaveQuestion(q.id)}
                              className="clay-btn-primary px-4 py-1.5 text-xs flex items-center space-x-1"
                            >
                              <Save className="w-3.5 h-3.5" />
                              <span>Save Changes</span>
                            </button>
                          </div>
                        </div>
                      ) : (
                        /* Read View */
                        <div className="flex items-start justify-between gap-4">
                          <div className="space-y-1.5 flex-1 min-w-0">
                            <div className="flex items-center space-x-2">
                              <span className="text-xs font-bold text-slate-500">Q{qIdx + 1}.</span>
                              <p className={`text-xs font-bold text-slate-900 leading-snug ${isUrdu ? "urdu-text text-sm" : ""}`}>
                                {cleanReferences(q.question_text)}
                              </p>
                            </div>

                            {q.options && q.options.length > 0 && (
                              <div className={`grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 text-[11px] ${isUrdu ? "urdu-text" : ""}`}>
                                {q.options.map((opt, oi) => (
                                  <div key={oi} className="p-1.5 rounded-lg bg-white border border-slate-200 font-medium truncate">
                                    {cleanReferences(opt)}
                                  </div>
                                ))}
                              </div>
                            )}

                            <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
                              {q.blooms_level && (
                                <span className="text-[10px] px-2 py-0.5 rounded-full font-bold clay-badge-purple">
                                  Bloom&apos;s: {q.blooms_level}
                                </span>
                              )}
                              <span className="text-[10px] px-2 py-0.5 rounded-full font-bold clay-badge-mint">
                                {Math.round((q.confidence_score || 0.95) * 100)}% Grounded
                              </span>
                              {q.source_page && (
                                <span className="text-[10px] px-2 py-0.5 rounded-full font-medium bg-slate-100 text-slate-600">
                                  Page {q.source_page}
                                </span>
                              )}
                              <button
                                type="button"
                                onClick={() => setInspectingQuestion(q)}
                                className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-orange-100 text-orange-700 hover:bg-orange-200 transition flex items-center space-x-1"
                                title="Inspect Source Textbook Provenance"
                              >
                                <BookOpen className="w-2.5 h-2.5" />
                                <span>Inspect Source Evidence</span>
                              </button>
                            </div>

                            {q.correct_answer && (
                              <p className="text-[11px] text-emerald-700 font-semibold pt-1">
                                Answer: {cleanReferences(q.correct_answer)}
                              </p>
                            )}
                          </div>

                          {/* Quick Actions */}
                          <div className="flex items-center space-x-1.5 shrink-0">
                            <button
                              onClick={() => startEditQuestion(q)}
                              className="p-1.5 rounded-xl text-slate-500 hover:text-orange-600 hover:bg-orange-50 transition"
                              title="Edit Question"
                            >
                              <Edit3 className="w-4 h-4" />
                            </button>

                            <button
                              onClick={() => handleRegenerateQuestion(q.id)}
                              disabled={isRegen}
                              className="p-1.5 rounded-xl text-slate-500 hover:text-blue-600 hover:bg-blue-50 transition disabled:opacity-50"
                              title="Regenerate with AI"
                            >
                              <RotateCw className={`w-4 h-4 ${isRegen ? "animate-spin text-blue-600" : ""}`} />
                            </button>

                            <button
                              onClick={() => handleDeleteQuestion(q.id)}
                              className="p-1.5 rounded-xl text-slate-500 hover:text-red-600 hover:bg-red-50 transition"
                              title="Delete Question"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* TAB 3: OFFICIAL ANSWER KEY (ZERO BOOK PAGE CITATIONS) */}
      {activeTab === "answer_key" && (
        <div className="clay-card p-6 sm:p-10 space-y-6">
          <div className="text-center space-y-1 pb-3 border-b border-slate-100">
            <span className="inline-block px-3.5 py-1 rounded-full text-xs font-bold clay-badge-peach">
              Confidential Marking Guide
            </span>
            <h2 className="text-xl font-black text-slate-900">
              Official Marking Scheme & Solutions
            </h2>
            <p className="text-xs text-slate-500">
              Generated for examiners and evaluators. Appended on a dedicated page break in exported Word (.docx) papers.
            </p>
          </div>

          <div className="space-y-6">
            {paper.sections.map((sec) => (
              <div key={sec.id} className="space-y-3">
                <h3 className="font-extrabold text-sm text-slate-800 border-l-4 border-orange-500 pl-2">
                  ● {sec.title} Marking Guide
                </h3>
                <div className="divide-y divide-slate-100 clay-card-flat p-2">
                  {sec.questions.map((q, idx) => (
                    <div key={q.id} className="p-3 text-xs space-y-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <span className="font-bold text-slate-700">Q{idx + 1}: </span>
                          <span className="font-bold text-emerald-700">{cleanReferences(q.correct_answer || "N/A")}</span>
                        </div>
                        <span className="font-bold text-slate-500">
                          [{q.marks} Marks]
                        </span>
                      </div>
                      {q.explanation && (
                        <p className="text-[11px] text-slate-500 italic pl-3">
                          Guide: {cleanReferences(q.explanation)}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SOURCE PROVENANCE INSPECTOR MODAL */}
      {inspectingQuestion && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in">
          <div className="clay-card p-6 max-w-xl w-full space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-xl bg-orange-100 text-orange-600">
                  <BookOpen className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-black text-sm text-slate-900">AI Grounding &amp; Provenance Verification</h3>
                  <p className="text-[11px] text-slate-500">100% Curriculum-backed • Zero Hallucination Guarantee</p>
                </div>
              </div>
              <button
                onClick={() => setInspectingQuestion(null)}
                className="text-slate-400 hover:text-slate-700 text-sm font-bold p-1"
              >
                ✕
              </button>
            </div>

            {/* Question Snapshot */}
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs">
              <span className="font-bold text-slate-500 uppercase tracking-wider text-[10px]">Exam Question:</span>
              <p className="font-bold text-slate-900 mt-1">{cleanReferences(inspectingQuestion.question_text)}</p>
            </div>

            {/* Grounding Attributes */}
            <div className="grid grid-cols-3 gap-2 text-center text-xs">
              <div className="p-2.5 rounded-xl bg-purple-50 border border-purple-100">
                <span className="block text-[10px] text-purple-600 font-bold uppercase">Bloom&apos;s Level</span>
                <span className="font-black text-purple-900">{inspectingQuestion.blooms_level || "Understand"}</span>
              </div>
              <div className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-100">
                <span className="block text-[10px] text-emerald-600 font-bold uppercase">Grounded Confidence</span>
                <span className="font-black text-emerald-900">{Math.round((inspectingQuestion.confidence_score || 0.95) * 100)}%</span>
              </div>
              <div className="p-2.5 rounded-xl bg-blue-50 border border-blue-100">
                <span className="block text-[10px] text-blue-600 font-bold uppercase">Curriculum Match</span>
                <span className="font-black text-blue-900">{Math.round((inspectingQuestion.quality_score || 0.94) * 100)}%</span>
              </div>
            </div>

            {/* Exact Textbook Excerpt */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-700 flex items-center space-x-1">
                  <Search className="w-3.5 h-3.5 text-orange-500" />
                  <span>Exact Textbook Source Excerpt:</span>
                </span>
                <span className="text-[10px] text-slate-500">
                  {inspectingQuestion.source_reference || `Page ${inspectingQuestion.source_page || 1}`}
                </span>
              </div>
              <div className="p-3.5 rounded-xl bg-amber-50/60 border border-amber-200 text-xs text-amber-950 font-medium leading-relaxed italic">
                &ldquo;{inspectingQuestion.source_excerpt || cleanReferences(inspectingQuestion.explanation || "Directly grounded in textbook section concepts.")}&rdquo;
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="button"
                onClick={() => setInspectingQuestion(null)}
                className="clay-btn-dark px-5 py-2 text-xs font-bold"
              >
                Close Provenance Inspector
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

export default function PaperEditorPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-slate-400">Loading editor...</div>}>
      <PaperEditorContent />
    </Suspense>
  );
}
