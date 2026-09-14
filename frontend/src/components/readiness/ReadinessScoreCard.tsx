'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Trophy, CheckCircle, AlertTriangle, ShieldCheck } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { InterviewReadinessData } from '@/types/interviewReadiness';

interface ReadinessScoreCardProps {
  data: InterviewReadinessData;
}

export const ReadinessScoreCard: React.FC<ReadinessScoreCardProps> = ({ data }) => {
  const { overallScore, maxScore, readinessTier, summary } = data;
  const percentage = Math.round((overallScore / maxScore) * 100);

  // SVG Circle parameters
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <Card className="p-6 relative overflow-hidden bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-blue-950/40 border border-blue-500/20 shadow-xl backdrop-blur-xl">
      {/* Background ambient glow */}
      <div className="absolute -top-24 -right-24 w-60 h-60 bg-blue-500/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -left-24 w-60 h-60 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 flex flex-col lg:flex-row items-center justify-between gap-6">
        {/* Left Side: Score & Tier */}
        <div className="flex flex-col sm:flex-row items-center gap-6 text-center sm:text-left">
          {/* Circular Progress Gauge */}
          <div className="relative flex items-center justify-center shrink-0">
            <svg className="w-44 h-44 transform -rotate-90" viewBox="0 0 160 160">
              {/* Background Track */}
              <circle
                cx="80"
                cy="80"
                r={radius}
                className="stroke-slate-800"
                strokeWidth="12"
                fill="transparent"
              />
              {/* Gradient stroke definition */}
              <defs>
                <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="50%" stopColor="#6366f1" />
                  <stop offset="100%" stopColor="#a855f7" />
                </linearGradient>
              </defs>
              {/* Animated Progress Circle */}
              <motion.circle
                cx="80"
                cy="80"
                r={radius}
                stroke="url(#scoreGradient)"
                strokeWidth="12"
                strokeLinecap="round"
                fill="transparent"
                strokeDasharray={circumference}
                initial={{ strokeDashoffset: circumference }}
                animate={{ strokeDashoffset }}
                transition={{ duration: 1.5, ease: 'easeOut' }}
              />
            </svg>

            {/* Score Text inside Circle */}
            <div className="absolute flex flex-col items-center justify-center text-center">
              <motion.span
                className="text-4xl font-extrabold font-mono text-white tracking-tight"
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                {overallScore}
              </motion.span>
              <span className="text-xs text-slate-400 font-medium">out of {maxScore}</span>
            </div>
          </div>

          {/* Tier & Details */}
          <div className="space-y-2.5">
            <div className="flex items-center justify-center sm:justify-start gap-2">
              <Badge variant="primary" className="px-3 py-1 text-xs gap-1.5 font-semibold">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                AI INTERVIEW READINESS
              </Badge>
              <Badge variant="success" className="px-2.5 py-0.5 text-xs font-medium">
                Top 15% Candidates
              </Badge>
            </div>

            <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center justify-center sm:justify-start gap-2">
              {readinessTier}
              <ShieldCheck className="w-6 h-6 text-emerald-400 inline shrink-0" />
            </h2>

            <p className="text-sm text-slate-300 max-w-xl leading-relaxed">
              {summary}
            </p>
          </div>
        </div>

        {/* Right Side: Key Metrics Pill Box */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-1 gap-3 w-full lg:w-64 shrink-0">
          <div className="rounded-xl border border-slate-800/80 bg-slate-950/60 p-3 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <Trophy className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">Target Match</div>
              <div className="text-sm font-bold text-white">88% Avg Tier-1</div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-800/80 bg-slate-950/60 p-3 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <CheckCircle className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">Strong Skills</div>
              <div className="text-sm font-bold text-white">4 Core Areas</div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-800/80 bg-slate-950/60 p-3 flex items-center gap-3 col-span-2 sm:col-span-1 lg:col-span-1">
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">Action Needed</div>
              <div className="text-sm font-bold text-white">4 Missing Topics</div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
