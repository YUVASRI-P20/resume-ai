'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { CheckSquare, Square, CheckCircle2, Clock, ArrowUpRight } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { PreparationChecklistItem } from '@/types/interviewReadiness';

interface PreparationChecklistProps {
  checklist: PreparationChecklistItem[];
  onToggle: (id: string) => void;
}

export const PreparationChecklist: React.FC<PreparationChecklistProps> = ({ checklist, onToggle }) => {
  const completedCount = checklist.filter((item) => item.completed).length;
  const progressPct = Math.round((completedCount / checklist.length) * 100);

  return (
    <Card className="p-6 space-y-6 bg-slate-900/80 border-slate-800 backdrop-blur-xl">
      {/* Header & Overall Counter */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-emerald-400" />
            <h3 className="text-lg font-bold text-white">Interview Preparation Checklist</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Interactive action list ensuring 100% readiness across resume, coding, and mock rounds.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Badge variant={progressPct === 100 ? 'success' : 'primary'} className="text-xs">
            {completedCount}/{checklist.length} Completed ({progressPct}%)
          </Badge>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-1.5">
        <ProgressBar progress={progressPct} color={progressPct === 100 ? 'emerald' : 'blue'} className="h-2.5" showPercentage={false} />
      </div>

      {/* Grid of Checklist Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {checklist.map((item, idx) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: idx * 0.04 }}
            onClick={() => onToggle(item.id)}
            className={`p-4 rounded-2xl border transition-all cursor-pointer flex items-start gap-3 select-none ${
              item.completed
                ? 'border-emerald-500/30 bg-emerald-500/5'
                : 'border-slate-800 bg-slate-950/70 hover:border-slate-700 hover:bg-slate-900/60'
            }`}
          >
            {/* Custom Checkbox Toggle */}
            <div className="pt-0.5 shrink-0">
              {item.completed ? (
                <div className="h-5 w-5 rounded-md bg-emerald-500 flex items-center justify-center text-slate-950 shadow-sm">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
              ) : (
                <div className="h-5 w-5 rounded-md border-2 border-slate-600 bg-slate-900 hover:border-blue-400 transition-colors" />
              )}
            </div>

            {/* Checklist Details */}
            <div className="flex-1 space-y-1">
              <div className="flex items-center justify-between gap-2">
                <h4
                  className={`text-sm font-bold transition-colors ${
                    item.completed ? 'text-slate-400 line-through' : 'text-white'
                  }`}
                >
                  {item.title}
                </h4>
                <span className="text-[10px] text-slate-500 font-mono">{item.category}</span>
              </div>

              <p className={`text-xs ${item.completed ? 'text-slate-500' : 'text-slate-300'}`}>
                {item.description}
              </p>

              <div className="flex items-center justify-between pt-1 text-[11px] font-mono text-slate-400">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-blue-400" /> ~{item.estimatedMinutes} mins
                </span>
                {item.actionRoute && (
                  <Link
                    href={item.actionRoute}
                    onClick={(e) => e.stopPropagation()}
                    className="text-blue-400 hover:text-blue-300 flex items-center gap-0.5 hover:underline"
                  >
                    Go <ArrowUpRight className="w-3 h-3" />
                  </Link>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </Card>
  );
};
