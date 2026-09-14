'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  ArrowRight,
  Brain,
  ShieldAlert,
  Code2,
  GitBranch,
  Target,
  CheckCircle2,
  ChevronDown,
  Play,
  Cpu,
  Star,
  Layers,
  Zap,
} from 'lucide-react';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export default function LandingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  const features = [
    {
      icon: Brain,
      title: 'Adaptive AI Technical Interview',
      description: 'Generates intelligent follow-up questions in real-time based on your exact answers, testing depth of knowledge rather than static trivia.',
      badge: 'Core Engine',
    },
    {
      icon: ShieldAlert,
      title: 'Technical Hallucination Detection',
      description: 'Catches incorrect technical explanations or exaggerated claims immediately and provides accurate, production-grade corrections.',
      badge: 'Patent Pending',
    },
    {
      icon: Code2,
      title: 'Monaco Live Coding Simulator',
      description: 'Execute algorithms with real-time test cases, complexity analysis, and line-by-line AI critique right inside the browser.',
      badge: 'Real-time',
    },
    {
      icon: GitBranch,
      title: 'Interactive Knowledge Graph',
      description: 'Visualizes your technical mastery across React internals, System Design, SQL, and Web Security with dynamic topic node clustering.',
      badge: 'Visual AI',
    },
    {
      icon: Target,
      title: 'Personalized Study Roadmap',
      description: 'Auto-generates weekly study plans and daily micro-tasks targeted specifically at fixing your detected technical knowledge gaps.',
      badge: 'Personalized',
    },
    {
      icon: Layers,
      title: 'Resume Claim Verification',
      description: 'Scans your uploaded resume and crafts targeted deep-dive questions to verify every listed project claim and tech stack competency.',
      badge: 'Resume AI',
    },
  ];

  const steps = [
    { step: '01', title: 'Upload Resume & Stack', desc: 'Sync your target role (Frontend, Backend, System Design) and company focus.' },
    { step: '02', title: 'Conduct Adaptive Interview', desc: 'Engage with AI voice and live coding prompts that adjust difficulty dynamically.' },
    { step: '03', title: 'Receive Deep Feedback', desc: 'Inspect technical score breakdown, radar metrics, and detected hallucinations.' },
    { step: '04', title: 'Master Your Roadmap', desc: 'Follow structured daily tasks to patch knowledge gaps and secure your dream offer.' },
  ];

  const stats = [
    { value: '94.8%', label: 'Offer Conversion Rate' },
    { value: '50,000+', label: 'Adaptive Mock Interviews' },
    { value: '< 150ms', label: 'AI Voice Response Latency' },
    { value: '100%', label: 'API Ready for FastAPI' },
  ];

  const testimonials = [
    {
      name: 'Elena Rostova',
      role: 'Staff Frontend Engineer at Vercel',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250',
      text: 'InterviewIQ caught a subtle hallucination I had about React 18 automatic batching in async callbacks. The AI follow-ups pushed me harder than my actual Vercel interview!',
    },
    {
      name: 'David Kim',
      role: 'Backend Architect at Stripe',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=250',
      text: 'The Knowledge Graph pinpointed my exact weak spots in distributed Redis locks. Following the generated weekly roadmap got me from rejection to a L6 offer.',
    },
    {
      name: 'Sophia Patel',
      role: 'Fullstack Lead at OpenAI',
      avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=250',
      text: 'The Monaco editor integration combined with live voice critique is game-changing. It feels like pair programming with a Principal Staff Engineer.',
    },
  ];

  const faqs = [
    {
      q: 'How does InterviewIQ AI differ from static question platforms?',
      a: 'Static platforms give rigid generic questions. InterviewIQ AI listens to your answer, evaluates your technical precision, detects hallucinations, and asks dynamic follow-up questions tailored to your exact responses.',
    },
    {
      q: 'Can I practice coding interviews in real-time?',
      a: 'Yes! Our built-in Monaco Code Simulator provides syntax highlighting, custom test case runners, time complexity checks, and immediate AI code review.',
    },
    {
      q: 'How does Knowledge Gap Detection work?',
      a: 'Every mock interview question performance is converted into data points that map onto a 3D Knowledge Graph. Topics marked red/yellow automatically feed into your custom weekly study plan.',
    },
    {
      q: 'Is the frontend ready for backend integration?',
      a: '100%. Built with Next.js 15, TypeScript, Axios client services, and structured REST data contracts ready to plug into any FastAPI backend URL.',
    },
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans selection:bg-blue-600">
      <Navbar />

      {/* Hero Section */}
      <section className="relative pt-24 pb-20 overflow-hidden bg-grid-pattern">
        {/* Glowing Radial Background Gradients */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-600/15 rounded-full blur-[140px] pointer-events-none" />
        <div className="absolute top-1/3 right-10 w-[450px] h-[450px] bg-purple-600/15 rounded-full blur-[140px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-8 animate-fade-in">
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>Next-Gen Technical Interview Intelligence</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white max-w-5xl mx-auto leading-[1.1] mb-6">
            Your Personal <span className="gradient-text">AI Technical Interview</span> Coach
          </h1>

          <p className="text-lg sm:text-xl text-slate-300 max-w-3xl mx-auto mb-10 leading-relaxed font-normal">
            Adaptive mock interviews that generate intelligent follow-ups, detect technical hallucinations, map your knowledge gaps, and guarantee technical interview readiness.
          </p>

          {/* CTA Group */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <Link href="/dashboard/interview-setup">
              <Button variant="glow" size="lg" className="w-full sm:w-auto gap-2 text-base px-8">
                <span>Start Mock Interview Free</span>
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
            <Link href="/dashboard/coding-interview">
              <Button variant="outline" size="lg" className="w-full sm:w-auto gap-2 text-base px-8">
                <Play className="w-4 h-4 text-blue-400 fill-blue-400" />
                <span>Try Live Code Simulator</span>
              </Button>
            </Link>
          </div>

          {/* Interactive Graphic Illustration Card */}
          <div className="max-w-5xl mx-auto rounded-2xl glass-panel p-4 sm:p-6 border border-slate-700/80 shadow-2xl relative group overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-700/80 pb-4 mb-4 text-xs font-mono text-slate-400">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-red-500/80 inline-block" />
                <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block" />
                <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block" />
                <span className="ml-2 text-slate-300 font-bold">InterviewIQ AI Engine v2.4</span>
              </div>
              <div className="flex items-center space-x-3 text-blue-400">
                <Zap className="w-3.5 h-3.5 animate-pulse" /> 140ms Voice Latency
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
              {/* Question Card */}
              <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-700/80 space-y-2">
                <span className="text-[10px] font-mono text-purple-400 uppercase tracking-wider block">AI Interviewer Prompt</span>
                <p className="text-xs text-slate-200 font-medium">
                  &quot;You mentioned using React Fiber for concurrency. How does Fiber prioritize user input over background data fetches during rendering?&quot;
                </p>
              </div>

              {/* Candidate Answer */}
              <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-700/80 space-y-2">
                <span className="text-[10px] font-mono text-blue-400 uppercase tracking-wider block">Candidate Response (Live Audio)</span>
                <p className="text-xs text-slate-300 italic">
                  &quot;React assigns priority levels. User input uses DiscretePriority while background fetches use NormalPriority, breaking work into time slices.&quot;
                </p>
              </div>

              {/* AI Verification */}
              <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/30 space-y-2">
                <span className="text-[10px] font-mono text-emerald-400 uppercase tracking-wider block flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Hallucination Check Passed
                </span>
                <p className="text-xs text-emerald-200">
                  Precision Score: <span className="font-bold font-mono text-white">96/100</span>. Verified concepts: Time Slicing & Fiber Priority Lanes.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Counter */}
      <section className="border-y border-slate-800 bg-slate-950/60 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {stats.map((item, idx) => (
            <div key={idx} className="space-y-1">
              <div className="text-3xl sm:text-4xl font-extrabold text-white font-mono">{item.value}</div>
              <div className="text-xs sm:text-sm text-slate-400 font-medium">{item.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <Badge variant="primary" className="mb-4">ENGINEERED FOR EXCELLENCE</Badge>
          <h2 className="text-3xl sm:text-5xl font-bold text-white tracking-tight mb-4">
            Solving the Flaws of Static Interview Prep
          </h2>
          <p className="text-slate-400 text-base sm:text-lg">
            Say goodbye to memorizing static answers. Master adaptive problem solving designed by Staff Engineers.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <Card key={idx} className="glass-panel-hover flex flex-col justify-between p-8">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="w-12 h-12 rounded-2xl bg-blue-600/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
                      <Icon className="w-6 h-6" />
                    </div>
                    <Badge variant="secondary">{feat.badge}</Badge>
                  </div>
                  <h3 className="text-xl font-bold text-white tracking-tight">{feat.title}</h3>
                  <p className="text-slate-400 text-sm leading-relaxed">{feat.description}</p>
                </div>
                <div className="pt-6 mt-6 border-t border-slate-800 text-xs font-semibold text-blue-400 flex items-center gap-1 group-hover:gap-2 transition-all">
                  <span>Learn workflow</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </Card>
            );
          })}
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 border-t border-slate-800 bg-slate-950/40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <Badge variant="secondary" className="mb-4">4-STEP WORKFLOW</Badge>
            <h2 className="text-3xl sm:text-5xl font-bold text-white tracking-tight mb-4">
              How InterviewIQ Works
            </h2>
            <p className="text-slate-400 text-base sm:text-lg">
              From resume scanning to offer acceptance in four seamless AI steps.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {steps.map((item, idx) => (
              <div key={idx} className="p-6 rounded-2xl bg-slate-900 border border-slate-800 relative space-y-3">
                <span className="text-3xl font-extrabold font-mono text-blue-500/40 block">{item.step}</span>
                <h4 className="text-lg font-bold text-white">{item.title}</h4>
                <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <Badge variant="success" className="mb-4 font-mono">PROVEN SUCCESS</Badge>
          <h2 className="text-3xl sm:text-5xl font-bold text-white tracking-tight mb-4">
            Trusted by Top Engineers
          </h2>
          <p className="text-slate-400 text-base">
            Engineers placed at Vercel, OpenAI, Stripe, Linear, Apple, and Notion.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((t, idx) => (
            <Card key={idx} className="p-8 space-y-6">
              <div className="flex items-center space-x-1 text-amber-400">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-amber-400" />
                ))}
              </div>
              <p className="text-sm text-slate-300 leading-relaxed italic">&quot;{t.text}&quot;</p>
              <div className="flex items-center space-x-3 pt-4 border-t border-slate-800">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={t.avatar} alt={t.name} className="w-10 h-10 rounded-full object-cover ring-2 ring-blue-500/30" />
                <div>
                  <h4 className="text-sm font-bold text-white">{t.name}</h4>
                  <p className="text-xs text-slate-400 font-mono">{t.role}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* FAQ Accordion */}
      <section id="faq" className="py-24 border-t border-slate-800 bg-slate-950/40">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">Frequently Asked Questions</h2>
            <p className="text-slate-400 text-sm">Everything you need to know about InterviewIQ AI.</p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, idx) => (
              <div key={idx} className="rounded-2xl bg-slate-900 border border-slate-800 overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                  className="w-full px-6 py-5 flex items-center justify-between text-left font-semibold text-white hover:text-blue-400 transition-colors"
                >
                  <span>{faq.q}</span>
                  <ChevronDown className={`w-5 h-5 transition-transform duration-200 ${openFaq === idx ? 'rotate-180 text-blue-400' : 'text-slate-400'}`} />
                </button>
                {openFaq === idx && (
                  <div className="px-6 pb-6 text-sm text-slate-400 leading-relaxed border-t border-slate-800/60 pt-4">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final Call to Action */}
      <section className="py-24 relative overflow-hidden bg-gradient-to-b from-slate-900 to-slate-950">
        <div className="max-w-5xl mx-auto px-4 text-center relative z-10 space-y-8">
          <div className="w-16 h-16 rounded-3xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center mx-auto text-blue-400">
            <Cpu className="w-8 h-8" />
          </div>
          <h2 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight">
            Ready to Pass Your Technical Interview?
          </h2>
          <p className="text-slate-300 text-lg max-w-2xl mx-auto">
            Join thousands of senior software engineers using InterviewIQ AI to land senior & staff roles at top-tier SaaS companies.
          </p>
          <div className="pt-4">
            <Link href="/register">
              <Button variant="glow" size="lg" className="px-10 text-lg">
                Create Free Account Now
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
