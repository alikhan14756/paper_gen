"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ApiClient, Paper } from "@/lib/api";
import { 
  FileText, 
  Download, 
  PlusCircle, 
  Calendar, 
  Award, 
  Clock, 
  Search, 
  Loader2,
  ChevronRight,
  GraduationCap
} from "lucide-react";

export default function PapersListPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterLang, setFilterLang] = useState<string>("all");
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  useEffect(() => {
    loadPapers();
  }, []);

  const loadPapers = async () => {
    setLoading(true);
    try {
      const data = await ApiClient.listPapers();
      setPapers(data);
    } catch (err: any) {
      alert("Failed to load papers: " + err.message);
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

  const filteredPapers = papers.filter((p) => {
    const matchSearch =
      p.title.toLowerCase().includes(search.toLowerCase()) ||
      p.subject.toLowerCase().includes(search.toLowerCase()) ||
      p.grade.toLowerCase().includes(search.toLowerCase());
    const matchLang = filterLang === "all" || p.language === filterLang;
    return matchSearch && matchLang;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Header Banner */}
      <div className="clay-card p-6 sm:p-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold clay-badge-mint mb-2">
            <GraduationCap className="w-3.5 h-3.5 mr-1" />
            BISE Peshawar & Board Examination Archive
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Saved Examination Papers
          </h1>
          <p className="text-slate-600 text-xs sm:text-sm mt-1">
            Access, edit questions, inspect answer keys, and export Microsoft Word (.docx) papers.
          </p>
        </div>

        <Link
          href="/papers/generate"
          className="clay-btn-primary px-5 py-3 text-xs flex items-center space-x-2 self-start md:self-auto font-bold"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Generate New Paper</span>
        </Link>
      </div>

      {/* Filter and Search Bar (Clay Card) */}
      <div className="clay-card p-4 flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-96">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search by title, subject, grade..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full clay-input pl-10 pr-3 py-2 text-xs"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <span className="text-xs font-bold text-slate-600">Language:</span>
          <select
            value={filterLang}
            onChange={(e) => setFilterLang(e.target.value)}
            className="clay-input px-3 py-1.5 text-xs font-semibold"
          >
            <option value="all">All Languages ({papers.length})</option>
            <option value="en">English (LTR)</option>
            <option value="ur">اردو (Urdu RTL)</option>
          </select>
        </div>
      </div>

      {/* Papers Grid */}
      {loading ? (
        <div className="clay-card p-16 text-center text-slate-400 flex flex-col items-center justify-center">
          <Loader2 className="w-10 h-10 animate-spin text-orange-500 mb-2" />
          <p className="text-xs font-bold uppercase tracking-wider">Loading saved papers...</p>
        </div>
      ) : filteredPapers.length === 0 ? (
        <div className="clay-card p-16 text-center">
          <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="font-extrabold text-base text-slate-700">No examination papers match your criteria</h3>
          <p className="text-xs text-slate-500 mt-1">Try resetting the search filters or create a new paper.</p>
          <Link
            href="/papers/generate"
            className="clay-btn-primary px-5 py-2.5 text-xs inline-flex items-center mt-5"
          >
            <PlusCircle className="w-3.5 h-3.5 mr-1.5" />
            Generate Paper Now
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPapers.map((paper) => {
            const isUrdu = paper.language === "ur";
            const totalQuestions = paper.sections?.reduce(
              (acc, s) => acc + (s.questions?.length || 0),
              0
            );

            return (
              <div
                key={paper.id}
                className="clay-card-interactive p-6 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className={`text-[10px] px-3 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                      isUrdu ? "clay-badge-mint" : "clay-badge-sky"
                    }`}>
                      {isUrdu ? "اردو (Urdu RTL)" : "English (LTR)"}
                    </span>
                    <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full clay-badge-peach">
                      {paper.total_marks} Marks
                    </span>
                  </div>

                  <h3 className={`font-black text-base text-slate-900 leading-snug line-clamp-2 ${isUrdu ? "urdu-text text-base" : ""}`}>
                    {paper.title}
                  </h3>

                  <div className="mt-3.5 space-y-1.5 text-xs text-slate-500">
                    <p className="flex items-center font-medium">
                      <Award className="w-3.5 h-3.5 mr-2 text-slate-400" />
                      {paper.subject} • Grade {paper.grade}
                    </p>
                    <p className="flex items-center font-medium">
                      <Clock className="w-3.5 h-3.5 mr-2 text-slate-400" />
                      {paper.time_allowed_minutes} Minutes Allowed
                    </p>
                    <p className="flex items-center font-medium">
                      <Calendar className="w-3.5 h-3.5 mr-2 text-slate-400" />
                      Session {paper.academic_session}
                    </p>
                  </div>
                </div>

                <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[11px] font-bold text-slate-400">
                    {paper.sections?.length || 0} Sections • {totalQuestions || 0} Qs
                  </span>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleDownload(paper)}
                      disabled={downloadingId === paper.id}
                      title="Download Word (.docx)"
                      className="clay-btn-primary p-2 text-white disabled:opacity-50"
                    >
                      {downloadingId === paper.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Download className="w-4 h-4" />
                      )}
                    </button>
                    
                    <Link
                      href={`/papers/${paper.id}`}
                      className="clay-btn-light px-3 py-1.5 text-xs flex items-center space-x-1 text-slate-700"
                    >
                      <span>Editor</span>
                      <ChevronRight className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
