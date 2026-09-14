'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Search, History, Plus, ArrowRight, Loader2 } from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { interviewService, Interview } from '@/services/interviewService';

const statusVariant = (status: Interview['status']) =>
  status === 'COMPLETED' ? 'success' : status === 'IN_PROGRESS' ? 'primary' : 'outline';

export default function InterviewHistoryPage() {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    interviewService
      .history()
      .then(setInterviews)
      .catch(() => setError('Could not load your interview history.'))
      .finally(() => setIsLoading(false));
  }, []);

  const filtered = interviews.filter(
    (i) =>
      i.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
      i.job_role.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex-1 space-y-6">
      <DashboardHeader
        title="Interview History"
        subtitle="All your AI interview sessions — resume-grounded questions with real evaluations."
      />

      <main className="p-6 max-w-7xl mx-auto space-y-8">
        {/* Search & actions */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-white border border-slate-200">
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by company or role..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full h-10 pl-10 pr-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-500"
            />
          </div>

          <Link href="/dashboard/interview-setup">
            <Button variant="primary" size="sm" className="gap-1 text-xs">
              <Plus className="w-4 h-4" /> Start New Session
            </Button>
          </Link>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : error ? (
          <Card className="p-8 text-center text-sm text-slate-600">{error}</Card>
        ) : filtered.length === 0 ? (
          <Card className="p-10 text-center space-y-3">
            <History className="w-10 h-10 text-slate-300 mx-auto" />
            <p className="text-base font-semibold text-slate-700">No interviews yet</p>
            <p className="text-sm text-slate-500">
              Start your first resume-grounded AI interview to see your history here.
            </p>
            <Link href="/dashboard/interview-setup" className="inline-block pt-1">
              <Button variant="primary" size="md">Start Interview</Button>
            </Link>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((iv) => (
              <Card key={iv.id} className="p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-900">{iv.company}</h3>
                  <Badge variant={statusVariant(iv.status)}>{iv.status.replace('_', ' ')}</Badge>
                </div>
                <p className="text-xs text-slate-500">{iv.job_role} • {iv.domain}</p>
                <div className="flex items-center gap-3 text-[11px] font-mono text-slate-400">
                  <span>{iv.completed_question_count}/{iv.number_of_questions} answered</span>
                  <span>•</span>
                  <span>{iv.difficulty}</span>
                </div>
                <p className="text-[11px] text-slate-400">
                  {new Date(iv.created_at).toLocaleString()}
                </p>
                <div className="flex gap-2 pt-1">
                  {iv.status === 'IN_PROGRESS' ? (
                    <Link href="/dashboard/live-interview" className="flex-1">
                      <Button variant="primary" size="sm" className="w-full text-xs gap-1">
                        Resume <ArrowRight className="w-3.5 h-3.5" />
                      </Button>
                    </Link>
                  ) : (
                    <>
                      <Link href={`/dashboard/ai-feedback?interview_id=${iv.id}`} className="flex-1">
                        <Button variant="outline" size="sm" className="w-full text-xs">Report</Button>
                      </Link>
                      <Link href={`/dashboard/roadmap?interview_id=${iv.id}`} className="flex-1">
                        <Button variant="secondary" size="sm" className="w-full text-xs">Roadmap</Button>
                      </Link>
                    </>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
