'use client';

import React, { Suspense, useEffect, useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
  BrainCircuit,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  ArrowRight,
  Loader2,
  FileCheck,
} from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { feedbackService, FeedbackReport } from '@/services/feedbackService';

function ReportContent() {
  const searchParams = useSearchParams();
  const interviewId = searchParams.get('interview_id');

  const [report, setReport] = useState<FeedbackReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!interviewId) {
      setError('Open a completed interview from your history to see its report.');
      setIsLoading(false);
      return;
    }
    feedbackService
      .getReport(interviewId)
      .then(setReport)
      .catch(() => setError('Could not load the report. Complete the interview first.'))
      .finally(() => setIsLoading(false));
  }, [interviewId]);

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-screen space-y-3">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <p className="text-sm text-slate-500">Generating your final report...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <main className="p-6 max-w-3xl mx-auto">
        <Card className="p-8 text-center space-y-3">
          <AlertTriangle className="w-8 h-8 text-amber-500 mx-auto" />
          <p className="text-sm text-slate-600">{error}</p>
          <Link href="/dashboard/history">
            <Button variant="outline" size="sm">Go to History</Button>
          </Link>
        </Card>
      </main>
    );
  }

  const scoreCards = [
    { label: 'Overall Score', value: report.overall_score, color: 'text-blue-700' },
    { label: 'Technical Depth', value: report.technical_score, color: 'text-indigo-700' },
    { label: 'Communication', value: report.communication_score, color: 'text-emerald-700' },
    { label: 'Coding Score', value: report.coding_score, color: 'text-amber-700' },
  ];

  return (
    <main className="p-6 max-w-6xl mx-auto space-y-8">
      {/* Score Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {scoreCards.map((c) => (
          <Card key={c.label} className="p-4 space-y-1">
            <span className="text-[10px] text-slate-500 uppercase font-mono block">{c.label}</span>
            <div className={`text-3xl font-extrabold ${c.color} font-mono`}>{Math.round(c.value)}%</div>
          </Card>
        ))}
      </div>

      {/* Summaries */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6 space-y-2">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <FileCheck className="w-5 h-5 text-blue-600" /> Interview Summary
          </h3>
          <p className="text-sm text-slate-600">{report.interview_summary}</p>
        </Card>
        <Card className="p-6 space-y-2">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <BrainCircuit className="w-5 h-5 text-indigo-600" /> Detailed Feedback
          </h3>
          <p className="text-sm text-slate-600 whitespace-pre-wrap">{report.detailed_feedback}</p>
        </Card>
      </div>

      {/* Categories */}
      {report.categories.length > 0 && (
        <Card className="p-6 space-y-4">
          <h3 className="text-base font-bold text-slate-900">Score Breakdown</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {report.categories.map((c) => (
              <div key={c.id} className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold text-slate-800">{c.category_name}</span>
                  <span className="text-sm font-mono font-bold text-blue-700">{Math.round(c.score)}</span>
                </div>
                <p className="text-xs text-slate-500">{c.comments}</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Strengths */}
        <Card className="p-6 space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" /> Strong Areas
          </h3>
          {report.strengths.length === 0 ? (
            <p className="text-xs text-slate-400 italic">No strengths recorded yet.</p>
          ) : (
            <ul className="space-y-2">
              {report.strengths.map((s) => (
                <li key={s.id} className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900">
                  <strong className="block">{s.title}</strong>
                  <span className="text-emerald-700">{s.description}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        {/* Weaknesses */}
        <Card className="p-6 space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-500" /> Weak Areas
          </h3>
          {report.weaknesses.length === 0 ? (
            <p className="text-xs text-slate-400 italic">No weaknesses recorded yet.</p>
          ) : (
            <ul className="space-y-2">
              {report.weaknesses.map((w) => (
                <li key={w.id} className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900">
                  <strong className="block">{w.title}</strong>
                  <span className="text-amber-700">{w.description}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hallucinations */}
        <Card className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-red-500" /> Hallucination Audit
            </h3>
            <Badge variant={report.hallucinations.length > 0 ? 'error' : 'success'}>
              {report.hallucinations.length} detected
            </Badge>
          </div>
          {report.hallucinations.length === 0 ? (
            <p className="text-xs text-slate-400 italic">
              No technical inaccuracies were detected in your answers.
            </p>
          ) : (
            <div className="space-y-3">
              {report.hallucinations.map((h) => (
                <div key={h.id} className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-red-600 font-bold uppercase">{h.concept}</span>
                    <Badge variant="error">{h.severity}</Badge>
                  </div>
                  <p className="text-xs text-slate-600 italic">&quot;{h.candidate_claim}&quot;</p>
                  <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-xs text-red-800">
                    <strong className="block font-mono text-[10px] text-red-600 mb-1">Correct explanation:</strong>
                    {h.correct_explanation}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* CTA to roadmap */}
        <Card className="p-6 flex flex-col justify-between space-y-4">
          <div className="space-y-1">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-amber-500" /> What&apos;s next?
            </h3>
            <p className="text-sm text-slate-600">
              Turn these results into a personalized 15-day improvement plan targeting your weakest
              topics and missing job requirements.
            </p>
          </div>
          <Link href={`/dashboard/roadmap?interview_id=${report.interview_id}`} className="self-start">
            <Button variant="primary" size="md" className="gap-2">
              <span>Generate 15-Day Roadmap</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </Card>
      </div>
    </main>
  );
}

export default function AIFeedbackPage() {
  return (
    <div className="flex-1 space-y-6">
      <DashboardHeader
        title="Final Interview Report"
        subtitle="Performance analysis derived from your actual interview answers and coding submissions."
      />
      <Suspense
        fallback={
          <div className="flex-1 flex items-center justify-center min-h-[50vh]">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        }
      >
        <ReportContent />
      </Suspense>
    </div>
  );
}
