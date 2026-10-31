"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth, DEMO_CREDENTIALS } from "@/lib/auth-context";
import { 
  FileText, 
  BookOpen, 
  PlusCircle, 
  Building2, 
  Sparkles,
  LogOut,
  UserCheck,
  GraduationCap,
  Info,
  LogIn,
  School
} from "lucide-react";

export const Navbar: React.FC = () => {
  const { user, switchRole, logout } = useAuth();
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const isTeacher = user?.role === "teacher";
  const isSchoolAdmin = user?.role === "school_admin";
  const isSuperAdmin = user?.role === "super_admin";

  return (
    <header className="sticky top-3 z-50 px-4 sm:px-6 lg:px-8 mb-4">
      <div className="max-w-7xl mx-auto clay-card px-4 sm:px-6 py-2.5 backdrop-blur-md bg-white/95">
        <div className="flex items-center justify-between h-14">
          
          {/* Logo & Brand Pill */}
          <div className="flex items-center space-x-3">
            <Link href="/" className="flex items-center space-x-2.5 group">
              <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center text-white shadow-md shadow-orange-500/30 group-hover:scale-105 transition transform">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <span className="font-black text-xl tracking-tight bg-gradient-to-r from-slate-900 via-slate-800 to-orange-600 bg-clip-text text-transparent">
                  ExamForge
                </span>
                <span className="block text-[10px] text-orange-600 font-extrabold tracking-wider uppercase">
                  BISEP KPK Edition
                </span>
              </div>
            </Link>

            {/* KPK Peshawar Board Badge */}
            <div className="hidden lg:flex items-center px-3 py-1 rounded-full text-[11px] font-bold clay-badge-mint">
              <GraduationCap className="w-3.5 h-3.5 mr-1" />
              BISE Peshawar Syllabus
            </div>

            {mounted && user?.school_name && (
              <span className="hidden xl:inline-flex items-center px-3 py-1 rounded-full text-[11px] font-semibold clay-badge-sky">
                <Building2 className="w-3 h-3 mr-1" />
                {user.school_name}
              </span>
            )}
          </div>

          {/* Navigation Links (Clay Pills) */}
          <nav className="hidden md:flex items-center space-x-2">
            <Link
              href="/"
              className={`px-4 py-2 rounded-2xl text-xs font-bold transition-all ${
                pathname === "/"
                  ? "clay-btn-dark shadow-sm"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/80"
              }`}
            >
              Dashboard
            </Link>

            <Link
              href="/papers/generate"
              className={`flex items-center space-x-1.5 px-4 py-2 rounded-2xl text-xs font-bold transition-all ${
                pathname === "/papers/generate"
                  ? "clay-btn-primary"
                  : "text-orange-600 hover:bg-orange-50"
              }`}
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Generate Paper</span>
            </Link>

            <Link
              href="/papers"
              className={`flex items-center space-x-1.5 px-4 py-2 rounded-2xl text-xs font-bold transition-all ${
                pathname === "/papers"
                  ? "clay-btn-dark shadow-sm"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/80"
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>My Papers</span>
            </Link>

            <Link
              href="/books"
              className={`flex items-center space-x-1.5 px-4 py-2 rounded-2xl text-xs font-bold transition-all ${
                pathname.startsWith("/books")
                  ? "clay-btn-dark shadow-sm"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/80"
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>KPK Syllabus Books</span>
            </Link>

            <Link
              href="/about"
              className={`flex items-center space-x-1.5 px-4 py-2 rounded-2xl text-xs font-bold transition-all ${
                pathname === "/about"
                  ? "clay-btn-dark shadow-sm"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/80"
              }`}
            >
              <Info className="w-3.5 h-3.5" />
              <span>About</span>
            </Link>
          </nav>

          {/* Right Action & User Profile Pill */}
          <div className="flex items-center space-x-2.5">
            {/* Quick Demo Switcher (Clay Pill) */}
            {mounted && user && (
              <div className="hidden xl:flex items-center clay-card-flat p-1 text-[11px] font-semibold">
                <span className="text-slate-400 px-2 flex items-center">
                  <UserCheck className="w-3 h-3 mr-1" /> Role:
                </span>
                <button
                  onClick={() => switchRole("teacher")}
                  className={`px-2.5 py-1 rounded-xl transition ${
                    isTeacher ? "bg-orange-600 text-white font-bold shadow-sm" : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  Teacher
                </button>
                <button
                  onClick={() => switchRole("school_admin")}
                  className={`px-2.5 py-1 rounded-xl transition ${
                    isSchoolAdmin ? "bg-orange-600 text-white font-bold shadow-sm" : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  Admin
                </button>
              </div>
            )}

            {mounted ? (
              user ? (
                <div className="flex items-center space-x-2 clay-card-flat px-3 py-1.5 rounded-2xl">
                  <div className="text-right">
                    <p className="text-xs font-bold text-slate-800 leading-tight">{user.full_name}</p>
                    <p className="text-[10px] text-orange-600 font-semibold capitalize leading-tight">
                      {user.role.replace("_", " ")}
                    </p>
                  </div>
                  <button
                    onClick={logout}
                    title="Logout"
                    className="p-1.5 rounded-xl text-slate-400 hover:text-red-600 hover:bg-red-50 transition"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                  </button>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Link
                    href="/login"
                    className="clay-btn-light px-3.5 py-2 text-xs font-bold flex items-center space-x-1.5"
                  >
                    <LogIn className="w-3.5 h-3.5 text-slate-700" />
                    <span>Sign In</span>
                  </Link>
                  <Link
                    href="/register"
                    className="clay-btn-primary px-4 py-2 text-xs font-bold flex items-center space-x-1.5"
                  >
                    <School className="w-3.5 h-3.5" />
                    <span>Register School</span>
                  </Link>
                </div>
              )
            ) : (
              <div className="h-9 w-24 bg-slate-100 rounded-2xl animate-pulse" />
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
