'use client';

import React, { useState } from 'react';
import { Play, Pause, RotateCcw, Volume2, Clock, CheckCircle2, AlertTriangle, Sparkles, BrainCircuit } from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { MOCK_RECENT_INTERVIEWS } from '@/constants/mockData';

export default function InterviewReplayPage() {
  const session = MOCK_RECENT_INTERVIEWS[0];
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState('1.0x');
  const [selectedQuestionIndex, setSelectedQuestionIndex] = useState(0);

  return (
    <div className="flex-1 space-y-6">
      <DashboardHeader
        title="Interview Replay & Audio Transcript"
        subtitle={`Session Timeline Player — ${session.title}`}
      />

      <main className="p-6 max-w-6xl mx-auto space-y-8">
        {/* Timeline Audio Player Control Bar */}
        <Card className="glass-panel p-6 space-y-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="w-12 h-12 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white flex items-center justify-center shadow-lg shadow-blue-600/30 transition-transform active:scale-95"
              >
                {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 fill-white" />}
              </button>
              <div>
                <h3 className="text-base font-bold text-white">Audio Replay Timeline</h3>
                <span className="text-xs text-slate-400 font-mono">Timestamp: 04:12 / 45:00</span>
              </div>
            </div>

            <div className="flex items-center space-x-3 text-xs font-mono">
              <span className="text-slate-400">Speed:</span>
              {(['1.0x', '1.25x', '1.5x', '2.0x'] as const).map((spd) => (
                <button
                  key={spd}
                  onClick={() => setPlaybackSpeed(spd)}
                  className={`px-2.5 py-1 rounded-lg border transition-colors ${
                    playbackSpeed === spd
                      ? 'bg-blue-600/20 border-blue-500 text-blue-400 font-bold'
                      : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  {spd}
                </button>
              ))}
            </div>
          </div>

          {/* Audio Waveform Timeline */}
          <div className="w-full bg-slate-900 rounded-xl p-3 border border-slate-800 flex items-center space-x-1 h-14">
            {[30, 60, 40, 90, 70, 50, 100, 40, 80, 60, 30, 75, 45, 95, 60, 30, 80, 50, 90, 40, 70, 30, 60, 85].map((val, i) => (
              <div
                key={i}
                className={`flex-1 rounded-full transition-all ${
                  i < 8 ? 'bg-blue-500' : 'bg-slate-800'
                }`}
                style={{ height: `${val}%` }}
              />
            ))}
          </div>
        </Card>

        {/* Question-by-Question Transcript Replay Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Timeline Question List */}
          <div className="lg:col-span-4 space-y-3">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              Interview Questions ({session.questions.length})
            </h3>

            {session.questions.map((q, idx) => (
              <div
                key={q.id}
                onClick={() => setSelectedQuestionIndex(idx)}
                className={`p-4 rounded-xl border cursor-pointer transition-all space-y-1.5 ${
                  selectedQuestionIndex === idx
                    ? 'bg-blue-600/20 border-blue-500 text-white shadow-md'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-blue-400 font-bold">Question 0{idx + 1}</span>
                  <Badge variant="outline">{q.category}</Badge>
                </div>
                <h4 className="text-sm font-bold text-white line-clamp-1">{q.title}</h4>
              </div>
            ))}
          </div>

          {/* Transcript & AI Critique Detail */}
          <Card className="lg:col-span-8 p-6 space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="text-xs text-blue-400 font-mono font-bold">
                  TIMESTAMP: 08:30 • {session.questions[selectedQuestionIndex]?.title}
                </span>
                <Badge variant="success">95% Answer Precision</Badge>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                <span className="text-[10px] uppercase font-mono text-purple-400 font-bold block">Interviewer Spoken Prompt</span>
                <p className="text-sm text-slate-200">
                  {session.questions[selectedQuestionIndex]?.prompt}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                <span className="text-[10px] uppercase font-mono text-blue-400 font-bold block">Candidate Spoken Response</span>
                <p className="text-sm text-slate-300 italic">
                  &quot;React Fiber reconciles updates by building a linked list tree of work units. It allows time slicing via requestIdleCallback semantics so user input receives DiscretePriority.&quot;
                </p>
              </div>

              <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/30 space-y-2">
                <span className="text-[10px] uppercase font-mono text-emerald-400 font-bold block flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" /> AI Coach Critique & Feedback
                </span>
                <p className="text-xs text-emerald-200 leading-relaxed">
                  Excellent answer! Clear explanation of Fiber linked-list traversal and priority scheduling. Zero hallucinations detected for this response.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
}
