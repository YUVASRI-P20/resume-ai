'use client';

import React, { useMemo, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Download, Sparkles, CheckCircle2, XCircle, RotateCcw, Briefcase, BrainCircuit, TrendingUp, FileText, BadgeCheck, ListChecks } from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { getResumeOptimizerData } from '@/services/resumeOptimizerService';
import { ResumeOptimizerSuggestion, ResumeOptimizerSuggestionStatus } from '@/types/resumeOptimizer';

export default function ResumeOptimizerPage() {
  const initialData = useMemo(() => getResumeOptimizerData(), []);
  const [suggestions, setSuggestions] = useState<ResumeOptimizerSuggestion[]>(initialData.suggestions);
  const [acceptedCount, setAcceptedCount] = useState(0);

  const handleSuggestionAction = (id: string, action: ResumeOptimizerSuggestionStatus) => {
    setSuggestions((current) =>
      current.map((suggestion) => {
        if (suggestion.id === id) {
          if (action === 'accepted') {
            setAcceptedCount((count) => count + 1);
          }
          return { ...suggestion, status: action };
        }
        return suggestion;
      })
    );
  };

  const handleAcceptAll = () => {
    setSuggestions((current) => current.map((item) => ({ ...item, status: 'accepted' })));
    setAcceptedCount(3);
  };

  const handleReset = () => {
    setSuggestions(initialData.suggestions);
    setAcceptedCount(0);
  };

  const pendingCount = suggestions.filter((item) => item.status === 'pending').length;
  const accepted = suggestions.filter((item) => item.status === 'accepted').length;
  const rejected = suggestions.filter((item) => item.status === 'rejected').length;

  return (
    <div className="flex-1 space-y-6">
      <DashboardHeader title="AI Resume Optimizer" subtitle="Transform your resume for stronger recruiter and ATS alignment" />

      <main className="p-6 max-w-7xl mx-auto space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <Link href="/dashboard/resume-analysis" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white">
            <ArrowLeft className="w-4 h-4" /> Back to Resume Analysis
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/dashboard/interview-readiness">
              <Button variant="glow" className="gap-2 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 shadow-lg shadow-indigo-500/20">
                🚀 Predict My Interview Readiness
              </Button>
            </Link>
            <Button variant="secondary" className="gap-2">
              <Download className="w-4 h-4" /> Download Optimized Resume
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[1.2fr_0.8fr] gap-6">
          <Card className="p-6 space-y-6">
            <div className="flex items-start justify-between">
              <div>
                <Badge variant="primary" className="mb-2">AI GENERATED OPTIMIZATION</Badge>
                <h2 className="text-xl font-bold text-white">Original vs AI Optimized Resume</h2>
                <p className="text-sm text-slate-400 mt-1">A realistic preview of how your resume can improve for the target role and recruiter screening.</p>
              </div>
              <div className="flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-emerald-300">
                <Sparkles className="w-4 h-4" /> ATS Ready
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-2xl border border-slate-700/70 bg-slate-950/70 p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-white">Original Summary</h3>
                  <Badge variant="outline">Resume Score {initialData.currentResumeScore}</Badge>
                </div>
                <p className="text-sm text-slate-300">{initialData.summary.original}</p>
              </div>
              <div className="rounded-2xl border border-blue-500/20 bg-blue-500/10 p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-white">AI Optimized Summary</h3>
                  <Badge variant="success">Resume Score {initialData.optimizedResumeScore}</Badge>
                </div>
                <p className="text-sm text-slate-200">{initialData.summary.optimized}</p>
              </div>
            </div>

            <div className="grid gap-4 lg:grid-cols-3">
              <Card className="p-4" glass={false}>
                <div className="flex items-center gap-2 text-blue-400">
                  <TrendingUp className="w-4 h-4" />
                  <span className="text-xs font-semibold uppercase tracking-wider">Resume Score Improvement</span>
                </div>
                <div className="mt-3 text-3xl font-bold text-white">+{initialData.optimizedResumeScore - initialData.currentResumeScore}</div>
                <p className="text-sm text-slate-400 mt-1">Stronger impact language and clearer proof points.</p>
              </Card>
              <Card className="p-4" glass={false}>
                <div className="flex items-center gap-2 text-purple-400">
                  <BrainCircuit className="w-4 h-4" />
                  <span className="text-xs font-semibold uppercase tracking-wider">ATS Score Improvement</span>
                </div>
                <div className="mt-3 text-3xl font-bold text-white">+{initialData.optimizedAtsScore - initialData.currentAtsScore}</div>
                <p className="text-sm text-slate-400 mt-1">Better keyword density and section alignment.</p>
              </Card>
              <Card className="p-4" glass={false}>
                <div className="flex items-center gap-2 text-emerald-400">
                  <ListChecks className="w-4 h-4" />
                  <span className="text-xs font-semibold uppercase tracking-wider">Suggested Changes</span>
                </div>
                <div className="mt-3 text-3xl font-bold text-white">{suggestions.length}</div>
                <p className="text-sm text-slate-400 mt-1">Review and apply the proposed updates.</p>
              </Card>
            </div>
          </Card>

          <Card className="p-6 space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white">Optimization Controls</h3>
                <p className="text-sm text-slate-400">Apply the AI draft to your resume.</p>
              </div>
              <Badge variant="secondary">{acceptedCount}/{suggestions.length} accepted</Badge>
            </div>

            <div className="space-y-2">
              <Button variant="glow" className="w-full justify-center gap-2" onClick={handleAcceptAll}>
                <CheckCircle2 className="w-4 h-4" /> Accept All Changes
              </Button>
              <Button variant="secondary" className="w-full justify-center gap-2" onClick={handleReset}>
                <RotateCcw className="w-4 h-4" /> Reset Changes
              </Button>
            </div>

            <div className="rounded-2xl border border-slate-700/70 bg-slate-950/60 p-4 space-y-3">
              <div className="flex items-center gap-2 text-blue-400">
                <FileText className="w-4 h-4" />
                <span className="text-sm font-semibold">AI Suggestions Timeline</span>
              </div>
              {initialData.timeline.map((item, index) => (
                <div key={index} className="border-l border-slate-700/70 pl-4 py-1">
                  <div className="text-sm font-semibold text-white">{item.title}</div>
                  <div className="text-xs text-slate-400">{item.detail}</div>
                  <div className="text-[11px] text-blue-400 mt-1">{item.time}</div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[1.2fr_0.8fr] gap-6">
          <Card className="p-6 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white">Resume Content Improvements</h3>
                <p className="text-sm text-slate-400">Review and accept the most impactful rewrites.</p>
              </div>
              <Badge variant="warning">{pendingCount} pending</Badge>
            </div>

            <div className="space-y-4">
              {suggestions.map((suggestion) => (
                <div key={suggestion.id} className="rounded-2xl border border-slate-700/70 bg-slate-950/60 p-4 space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-semibold text-white">{suggestion.title}</h4>
                        <Badge variant="outline">{suggestion.category}</Badge>
                      </div>
                      <p className="text-xs text-slate-400 mt-1">{suggestion.impact}</p>
                    </div>
                    {suggestion.status === 'accepted' ? (
                      <Badge variant="success">Accepted</Badge>
                    ) : suggestion.status === 'rejected' ? (
                      <Badge variant="error">Rejected</Badge>
                    ) : (
                      <Badge variant="warning">Pending</Badge>
                    )}
                  </div>

                  <div className="grid gap-3 md:grid-cols-2">
                    <div className="rounded-xl border border-slate-700/60 bg-slate-900/70 p-3">
                      <div className="text-[11px] uppercase tracking-wider text-slate-500 mb-2">Original</div>
                      <p className="text-sm text-slate-300">{suggestion.original}</p>
                    </div>
                    <div className="rounded-xl border border-blue-500/20 bg-blue-500/10 p-3">
                      <div className="text-[11px] uppercase tracking-wider text-blue-300 mb-2">Optimized</div>
                      <p className="text-sm text-slate-200">{suggestion.optimized}</p>
                    </div>
                  </div>

                  {suggestion.status === 'pending' ? (
                    <div className="flex gap-2">
                      <Button size="sm" variant="glow" className="gap-1.5" onClick={() => handleSuggestionAction(suggestion.id, 'accepted')}>
                        <CheckCircle2 className="w-4 h-4" /> Accept
                      </Button>
                      <Button size="sm" variant="secondary" className="gap-1.5" onClick={() => handleSuggestionAction(suggestion.id, 'rejected')}>
                        <XCircle className="w-4 h-4" /> Reject
                      </Button>
                    </div>
                  ) : (
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" className="gap-1.5" onClick={() => handleSuggestionAction(suggestion.id, 'accepted')}>
                        <CheckCircle2 className="w-4 h-4" /> Accept Again
                      </Button>
                      <Button size="sm" variant="outline" className="gap-1.5" onClick={() => handleSuggestionAction(suggestion.id, 'rejected')}>
                        <XCircle className="w-4 h-4" /> Reject
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-6 space-y-6">
            <div>
              <h3 className="text-lg font-bold text-white">AI Optimization Insights</h3>
              <p className="text-sm text-slate-400">Useful additions to strengthen your resume profile.</p>
            </div>

            <div className="space-y-4">
              <div className="rounded-2xl border border-slate-700/70 bg-slate-950/60 p-4">
                <div className="flex items-center gap-2 text-amber-400 mb-3">
                  <BadgeCheck className="w-4 h-4" />
                  <h4 className="text-sm font-semibold text-white">Suggested Technical Keywords</h4>
                </div>
                <div className="flex flex-wrap gap-2">
                  {initialData.technicalKeywords.map((keyword) => (
                    <Badge key={keyword} variant="secondary">{keyword}</Badge>
                  ))}
                </div>
              </div>

              <div className="rounded-2xl border border-slate-700/70 bg-slate-950/60 p-4">
                <div className="flex items-center gap-2 text-emerald-400 mb-3">
                  <Briefcase className="w-4 h-4" />
                  <h4 className="text-sm font-semibold text-white">Missing Skills</h4>
                </div>
                <div className="space-y-2">
                  {initialData.missingSkills.map((skill) => (
                    <div key={skill} className="rounded-xl border border-slate-700/60 bg-slate-900/70 px-3 py-2 text-sm text-slate-300">{skill}</div>
                  ))}
                </div>
              </div>

              <div className="rounded-2xl border border-slate-700/70 bg-slate-950/60 p-4">
                <div className="flex items-center gap-2 text-purple-400 mb-3">
                  <FileText className="w-4 h-4" />
                  <h4 className="text-sm font-semibold text-white">Missing Sections</h4>
                </div>
                <div className="space-y-2">
                  {initialData.missingSections.map((section) => (
                    <div key={section} className="flex items-center justify-between rounded-xl border border-slate-700/60 bg-slate-900/70 px-3 py-2 text-sm text-slate-300">
                      <span>{section}</span>
                      <Badge variant="warning">Add</Badge>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </div>

        <Card className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-white">Suggested Resume Enhancements</h3>
              <p className="text-sm text-slate-400">Additional areas the optimizer recommends improving.</p>
            </div>
            <Badge variant="primary">AI Review</Badge>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-slate-700/70 bg-slate-950/60 p-4">
              <h4 className="text-sm font-semibold text-white mb-3">Improve Project Descriptions</h4>
              <div className="space-y-3">
                {initialData.projectHighlights.map((item) => (
                  <div key={item.optimized} className="rounded-xl border border-slate-700/60 bg-slate-900/70 p-3">
                    <div className="text-[11px] uppercase tracking-wider text-slate-500 mb-1">Before</div>
                    <p className="text-sm text-slate-300">{item.original}</p>
                    <div className="text-[11px] uppercase tracking-wider text-blue-300 mt-2">After</div>
                    <p className="text-sm text-slate-200">{item.optimized}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-slate-700/70 bg-slate-950/60 p-4">
              <h4 className="text-sm font-semibold text-white mb-3">Enhance Resume Bullet Points</h4>
              <div className="space-y-3">
                {initialData.bulletPoints.map((item) => (
                  <div key={item.optimized} className="rounded-xl border border-slate-700/60 bg-slate-900/70 p-3">
                    <div className="text-[11px] uppercase tracking-wider text-slate-500 mb-1">Before</div>
                    <p className="text-sm text-slate-300">{item.original}</p>
                    <div className="text-[11px] uppercase tracking-wider text-blue-300 mt-2">After</div>
                    <p className="text-sm text-slate-200">{item.optimized}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Card>
      </main>
    </div>
  );
}
