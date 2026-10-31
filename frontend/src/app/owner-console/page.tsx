"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ApiClient } from "@/lib/api";
import { 
  ShieldCheck, 
  Smartphone, 
  Mail, 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  Search, 
  RefreshCw, 
  Lock, 
  Building2, 
  ArrowLeft,
  UserCheck,
  Send,
  SlidersHorizontal,
  KeyRound
} from "lucide-react";

interface VerificationItem {
  id: string;
  identifier: string;
  school_name: string | null;
  principal_name: string | null;
  delivery_channel: string;
  status: string;
  attempts: number;
  created_at: string;
  expires_at: string;
  is_locked: boolean;
}

export default function OwnerConsolePage() {
  const [items, setItems] = useState<VerificationItem[]>([]);
  const [metrics, setMetrics] = useState({
    total_schools: 0,
    verified_schools: 0,
    pending_verifications: 0,
    locked_accounts: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Filters
  const [channelFilter, setChannelFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Owner Quick Auth
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [ownerPassword, setOwnerPassword] = useState("");
  const [authError, setAuthError] = useState<string | null>(null);

  useEffect(() => {
    checkOwnerAuth();
  }, []);

  const checkOwnerAuth = async () => {
    try {
      const user = await ApiClient.getMe();
      if (user.role === "super_owner" || user.role === "super_admin") {
        setIsAuthenticated(true);
        fetchVerifications();
      } else {
        setIsAuthenticated(false);
        setLoading(false);
      }
    } catch {
      setIsAuthenticated(false);
      setLoading(false);
    }
  };

  const handleOwnerLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    try {
      const res = await ApiClient.login("alikhanwebdeveloper@gmail.com", ownerPassword);
      localStorage.setItem("examforge_token", res.access_token);
      setIsAuthenticated(true);
      fetchVerifications();
    } catch (err: any) {
      setAuthError(err.message || "Invalid owner credentials. Please try again.");
    }
  };

  const fetchVerifications = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await ApiClient.getOwnerVerifications({
        channel: channelFilter,
        status: statusFilter,
        query: searchQuery,
      });
      setItems(data.items);
      setMetrics({
        total_schools: data.total_schools,
        verified_schools: data.verified_schools,
        pending_verifications: data.pending_verifications,
        locked_accounts: data.locked_accounts,
      });
    } catch (err: any) {
      setError(err.message || "Failed to load verification logs.");
    } finally {
      setLoading(false);
    }
  };

  const handleManualVerify = async (otpId: string, targetName: string) => {
    if (!confirm(`Are you sure you want to manually approve and verify ${targetName}?`)) return;
    try {
      await ApiClient.ownerManualVerify(otpId);
      setActionSuccess(`Successfully verified: ${targetName}`);
      fetchVerifications();
      setTimeout(() => setActionSuccess(null), 4000);
    } catch (err: any) {
      alert(`Manual verification failed: ${err.message}`);
    }
  };

  const handleResendOTP = async (otpId: string, identifier: string) => {
    try {
      const res = await ApiClient.ownerResendOTP(otpId);
      setActionSuccess(res.message || `OTP re-dispatched to ${identifier}`);
      fetchVerifications();
      setTimeout(() => setActionSuccess(null), 4000);
    } catch (err: any) {
      alert(`Failed to resend OTP: ${err.message}`);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <div className="flex items-center space-x-2.5 mb-1">
            <Link href="/" className="text-slate-400 hover:text-slate-600">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <span className="clay-badge-orange text-xs font-black px-3 py-1 rounded-full flex items-center space-x-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-orange-600" />
              <span>Owner & Site Coder Portal</span>
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            OTP Verifications & School Approvals Console
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time monitoring of all registration OTPs, WhatsApp/Email deliveries, and manual approval triggers.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="text-right text-xs hidden sm:block">
            <p className="font-extrabold text-slate-900">Muhammad Ali (AliBuild)</p>
            <p className="text-slate-500">+923215423874 &bull; alikhanwebdeveloper@gmail.com</p>
          </div>
          <button
            onClick={fetchVerifications}
            className="clay-btn-secondary p-2.5 rounded-xl text-slate-700 hover:text-slate-900"
            title="Refresh Logs"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {!isAuthenticated ? (
        /* OWNER LOGIN GUARD */
        <div className="max-w-md mx-auto clay-card p-8 space-y-6">
          <div className="text-center space-y-2">
            <div className="w-12 h-12 rounded-2xl bg-orange-500 text-white flex items-center justify-center mx-auto shadow-md">
              <Lock className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-black text-slate-900">Owner Access Required</h3>
            <p className="text-xs text-slate-500">
              Authenticate as Site Architect & Owner (alikhanwebdeveloper@gmail.com) to access telecommunication verification controls.
            </p>
          </div>

          {authError && (
            <div className="p-3 text-xs bg-red-50 border border-red-200 text-red-700 rounded-xl font-medium">
              {authError}
            </div>
          )}

          <form onSubmit={handleOwnerLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Owner Email</label>
              <input
                type="text"
                disabled
                value="alikhanwebdeveloper@gmail.com"
                className="w-full clay-input p-2.5 text-xs font-bold text-slate-500 bg-slate-100"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Owner Security Password</label>
              <input
                type="password"
                required
                value={ownerPassword}
                onChange={(e) => setOwnerPassword(e.target.value)}
                placeholder="Enter password (e.g. OwnerPass2026!)"
                className="w-full clay-input p-2.5 text-xs font-semibold text-slate-800"
              />
            </div>

            <button
              type="submit"
              className="w-full clay-btn-primary py-3 text-xs font-bold flex items-center justify-center space-x-2"
            >
              <KeyRound className="w-4 h-4" />
              <span>Unlock Owner Console</span>
            </button>
          </form>
        </div>
      ) : (
        /* AUTHENTICATED OWNER DASHBOARD */
        <>
          {actionSuccess && (
            <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold flex items-center space-x-2 animate-in fade-in">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{actionSuccess}</span>
            </div>
          )}

          {/* Metric Cards Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="clay-card p-5 space-y-1">
              <p className="text-xs font-bold text-slate-500">Total Schools</p>
              <h3 className="text-2xl font-black text-slate-900">{metrics.total_schools}</h3>
              <p className="text-[11px] text-slate-400">Registered on portal</p>
            </div>

            <div className="clay-card p-5 space-y-1">
              <p className="text-xs font-bold text-emerald-600">Verified Schools</p>
              <h3 className="text-2xl font-black text-emerald-600">{metrics.verified_schools}</h3>
              <p className="text-[11px] text-slate-400">Active Free Trial accounts</p>
            </div>

            <div className="clay-card p-5 space-y-1">
              <p className="text-xs font-bold text-orange-600">Pending OTPs</p>
              <h3 className="text-2xl font-black text-orange-600">{metrics.pending_verifications}</h3>
              <p className="text-[11px] text-slate-400">Awaiting code entry</p>
            </div>

            <div className="clay-card p-5 space-y-1">
              <p className="text-xs font-bold text-red-600">Locked / Exceeded</p>
              <h3 className="text-2xl font-black text-red-600">{metrics.locked_accounts}</h3>
              <p className="text-[11px] text-slate-400">&ge; 3 failed attempts</p>
            </div>
          </div>

          {/* Filters & Search Toolbar */}
          <div className="clay-card p-4 flex flex-col md:flex-row items-center justify-between gap-3">
            <div className="flex-1 w-full relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && fetchVerifications()}
                placeholder="Search by school, principal name, +92 phone, or email..."
                className="w-full clay-input pl-9 p-2 text-xs font-medium"
              />
            </div>

            <div className="flex items-center space-x-2 w-full md:w-auto">
              <select
                value={channelFilter}
                onChange={(e) => setChannelFilter(e.target.value)}
                className="clay-input p-2 text-xs font-semibold text-slate-700"
              >
                <option value="all">All Channels</option>
                <option value="whatsapp">WhatsApp (+92)</option>
                <option value="email">Email</option>
              </select>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="clay-input p-2 text-xs font-semibold text-slate-700"
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="verified">Verified</option>
                <option value="locked">Locked</option>
                <option value="expired">Expired</option>
              </select>

              <button
                onClick={fetchVerifications}
                className="clay-btn-primary px-4 py-2 text-xs font-bold"
              >
                Filter
              </button>
            </div>
          </div>

          {/* Verification Logs Table */}
          <div className="clay-card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider text-[10px]">
                  <tr>
                    <th className="py-3 px-4">Timestamp</th>
                    <th className="py-3 px-4">School & Principal</th>
                    <th className="py-3 px-4">Destination</th>
                    <th className="py-3 px-4">Channel</th>
                    <th className="py-3 px-4">Attempts</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Admin Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {items.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-slate-400">
                        {loading ? "Loading verification logs..." : "No verification requests found matching your filters."}
                      </td>
                    </tr>
                  ) : (
                    items.map((item) => (
                      <tr key={item.id} className="hover:bg-slate-50/80 transition">
                        <td className="py-3.5 px-4 text-slate-500 whitespace-nowrap">
                          {item.created_at ? new Date(item.created_at).toLocaleString() : "Just now"}
                        </td>
                        <td className="py-3.5 px-4">
                          <p className="font-extrabold text-slate-900">{item.school_name || "Unassigned School"}</p>
                          <p className="text-[11px] text-slate-500">{item.principal_name || "Principal"}</p>
                        </td>
                        <td className="py-3.5 px-4 font-mono text-slate-700 text-[11px]">
                          {item.identifier}
                        </td>
                        <td className="py-3.5 px-4">
                          {item.delivery_channel === "whatsapp" ? (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                              <Smartphone className="w-3 h-3 mr-1 text-emerald-600" />
                              WhatsApp
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800">
                              <Mail className="w-3 h-3 mr-1 text-blue-600" />
                              Email
                            </span>
                          )}
                        </td>
                        <td className="py-3.5 px-4">
                          <span className={`font-bold ${item.attempts >= 3 ? "text-red-600" : "text-slate-600"}`}>
                            {item.attempts} / 3
                          </span>
                        </td>
                        <td className="py-3.5 px-4">
                          {item.status === "verified" ? (
                            <span className="clay-badge-mint text-[10px] font-bold px-2 py-0.5 rounded-full">
                              Verified
                            </span>
                          ) : item.status === "locked" || item.is_locked ? (
                            <span className="bg-red-100 text-red-800 border border-red-200 text-[10px] font-bold px-2 py-0.5 rounded-full">
                              Locked (30m)
                            </span>
                          ) : item.status === "expired" ? (
                            <span className="bg-slate-200 text-slate-700 text-[10px] font-bold px-2 py-0.5 rounded-full">
                              Expired
                            </span>
                          ) : (
                            <span className="clay-badge-orange text-[10px] font-bold px-2 py-0.5 rounded-full">
                              Delivered / Pending
                            </span>
                          )}
                        </td>
                        <td className="py-3.5 px-4 text-right space-x-1.5 whitespace-nowrap">
                          {item.status !== "verified" && (
                            <button
                              onClick={() => handleManualVerify(item.id, item.school_name || item.identifier)}
                              className="px-2.5 py-1 text-[11px] font-bold rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm"
                              title="Manually approve school if SMS/email delivery fails"
                            >
                              Manual Verify
                            </button>
                          )}
                          <button
                            onClick={() => handleResendOTP(item.id, item.identifier)}
                            className="px-2.5 py-1 text-[11px] font-bold rounded-lg bg-slate-200 text-slate-800 hover:bg-slate-300"
                            title="Force re-dispatch fresh OTP code"
                          >
                            Resend Code
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
