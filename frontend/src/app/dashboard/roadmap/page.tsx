'use client';

import React, { Suspense, useEffect, useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
  Map,
  CheckCircle2,
  Clock,
  BookOpen,
  Code2,
  Layers,
  ArrowRight,
  Sparkles,
  RefreshCw,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { roadmapService, Roadmap, RoadmapTask } from '@/services/roadmapService';

function RoadmapContent() {
  const searchParams = useSearchParams();
  const interviewId = searchParams.get('interview_id');

  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setIsLoading(true);
    setError(null);
    const fetcher = interviewId
      ? roadmapService.getByInterview(interviewId)
      : roadmapService.getMine();
    fetcher
      .then(setRoadmap)
      .catch(() =>
        setError(
          'Could not load your roadmap. A completed interview with evaluated answers is needed to personalize it.'
        )
      )
      .finally(() => setIsLoading(false));
  };

  useEffect(load, [interviewId]);

  const toggleTask = async (task: RoadmapTask) => {
    if (!roadmap) return;
    const updated = await roadmapService.setTaskCompleted(task.id, !task.is_completed);
    setRoadmap((prev) =>
      prev
        ? {
            ...prev,
            weeks: prev.weeks.map((w) =>
              w.id === updated.id
                ? w
                : {
                    ...w,
                    tasks: w.tasks.map((t) => (t.id === updated.id ? { ...t, is_completed: !task.is_completed } : t)),
                  }
            ),
          }
        : prev
    );
    // Recompute completion locally for immediate feedback.
    setRoadmap((prev) => {
      if (!prev) return prev;
      const all = prev.weeks.flatMap((w) => w.tasks);
      const done = all.filter((t) => t.is_completed).length;
      return { ...prev, completion_percentage: all.length ? (done / all.length) * 100 : 0 };
    });
  };

  const regenerate = async () => {
    setIsRegenerating(true);
    try {
      const fresh = await roadmapService.regenerate();
      setRoadmap(fresh);
    } catch {
      setError('Could not regenerate the roadmap.');
    } finally {
      setIsRegenerating(false);
    }
  };

  const getTaskIcon = (task: RoadmapTask) => {
    const text = task.description.toLowerCase();
    if (text.includes('coding') || text.includes('problem')) return Code2;
    if (text.includes('read') || text.includes('study')) return BookOpen;
    return Layers;
  };

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-screen space-y-3">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <p className="text-sm text-slate-500">Generating your personalized 15-day roadmap...</p>
      </div>
    );
  }

  if (error || !roadmap) {
    return (
      <main className="p-6 max-w-3xl mx-auto">
        <Card className="p-8 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-amber-500 mx-auto" />
          <p className="text-sm text-slate-600">{error}</p>
          <Link href="/dashboard/history">
            <Button variant="outline" size="sm">Go to History</Button>
          </Link>
        </Card>
      </main>
    );
  }

  const allTasks = roadmap.weeks.flatMap((w) => w.tasks).sort((a, b) => a.day_number - b.day_number);

  return (
    <main className="p-6 max-w-5xl mx-auto space-y-8">
      {/* Progress header */}
      <Card className="p-6 flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="space-y-2 w-full sm:w-2/3">
          <div className="flex items-center space-x-2">
            <Badge variant="primary">PERSONALIZED FROM YOUR RESULTS</Badge>
          </div>
          <h2 className="text-xl font-bold text-slate-900">{roadmap.title}</h2>
          <p className="text-xs text-slate-500">{roadmap.summary}</p>
          <ProgressBar progress={roadmap.completion_percentage} label="Plan completion" color="blue" />
        </div>

        <div className="flex flex-col gap-2 shrink-0">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center">
            <span className="text-[10px] text-slate-500 uppercase font-mono block">Days</span>
            <span className="text-xl font-bold text-blue-700 font-mono">{allTasks.length}</span>
          </div>
          <Button variant="outline" size="sm" onClick={regenerate} disabled={isRegenerating} className="gap-1.5 text-xs">
            <RefreshCw className={`w-3.5 h-3.5 ${isRegenerating ? 'animate-spin' : ''}`} /> Regenerate
          </Button>
        </div>
      </Card>

      {/* Day-by-day plan */}
      <div className="space-y-3">
        {allTasks.map((task) => {
          const Icon = getTaskIcon(task);
          return (
            <Card
              key={task.id}
              className={`p-4 flex flex-col sm:flex-row sm:items-start justify-between gap-4 ${
                task.is_completed ? 'opacity-70' : ''
              }`}
            >
              <div className="flex items-start space-x-3">
                <button
                  type="button"
                  onClick={() => toggleTask(task)}
                  className={`w-5 h-5 rounded-md border flex items-center justify-center transition-colors mt-0.5 ${
                    task.is_completed ? 'bg-emerald-500 border-emerald-500 text-white' : 'border-slate-300 hover:border-blue-400'
                  }`}
                  aria-label={task.is_completed ? 'Mark as not done' : 'Mark as done'}
                >
                  {task.is_completed && <CheckCircle2 className="w-4 h-4" />}
                </button>

                <div className="space-y-1">
                  <div className="flex items-center flex-wrap gap-2">
                    <span className="text-xs font-mono text-blue-700 font-bold">DAY {task.day_number}</span>
                    <h4 className={`text-sm font-bold ${task.is_completed ? 'line-through text-slate-400' : 'text-slate-900'}`}>
                      {task.task_title}
                    </h4>
                    <Badge
                      variant={
                        task.priority === 'Critical' || task.priority === 'High'
                          ? 'error'
                          : task.priority === 'Medium'
                          ? 'warning'
                          : 'outline'
                      }
                    >
                      {task.priority}
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-600 whitespace-pre-line">{task.description}</p>
                  {task.resources.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {task.resources.map((r, i) => (
                        <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-blue-50 border border-blue-200 text-blue-700">
                          {r}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-3 shrink-0 sm:self-start">
                <Icon className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-mono text-slate-400 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" /> {task.study_time_hours}h
                </span>
              </div>
            </Card>
          );
        })}
      </div>
    </main>
  );
}

export default function LearningRoadmapPage() {
  return (
    <div className="flex-1 space-y-6">
      <DashboardHeader
        title="15-Day Improvement Roadmap"
        subtitle="Built from your interview weaknesses, coding results and job requirement gaps."
      />
      <Suspense
        fallback={
          <div className="flex-1 flex items-center justify-center min-h-[50vh]">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        }
      >
        <RoadmapContent />
      </Suspense>
    </div>
  );
}
