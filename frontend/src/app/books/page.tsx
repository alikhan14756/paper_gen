"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ApiClient, Book, Chapter } from "@/lib/api";
import { 
  BookOpen, 
  Upload, 
  CheckCircle, 
  AlertCircle, 
  Edit3, 
  Plus, 
  Trash2, 
  FileText,
  Loader2,
  X,
  GraduationCap,
  Sparkles,
  ArrowRight,
  BookCheck,
  Download
} from "lucide-react";

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [title, setTitle] = useState("");
  const [subject, setSubject] = useState("");
  const [grade, setGrade] = useState("10");
  const [language, setLanguage] = useState("en");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);

  // Selected book for chapter review
  const [activeBook, setActiveBook] = useState<Book | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const handleDownloadPdf = async (book: Book, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setDownloadingId(book.id);
    setError(null);
    try {
      await ApiClient.downloadBookPdf(book.id, book.title);
    } catch (err: any) {
      setError(err.message || "Failed to download PDF textbook.");
    } finally {
      setDownloadingId(null);
    }
  };

  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    setLoading(true);
    try {
      const data = await ApiClient.listBooks();
      setBooks(data);
      if (data.length > 0 && !activeBook) {
        setActiveBook(data[0]);
      } else if (activeBook) {
        const updated = data.find((b) => b.id === activeBook.id);
        if (updated) setActiveBook(updated);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setError("Please select a PDF textbook file");
      return;
    }

    setUploading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("title", title);
      formData.append("subject", subject);
      formData.append("grade", grade);
      formData.append("language", language);
      formData.append("file", selectedFile);

      await ApiClient.uploadBook(formData);
      setTitle("");
      setSubject("");
      setSelectedFile(null);
      setShowUploadModal(false);
      await fetchBooks();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Top Header Banner */}
      <div className="clay-card p-6 sm:p-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold clay-badge-mint mb-2">
            <GraduationCap className="w-3.5 h-3.5 mr-1" />
            KPK Textbook Board Peshawar & Board Syllabus Library
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Textbooks & Syllabus Catalog
          </h1>
          <p className="text-slate-600 text-xs sm:text-sm mt-1">
            Official curriculum textbooks parsed and indexed by page ranges and chapters for exam generation.
          </p>
        </div>

        <button
          onClick={() => setShowUploadModal(true)}
          className="clay-btn-primary px-5 py-3 text-xs flex items-center space-x-2 self-start md:self-auto font-bold"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Custom PDF Book</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-red-500 hover:text-red-700">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Main Grid: Books List & Active Chapter Explorer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Books List (1 Col) */}
        <div className="space-y-4">
          <h2 className="text-lg font-black text-slate-900 flex items-center">
            <BookOpen className="w-4 h-4 mr-2 text-orange-600" />
            Available Textbooks ({books.length})
          </h2>

          {loading ? (
            <div className="clay-card p-12 text-center text-slate-400 flex flex-col items-center">
              <Loader2 className="w-8 h-8 animate-spin text-orange-500 mb-2" />
              <p className="text-xs font-bold">Loading curriculum...</p>
            </div>
          ) : (
            <div className="space-y-3">
              {books.map((b) => {
                const isActive = activeBook?.id === b.id;
                const isUrdu = b.language === "ur";
                const isKPK = b.title.includes("KPK") || b.title.includes("خیبر");

                return (
                  <div
                    key={b.id}
                    onClick={() => setActiveBook(b)}
                    className={`clay-card-interactive p-4 cursor-pointer relative ${
                      isActive ? "ring-2 ring-orange-500 bg-orange-50/20" : ""
                    }`}
                  >
                    <div className="flex items-center space-x-2 mb-1.5">
                      {isKPK && (
                        <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full clay-badge-mint">
                          KPK Board
                        </span>
                      )}
                      <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full ${
                        isUrdu ? "clay-badge-peach" : "clay-badge-sky"
                      }`}>
                        {isUrdu ? "اردو" : "English"}
                      </span>
                    </div>

                    <h3 className={`font-black text-xs sm:text-sm text-slate-900 ${isUrdu ? "urdu-text" : ""}`}>
                      {b.title}
                    </h3>

                    <div className="flex items-center justify-between text-xs text-slate-500 mt-2 pt-2 border-t border-slate-100">
                      <span>Grade {b.grade} • {b.subject}</span>
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-slate-700">{b.chapters?.length || 0} Chs</span>
                        <button
                          onClick={(e) => handleDownloadPdf(b, e)}
                          title="Download Book PDF"
                          className="p-1 rounded-lg text-slate-400 hover:text-orange-600 hover:bg-orange-50 transition"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Chapters & Syllabus Explorer (2 Cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <h2 className="text-lg font-black text-slate-900 flex items-center">
              <BookCheck className="w-4 h-4 mr-2 text-emerald-600" />
              Syllabus Chapters Explorer
            </h2>

            {activeBook && (
              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={() => handleDownloadPdf(activeBook)}
                  disabled={downloadingId === activeBook.id}
                  className="clay-btn-light px-3.5 py-2 text-xs flex items-center space-x-1.5 font-bold"
                  title="Download Authentic Board PDF"
                >
                  {downloadingId === activeBook.id ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Download className="w-3.5 h-3.5 text-orange-600" />
                  )}
                  <span>Download PDF</span>
                </button>

                <Link
                  href={`/papers/generate?book_id=${activeBook.id}`}
                  className="clay-btn-primary px-4 py-2 text-xs flex items-center space-x-1.5"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Generate Exam with this Book</span>
                </Link>
              </div>
            )}
          </div>

          {activeBook ? (
            <div className="clay-card p-6 sm:p-8 space-y-6">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Selected Curriculum Book
                </span>
                <h3 className={`text-xl font-black text-slate-900 mt-1 ${activeBook.language === "ur" ? "urdu-text text-xl" : ""}`}>
                  {activeBook.title}
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Grade {activeBook.grade} • Subject: <strong>{activeBook.subject}</strong> • Total Pages: {activeBook.total_pages}
                </p>
              </div>

              {/* Chapters Table */}
              <div className="space-y-3">
                <h4 className="text-xs font-black uppercase tracking-wider text-slate-700">
                  Detected & Indexed Chapters ({activeBook.chapters?.length || 0})
                </h4>

                <div className="divide-y divide-slate-100 clay-card-flat p-2">
                  {activeBook.chapters?.map((ch, idx) => (
                    <div
                      key={ch.id}
                      className="p-3 flex items-center justify-between text-xs hover:bg-white/80 transition rounded-xl"
                    >
                      <div className="min-w-0 pr-4">
                        <div className="flex items-center space-x-2">
                          <span className="font-mono font-bold text-orange-600 bg-orange-50 px-2 py-0.5 rounded text-[11px]">
                            Ch #{ch.chapter_number}
                          </span>
                          <span className={`font-bold text-slate-900 truncate ${activeBook.language === "ur" ? "urdu-text" : ""}`}>
                            {ch.title}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2 shrink-0">
                        <span className="clay-badge-sky px-2.5 py-0.5 rounded-full text-[10px] font-bold">
                          Pages {ch.start_page}–{ch.end_page}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="clay-card p-12 text-center text-slate-400">
              <BookOpen className="w-10 h-10 mx-auto mb-2 text-slate-300" />
              <p className="text-xs font-semibold">Select a textbook from the left to view its syllabus chapters.</p>
            </div>
          )}
        </div>

      </div>

      {/* Upload Modal (Clay Dialog) */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="clay-card p-6 sm:p-8 max-w-lg w-full space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-black text-slate-900 flex items-center">
                <Upload className="w-4 h-4 mr-2 text-orange-600" />
                Upload Textbook PDF
              </h3>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-slate-400 hover:text-slate-700"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpload} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Textbook Title *
                </label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Physics Class 10 (KPK Board)"
                  className="w-full clay-input p-2.5 text-xs"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">
                    Subject *
                  </label>
                  <input
                    type="text"
                    required
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    placeholder="Physics, Chemistry..."
                    className="w-full clay-input p-2.5 text-xs"
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-700 mb-1">
                    Class / Grade *
                  </label>
                  <input
                    type="text"
                    required
                    value={grade}
                    onChange={(e) => setGrade(e.target.value)}
                    placeholder="9, 10, 11, 12"
                    className="w-full clay-input p-2.5 text-xs"
                  />
                </div>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Language
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full clay-input p-2.5 text-xs font-semibold"
                >
                  <option value="en">English (LTR)</option>
                  <option value="ur">اردو (Urdu RTL)</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  PDF Textbook File *
                </label>
                <input
                  type="file"
                  required
                  accept=".pdf"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="w-full clay-input p-2 text-xs"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="clay-btn-light px-4 py-2 text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="clay-btn-primary px-5 py-2 text-xs flex items-center space-x-1.5 disabled:opacity-50"
                >
                  {uploading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Upload className="w-3.5 h-3.5" />}
                  <span>{uploading ? "Extracting Text..." : "Upload & Parse"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
