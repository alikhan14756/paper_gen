import type { Metadata } from "next";
import { Suspense } from "react";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

export const metadata: Metadata = {
  title: "ExamForge AI — KPK Peshawar Board Examination Paper Generator",
  description: "Claymorphic Examination Paper Generator supporting KPK Peshawar Board (BISEP), Federal, and Punjab boards with bilingual Urdu/English capability. Designed and developed by Muhammad Ali (alibuild.site).",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen flex flex-col antialiased selection:bg-orange-500 selection:text-white" suppressHydrationWarning>
        <AuthProvider>
          <Suspense fallback={<div className="h-20" />}>
            <Navbar />
          </Suspense>
          <main className="flex-1 pb-12">{children}</main>
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}
