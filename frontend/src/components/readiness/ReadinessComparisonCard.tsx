'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Calendar, ArrowRight, Zap, Award } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ReadinessComparison, ReadinessTimeframe } from '@/types/interviewReadiness';

interface ReadinessComparisonCardProps {
  comparison: ReadinessComparison;
  timeframes: ReadinessTimeframe[];
  activeTimeframeDays: 7 | 14 | 21;
  onSelectTimeframe: (days: 7 | 14 | 21) => void;
}

export const ReadinessComparisonCard: React.FC<ReadinessComparisonCardProps> = ({
  comparison,
  timeframes,
  activeTimeframeDays,
  onSelectTimeframe,
}) => {
  const activeTf = timeframes.find((t) => t.days === activeTimeframeDays) || timeframes[1];

  return (
    <Card className="p-6 space-y-6 bg-slate-900/80 border-slate-800 backdrop-blur-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            <h3 className="text-lg font-bold text-white">Estimated Preparation Time & Expected Improvement</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Predictive growth curve showing performance trajectory based on study timeframe.
          </p>
        </div>

        {/* Timeframe Selector Tabs */}
        <div className="flex items-center rounded-xl bg-slate-950 p-1 border border-slate-800">
          {timeframes.map((tf) => (
            <button
              key={tf.days}
              onClick={() => onSelectTimeframe(tf.days)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTimeframeDays === tf.days
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Ready in {tf.days} Days
            </button>
          ))}
        </div>
      </div>

      {/* Readiness Improvement Comparison Header */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Current Card */}
        <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 space-y-1">
          <span className="text-xs text-slate-400 font-mono uppercase tracking-wider">Current Readiness</span>
          <div className="text-3xl font-extrabold font-mono text-slate-200">{comparison.currentReadiness}%</div>
          <p className="text-[11px] text-slate-400">Baseline score evaluated from uploaded resume & mock tests.</p>
        </div>

        {/* Arrow Transition */}
        <div className="rounded-2xl border border-blue-500/20 bg-blue-500/10 p-4 flex flex-col justify-between space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-blue-300 font-mono uppercase tracking-wider">Predicted Growth</span>
            <Zap className="w-4 h-4 text-amber-400 animate-bounce" />
          </div>
          <div className="flex items-center gap-2 text-2xl font-extrabold text-blue-400">
            +{activeTf.predictedScore - comparison.currentReadiness}% Score Lift
            <ArrowRight className="w-5 h-5 text-blue-400" />
          </div>
          <p className="text-[11px] text-blue-200">{activeTf.recommendedPace}</p>
        </div>

        {/* Predicted Card */}
        <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4 space-y-1">
          <span className="text-xs text-emerald-300 font-mono uppercase tracking-wider">
            Predicted Readiness ({activeTimeframeDays} Days)
          </span>
          <div className="text-3xl font-extrabold font-mono text-emerald-400">{activeTf.predictedScore}%</div>
          <p className="text-[11px] text-emerald-200/80">{activeTf.milestone}</p>
        </div>
      </div>

      {/* Recharts Line Chart */}
      <div className="h-64 w-full pt-4 bg-slate-950/60 rounded-2xl border border-slate-800 p-3">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={comparison.historyData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="day" stroke="#94a3b8" fontSize={11} />
            <YAxis stroke="#94a3b8" fontSize={11} domain={[50, 100]} tickFormatter={(v) => `${v}%`} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#090d16',
                borderColor: '#1e293b',
                borderRadius: '12px',
                color: '#fff',
                fontSize: '12px',
              }}
              formatter={(val: any, name: any) => [
                `${val}% Score`,
                name === 'current' ? 'Current Baseline' : 'Predicted Target',
              ]}
            />
            <Line
              type="monotone"
              dataKey="current"
              stroke="#64748b"
              strokeWidth={2}
              dot={{ r: 4, fill: '#64748b' }}
            />
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="#10b981"
              strokeWidth={3}
              dot={{ r: 5, fill: '#10b981' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
