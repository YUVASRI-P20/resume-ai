'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, Code2, Award, Briefcase, GitBranch, Globe, Layout, ArrowUpRight } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { CareerInsight } from '@/types/interviewReadiness';

interface CareerInsightCardProps {
  insights: CareerInsight[];
}

export const CareerInsightCard: React.FC<CareerInsightCardProps> = ({ insights }) => {
  const [activeTab, setActiveTab] = useState<string>('all');

  const filteredInsights =
    activeTab === 'all' ? insights : insights.filter((item) => item.type === activeTab);

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'technology': return <Code2 className="w-4 h-4 text-blue-400" />;
      case 'certification': return <Award className="w-4 h-4 text-purple-400" />;
      case 'project': return <Briefcase className="w-4 h-4 text-emerald-400" />;
      case 'github': return <GitBranch className="w-4 h-4 text-slate-200" />;
      case 'linkedin': return <Globe className="w-4 h-4 text-blue-500" />;
      default: return <Layout className="w-4 h-4 text-amber-400" />;
    }
  };

  return (
    <Card className="p-6 space-y-6 bg-slate-900/80 border-slate-800 backdrop-blur-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-amber-400" />
            <h3 className="text-lg font-bold text-white">AI Career Insights & Recommendations</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Tailored suggestions to boost recruiter callback rates and land tier-1 interviews.
          </p>
        </div>

        <Badge variant="primary" className="text-xs">
          {insights.length} AI Recommendations
        </Badge>
      </div>

      {/* Insight Category Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 text-xs border-b border-slate-800 scrollbar-none">
        <button
          onClick={() => setActiveTab('all')}
          className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
            activeTab === 'all'
              ? 'bg-blue-600 text-white'
              : 'text-slate-400 hover:text-white bg-slate-950/60 border border-slate-800'
          }`}
        >
          All Recommendations
        </button>
        <button
          onClick={() => setActiveTab('technology')}
          className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
            activeTab === 'technology'
              ? 'bg-blue-600 text-white'
              : 'text-slate-400 hover:text-white bg-slate-950/60 border border-slate-800'
          }`}
        >
          Tech Stack
        </button>
        <button
          onClick={() => setActiveTab('certification')}
          className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
            activeTab === 'certification'
              ? 'bg-purple-600 text-white'
              : 'text-slate-400 hover:text-white bg-slate-950/60 border border-slate-800'
          }`}
        >
          Certifications
        </button>
        <button
          onClick={() => setActiveTab('project')}
          className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
            activeTab === 'project'
              ? 'bg-emerald-600 text-white'
              : 'text-slate-400 hover:text-white bg-slate-950/60 border border-slate-800'
          }`}
        >
          Projects
        </button>
        <button
          onClick={() => setActiveTab('github')}
          className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
            activeTab === 'github'
              ? 'bg-slate-700 text-white'
              : 'text-slate-400 hover:text-white bg-slate-950/60 border border-slate-800'
          }`}
        >
          GitHub & LinkedIn
        </button>
      </div>

      {/* Grid of Insight Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredInsights.map((insight, idx) => (
          <motion.div
            key={insight.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: idx * 0.05 }}
            className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 space-y-3 flex flex-col justify-between hover:border-slate-700 transition-all"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-xl bg-slate-900 border border-slate-800">
                    {getInsightIcon(insight.type)}
                  </div>
                  <h4 className="text-sm font-bold text-white tracking-tight">{insight.title}</h4>
                </div>
                <Badge variant="success" className="text-[10px] font-mono">
                  {insight.impactScore}
                </Badge>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">{insight.description}</p>
            </div>

            <div className="space-y-3 pt-2">
              <div className="flex flex-wrap gap-1.5">
                {insight.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="text-[10px]">
                    {tag}
                  </Badge>
                ))}
              </div>

              <Button size="sm" variant="outline" className="w-full justify-center gap-1.5 text-xs">
                <span>{insight.actionText}</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </Button>
            </div>
          </motion.div>
        ))}
      </div>
    </Card>
  );
};
