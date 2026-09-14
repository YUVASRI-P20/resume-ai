'use client';

import React from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { ShieldCheck, Download, ArrowLeft, CheckCircle2, AlertTriangle, FileText, BrainCircuit } from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { MOCK_RECRUITER_CANDIDATES } from '@/constants/mockData';

export default function CandidateDetailPage() {
  const params = useParams();
  const id = params?.id as string;
  const candidate = MOCK_RECRUITER_CANDIDATES.find((c) => c.id === id) || MOCK_RECRUITER_CANDIDATES[0];

  return (
    <div className="flex-1 space-y-6">
      <DashboardHeader
        title={`Candidate Audit Report: ${candidate.name}`}
        subtitle={`Applied Role: ${candidate.appliedRole} • Interview Date: ${candidate.interviewDate}`}
      />

      <main className="p-6 max-w-6xl mx-auto space-y-8">
        <Link href="/dashboard/recruiter" className="inline-flex items-center space-x-2 text-xs text-slate-400 hover:text-white">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Candidate Pipeline</span>
        </Link>

        {/* Candidate Profile Header Card */}
        <Card className="glass-panel p-6 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center space-x-4">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={candidate.avatarUrl} alt={candidate.name} className="w-16 h-16 rounded-full object-cover ring-2 ring-blue-500/40" />
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <h2 className="text-xl font-bold text-white">{candidate.name}</h2>
                <Badge variant={candidate.recommendation === 'Strong Hire' ? 'success' : 'primary'}>
                  {candidate.recommendation}
                </Badge>
              </div>
              <p className="text-xs text-slate-400 font-mono">{candidate.appliedRole}</p>
            </div>
          </div>

          <Button variant="glow" size="sm" className="gap-2">
            <Download className="w-4 h-4" /> Download Official AI Hiring Report PDF
          </Button>
        </Card>

        {/* Score Cards Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="p-4 space-y-1 text-center">
            <span className="text-[10px] text-slate-400 font-mono uppercase">Overall AI Score</span>
            <div className="text-3xl font-extrabold text-blue-400 font-mono">{candidate.overallScore}%</div>
          </Card>
          <Card className="p-4 space-y-1 text-center">
            <span className="text-[10px] text-slate-400 font-mono uppercase">Technical Precision</span>
            <div className="text-3xl font-extrabold text-purple-400 font-mono">{candidate.technicalScore}%</div>
          </Card>
          <Card className="p-4 space-y-1 text-center">
            <span className="text-[10px] text-slate-400 font-mono uppercase">Communication</span>
            <div className="text-3xl font-extrabold text-emerald-400 font-mono">{candidate.communicationScore}%</div>
          </Card>
          <Card className="p-4 space-y-1 text-center">
            <span className="text-[10px] text-slate-400 font-mono uppercase">Resume Match</span>
            <div className="text-3xl font-extrabold text-amber-400 font-mono">{candidate.resumeMatchScore}%</div>
          </Card>
        </div>

        {/* Strengths vs Flagged Gaps */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="p-6 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" /> Key Demonstrated Strengths
            </h3>
            <ul className="space-y-2">
              {candidate.keyStrengths.map((str, idx) => (
                <li key={idx} className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-xs text-emerald-200">
                  {str}
                </li>
              ))}
            </ul>
          </Card>

          <Card className="p-6 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" /> Flagged Knowledge Gaps
            </h3>
            <ul className="space-y-2">
              {candidate.flaggedGaps.map((gap, idx) => (
                <li key={idx} className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-200">
                  {gap}
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </main>
    </div>
  );
}
