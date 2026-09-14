'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  Code,
  Binary,
  Cpu,
  Database,
  Server,
  Globe,
  Layers,
  Box,
  Table,
  GitBranch,
  Webhook,
  Cloud,
  CheckCircle2,
  BookOpen,
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { TechnicalKnowledgeCategory } from '@/types/interviewReadiness';

interface KnowledgeCoverageCardProps {
  categories: TechnicalKnowledgeCategory[];
}

const iconMap: Record<string, React.ElementType> = {
  Code,
  Binary,
  Cpu,
  Database,
  Server,
  Globe,
  Layers,
  Box,
  Table,
  GitBranch,
  Webhook,
  Cloud,
};

export const KnowledgeCoverageCard: React.FC<KnowledgeCoverageCardProps> = ({ categories }) => {
  return (
    <Card className="p-6 space-y-6 bg-slate-900/80 border-slate-800 backdrop-blur-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-blue-400" />
            <h3 className="text-lg font-bold text-white">Technical Knowledge Coverage</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Deep dive evaluation across 12 fundamental computer science and engineering domains.
          </p>
        </div>

        <Badge variant="primary" className="text-xs">
          12 Core Engineering Categories
        </Badge>
      </div>

      {/* Grid of 12 categories */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {categories.map((cat, idx) => {
          const IconComponent = iconMap[cat.iconName] || Code;
          const isTargetAchieved = cat.currentLevel >= cat.targetLevel;

          return (
            <motion.div
              key={cat.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: idx * 0.03 }}
              className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 space-y-3 hover:border-slate-700 transition-all group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 group-hover:bg-blue-500/20 transition-colors">
                    <IconComponent className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white tracking-tight">{cat.name}</h4>
                    <span className="text-[11px] text-slate-400">
                      {cat.topicsCovered}/{cat.totalTopics} Topics Covered
                    </span>
                  </div>
                </div>

                {isTargetAchieved ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : (
                  <span className="text-[11px] font-mono text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20">
                    Gap: -{cat.targetLevel - cat.currentLevel}%
                  </span>
                )}
              </div>

              {/* Levels & Bar */}
              <div className="space-y-1.5 pt-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">
                    Current Level: <strong className="text-white">{cat.currentLevel}%</strong>
                  </span>
                  <span className="text-slate-400">
                    Target: <strong className="text-blue-400">{cat.targetLevel}%</strong>
                  </span>
                </div>
                <ProgressBar
                  progress={cat.currentLevel}
                  color={isTargetAchieved ? 'emerald' : cat.currentLevel >= 70 ? 'blue' : 'purple'}
                  className="h-2"
                  showPercentage={false}
                />
              </div>
            </motion.div>
          );
        })}
      </div>
    </Card>
  );
};
