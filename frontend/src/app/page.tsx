"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { ApiClient, Book, Paper } from "@/lib/api";
import { 
  FileText, 
  BookOpen, 
  PlusCircle, 
  Sparkles, 
  Download, 
  Clock, 
  CheckCircle2, 
  Building2, 
  ChevronRight, 
  Loader2, 
  GraduationCap, 
  Award, 
  ArrowRight,
  BookCheck,
  Compass
} from "lucide-react";

export default function Dashboard() {
  const { user } = useAuth();
  const [books, setBooks] = useState<Book[]>([]);
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState<"all" | "kpk" | "urdu" | "english">("all");

  useEffect(() => {
    setMounted(true);
    loadData();
  }, [user]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [fetchedBooks, fetchedPapers] = await Promise.all([
        ApiClient.listBooks().catch(() => []),
        ApiClient.listPapers().catch(() => []),
      ]);
      setBooks(fetchedBooks);
      setPapers(fetchedPapers);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (paper: Paper) => {
    setDownloadingId(paper.id);
    try {
      const safeTitle = paper.title.replace(/[^a-zA-Z0-9_-]/g, "_");
      await ApiClient.downloadDocx(paper.id, `${paper.subject}_${paper.grade}_${safeTitle}.docx`);
    } catch (err: any) {
      alert("Download failed: " + err.message);
    } finally {
      setDownloadingId(null);
    }
  };

  const kpkBooks = books.filter(b => 
    b.title.toLowerCase().includes("kpk") || 
    b.title.includes("خیبر") || 
    b.title.toLowerCase().includes("peshawar")
  );

  const filteredPapers = papers.filter(p => {
    if (selectedFilter === "urdu") return p.language === "ur";
    if (selectedFilter === "english") return p.language === "en";
    if (selectedFilter === "kpk") {
      return p.title.toLowerCase().includes("kpk") || 
             p.title.includes("پشاور") || 
             p.subject.includes("پاکستان") ||
             p.subject.toLowerCase().includes("physics");
    }
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
      
      {/* 1. Hero Claymorphic Banner */}
      <div className="clay-card p-6 sm:p-10 relative overflow-hidden bg-gradient-to-br from-white via-orange-50/30 to-amber-50/40">
        <div className="absolute right-0 top-0 translate-x-12 -translate-y-12 w-80 h-80 bg-orange-400/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute left-1/3 bottom-0 translate-y-16 w-60 h-60 bg-blue-400/10 rounded-full blur-2xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center px-3.5 py-1.5 rounded-full text-xs font-bold clay-badge-peach mb-3">
              <Sparkles className="w-3.5 h-3.5 mr-1.5 text-orange-600 animate-pulse" />
              KPK Peshawar Board (BISEP) Edition
            </div>
            
            <h1 className="text-2xl sm:text-4xl font-black text-slate-900 tracking-tight leading-tight">
              {mounted && user?.full_name ? `Assalam-o-Alaikum, ${user.full_name}` : "Examination Paper Generator"}
            </h1>
            
            <p className="text-slate-600 text-sm sm:text-base mt-2 leading-relaxed">
              Generate authentic, board-pattern examination papers in English and Urdu. Supporting Khyber Pakhtunkhwa (BISE Peshawar) textbooks, syllabus chapter selection, editable marks breakdown, and 1-click Word (.docx) export.
            </p>

            {/* Quick Badges */}
            <div className="flex flex-wrap items-center gap-2 mt-4 pt-1">
              <span className="px-3 py-1 rounded-full text-[11px] font-bold clay-badge-mint">
                ✓ Authentic BISEP Pattern
              </span>
              <span className="px-3 py-1 rounded-full text-[11px] font-bold clay-badge-sky">
                ✓ Rounded Bubble OMR Choices ◯
              </span>
              <span className="px-3 py-1 rounded-full text-[11px] font-bold clay-badge-purple">
                ✓ Clean Urdu RTL Writing
              </span>
            </div>
          </div>

          {/* Quick CTA Actions */}
          <div className="flex flex-col sm:flex-row lg:flex-col gap-3 min-w-[200px]">
            <Link
              href="/papers/generate"
              className="clay-btn-primary px-6 py-3.5 text-center text-sm font-bold flex items-center justify-center space-x-2"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Create Paper Now</span>
            </Link>
            <Link
              href="/books"
              className="clay-btn-light px-5 py-3 text-center text-xs font-bold flex items-center justify-center space-x-2 text-slate-700 hover:text-orange-600"
            >
              <BookOpen className="w-4 h-4 text-orange-600" />
              <span>KPK Syllabus Books ({books.length})</span>
            </Link>
          </div>
        </div>
      </div>

      {/* 2. Claymorphic Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        
        {/* Stat 1: KPK Books */}
        <div className="clay-card p-5 flex items-center justify-between">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">KPK Syllabus Books</p>
            <p className="text-3xl font-black text-slate-900 mt-1">{books.length}</p>
            <p className="text-xs text-emerald-600 font-bold mt-1 flex items-center">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Ready for Paper Generation
            </p>
          </div>
          <div className="w-13 h-13 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center text-white shadow-md shadow-emerald-500/20 font-bold">
            <BookCheck className="w-6 h-6" />
          </div>
        </div>

        {/* Stat 2: Papers Created */}
        <div className="clay-card p-5 flex items-center justify-between">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Exam Papers Created</p>
            <p className="text-3xl font-black text-slate-900 mt-1">{papers.length}</p>
            <p className="text-xs text-orange-600 font-bold mt-1 flex items-center">
              <Sparkles className="w-3.5 h-3.5 mr-1" /> Editable & DOCX Exportable
            </p>
          </div>
          <div className="w-13 h-13 rounded-2xl bg-gradient-to-br from-orange-400 to-amber-600 flex items-center justify-center text-white shadow-md shadow-orange-500/20 font-bold">
            <FileText className="w-6 h-6" />
          </div>
        </div>

        {/* Stat 3: Board Standard */}
        <div className="clay-card p-5 flex items-center justify-between">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Target Board</p>
            <p className="text-xl font-black text-slate-900 mt-1">BISE Peshawar</p>
            <p className="text-xs text-blue-600 font-bold mt-1 flex items-center">
              <GraduationCap className="w-3.5 h-3.5 mr-1" /> KPK Board Standard
            </p>
          </div>
          <div className="w-13 h-13 rounded-2xl bg-gradient-to-br from-blue-400 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 font-bold">
            <Compass className="w-6 h-6" />
          </div>
        </div>

        {/* Stat 4: Bilingual Engine */}
        <div className="clay-card p-5 flex items-center justify-between">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Bilingual Support</p>
            <p className="text-xl font-black text-slate-900 mt-1">اردو & English</p>
            <p className="text-xs text-purple-600 font-bold mt-1 flex items-center">
              <Award className="w-3.5 h-3.5 mr-1" /> OpenXML RTL Formatting
            </p>
          </div>
          <div className="w-13 h-13 rounded-2xl bg-gradient-to-br from-purple-400 to-pink-600 flex items-center justify-center text-white shadow-md shadow-purple-500/20 font-black text-base">
            اردو
          </div>
        </div>

      </div>

      {/* 3. Main Content: Recent Papers & KPK Syllabus Highlights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column (2 Cols): Recent Examination Papers */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-1">
            <div>
              <h2 className="text-xl font-black text-slate-900 flex items-center">
                <FileText className="w-5 h-5 mr-2 text-orange-600" />
                Examination Papers
              </h2>
              <p className="text-xs text-slate-500">Recent papers generated for your school</p>
            </div>

            {/* Filter Pills */}
            <div className="flex items-center clay-card-flat p-1 text-xs font-bold space-x-1">
              <button
                onClick={() => setSelectedFilter("all")}
                className={`px-3 py-1 rounded-xl transition ${selectedFilter === "all" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-800"}`}
              >
                All ({papers.length})
              </button>
              <button
                onClick={() => setSelectedFilter("kpk")}
                className={`px-3 py-1 rounded-xl transition ${selectedFilter === "kpk" ? "bg-white text-orange-600 shadow-sm" : "text-slate-500 hover:text-slate-800"}`}
              >
                KPK Board
              </button>
              <button
                onClick={() => setSelectedFilter("urdu")}
                className={`px-3 py-1 rounded-xl transition ${selectedFilter === "urdu" ? "bg-white text-emerald-600 shadow-sm" : "text-slate-500 hover:text-slate-800"}`}
              >
                اردو Papers
              </button>
              <button
                onClick={() => setSelectedFilter("english")}
                className={`px-3 py-1 rounded-xl transition ${selectedFilter === "english" ? "bg-white text-blue-600 shadow-sm" : "text-slate-500 hover:text-slate-800"}`}
              >
                English
              </button>
            </div>
          </div>

          {loading ? (
            <div className="clay-card p-12 text-center text-slate-400 flex flex-col items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-orange-500 mb-2" />
              <p className="text-xs font-semibold">Loading papers catalog...</p>
            </div>
          ) : filteredPapers.length === 0 ? (
            <div className="clay-card p-12 text-center">
              <div className="w-16 h-16 rounded-3xl bg-orange-50 text-orange-600 flex items-center justify-center mx-auto mb-4 font-bold">
                <FileText className="w-8 h-8" />
              </div>
              <h3 className="text-base font-extrabold text-slate-800">No examination papers yet</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
                Select chapters from the KPK Peshawar Board syllabus and generate your first exam paper.
              </p>
              <Link
                href="/papers/generate"
                className="clay-btn-primary px-5 py-2.5 text-xs inline-flex items-center mt-5"
              >
                <PlusCircle className="w-3.5 h-3.5 mr-1.5" /> Generate BISEP Exam Paper
              </Link>
            </div>
          ) : (
            <div className="space-y-3.5">
              {filteredPapers.map((paper) => {
                const isUrdu = paper.language === "ur";
                return (
                  <div
                    key={paper.id}
                    className="clay-card-interactive p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                  >
                    <div className="space-y-1.5 flex-1 min-w-0">
                      <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                        <span className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                          isUrdu ? "clay-badge-mint" : "clay-badge-sky"
                        }`}>
                          {isUrdu ? "اردو (Urdu RTL)" : "English (LTR)"}
                        </span>
                        <span className="text-[10px] px-2.5 py-0.5 rounded-full font-bold clay-badge-peach">
                          {paper.total_marks} Marks
                        </span>
                        <span className="text-[10px] font-semibold text-slate-400">
                          {paper.time_allowed_minutes} Mins
                        </span>
                      </div>

                      <h3 className={`font-black text-sm sm:text-base text-slate-900 truncate ${isUrdu ? "urdu-text text-base" : ""}`}>
                        {paper.title}
                      </h3>

                      <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                        <span>Subject: <strong className="text-slate-700">{paper.subject}</strong></span>
                        <span>•</span>
                        <span>Grade: <strong className="text-slate-700">{paper.grade}</strong></span>
                        <span>•</span>
                        <span>{paper.sections?.length || 0} Sections</span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center space-x-2 shrink-0">
                      <button
                        onClick={() => handleDownload(paper)}
                        disabled={downloadingId === paper.id}
                        className="clay-btn-primary px-3.5 py-2 text-xs flex items-center space-x-1.5 disabled:opacity-50"
                        title="Download Word Document (.docx)"
                      >
                        {downloadingId === paper.id ? (
                          <>
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            <span>Downloading...</span>
                          </>
                        ) : (
                          <>
                            <Download className="w-3.5 h-3.5" />
                            <span>Download DOCX</span>
                          </>
                        )}
                      </button>

                      <Link
                        href={`/papers/${paper.id}`}
                        className="clay-btn-light px-3.5 py-2 text-xs flex items-center space-x-1 text-slate-700 hover:text-slate-900"
                      >
                        <span>Editor</span>
                        <ChevronRight className="w-3 h-3" />
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Column (1 Col): KPK Textbook Board Syllabus Showcase */}
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-1">
            <div>
              <h2 className="text-xl font-black text-slate-900 flex items-center">
                <GraduationCap className="w-5 h-5 mr-2 text-emerald-600" />
                KPK Syllabus
              </h2>
              <p className="text-xs text-slate-500">Pre-loaded textbook curriculum</p>
            </div>
            <Link
              href="/books"
              className="text-xs font-bold text-orange-600 hover:underline"
            >
              View All
            </Link>
          </div>

          <div className="clay-card p-5 space-y-3.5">
            <p className="text-xs text-slate-600 leading-relaxed">
              Official textbook curriculum aligned with the <strong>Khyber Pakhtunkhwa (KPK) Textbook Board Peshawar</strong>:
            </p>

            <div className="space-y-2.5">
              {books.slice(0, 5).map((book) => {
                const isUrdu = book.language === "ur";
                return (
                  <div
                    key={book.id}
                    className="clay-card-flat p-3 flex items-center justify-between hover:bg-slate-100/70 transition"
                  >
                    <div className="min-w-0 pr-2">
                      <p className={`font-bold text-xs text-slate-900 truncate ${isUrdu ? "urdu-text" : ""}`}>
                        {book.title}
                      </p>
                      <p className="text-[11px] text-slate-500 mt-0.5">
                        Grade {book.grade} • {book.chapters?.length || 0} Chapters
                      </p>
                    </div>

                    <Link
                      href={`/papers/generate?book_id=${book.id}`}
                      className="clay-btn-primary px-2.5 py-1 text-[11px] shrink-0 font-bold"
                      title="Generate Paper with this Book"
                    >
                      Use
                    </Link>
                  </div>
                );
              })}
            </div>

            <div className="pt-2 border-t border-slate-100">
              <Link
                href="/papers/generate"
                className="w-full clay-btn-dark py-2.5 text-xs text-center font-bold flex items-center justify-center space-x-2"
              >
                <span>Launch Paper Generator</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Quick Help Card */}
          <div className="clay-card p-5 bg-gradient-to-br from-white to-orange-50/40">
            <h4 className="text-xs font-black uppercase tracking-wider text-orange-700 flex items-center">
              <Award className="w-4 h-4 mr-1.5" />
              BISEP Exam Guidelines
            </h4>
            <ul className="text-xs text-slate-600 mt-2 space-y-1.5 list-disc list-inside">
              <li>Section A: 10/12/15 MCQs with bubble choices ◯.</li>
              <li>Section B: Short Questions with choice (e.g. 5 of 8).</li>
              <li>Section C: Detailed long questions with marks [5].</li>
              <li>Official roll number and candidate block included.</li>
            </ul>
          </div>
        </div>

      </div>

    </div>
  );
}
