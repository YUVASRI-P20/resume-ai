import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "InterviewIQ AI | Your Personal AI Technical Interview Coach",
  description:
    "InterviewIQ AI conducts adaptive technical interviews, generates intelligent follow-up questions, identifies knowledge gaps, detects incorrect technical explanations, and provides personalized learning roadmaps.",
  keywords: [
    "AI Interview",
    "Technical Interview Prep",
    "Coding Interview",
    "System Design",
    "Knowledge Graph",
    "Learning Roadmap",
    "Mock Interview",
    "Hallucination Detection",
  ],
  authors: [{ name: "InterviewIQ AI Team" }],
  viewport: "width=device-width, initial-scale=1",
  openGraph: {
    title: "InterviewIQ AI — Adaptive AI Technical Interview Coach",
    description:
      "Master your technical interviews with AI-driven adaptive mock interviews, hallucination detection, real-time code editor, and personalized roadmaps.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} dark scroll-smooth`}>
      <body className="bg-slate-900 text-slate-50 antialiased min-h-screen flex flex-col font-sans selection:bg-blue-600 selection:text-white">
        {children}
      </body>
    </html>
  );
}
