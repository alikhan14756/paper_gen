import React from "react";
import Link from "next/link";
import { 
  Sparkles, 
  ExternalLink, 
  Globe, 
  Mail, 
  ShieldCheck, 
  BookOpen, 
  Award, 
  CheckCircle2, 
  Cpu, 
  Layers, 
  FileText, 
  Fingerprint, 
  Lock,
  ArrowRight,
  Code2
} from "lucide-react";

export const metadata = {
  title: "About ExamForge AI — Developed by Muhammad Ali",
  description: "Learn about ExamForge AI's bilingual examination platform architecture, Bloom's Taxonomy cognitive grounding, and its creator Muhammad Ali (AliBuild).",
};

export default function AboutPage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      
      {/* Hero Section */}
      <div className="clay-card p-8 sm:p-12 text-center relative overflow-hidden bg-gradient-to-b from-white via-white to-orange-50/30">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full clay-badge-mint text-xs font-bold mb-4">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Next-Gen Assessment Architecture</span>
        </div>
        
        <h1 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight mb-4">
          About <span className="bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">ExamForge AI</span>
        </h1>
        
        <p className="max-w-3xl mx-auto text-base sm:text-lg text-slate-600 leading-relaxed">
          ExamForge AI is a multi-tenant, bilingual (Urdu & English) examination management SaaS engineered 
          specifically for Pakistani educational boards (BISE Peshawar, Federal Board, and Punjab Boards). 
          It bridges rigorous textbook provenance with Bloom&apos;s Taxonomy cognitive modeling.
        </p>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link href="/papers/generate" className="clay-btn-primary px-6 py-3 text-sm flex items-center space-x-2">
            <span>Generate Examination</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <a 
            href="https://alibuild.site" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="clay-btn-light px-5 py-3 text-sm flex items-center space-x-2"
          >
            <Globe className="w-4 h-4 text-orange-600" />
            <span>Developer Portfolio (AliBuild)</span>
            <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
          </a>
        </div>
      </div>

      {/* Creator Spotlight Section */}
      <div className="clay-card p-8 sm:p-10 border-2 border-orange-200/80 bg-gradient-to-br from-white via-orange-50/20 to-white">
        <div className="flex flex-col lg:flex-row items-center lg:items-start gap-8">
          <div className="h-28 w-28 sm:h-36 sm:w-36 rounded-3xl bg-gradient-to-tr from-slate-900 via-slate-800 to-orange-600 flex items-center justify-center text-white text-3xl font-black shadow-xl shadow-orange-500/20 flex-shrink-0">
            MA
          </div>

          <div className="flex-1 space-y-4 text-center lg:text-left">
            <div className="space-y-1">
              <span className="text-xs font-bold uppercase tracking-wider text-orange-600">Lead Creator & Architect</span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900">Muhammad Ali</h2>
              <p className="text-slate-600 font-medium text-sm sm:text-base">
                Frontend Developer & Web Developer • Founder of AliBuild
              </p>
            </div>

            <p className="text-sm text-slate-600 leading-relaxed">
              Muhammad Ali designed and developed ExamForge AI with a vision to modernize educational testing in Pakistan. 
              By merging modern tactile claymorphism user experiences with robust backend multi-tenant security, 
              verbatim textbook citation engines, and authentic BISEP layout generation, ExamForge AI sets a standard 
              for secure, localized EdTech solutions.
            </p>

            <div className="flex flex-wrap items-center justify-center lg:justify-start gap-3 pt-2">
              <a
                href="https://alibuild.site"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-2 clay-btn-primary px-4 py-2 text-xs font-bold"
              >
                <Globe className="w-4 h-4" />
                <span>alibuild.site (Portfolio)</span>
                <ExternalLink className="w-3 h-3" />
              </a>

              <a
                href="mailto:alikhanwebdeveloper@gmail.com"
                className="inline-flex items-center space-x-2 clay-card-flat px-4 py-2 text-xs font-bold text-slate-700 hover:text-slate-900 hover:bg-slate-100 transition"
              >
                <Mail className="w-4 h-4 text-orange-600" />
                <span>alikhanwebdeveloper@gmail.com</span>
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Core Architectural Pillars */}
      <div className="space-y-6">
        <div className="text-center space-y-1">
          <h2 className="text-2xl font-black text-slate-900">Engineering & System Architecture</h2>
          <p className="text-xs text-slate-500 max-w-xl mx-auto">
            ExamForge AI is built with an enterprise multi-tenant framework prioritizing isolation, accuracy, and compliance.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {/* Pillar 1 */}
          <div className="clay-card p-6 space-y-3">
            <div className="h-10 w-10 rounded-2xl bg-orange-100 text-orange-600 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900 text-base">Multi-Tenant Isolation & RBAC</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Strict row-level school isolation across 24 relational models. Enforces role-based permissions (Superadmin, School Admin, Teacher) preventing cross-tenant document and paper leakage.
            </p>
          </div>

          {/* Pillar 2 */}
          <div className="clay-card p-6 space-y-3">
            <div className="h-10 w-10 rounded-2xl bg-blue-100 text-blue-600 flex items-center justify-center">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900 text-base">Verbatim Textbook Grounding</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Every question links directly to exact textbook page coordinates, paragraph excerpts, and cognitive confidence scores, eliminating AI hallucinations and ensuring exam syllabus fidelity.
            </p>
          </div>

          {/* Pillar 3 */}
          <div className="clay-card p-6 space-y-3">
            <div className="h-10 w-10 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center">
              <Layers className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900 text-base">Bloom&apos;s Taxonomy Engine</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Automated cognitive blueprinting mapping questions across Remember (Knowledge), Understand, Apply, Analyze, Evaluate, and Create to balance exam difficulty scientifically.
            </p>
          </div>

          {/* Pillar 4 */}
          <div className="clay-card p-6 space-y-3">
            <div className="h-10 w-10 rounded-2xl bg-purple-100 text-purple-600 flex items-center justify-center">
              <BookOpen className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900 text-base">Bilingual Urdu RTL & English DOCX</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              True native right-to-left (RTL) formatting using Noto Nastaliq Urdu alongside English serif headers, complete with BISEP bubble answer grids and invigilator signature blocks.
            </p>
          </div>

          {/* Pillar 5 */}
          <div className="clay-card p-6 space-y-3">
            <div className="h-10 w-10 rounded-2xl bg-amber-100 text-amber-600 flex items-center justify-center">
              <Lock className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900 text-base">Confidential Marking Schemes</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Automated generation of secure, teacher-only answer keys, cognitive classification summaries, and marks allocation rubrics separated from student exam papers.
            </p>
          </div>

          {/* Pillar 6 */}
          <div className="clay-card p-6 space-y-3">
            <div className="h-10 w-10 rounded-2xl bg-teal-100 text-teal-600 flex items-center justify-center">
              <Fingerprint className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900 text-base">Public Verification & Anti-Tamper</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Each generated paper embeds a cryptographic verification code (`EF-XXXX-YYYY`) allowing schools, boards, and invigilators to authenticate papers instantly online.
            </p>
          </div>
        </div>
      </div>

      {/* BISEP Board Compliance Banner */}
      <div className="clay-card p-6 sm:p-8 bg-slate-900 text-white flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-2 text-center md:text-left">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-orange-600/30 text-orange-400 text-xs font-bold border border-orange-500/30">
            <Award className="w-3.5 h-3.5" />
            <span>KPK Provincial Standard</span>
          </div>
          <h3 className="text-xl sm:text-2xl font-bold">BISE Peshawar & KPK Board Standardized Layout</h3>
          <p className="text-xs text-slate-300 max-w-xl">
            Formatted in strict adherence to Khyber Pakhtunkhwa Board of Intermediate and Secondary Education (BISEP) specifications, complete with Section A (Objective/MCQs), Section B (Short Questions), and Section C (Long/Descriptive).
          </p>
        </div>

        <Link
          href="/papers/generate"
          className="clay-btn-primary px-6 py-3 text-xs whitespace-nowrap"
        >
          Create BISEP Paper Now
        </Link>
      </div>

    </div>
  );
}
