'use client';

import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, RefreshCw, Sparkles, ShieldCheck } from 'lucide-react';
import Link from 'next/link';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { useInterviewReadinessStore } from '@/store/useInterviewReadinessStore';
import { ReadinessScoreCard } from '@/components/readiness/ReadinessScoreCard';
import { CompanyMatchCard } from '@/components/readiness/CompanyMatchCard';
import { SkillAnalysisCard } from '@/components/readiness/SkillAnalysisCard';
import { KnowledgeCoverageCard } from '@/components/readiness/KnowledgeCoverageCard';
import { ConfidenceRadarCard } from '@/components/readiness/ConfidenceRadarCard';
import { MissingTopicsCard } from '@/components/readiness/MissingTopicsCard';
import { PreparationTimeline } from '@/components/readiness/PreparationTimeline';
import { ReadinessComparisonCard } from '@/components/readiness/ReadinessComparisonCard';
import { PreparationChecklist } from '@/components/readiness/PreparationChecklist';
import { CareerInsightCard } from '@/components/readiness/CareerInsightCard';
import { QuickActionsCard } from '@/components/readiness/QuickActionsCard';

export default function InterviewReadinessPage() {
  const {
    data,
    isLoading,
    fetchData,
    selectedCompanyId,
    setSelectedCompany,
    toggleChecklistItem,
    activeTimeframeDays,
    setActiveTimeframeDays,
  } = useInterviewReadinessStore();

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-screen p-6 text-center space-y-4">
        <div className="h-12 w-12 rounded-2xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center animate-spin text-blue-400">
          <RefreshCw className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-white">Analyzing AI Interview Readiness Profile...</h3>
        <p className="text-xs text-slate-400 max-w-sm">
          Evaluating 12 CS knowledge areas, 10 target company hiring benchmarks, and resume optimization metrics.
        </p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="flex-1 space-y-6 pb-16"
    >
      <DashboardHeader
        title="AI Interview Readiness Predictor"
        subtitle="Predictive readiness analytics, target company match scores, and personalized preparation roadmaps"
      />

      <main className="p-6 max-w-7xl mx-auto space-y-8">
        {/* Top Breadcrumb & Refresh Bar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <Link
            href="/dashboard/resume-optimizer"
            className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Resume Optimizer
          </Link>

          <div className="flex items-center gap-3 self-end sm:self-auto">
            <span className="text-xs text-slate-400 font-mono">Last Evaluated: {data.lastUpdated}</span>
            <Button size="sm" variant="outline" className="gap-2 text-xs" onClick={() => fetchData()}>
              <RefreshCw className="w-3.5 h-3.5" /> Re-evaluate Score
            </Button>
          </div>
        </div>

        {/* 1. Overall Interview Readiness Score */}
        <section aria-label="Overall Interview Readiness Score">
          <ReadinessScoreCard data={data} />
        </section>

        {/* 2. Company Role Match */}
        <section aria-label="Company Role Match">
          <CompanyMatchCard
            companies={data.companies}
            selectedCompanyId={selectedCompanyId}
            onSelectCompany={setSelectedCompany}
          />
        </section>

        {/* 3. Skill Readiness Analysis */}
        <section aria-label="Skill Readiness Analysis">
          <SkillAnalysisCard skills={data.skills} />
        </section>

        {/* 4. Technical Knowledge Coverage */}
        <section aria-label="Technical Knowledge Coverage">
          <KnowledgeCoverageCard categories={data.technicalKnowledge} />
        </section>

        {/* 5. Interview Confidence Dashboard */}
        <section aria-label="Interview Confidence Dashboard">
          <ConfidenceRadarCard confidenceScores={data.confidenceDashboard} />
        </section>

        {/* 6 & 7. Missing Topics & Personalized AI Action Plan Roadmap */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <section aria-label="Missing Topics Before Interview">
            <MissingTopicsCard topics={data.missingTopics} />
          </section>

          <section aria-label="Personalized AI Action Plan Roadmap">
            <PreparationTimeline actionPlan={data.actionPlan} />
          </section>
        </div>

        {/* 8 & 9. Estimated Preparation Time & Expected Improvement */}
        <section aria-label="Estimated Preparation Time & Expected Improvement">
          <ReadinessComparisonCard
            comparison={data.comparison}
            timeframes={data.preparationTimeframes}
            activeTimeframeDays={activeTimeframeDays}
            onSelectTimeframe={setActiveTimeframeDays}
          />
        </section>

        {/* 10. Interview Preparation Checklist */}
        <section aria-label="Interview Preparation Checklist">
          <PreparationChecklist checklist={data.checklist} onToggle={toggleChecklistItem} />
        </section>

        {/* 11. AI Career Insights */}
        <section aria-label="AI Career Insights">
          <CareerInsightCard insights={data.careerInsights} />
        </section>

        {/* 12. Quick Actions */}
        <section aria-label="Quick Actions">
          <QuickActionsCard />
        </section>
      </main>
    </motion.div>
  );
}
