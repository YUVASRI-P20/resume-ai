'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, CheckCircle2, AlertCircle, HelpCircle, XCircle, Filter } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { SkillAnalysisItem, SkillLevel } from '@/types/interviewReadiness';

interface SkillAnalysisCardProps {
  skills: SkillAnalysisItem[];
}

export const SkillAnalysisCard: React.FC<SkillAnalysisCardProps> = ({ skills }) => {
  const [filter, setFilter] = useState<SkillLevel | 'all'>('all');

  const strongCount = skills.filter((s) => s.level === 'strong').length;
  const averageCount = skills.filter((s) => s.level === 'average').length;
  const weakCount = skills.filter((s) => s.level === 'weak').length;
  const missingCount = skills.filter((s) => s.level === 'missing').length;

  const filteredSkills = filter === 'all' ? skills : skills.filter((s) => s.level === filter);

  const getLevelBadge = (level: SkillLevel) => {
    switch (level) {
      case 'strong':
        return <Badge variant="success" className="gap-1"><CheckCircle2 className="w-3 h-3" /> Strong</Badge>;
      case 'average':
        return <Badge variant="primary" className="gap-1"><Sparkles className="w-3 h-3" /> Average</Badge>;
      case 'weak':
        return <Badge variant="warning" className="gap-1"><AlertCircle className="w-3 h-3" /> Weak</Badge>;
      case 'missing':
        return <Badge variant="error" className="gap-1"><XCircle className="w-3 h-3" /> Missing</Badge>;
    }
  };

  const getProgressColor = (level: SkillLevel): 'emerald' | 'blue' | 'purple' => {
    switch (level) {
      case 'strong': return 'emerald';
      case 'average': return 'blue';
      case 'weak': return 'purple';
      case 'missing': return 'purple';
    }
  };

  return (
    <Card className="p-6 space-y-6 bg-slate-900/80 border-slate-800 backdrop-blur-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            <h3 className="text-lg font-bold text-white">Skill Readiness Analysis</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Categorized evaluation of your technical skills against market expectations.
          </p>
        </div>

        {/* Category Pill Counters */}
        <div className="flex items-center gap-2 text-xs flex-wrap">
          <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-semibold">
            {strongCount} Strong
          </span>
          <span className="px-2.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 font-semibold">
            {averageCount} Average
          </span>
          <span className="px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 font-semibold">
            {weakCount} Weak
          </span>
          <span className="px-2.5 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 font-semibold">
            {missingCount} Missing
          </span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 text-xs border-b border-slate-800 scrollbar-none">
        <button
          onClick={() => setFilter('all')}
          className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
            filter === 'all'
              ? 'bg-blue-600 text-white'
              : 'text-slate-400 hover:text-white bg-slate-950/60 border border-slate-800'
          }`}
        >
          All Skills ({skills.length})
        </button>
        <button
          onClick={() => setFilter('strong')}
          className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
            filter === 'strong'
              ? 'bg-emerald-600 text-white'
              : 'text-slate-400 hover:text-white bg-slate-950/60 border border-slate-800'
          }`}
        >
          Strong ({strongCount})
        </button>
        <button
          onClick={() => setFilter('average')}
          className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
            filter === 'average'
              ? 'bg-blue-600 text-white'
              : 'text-slate-400 hover:text-white bg-slate-950/60 border border-slate-800'
          }`}
        >
          Average ({averageCount})
        </button>
        <button
          onClick={() => setFilter('weak')}
          className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
            filter === 'weak'
              ? 'bg-amber-600 text-white'
              : 'text-slate-400 hover:text-white bg-slate-950/60 border border-slate-800'
          }`}
        >
          Weak ({weakCount})
        </button>
        <button
          onClick={() => setFilter('missing')}
          className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
            filter === 'missing'
              ? 'bg-rose-600 text-white'
              : 'text-slate-400 hover:text-white bg-slate-950/60 border border-slate-800'
          }`}
        >
          Missing ({missingCount})
        </button>
      </div>

      {/* Skills List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredSkills.map((skill, index) => (
          <motion.div
            key={skill.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 space-y-3"
          >
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-semibold text-white">{skill.name}</h4>
                <span className="text-[11px] text-slate-400 font-mono">{skill.category}</span>
              </div>
              {getLevelBadge(skill.level)}
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-400">Score: <strong className="text-white">{skill.score}%</strong></span>
                <span className="text-slate-400">Benchmark: <strong className="text-slate-300">{skill.industryBenchmark}%</strong></span>
              </div>
              <ProgressBar progress={skill.score} color={getProgressColor(skill.level)} className="h-2" showPercentage={false} />
            </div>
          </motion.div>
        ))}
      </div>
    </Card>
  );
};
