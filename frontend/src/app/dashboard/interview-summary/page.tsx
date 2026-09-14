'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useSearchParams, useRouter } from 'next/navigation';
import { CheckCircle2, ArrowRight, BrainCircuit, Code2, Map, AlertCircle, Loader2 } from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { interviewService, InterviewSummary } from '@/services/interviewService';

export default function InterviewSummaryPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const interviewId = searchParams.get('interview_id');

  const [summary, setSummary] = useState<InterviewSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!interviewId) {
      router.replace('/dashboard/history');
      return;
    }
    interviewService
      .get(interviewId)
      .then(async (interview) => {
        const s = await interviewService.complete(interview.id);
        setSummary(s);
      })
      .catch(() => setError('Could not load the interview results. Make sure the interview is completed.'))
      .finally(() => setIsLoading(false));
  }, [interviewId, router]);

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-screen space-y-3">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <p className="text-sm text-slate-500">Loading your interview results...</p>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="flex-1 space-y-6">
        <DashboardHeader title="Interview Summary" />
        <main className="p-6 max-w-3xl mx-auto">
          <Card className="p-8 text-center space-y-3">
            <AlertCircle className="w-8 h-8 text-amber-500 mx-auto" />
            <p className="text-sm text-slate-600">{error || 'No results available yet.'}</p>
            <Link href="/dashboard/history">
              <Button variant="outline" size="sm">Back to History</Button>
            </Link>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-6">
      <DashboardHeader
        title="Interview Completed!"
        subtitle="Your adaptive AI session has been evaluated. Every score below comes from your actual answers."
      />

      <main className="p-6 max-w-4xl mx-auto space-y-8">
        <Card className="p-8 text-center space-y-6">
          <div className="w-20 h-20 rounded-3xl bg-emerald-50 border border-emerald-200 flex items-center justify-center mx-auto text-emerald-600">
            <CheckCircle2 className="w-10 h-10" />
          </div>

          <div className="space-y-2">
            <Badge variant="success" className="mb-2 font-mono">SESSION COMPLETE</Badge>
            <h2 className="text-2xl font-extrabold text-slate-900">Average Score: {Math.round(summary.average_score)}/100</h2>
          </div>

          <div className="grid grid-cols-1 gap-4 text-left">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Overall Performance</h4>
              <p className="text-sm text-slate-700">{summary.overall_performance}</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Technical Performance</h4>
              <p className="text-sm text-slate-700">{summary.technical_performance}</p>
            </div>

            {summary.strong_topics.length > 0 && (
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
                <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-700 mb-2">Strong Topics</h4>
                <div className="flex flex-wrap gap-2">
                  {summary.strong_topics.map((t, i) => (
                    <Badge key={i} variant="success">{t}</Badge>
                  ))}
                </div>
              </div>
            )}

            {summary.weak_topics.length > 0 && (
              <div className="p-4 rounded-xl bg-amber-50 border border-amber-200">
                <h4 className="text-xs font-bold uppercase tracking-wider text-amber-700 mb-2">Weak Topics</h4>
                <div className="flex flex-wrap gap-2">
                  {summary.weak_topics.map((t, i) => (
                    <Badge key={i} variant="warning">{t}</Badge>
                  ))}
                </div>
              </div>
            )}

            {summary.knowledge_gaps && summary.knowledge_gaps.length > 0 && (
              <div className="p-4 rounded-xl bg-red-50 border border-red-200">
                <h4 className="text-xs font-bold uppercase tracking-wider text-red-700 mb-2">Knowledge Gaps</h4>
                <ul className="list-disc list-inside text-sm text-red-800 space-y-1">
                  {summary.knowledge_gaps.map((g, i) => <li key={i}>{g}</li>)}
                </ul>
              </div>
            )}

            {summary.improvement_suggestions.length > 0 && (
              <div className="p-4 rounded-xl bg-blue-50 border border-blue-200">
                <h4 className="text-xs font-bold uppercase tracking-wider text-blue-700 mb-2">Improvement Suggestions</h4>
                <ul className="list-disc list-inside text-sm text-blue-900 space-y-1">
                  {summary.improvement_suggestions.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href={`/dashboard/ai-feedback?interview_id=${interviewId}`}>
              <Button variant="primary" size="lg" className="gap-2">
                <BrainCircuit className="w-4 h-4" /> View Final Report
              </Button>
            </Link>
            <Link href={`/dashboard/coding-interview?interview_id=${interviewId}`}>
              <Button variant="outline" size="lg" className="gap-2">
                <Code2 className="w-4 h-4 text-blue-600" /> Take Coding Test
              </Button>
            </Link>
            <Link href={`/dashboard/roadmap?interview_id=${interviewId}`}>
              <Button variant="secondary" size="lg" className="gap-2">
                <Map className="w-4 h-4" /> 15-Day Roadmap
              </Button>
            </Link>
          </div>
        </Card>
      </main>
    </div>
  );
}
