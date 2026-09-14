'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  Flame,
  Award,
  Video,
  FileUp,
  Code2,
  Map,
  ArrowRight,
  Clock,
  TrendingUp,
  FileText,
} from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { careerService, DashboardData } from '@/services/careerService';

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    careerService
      .getDashboard()
      .then(setData)
      .catch(() => setError('Could not load your dashboard. Is the backend running?'))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-screen">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-100 border-t-blue-600" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex-1 space-y-6">
        <DashboardHeader title="Overview" />
        <main className="p-6 max-w-5xl mx-auto">
          <Card className="p-8 text-center space-y-2">
            <p className="text-sm text-slate-600">{error}</p>
          </Card>
        </main>
      </div>
    );
  }

  const hasResume = Boolean(data.resume);
  const hasInterviews = data.interview_progress.total > 0;

  return (
    <div className="flex-1 space-y-6">
      <DashboardHeader
        title={`Welcome back, ${data.user_name.split(' ')[0]}!`}
        subtitle="Your real interview prep progress — every number comes from your activity."
      />

      <main className="p-6 space-y-8 max-w-7xl mx-auto">
        {/* Top: readiness summary + streak */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2 p-8 flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="primary" className="gap-1">
                  <Sparkles className="w-3.5 h-3.5" /> AI Coach Ready
                </Badge>
                {data.selected_company && (
                  <Badge variant="outline" className="font-mono">
                    Targeting: {data.selected_company} — {data.selected_role}
                  </Badge>
                )}
              </div>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                {hasResume
                  ? hasInterviews
                    ? 'Keep the momentum going'
                    : 'Run your first personalized interview'
                  : 'Start by uploading your resume'}
              </h2>
              <p className="text-slate-500 text-sm max-w-xl leading-relaxed">
                {hasResume
                  ? 'Your resume is parsed. Match it against a real job role, run an AI interview grounded in your skills, then follow your improvement roadmap.'
                  : 'InterviewIQ builds everything from your actual resume — skills extraction, job matching, personalized interviews and your improvement roadmap.'}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-4">
              {hasResume ? (
                <Link href="/dashboard/interview-setup">
                  <Button variant="primary" size="md" className="gap-2">
                    <Video className="w-4 h-4" /> Start AI Interview
                  </Button>
                </Link>
              ) : (
                <Link href="/dashboard/resume-upload">
                  <Button variant="primary" size="md" className="gap-2">
                    <FileUp className="w-4 h-4" /> Upload Resume
                  </Button>
                </Link>
              )}
              <Link href="/dashboard/resume-upload">
                <Button variant="outline" size="md" className="gap-2">
                  <FileText className="w-4 h-4 text-blue-600" /> Manage Resumes
                </Button>
              </Link>
            </div>
          </Card>

          {/* Real stats */}
          <Card className="flex flex-col justify-center p-6 space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 font-mono">
              Your Progress
            </span>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-xs text-slate-500 flex items-center gap-1.5">
                  <Flame className="w-3.5 h-3.5 text-amber-500" /> Study streak
                </span>
                <span className="font-bold text-slate-900 font-mono">{data.streak.streak_days} days</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-xs text-slate-500 flex items-center gap-1.5">
                  <Award className="w-3.5 h-3.5 text-blue-600" /> Interviews completed
                </span>
                <span className="font-bold text-slate-900 font-mono">{data.interview_progress.completed}</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-xs text-slate-500 flex items-center gap-1.5">
                  <TrendingUp className="w-3.5 h-3.5 text-emerald-600" /> Last score
                </span>
                <span className="font-bold text-slate-900 font-mono">
                  {data.interview_progress.last_score !== null ? `${Math.round(data.interview_progress.last_score)}/100` : '—'}
                </span>
              </div>
              {data.match_percentage !== null && (
                <div className="p-3 rounded-xl bg-blue-50 border border-blue-200">
                  <span className="text-[10px] text-blue-700 block mb-1">Job fit: {data.selected_role}</span>
                  <ProgressBar progress={data.match_percentage} color="blue" showPercentage={false} />
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Quick actions */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { href: '/dashboard/resume-upload', icon: FileUp, title: 'Resume Parser', desc: 'Real skill extraction', accent: 'text-blue-600' },
            { href: '/dashboard/coding-interview', icon: Code2, title: 'Coding Test', desc: 'Real test-case execution', accent: 'text-indigo-600' },
            { href: '/dashboard/knowledge-graph', icon: Sparkles, title: 'Knowledge Graph', desc: 'From your results', accent: 'text-emerald-600' },
            { href: '/dashboard/roadmap', icon: Map, title: '15-Day Roadmap', desc: 'Personalized plan', accent: 'text-amber-600' },
          ].map((item) => (
            <Link key={item.href} href={item.href}>
              <Card className="p-4 flex items-center space-x-3 cursor-pointer">
                <div className="w-10 h-10 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-center">
                  <item.icon className={`w-5 h-5 ${item.accent}`} />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-slate-900">{item.title}</h4>
                  <p className="text-[11px] text-slate-500">{item.desc}</p>
                </div>
              </Card>
            </Link>
          ))}
        </div>

        {/* Bottom: knowledge gaps + resume status */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-600" /> Recent Knowledge Gaps
            </h3>
            {data.knowledge_gaps.length === 0 ? (
              <Card className="p-6 text-center text-sm text-slate-500">
                No knowledge gaps recorded yet — complete an interview to identify them.
              </Card>
            ) : (
              <div className="space-y-2">
                {data.knowledge_gaps.slice(0, 5).map((g, i) => (
                  <Card key={i} className="p-4">
                    <span className="text-sm font-bold text-slate-900">{g.topic}</span>
                    <p className="text-xs text-slate-500">{g.description}</p>
                  </Card>
                ))}
              </div>
            )}
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" /> Resume Status
            </h3>
            {data.resume ? (
              <Card className="p-5 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold text-slate-900">{data.resume.original_filename}</span>
                  <Badge variant={data.resume.status === 'parsed' ? 'success' : 'warning'}>{data.resume.status}</Badge>
                </div>
                <p className="text-xs text-slate-500">
                  Uploaded {new Date(data.resume.uploaded_at).toLocaleDateString()}
                </p>
                <Link href="/dashboard/resume-analysis">
                  <Button variant="outline" size="sm" className="gap-1.5 text-xs mt-2">
                    View Analysis <ArrowRight className="w-3.5 h-3.5" />
                  </Button>
                </Link>
              </Card>
            ) : (
              <Card className="p-6 text-center text-sm text-slate-500">
                No resume uploaded yet.
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
