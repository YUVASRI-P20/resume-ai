'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { AlertOctagon, Clock, Gauge, Tag, BookOpenCheck } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { MissingTopic } from '@/types/interviewReadiness';

interface MissingTopicsCardProps {
  topics: MissingTopic[];
}

export const MissingTopicsCard: React.FC<MissingTopicsCardProps> = ({ topics }) => {
  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'Critical':
        return <Badge variant="error" className="text-[10px]">Critical Priority</Badge>;
      case 'High':
        return <Badge variant="warning" className="text-[10px]">High Priority</Badge>;
      default:
        return <Badge variant="secondary" className="text-[10px]">Medium Priority</Badge>;
    }
  };

  const getDifficultyBadge = (difficulty: string) => {
    switch (difficulty) {
      case 'Hard':
        return <Badge variant="outline" className="text-[10px] border-purple-500/40 text-purple-400">Hard</Badge>;
      case 'Medium':
        return <Badge variant="outline" className="text-[10px] border-blue-500/40 text-blue-400">Medium</Badge>;
      default:
        return <Badge variant="outline" className="text-[10px] border-emerald-500/40 text-emerald-400">Easy</Badge>;
    }
  };

  return (
    <Card className="p-6 space-y-6 bg-slate-900/80 border-slate-800 backdrop-blur-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <AlertOctagon className="w-5 h-5 text-amber-400" />
            <h3 className="text-lg font-bold text-white">Missing Topics Before Interview</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Crucial topics identified in target company rounds where your confidence gap is highest.
          </p>
        </div>

        <Badge variant="warning" className="text-xs">
          {topics.length} Priority Topics
        </Badge>
      </div>

      {/* Grid of Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {topics.map((item, idx) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: idx * 0.05 }}
            className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 space-y-3 flex flex-col justify-between hover:border-amber-500/30 transition-all"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between gap-2">
                {getPriorityBadge(item.priority)}
                <span className="text-[11px] text-slate-400 font-mono flex items-center gap-1">
                  <Tag className="w-3 h-3 text-slate-500" /> {item.category}
                </span>
              </div>

              <h4 className="text-sm font-bold text-white leading-snug">{item.topic}</h4>
            </div>

            <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2 text-xs">
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1 text-slate-300 font-mono">
                  <Clock className="w-3.5 h-3.5 text-blue-400" /> {item.estimatedHours} Hours
                </span>
                <span className="flex items-center gap-1">
                  <Gauge className="w-3.5 h-3.5 text-purple-400" /> {getDifficultyBadge(item.difficulty)}
                </span>
              </div>
            </div>

            <div className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800/80 text-[11px] text-slate-300 flex items-start gap-2">
              <BookOpenCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-white">Recommended Resource: </span>
                {item.recommendedResource}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </Card>
  );
};
