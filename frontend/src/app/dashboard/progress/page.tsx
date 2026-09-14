'use client';

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import { TrendingUp, Trophy, Award, Flame, Star, Crown, Sparkles, CheckCircle2 } from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';

export default function ProgressDashboardPage() {
  const trendData = [
    { date: 'Jul 01', score: 72, readiness: 70 },
    { date: 'Jul 08', score: 78, readiness: 75 },
    { date: 'Jul 15', score: 81, readiness: 80 },
    { date: 'Jul 22', score: 85, readiness: 83 },
    { date: 'Jul 29', score: 89, readiness: 86 },
    { date: 'Aug 04', score: 91, readiness: 88 },
  ];

  const badges = [
    { title: 'React 19 Master', desc: 'Achieved 95%+ in React Fiber & RSC interviews', icon: '⚡', color: 'blue' },
    { title: 'Hallucination Destroyer', desc: 'Conducted 5 consecutive sessions with 0 claims flagged', icon: '🛡️', color: 'purple' },
    { title: 'Monaco Speed Demon', desc: 'Passed all coding test cases in < 15 minutes', icon: '🚀', color: 'emerald' },
    { title: 'System Design Architect', desc: 'Successfully solved high-throughput rate limiter prompt', icon: '🏗️', color: 'amber' },
  ];

  const leaderboard = [
    { rank: 1, name: 'Alex Chen', score: 94, interviews: 14, streak: 12, role: 'Fullstack' },
    { rank: 2, name: 'Sarah Jenkins', score: 92, interviews: 18, streak: 9, role: 'Frontend' },
    { rank: 3, name: 'David Kim', score: 90, interviews: 11, streak: 15, role: 'Backend' },
    { rank: 4, name: 'Marcus Vance', score: 88, interviews: 10, streak: 6, role: 'DevOps' },
  ];

  return (
    <div className="flex-1 space-y-6">
      <DashboardHeader
        title="Progress Analytics & Peer Leaderboard"
        subtitle="Track long-term readiness growth, unlock achievement badges, and see global candidate rankings."
      />

      <main className="p-6 max-w-7xl mx-auto space-y-8">
        {/* Performance Trend Line Chart */}
        <Card className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-400" /> Long-Term Technical Score Growth
            </h3>
            <Badge variant="success" className="font-mono">+18% Growth (30 Days)</Badge>
          </div>

          <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#94A3B8" tick={{ fill: '#94A3B8', fontSize: 11 }} />
                <YAxis stroke="#94A3B8" tick={{ fill: '#94A3B8', fontSize: 11 }} domain={[60, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1E293B',
                    borderColor: '#334155',
                    borderRadius: '0.75rem',
                    color: '#F8FAFC',
                    fontSize: '12px',
                  }}
                />
                <Line type="monotone" dataKey="score" stroke="#2563EB" strokeWidth={3} name="Session Score %" />
                <Line type="monotone" dataKey="readiness" stroke="#7C3AED" strokeWidth={2} strokeDasharray="5 5" name="Target Readiness" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Achievements & Leaderboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Unlocked Badges */}
          <div className="lg:col-span-6 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Trophy className="w-5 h-5 text-amber-400" /> Unlocked Candidate Badges
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {badges.map((b, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2 flex items-start space-x-3">
                  <span className="text-3xl">{b.icon}</span>
                  <div className="space-y-0.5">
                    <h4 className="text-sm font-bold text-white">{b.title}</h4>
                    <p className="text-[11px] text-slate-400">{b.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Global Peer Leaderboard */}
          <Card className="lg:col-span-6 p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Crown className="w-5 h-5 text-yellow-400" /> Global Peer Leaderboard
              </h3>
              <Badge variant="primary" className="font-mono">Weekly Top Candidate</Badge>
            </div>

            <div className="space-y-2">
              {leaderboard.map((item) => (
                <div
                  key={item.rank}
                  className={`p-3 rounded-xl border flex items-center justify-between text-xs ${
                    item.rank === 1
                      ? 'bg-blue-950/40 border-blue-500/40 text-white font-semibold'
                      : 'bg-slate-900 border-slate-800 text-slate-300'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="w-6 h-6 rounded-full bg-slate-800 text-slate-300 font-mono font-bold flex items-center justify-center text-[11px]">
                      #{item.rank}
                    </span>
                    <div>
                      <h4 className="font-bold text-white">{item.name}</h4>
                      <span className="text-[10px] text-slate-400 font-mono">{item.role}</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4 font-mono">
                    <span className="text-amber-400 flex items-center gap-1">
                      <Flame className="w-3 h-3 fill-amber-400" /> {item.streak}d
                    </span>
                    <span className="font-bold text-blue-400 text-sm">{item.score}%</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
}
