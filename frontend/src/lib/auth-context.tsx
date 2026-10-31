"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User, ApiClient } from "./api";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  logout: () => void;
  switchRole: (role: "teacher" | "school_admin" | "super_admin") => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const DEMO_CREDENTIALS = {
  teacher: { email: "teacher@lgs.edu.pk", password: "Teacher@1234", label: "Teacher (Prof. Fatima)" },
  school_admin: { email: "admin@lgs.edu.pk", password: "Admin@1234", label: "School Admin (Principal Ahmad)" },
  super_admin: { email: "superadmin@examforge.ai", password: "Admin@1234", label: "Platform Super Admin" },
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("examforge_token");
    if (!token) {
      setLoading(false);
      return;
    }

    ApiClient.getMe()
      .then((userData) => {
        setUser(userData);
      })
      .catch(() => {
        localStorage.removeItem("examforge_token");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const autoLoginDefault = async () => {
    try {
      const res = await ApiClient.login(DEMO_CREDENTIALS.teacher.email, DEMO_CREDENTIALS.teacher.password);
      localStorage.setItem("examforge_token", res.access_token);
      setUser(res.user);
    } catch {
      // Backend might be offline during initial render
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, pass: string) => {
    setLoading(true);
    try {
      const res = await ApiClient.login(email, pass);
      localStorage.setItem("examforge_token", res.access_token);
      setUser(res.user);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("examforge_token");
    setUser(null);
  };

  const switchRole = async (role: "teacher" | "school_admin" | "super_admin") => {
    const creds = DEMO_CREDENTIALS[role];
    await login(creds.email, creds.password);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, switchRole }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
