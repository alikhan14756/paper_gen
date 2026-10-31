import React from "react";
import Link from "next/link";
import { ExternalLink, Sparkles, Heart, Globe, Mail, ShieldCheck } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="mt-auto px-4 sm:px-6 lg:px-8 pb-6 pt-10">
      <div className="max-w-7xl mx-auto clay-card px-6 py-6 backdrop-blur-md bg-white/95">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 border-b border-slate-100 pb-5">
          {/* Brand Info */}
          <div className="flex items-center space-x-3 text-center md:text-left">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center text-white shadow-md shadow-orange-500/20">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <p className="font-extrabold text-slate-800 text-sm tracking-tight">
                ExamForge AI <span className="text-orange-600 text-xs font-semibold">| KPK BISEP Edition</span>
              </p>
              <p className="text-[11px] text-slate-500">
                Multi-Tenant Bilingual Examination Generator & Assessment Platform
              </p>
            </div>
          </div>

          {/* Nav Links */}
          <div className="flex items-center flex-wrap justify-center gap-4 text-xs font-medium text-slate-600">
            <Link href="/" className="hover:text-orange-600 transition">
              Dashboard
            </Link>
            <Link href="/papers" className="hover:text-orange-600 transition">
              Examinations
            </Link>
            <Link href="/books" className="hover:text-orange-600 transition">
              Syllabus Textbooks
            </Link>
            <Link href="/about" className="hover:text-orange-600 font-bold text-orange-600 transition">
              About & Architecture
            </Link>
          </div>
        </div>

        {/* Creator Attribution Section (Muhammad Ali | AliBuild) */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 text-xs text-slate-600">
          <div className="flex items-center space-x-1.5 text-center sm:text-left">
            <span>ExamForge AI — Designed and developed by</span>
            <span className="font-bold text-slate-900">Muhammad Ali</span>
            <span className="text-slate-400">|</span>
            <span className="text-slate-600 hidden sm:inline">Frontend Developer & Web Developer</span>
          </div>

          <div className="flex items-center space-x-3">
            <a
              href="https://alibuild.site"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-1 text-orange-600 hover:text-orange-700 font-bold bg-orange-50 hover:bg-orange-100/80 px-2.5 py-1 rounded-xl transition"
              title="Visit Muhammad Ali's Portfolio (AliBuild)"
            >
              <Globe className="w-3.5 h-3.5" />
              <span>alibuild.site</span>
              <ExternalLink className="w-3 h-3 ml-0.5 opacity-70" />
            </a>

            <a
              href="mailto:alikhanwebdeveloper@gmail.com"
              className="inline-flex items-center space-x-1 text-slate-500 hover:text-slate-800 bg-slate-100 hover:bg-slate-200/80 px-2 py-1 rounded-xl transition"
              title="Contact Developer"
            >
              <Mail className="w-3.5 h-3.5" />
              <span className="hidden md:inline">Contact</span>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};
