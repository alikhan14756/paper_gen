"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { ApiClient } from "@/lib/api";
import { 
  Sparkles, 
  Lock, 
  Mail, 
  ArrowRight, 
  Loader2, 
  GraduationCap,
  KeyRound,
  RefreshCw,
  CheckCircle2
} from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Inline Email Verification State
  const [showVerification, setShowVerification] = useState(false);
  const [verificationCode, setVerificationCode] = useState("");
  const [verifying, setVerifying] = useState(false);
  const [resending, setResending] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Please fill in both email and password.");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMsg(null);
    try {
      await login(email, password);
      router.push("/");
    } catch (err: any) {
      const msg = err.message || "Invalid credentials. Please verify and try again.";
      if (msg.toLowerCase().includes("verified") || msg.toLowerCase().includes("verification code")) {
        setShowVerification(true);
        setError("Account not verified yet. A 6-digit verification code has been dispatched to your email.");
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCodeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!verificationCode.trim()) {
      setError("Please enter the 6-digit verification code sent to your email.");
      return;
    }

    setVerifying(true);
    setError(null);
    try {
      const res = await ApiClient.verifyEmail(email.trim(), verificationCode.trim());
      localStorage.setItem("examforge_token", res.access_token);
      setSuccessMsg("Account verified successfully! Redirecting...");
      setTimeout(() => {
        window.location.href = "/";
      }, 1000);
    } catch (err: any) {
      setError(err.message || "Verification code is incorrect or expired. Check your email.");
    } finally {
      setVerifying(false);
    }
  };

  const handleResendCode = async () => {
    if (!email.trim()) return;
    setResending(true);
    setError(null);
    try {
      await ApiClient.resendVerificationCode(email.trim());
      setSuccessMsg("A fresh 6-digit verification code has been dispatched to your email.");
    } catch (err: any) {
      setError(err.message || "Failed to resend verification code.");
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-md w-full space-y-6 clay-card p-8 sm:p-10">
        <div className="text-center space-y-2">
          <div className="mx-auto h-12 w-12 rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center text-white shadow-md shadow-orange-500/30">
            <Sparkles className="h-6 w-6" />
          </div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">
            Sign in to ExamForge AI
          </h2>
          <div className="inline-flex items-center px-3 py-1 rounded-full text-[11px] font-bold clay-badge-mint">
            <GraduationCap className="w-3.5 h-3.5 mr-1" />
            BISE Peshawar & KPK Schools Portal
          </div>
        </div>

        {error && (
          <div className="p-3.5 text-xs bg-red-50 border border-red-200 text-red-700 rounded-2xl space-y-2 font-medium">
            <div>{error}</div>
          </div>
        )}

        {successMsg && (
          <div className="p-3.5 text-xs bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-2xl flex items-center space-x-2 font-medium">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {showVerification ? (
          /* Inline Email Verification Step */
          <form onSubmit={handleVerifyCodeSubmit} className="space-y-4 pt-2">
            <div className="clay-card-flat p-4 rounded-2xl space-y-2 text-center">
              <Mail className="w-7 h-7 text-orange-600 mx-auto" />
              <p className="text-xs font-bold text-slate-800">
                Email Verification Code Required
              </p>
              <p className="text-[11px] text-slate-600">
                A 6-digit code was sent to <strong className="text-slate-900">{email}</strong>. Check your inbox and enter the code below:
              </p>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5 text-center">
                Enter 6-Digit Code from Email
              </label>
              <div className="relative max-w-xs mx-auto">
                <input
                  type="text"
                  maxLength={6}
                  required
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value.replace(/[^0-9]/g, ""))}
                  placeholder="Enter 6-digit code"
                  className="w-full clay-input text-center text-xl font-mono tracking-widest py-2.5 font-bold"
                  autoFocus
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={verifying || verificationCode.length < 6}
              className="w-full clay-btn-primary py-3 px-4 text-xs font-bold flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {verifying ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Verifying Code...</span>
                </>
              ) : (
                <>
                  <span>Verify Email & Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>

            <div className="flex items-center justify-between text-xs pt-1">
              <button
                type="button"
                onClick={handleResendCode}
                disabled={resending}
                className="inline-flex items-center space-x-1 text-orange-600 font-bold hover:underline disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${resending ? "animate-spin" : ""}`} />
                <span>Resend Code to Email</span>
              </button>

              <button
                type="button"
                onClick={() => { setShowVerification(false); setError(null); }}
                className="text-slate-500 hover:text-slate-900 font-medium"
              >
                Back to Password
              </button>
            </div>
          </form>
        ) : (
          /* Normal Sign In Form */
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Username or Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <KeyRound className="h-4 w-4" />
                </div>
                <input
                  type="text"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="e.g. pms or admin@school.edu.pk"
                  className="w-full clay-input pl-10 pr-3.5 py-2.5 text-xs font-medium"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your secret password"
                  className="w-full clay-input pl-10 pr-3.5 py-2.5 text-xs"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full clay-btn-primary py-3 px-4 text-xs font-bold flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        )}

        <div className="text-center pt-2">
          <p className="text-xs text-slate-500">
            Need to register your school?{" "}
            <Link href="/register" className="font-bold text-orange-600 hover:underline">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
