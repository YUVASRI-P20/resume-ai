'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, Award, Sparkles, Check, ArrowUpRight } from 'lucide-react';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Tooltip } from 'recharts';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { InterviewConfidence } from '@/types/interviewReadiness';

interface ConfidenceRadarCardProps {
  confidenceScores: InterviewConfidence[];
}

export const ConfidenceRadarCard: React.FC<ConfidenceRadarCardProps> = ({ confidenceScores }) => {
  // Format data for Recharts Radar
  const radarData = confidenceScores.map((c) => ({
    subject: c.roundName,
    Score: c.score,
    fullMark: 100,
  }));

  const getScoreBadgeVariant = (score: number): 'success' | 'primary' | 'warning' => {
    if (score >= 88) return 'success';
    if (score >= 80) return 'primary';
    return 'warning';
  };

  return (
    <Card className="p-6 space-y-6 bg-slate-900/80 border-slate-800 backdrop-blur-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-bold text-white">Interview Confidence Dashboard</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            AI confidence scores mapped across 6 critical evaluation rounds.
          </p>
        </div>

        <Badge variant="secondary" className="text-xs">
          Radar Analysis
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
        {/* Radar Chart Visualizer */}
        <div className="lg:col-span-5 h-72 w-full flex items-center justify-center bg-slate-950/60 rounded-2xl border border-slate-800 p-2">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
              <PolarGrid stroke="#334155" strokeDasharray="3 3" />
              <PolarAngleAxis dataKey="subject" stroke="#94a3b8" fontSize={11} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" fontSize={9} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#090d16',
                  borderColor: '#1e293b',
                  borderRadius: '12px',
                  color: '#fff',
                  fontSize: '12px',
                }}
                formatter={(val: any) => [`${val}% Confidence`, 'Score']}
              />
              <Radar
                name="Confidence"
                dataKey="Score"
                stroke="#a855f7"
                fill="#a855f7"
                fillOpacity={0.35}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* 6 Round Score Cards */}
        <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-3">
          {confidenceScores.map((item, idx) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: idx * 0.05 }}
              className="rounded-xl border border-slate-800 bg-slate-950/70 p-3.5 space-y-2 hover:border-slate-700 transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white">{item.roundName}</span>
                <Badge variant={getScoreBadgeVariant(item.score)} className="font-mono text-[11px]">
                  {item.score}% Confidence
                </Badge>
              </div>

              <p className="text-[11px] text-slate-300 line-clamp-2 leading-relaxed">
                {item.description}
              </p>

              <div className="pt-1 border-t border-slate-800/80 space-y-1 text-[10px]">
                <div className="text-emerald-400 flex items-center gap-1">
                  <Check className="w-3 h-3 shrink-0" /> <span className="text-slate-300 truncate">{item.keyStrengths}</span>
                </div>
                <div className="text-amber-400 flex items-center gap-1">
                  <ArrowUpRight className="w-3 h-3 shrink-0" /> <span className="text-slate-300 truncate">{item.areaToImprove}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </Card>
  );
};
