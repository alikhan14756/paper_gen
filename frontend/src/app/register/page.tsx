"use client";

import React, { useState, useEffect, useRef } from "react";
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
  CheckCircle2,
  RefreshCw,
  Gift,
  Phone,
  MessageSquare,
  ShieldCheck
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
  const [adminPhone, setAdminPhone] = useState("");
  const [adminPassword, setAdminPassword] = useState("");
  const [verificationMethod, setVerificationMethod] = useState<"whatsapp" | "email">("whatsapp");

  // Verification State
  const [verificationIdentifier, setVerificationIdentifier] = useState("");
  const [otpDigits, setOtpDigits] = useState<string[]>(["", "", "", "", "", ""]);
  const [resending, setResending] = useState(false);
  const [cooldownSeconds, setCooldownSeconds] = useState(0);

  // Teacher Form state
  const [selectedSchoolId, setSelectedSchoolId] = useState("");
  const [teacherName, setTeacherName] = useState("");
  const [teacherEmail, setTeacherEmail] = useState("");
  const [teacherPassword, setTeacherPassword] = useState("");

  const inputRefs = useRef<Array<HTMLInputElement | null>>([]);

  useEffect(() => {
    fetchSchools();
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const emailParam = params.get("verify_email") || params.get("email");
      if (emailParam) {
        setVerificationIdentifier(emailParam);
        setStep("verify");
      }
    }
  }, []);

  // Cooldown countdown effect
  useEffect(() => {
    if (cooldownSeconds <= 0) return;
    const timer = setInterval(() => {
      setCooldownSeconds((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [cooldownSeconds]);

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
      const res = await ApiClient.registerInitiate({
        school_name: schoolName,
        principal_name: adminName,
        email: adminEmail,
        phone_number: adminPhone,
        password: adminPassword,
        verification_method: verificationMethod,
      });

      setVerificationIdentifier(res.identifier);
      setStep("verify");
      setCooldownSeconds(60);
      setOtpDigits(["", "", "", "", "", ""]);
      setSuccessMsg(res.message);
      setTimeout(() => {
        if (inputRefs.current[0]) inputRefs.current[0]?.focus();
      }, 200);
    } catch (err: any) {
      setError(err.message || "Failed to register school. Please verify your details.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleOtpBoxChange = (index: number, val: string) => {
    const cleaned = val.replace(/[^0-9]/g, "");
    const newDigits = [...otpDigits];
    newDigits[index] = cleaned ? cleaned[0] : "";
    setOtpDigits(newDigits);

    if (cleaned && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !otpDigits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleOtpPaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pasteData = e.clipboardData.getData("text").replace(/[^0-9]/g, "").slice(0, 6);
    if (!pasteData) return;
    const newDigits = [...otpDigits];
    for (let i = 0; i < pasteData.length; i++) {
      newDigits[i] = pasteData[i];
    }
    setOtpDigits(newDigits);
    const nextIdx = Math.min(pasteData.length, 5);
    inputRefs.current[nextIdx]?.focus();
  };

  const handleVerifySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const code = otpDigits.join("");
    if (code.length < 6) {
      setError("Please enter all 6 digits of your verification code.");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const res = await ApiClient.verifyOTP({
        identifier: verificationIdentifier,
        otp_code: code,
        school_name: schoolName,
        principal_name: adminName,
        password: adminPassword,
      });

      localStorage.setItem("examforge_token", res.access_token);
      setSuccessMsg("Account verified successfully! Opening your Examination Blueprint Dashboard...");
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
    if (!verificationIdentifier || cooldownSeconds > 0) return;
    setResending(true);
    setError(null);
    try {
      const res = await ApiClient.resendOTP(verificationIdentifier);
      setCooldownSeconds(60);
      setOtpDigits(["", "", "", "", "", ""]);
      setSuccessMsg(res.message);
      if (inputRefs.current[0]) inputRefs.current[0]?.focus();
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
            {step === "verify" ? "Verify 6-Digit Security Code" : "Register School or Faculty"}
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
          /* STEP 2: 6-DIGIT OTP VERIFICATION FORM */
          <form onSubmit={handleVerifySubmit} className="space-y-5">
            <div className="clay-card-flat p-4 rounded-2xl space-y-2 text-center border border-emerald-200 bg-emerald-50/40">
              <div className="w-9 h-9 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto">
                {verificationMethod === "whatsapp" ? (
                  <MessageSquare className="w-5 h-5 text-emerald-600" />
                ) : (
                  <Mail className="w-5 h-5 text-blue-600" />
                )}
              </div>
              <p className="text-xs font-bold text-slate-800">
                6-Digit Security Code Dispatched!
              </p>
              <p className="text-sm font-extrabold text-slate-900 bg-white/90 py-1.5 px-3 rounded-xl border border-slate-200 inline-block font-mono">
                {verificationIdentifier}
              </p>
              <p className="text-[11px] text-slate-600">
                Dispatched from <strong className="text-orange-600 font-bold">{verificationMethod === "whatsapp" ? "+923215423874" : "alikhanwebdeveloper@gmail.com"}</strong>.
              </p>
              <p className="text-[10px] text-amber-800 font-bold bg-amber-100/70 inline-block px-2.5 py-0.5 rounded-full">
                ⏱ Code valid for 5 minutes &bull; Maximum 3 attempts
              </p>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-2 text-center">
                Enter 6-Digit Verification Code *
              </label>
              <div className="flex items-center justify-center space-x-2 sm:space-x-3">
                {otpDigits.map((digit, index) => (
                  <input
                    key={index}
                    ref={(el) => { inputRefs.current[index] = el; }}
                    type="text"
                    maxLength={1}
                    pattern="[0-9]"
                    value={digit}
                    onChange={(e) => handleOtpBoxChange(index, e.target.value)}
                    onKeyDown={(e) => handleOtpKeyDown(index, e)}
                    onPaste={handleOtpPaste}
                    autoComplete="off"
                    className="w-11 h-13 text-center text-xl font-mono font-black clay-input focus:border-orange-500 focus:scale-105 transition"
                  />
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <button
                type="submit"
                disabled={submitting || otpDigits.join("").length < 6}
                className="w-full clay-btn-primary py-3 px-4 text-xs font-extrabold flex items-center justify-center space-x-2 disabled:opacity-50"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Verifying Code...</span>
                  </>
                ) : (
                  <>
                    <span>Verify Code & Open Dashboard</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>

              <div className="flex items-center justify-between pt-1 text-xs">
                <button
                  type="button"
                  onClick={handleResendCode}
                  disabled={resending || cooldownSeconds > 0}
                  className="inline-flex items-center space-x-1 text-orange-600 font-bold hover:underline disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${resending ? "animate-spin" : ""}`} />
                  <span>
                    {cooldownSeconds > 0 ? `Resend Code (${cooldownSeconds}s)` : "Resend Code"}
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => { setStep("register"); setError(null); setSuccessMsg(null); }}
                  className="text-slate-500 hover:text-slate-900"
                >
                  Change Details
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
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      WhatsApp Mobile Number *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                        <Phone className="h-4 w-4" />
                      </div>
                      <input
                        type="text"
                        required
                        value={adminPhone}
                        onChange={(e) => setAdminPhone(e.target.value)}
                        placeholder="03215423874 or +92..."
                        className="w-full clay-input pl-10 pr-3 py-2 text-xs"
                      />
                    </div>
                  </div>
                </div>

                <div>
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

                {/* Verification Channel Selector */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">
                    Preferred OTP Verification Channel *
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <label className={`clay-card-flat p-2.5 rounded-xl flex items-center space-x-2.5 cursor-pointer border transition ${verificationMethod === 'whatsapp' ? 'border-orange-500 bg-orange-50/70' : 'border-transparent hover:border-orange-200'}`}>
                      <input
                        type="radio"
                        name="otp_method"
                        value="whatsapp"
                        checked={verificationMethod === "whatsapp"}
                        onChange={() => setVerificationMethod("whatsapp")}
                        className="text-orange-600 focus:ring-orange-500"
                      />
                      <div className="text-left">
                        <p className="text-xs font-black text-slate-900 flex items-center">
                          <MessageSquare className="w-3.5 h-3.5 text-emerald-600 mr-1" /> WhatsApp
                        </p>
                        <p className="text-[10px] text-slate-500">Via +923215423874</p>
                      </div>
                    </label>

                    <label className={`clay-card-flat p-2.5 rounded-xl flex items-center space-x-2.5 cursor-pointer border transition ${verificationMethod === 'email' ? 'border-orange-500 bg-orange-50/70' : 'border-transparent hover:border-orange-200'}`}>
                      <input
                        type="radio"
                        name="otp_method"
                        value="email"
                        checked={verificationMethod === "email"}
                        onChange={() => setVerificationMethod("email")}
                        className="text-orange-600 focus:ring-orange-500"
                      />
                      <div className="text-left">
                        <p className="text-xs font-black text-slate-900 flex items-center">
                          <Mail className="w-3.5 h-3.5 text-blue-600 mr-1" /> Email
                        </p>
                        <p className="text-[10px] text-slate-500">alikhanwebdeveloper@gmail.com</p>
                      </div>
                    </label>
                  </div>
                </div>

                {/* Official Sender Attribution Notice */}
                <div className="p-2.5 rounded-xl bg-orange-50/70 border border-orange-200/70 text-[11px] text-slate-700 flex items-start space-x-2">
                  <ShieldCheck className="w-4 h-4 text-orange-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-orange-900">Official Portal Sender Credentials: </span>
                    <span>Verification OTP dispatched from </span>
                    <strong className="text-slate-900">alikhanwebdeveloper@gmail.com</strong>
                    <span> / WhatsApp </span>
                    <strong className="text-slate-900">+923215423874</strong>.
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
                      <span>Sending 6-Digit Code...</span>
                    </>
                  ) : (
                    <>
                      <span>Send 6-Digit Verification Code</span>
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
