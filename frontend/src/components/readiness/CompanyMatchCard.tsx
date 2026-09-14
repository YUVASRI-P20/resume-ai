'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Building2, CheckCircle2, XCircle, TrendingUp, DollarSign, Award, ChevronRight, BarChart3, Grid } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { CompanyMatch } from '@/types/interviewReadiness';

interface CompanyMatchCardProps {
  companies: CompanyMatch[];
  selectedCompanyId: string;
  onSelectCompany: (id: string) => void;
}

export const CompanyMatchCard: React.FC<CompanyMatchCardProps> = ({
  companies,
  selectedCompanyId,
  onSelectCompany,
}) => {
  const [viewMode, setViewMode] = useState<'cards' | 'chart'>('cards');

  const activeCompany = companies.find((c) => c.id === selectedCompanyId) || companies[0];

  // Recharts data
  const chartData = companies.map((c) => ({
    name: c.name,
    matchScore: c.matchScore,
    id: c.id,
  }));

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
    if (score >= 80) return 'text-blue-400 border-blue-500/30 bg-blue-500/10';
    if (score >= 70) return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
  };

  const getBarFill = (score: number) => {
    if (score >= 90) return '#10b981';
    if (score >= 80) return '#3b82f6';
    if (score >= 70) return '#f59e0b';
    return '#f43f5e';
  };

  return (
    <Card className="p-6 space-y-6 bg-slate-900/80 border-slate-800 backdrop-blur-xl">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Building2 className="w-5 h-5 text-blue-400" />
            <h3 className="text-lg font-bold text-white">Target Company Role Match</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time AI evaluation comparing your resume & skill profile against hiring benchmarks of top companies.
          </p>
        </div>

        {/* View Switcher Tabs */}
        <div className="flex items-center rounded-xl bg-slate-950 p-1 border border-slate-800 self-end sm:self-auto">
          <button
            onClick={() => setViewMode('cards')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              viewMode === 'cards'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Grid className="w-3.5 h-3.5" /> Grid View
          </button>
          <button
            onClick={() => setViewMode('chart')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              viewMode === 'chart'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" /> Chart View
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      {viewMode === 'cards' ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {companies.map((company) => {
            const isSelected = company.id === activeCompany.id;
            return (
              <motion.button
                key={company.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => onSelectCompany(company.id)}
                className={`p-3.5 rounded-2xl border text-left transition-all relative overflow-hidden flex flex-col justify-between ${
                  isSelected
                    ? 'border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/10 ring-1 ring-blue-500'
                    : 'border-slate-800 bg-slate-950/60 hover:border-slate-700 hover:bg-slate-900/60'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-sm text-white">{company.name}</span>
                  <Badge variant={company.matchScore >= 85 ? 'success' : 'outline'} className="text-[10px]">
                    {company.matchScore}% Match
                  </Badge>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden mt-1">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      company.matchScore >= 90
                        ? 'bg-emerald-400'
                        : company.matchScore >= 80
                        ? 'bg-blue-400'
                        : 'bg-amber-400'
                    }`}
                    style={{ width: `${company.matchScore}%` }}
                  />
                </div>
              </motion.button>
            );
          })}
        </div>
      ) : (
        <div className="h-64 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis stroke="#94a3b8" fontSize={11} domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#090d16',
                  borderColor: '#1e293b',
                  borderRadius: '12px',
                  color: '#fff',
                  fontSize: '12px',
                }}
                formatter={(value: any) => [`${value}% Match Score`, 'Readiness Match']}
              />
              <Bar
                dataKey="matchScore"
                radius={[8, 8, 0, 0]}
                onClick={(entry: any) => entry && entry.id && onSelectCompany(entry.id)}
                className="cursor-pointer"
              >
                {chartData.map((entry) => (
                  <Cell key={`cell-${entry.id}`} fill={getBarFill(entry.matchScore)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Selected Company Focus Card */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeCompany.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3 }}
          className="rounded-2xl border border-slate-800 bg-slate-950/80 p-5 space-y-4"
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800/80">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center font-extrabold text-white text-lg shadow-md">
                {activeCompany.name.charAt(0)}
              </div>
              <div>
                <h4 className="text-base font-bold text-white flex items-center gap-2">
                  {activeCompany.name}
                  <span className="text-xs font-normal text-slate-400">• {activeCompany.role}</span>
                </h4>
                <div className="flex items-center gap-3 text-xs text-slate-400 mt-0.5">
                  <span className="flex items-center gap-1">
                    <Award className="w-3.5 h-3.5 text-amber-400" /> Difficulty: {activeCompany.hiringDifficulty}
                  </span>
                  <span className="flex items-center gap-1">
                    <DollarSign className="w-3.5 h-3.5 text-emerald-400" /> Package: {activeCompany.averagePackage}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 self-end sm:self-auto">
              <div className={`px-4 py-2 rounded-xl border font-mono font-bold text-lg ${getScoreColor(activeCompany.matchScore)}`}>
                {activeCompany.matchScore}% Match
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4 text-xs">
            {/* Matched Skills */}
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3.5 space-y-2">
              <div className="flex items-center gap-1.5 text-emerald-400 font-semibold uppercase tracking-wider text-[11px]">
                <CheckCircle2 className="w-4 h-4" /> Matched Benchmark Skills ({activeCompany.keySkillsMatched.length})
              </div>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {activeCompany.keySkillsMatched.map((skill) => (
                  <Badge key={skill} variant="success" className="text-[11px]">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Missing Critical Skills */}
            <div className="rounded-xl border border-rose-500/20 bg-rose-500/5 p-3.5 space-y-2">
              <div className="flex items-center gap-1.5 text-rose-400 font-semibold uppercase tracking-wider text-[11px]">
                <XCircle className="w-4 h-4" /> Missing Gap Skills to Reach 95%+ ({activeCompany.missingCriticalSkills.length})
              </div>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {activeCompany.missingCriticalSkills.map((skill) => (
                  <Badge key={skill} variant="error" className="text-[11px]">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </Card>
  );
};
