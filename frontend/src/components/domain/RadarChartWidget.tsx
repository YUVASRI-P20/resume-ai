'use client';

import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { RadarScorePoint } from '@/types/feedback';

interface RadarChartWidgetProps {
  data: RadarScorePoint[];
  title?: string;
}

export const RadarChartWidget: React.FC<RadarChartWidgetProps> = ({
  data,
  title = 'Skill Competency Radar',
}) => {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center">
      {title && <h3 className="text-sm font-semibold text-slate-300 mb-2 font-mono">{title}</h3>}
      <div className="w-full h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
            <PolarGrid stroke="#334155" />
            <PolarAngleAxis dataKey="subject" stroke="#94A3B8" tick={{ fill: '#94A3B8', fontSize: 11 }} />
            <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" tick={{ fill: '#64748B', fontSize: 9 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1E293B',
                borderColor: '#334155',
                borderRadius: '0.75rem',
                color: '#F8FAFC',
                fontSize: '12px',
              }}
            />
            <Radar
              name="Your Score"
              dataKey="A"
              stroke="#2563EB"
              fill="#2563EB"
              fillOpacity={0.45}
            />
            <Radar
              name="Benchmark Target"
              dataKey="B"
              stroke="#7C3AED"
              fill="#7C3AED"
              fillOpacity={0.2}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <div className="flex items-center space-x-6 text-xs mt-2 font-mono">
        <span className="flex items-center gap-2 text-slate-300">
          <span className="w-3 h-3 rounded-full bg-blue-600 inline-block shadow-sm" /> Candidate Performance
        </span>
        <span className="flex items-center gap-2 text-slate-400">
          <span className="w-3 h-3 rounded-full bg-purple-600 inline-block shadow-sm" /> Target Benchmark
        </span>
      </div>
    </div>
  );
};
