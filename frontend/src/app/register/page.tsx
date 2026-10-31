"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ApiClient } from "@/lib/api";
import { 
  Building2, 
  GraduationCap, 
  Sparkles, 
  Lock, 
  Mail, 
  User, 
  ArrowRight, 
  Loader2, 
  MapPin,
  Tag,
  KeyRound,
  CheckCircle2,
  RefreshCw,
  Gift
} from "lucide-react";

export default function RegisterPage() {
  const [step, setStep] = useState<"register" | "verify">("register");
  const [mode, setMode] = useState<"school" | "teacher">("school");
  const [schools, setSchools] = useState<Array<{ id: string; name: string; slug: string }>>([]);
  const [loadingSchools, setLoadingSchools] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // School Form state
  const [schoolName, setSchoolName] = useState("");
  const [schoolSlug, setSchoolSlug] = useState("");
  const [schoolAddress, setSchoolAddress] = useState("");
  const [adminName, setAdminName] = useState("");
  const [adminEmail, setAdminEmail] = useState("");
  const [adminPassword, setAdminPassword] = useState("");

  // Verification State
  const [verificationEmail, setVerificationEmail] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [resending, setResending] = useState(false);

  // Teacher Form state
  const [selectedSchoolId, setSelectedSchoolId] = useState("");
  const [teacherName, setTeacherName] = useState("");
  const [teacherEmail, setTeacherEmail] = useState("");
  const [teacherPassword, setTeacherPassword] = useState("");

  useEffect(() => {
    fetchSchools();
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const emailParam = params.get("verify_email") || params.get("email");
      if (emailParam) {
        setVerificationEmail(emailParam);
        setStep("verify");
      }
    }
  }, []);

  const fetchSchools = async () => {
    setLoadingSchools(true);
    try {
      const data = await ApiClient.listSchools();
      setSchools(data);
      if (data.length > 0 && !selectedSchoolId) {
        setSelectedSchoolId(data[0].id);
      }
    } catch {
      // Fallback
    } finally {
      setLoadingSchools(false);
    }
  };

  const handleSchoolSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const res = await ApiClient.registerSchool({
        school_name: schoolName,
        slug: schoolSlug || schoolName.toLowerCase().replace(/[^a-z0-9]/g, "-"),
        address: schoolAddress,
        admin_name: adminName,
        admin_email: adminEmail,
        admin_password: adminPassword,
      });

      setVerificationEmail(res.email);
      setStep("verify");
      setSuccessMsg(res.message);
    } catch (err: any) {
      setError(err.message || "Failed to register school.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleVerifySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!verificationCode.trim()) {
      setError("Please enter the 6-digit verification code.");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const res = await ApiClient.verifyEmail(verificationEmail, verificationCode.trim());
      localStorage.setItem("examforge_token", res.access_token);
      setSuccessMsg("Account verified successfully! Activating Free Trial...");
      setTimeout(() => {
        window.location.href = "/";
      }, 1000);
    } catch (err: any) {
      setError(err.message || "Verification failed. Please check the code.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleResendCode = async () => {
    if (!verificationEmail) return;
    setResending(true);
    setError(null);
    try {
      await ApiClient.resendVerificationCode(verificationEmail);
      setSuccessMsg("A fresh 6-digit verification code has been dispatched to your email. Please check your inbox.");
    } catch (err: any) {
      setError(err.message || "Failed to resend verification code.");
    } finally {
      setResending(false);
    }
  };

  const handleTeacherSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSchoolId) {
      setError("Please select your school.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const res = await ApiClient.registerTeacher({
        school_id: selectedSchoolId,
        full_name: teacherName,
        email: teacherEmail,
        password: teacherPassword,
      });
      localStorage.setItem("examforge_token", res.access_token);
      window.location.href = "/";
    } catch (err: any) {
      setError(err.message || "Failed to register teacher account.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-xl w-full space-y-6 clay-card p-8 sm:p-10">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="mx-auto h-12 w-12 rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center text-white shadow-md shadow-orange-500/30">
            <Sparkles className="h-6 w-6" />
          </div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">
            {step === "verify" ? "Verify School Email" : "Register School or Faculty"}
          </h2>
          <div className="inline-flex items-center px-3 py-1 rounded-full text-[11px] font-bold clay-badge-mint">
            <GraduationCap className="w-3.5 h-3.5 mr-1" />
            KPK Peshawar Board (BISEP) & Pakistan Education Portal
          </div>
        </div>

        {/* Free Trial Banner */}
        <div className="clay-card-flat p-3.5 rounded-2xl flex items-center space-x-3 bg-gradient-to-r from-orange-50/60 to-amber-50/60 border border-orange-200/80">
          <div className="h-8 w-8 rounded-xl bg-orange-500 text-white flex items-center justify-center shrink-0 shadow-sm">
            <Gift className="w-4 h-4" />
          </div>
          <div className="text-xs">
            <p className="font-extrabold text-slate-900">
              Free Trial Activated upon Registration
            </p>
            <p className="text-slate-600 text-[11px]">
              Generate <strong className="text-orange-600">2 free papers per subject</strong> across all 18 Class 9th & 10th KPK Textbook Board books!
            </p>
          </div>
        </div>

        {error && (
          <div className="p-3.5 text-xs bg-red-50 border border-red-200 text-red-700 rounded-2xl font-medium">
            {error}
          </div>
        )}

        {successMsg && (
          <div className="p-3.5 text-xs bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-2xl font-medium flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {step === "verify" ? (
          /* STEP 2: EMAIL VERIFICATION CODE FORM */
          <form onSubmit={handleVerifySubmit} className="space-y-5">
            <div className="clay-card-flat p-4 rounded-2xl space-y-2 text-center">
              <Mail className="w-8 h-8 text-orange-600 mx-auto" />
              <p className="text-xs text-slate-700">
                A 6-digit email verification code was sent to:
              </p>
              <p className="text-sm font-extrabold text-slate-900 bg-white/80 py-1 px-3 rounded-xl border border-slate-200 inline-block">
                {verificationEmail}
              </p>
              <p className="text-[11px] text-slate-500">
                Please open your email inbox, copy the 6-digit code, and enter it below to activate your school account.
              </p>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5 text-center">
                Enter 6-Digit Verification Code *
              </label>
              <div className="relative max-w-xs mx-auto">
                <input
                  type="text"
                  maxLength={6}
                  required
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value.replace(/[^0-9]/g, ""))}
                  placeholder="Enter 6-digit code from email"
                  className="w-full clay-input text-center text-lg font-mono tracking-widest py-3 font-bold"
                  autoFocus
                />
              </div>
            </div>

            <div className="space-y-3">
              <button
                type="submit"
                disabled={submitting || verificationCode.length < 6}
                className="w-full clay-btn-primary py-3 px-4 text-xs font-bold flex items-center justify-center space-x-2 disabled:opacity-50"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Verifying Code...</span>
                  </>
                ) : (
                  <>
                    <span>Verify & Activate School Account</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>

              <div className="flex items-center justify-between pt-1 text-xs">
                <button
                  type="button"
                  onClick={handleResendCode}
                  disabled={resending}
                  className="inline-flex items-center space-x-1 text-orange-600 font-bold hover:underline disabled:opacity-50"
                >
                  <RefreshCw className={`w-3 h-3 ${resending ? "animate-spin" : ""}`} />
                  <span>Resend Verification Code</span>
                </button>

                <button
                  type="button"
                  onClick={() => { setStep("register"); setError(null); setSuccessMsg(null); }}
                  className="text-slate-500 hover:text-slate-900"
                >
                  Change Email
                </button>
              </div>
            </div>
          </form>
        ) : (
          /* STEP 1: REGISTRATION FORM */
          <>
            {/* Mode Selector (Clay Pills) */}
            <div className="clay-card-flat p-1 flex">
              <button
                type="button"
                onClick={() => { setMode("school"); setError(null); }}
                className={`flex-1 flex items-center justify-center py-2.5 text-xs font-bold rounded-xl transition ${
                  mode === "school"
                    ? "bg-white text-slate-900 shadow-sm"
                    : "text-slate-500 hover:text-slate-900"
                }`}
              >
                <Building2 className="w-3.5 h-3.5 mr-1.5 text-orange-600" />
                Register New School
              </button>
              <button
                type="button"
                onClick={() => { setMode("teacher"); setError(null); }}
                className={`flex-1 flex items-center justify-center py-2.5 text-xs font-bold rounded-xl transition ${
                  mode === "teacher"
                    ? "bg-white text-slate-900 shadow-sm"
                    : "text-slate-500 hover:text-slate-900"
                }`}
              >
                <GraduationCap className="w-3.5 h-3.5 mr-1.5 text-blue-600" />
                Join as Teacher
              </button>
            </div>

            {mode === "school" ? (
              <form onSubmit={handleSchoolSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      School / College Name *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                        <Building2 className="h-4 w-4" />
                      </div>
                      <input
                        type="text"
                        required
                        value={schoolName}
                        onChange={(e) => {
                          setSchoolName(e.target.value);
                          if (!schoolSlug) {
                            setSchoolSlug(e.target.value.toLowerCase().replace(/[^a-z0-9]/g, "-"));
                          }
                        }}
                        placeholder="Peshawar Model Degree College"
                        className="w-full clay-input pl-10 pr-3 py-2 text-xs"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      School Code / Short Identifier *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                        <Tag className="h-4 w-4" />
                      </div>
                      <input
                        type="text"
                        required
                        value={schoolSlug}
                        onChange={(e) => setSchoolSlug(e.target.value)}
                        placeholder="pmdc-peshawar"
                        className="w-full clay-input pl-10 pr-3 py-2 text-xs"
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Campus Address / District
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                      <MapPin className="h-4 w-4" />
                    </div>
                    <input
                      type="text"
                      value={schoolAddress}
                      onChange={(e) => setSchoolAddress(e.target.value)}
                      placeholder="University Road, Peshawar, Khyber Pakhtunkhwa"
                      className="w-full clay-input pl-10 pr-3 py-2 text-xs"
                    />
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-100">
                  <p className="text-[11px] font-black text-slate-400 uppercase tracking-wider mb-2">
                    Administrator Details (Verification Email)
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Principal / Admin Full Name *
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                          <User className="h-4 w-4" />
                        </div>
                        <input
                          type="text"
                          required
                          value={adminName}
                          onChange={(e) => setAdminName(e.target.value)}
                          placeholder="Prof. Tariq Ahmad"
                          className="w-full clay-input pl-10 pr-3 py-2 text-xs"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        School Official Email *
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                          <Mail className="h-4 w-4" />
                        </div>
                        <input
                          type="email"
                          required
                          value={adminEmail}
                          onChange={(e) => setAdminEmail(e.target.value)}
                          placeholder="principal@pmdc.edu.pk"
                          className="w-full clay-input pl-10 pr-3 py-2 text-xs"
                        />
                      </div>
                      <p className="text-[10px] text-slate-400 mt-0.5">Verification code will be sent to this email</p>
                    </div>
                  </div>

                  <div className="mt-3">
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Account Password *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                        <Lock className="h-4 w-4" />
                      </div>
                      <input
                        type="password"
                        required
                        value={adminPassword}
                        onChange={(e) => setAdminPassword(e.target.value)}
                        placeholder="Create strong password"
                        className="w-full clay-input pl-10 pr-3 py-2 text-xs"
                      />
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full clay-btn-primary py-3 px-4 text-xs font-bold flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Sending Verification Code...</span>
                    </>
                  ) : (
                    <>
                      <span>Continue & Receive Email Verification Code</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>
            ) : (
              <form onSubmit={handleTeacherSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Select Your School / Institution *
                  </label>
                  <select
                    required
                    value={selectedSchoolId}
                    onChange={(e) => setSelectedSchoolId(e.target.value)}
                    className="w-full clay-input px-3.5 py-2.5 text-xs font-semibold"
                  >
                    {schools.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name} ({s.slug})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Teacher Full Name *
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                      <User className="h-4 w-4" />
                    </div>
                    <input
                      type="text"
                      required
                      value={teacherName}
                      onChange={(e) => setTeacherName(e.target.value)}
                      placeholder="Prof. Muhammad Kamran"
                      className="w-full clay-input pl-10 pr-3 py-2 text-xs"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Teacher Email Address *
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                      <Mail className="h-4 w-4" />
                    </div>
                    <input
                      type="email"
                      required
                      value={teacherEmail}
                      onChange={(e) => setTeacherEmail(e.target.value)}
                      placeholder="teacher@school.edu.pk"
                      className="w-full clay-input pl-10 pr-3 py-2 text-xs"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Password *
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                      <Lock className="h-4 w-4" />
                    </div>
                    <input
                      type="password"
                      required
                      value={teacherPassword}
                      onChange={(e) => setTeacherPassword(e.target.value)}
                      placeholder="Create password"
                      className="w-full clay-input pl-10 pr-3 py-2 text-xs"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full clay-btn-primary py-3 px-4 text-xs font-bold flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Joining School Faculty...</span>
                    </>
                  ) : (
                    <>
                      <span>Join School Faculty</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>
            )}
          </>
        )}

        <div className="text-center pt-2">
          <p className="text-xs text-slate-500">
            Already have an active school or teacher account?{" "}
            <Link href="/login" className="font-bold text-orange-600 hover:underline">
              Sign In here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
