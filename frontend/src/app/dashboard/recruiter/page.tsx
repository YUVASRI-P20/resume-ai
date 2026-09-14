'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Users,
  ShieldCheck,
  FileSpreadsheet,
  ArrowRight,
  Sparkles,
  Download,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { MOCK_RECRUITER_CANDIDATES } from '@/constants/mockData';

export default function RecruiterDashboardPage() {
  const candidates = MOCK_RECRUITER_CANDIDATES;
  const [selectedCandidateA, setSelectedCandidateA] = useState(candidates[0]);
  const [selectedCandidateB, setSelectedCandidateB] = useState(candidates[1]);

  return (
    <div className="flex-1 space-y-6">
      <DashboardHeader
        title="Enterprise Recruiter & Hiring Suite"
        subtitle="Evaluate AI interview reports, compare candidate technical readiness side-by-side, and export hiring recommendations."
      />

      <main className="p-6 max-w-7xl mx-auto space-y-8">
        {/* Candidate List Roster */}
        <Card className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Badge variant="secondary">ENTERPRISE TALENT PIPELINE</Badge>
              <h3 className="text-lg font-bold text-white">Evaluated Candidates</h3>
            </div>
            <Button variant="outline" size="sm" className="gap-1.5 text-xs">
              <Download className="w-3.5 h-3.5" /> Export All PDF Reports
            </Button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-sans">
              <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 font-mono text-[10px] uppercase">
                <tr>
                  <th className="p-3">Candidate</th>
                  <th className="p-3">Applied Role</th>
                  <th className="p-3">Overall Score</th>
                  <th className="p-3">Tech Score</th>
                  <th className="p-3">Resume Match</th>
                  <th className="p-3">AI Recommendation</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {candidates.map((cand) => (
                  <tr key={cand.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="p-3 flex items-center space-x-3">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={cand.avatarUrl} alt={cand.name} className="w-8 h-8 rounded-full object-cover ring-1 ring-blue-500/30" />
                      <div>
                        <h4 className="font-bold text-white">{cand.name}</h4>
                        <span className="text-[10px] text-slate-400 font-mono">{cand.interviewDate}</span>
                      </div>
                    </td>
                    <td className="p-3 text-slate-300 font-medium">{cand.appliedRole}</td>
                    <td className="p-3 font-mono font-bold text-blue-400 text-sm">{cand.overallScore}%</td>
                    <td className="p-3 font-mono text-purple-400">{cand.technicalScore}%</td>
                    <td className="p-3 font-mono text-emerald-400">{cand.resumeMatchScore}%</td>
                    <td className="p-3">
                      <Badge variant={cand.recommendation === 'Strong Hire' ? 'success' : 'primary'}>
                        {cand.recommendation}
                      </Badge>
                    </td>
                    <td className="p-3 text-right">
                      <Link href={`/dashboard/recruiter/candidate/${cand.id}`}>
                        <Button variant="ghost" size="sm" className="gap-1 text-xs">
                          <span>View Report</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Side-by-Side Comparison Matrix */}
        <Card className="p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <FileSpreadsheet className="w-5 h-5 text-purple-400" /> Side-by-Side Candidate Comparison Matrix
            </h3>
            <span className="text-xs text-slate-400 font-mono">Select two candidates to compare metrics</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Candidate A Card */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="flex items-center space-x-3">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={selectedCandidateA.avatarUrl} alt={selectedCandidateA.name} className="w-10 h-10 rounded-full object-cover ring-2 ring-blue-500/30" />
                <div>
                  <h4 className="font-bold text-white">{selectedCandidateA.name}</h4>
                  <span className="text-xs text-blue-400 font-mono">{selectedCandidateA.appliedRole}</span>
                </div>
              </div>

              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between p-2 rounded bg-slate-950">
                  <span className="text-slate-400">Technical Competency:</span>
                  <span className="font-bold text-blue-400">{selectedCandidateA.technicalScore}%</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-950">
                  <span className="text-slate-400">Communication Clarity:</span>
                  <span className="font-bold text-emerald-400">{selectedCandidateA.communicationScore}%</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-950">
                  <span className="text-slate-400">Resume Match:</span>
                  <span className="font-bold text-purple-400">{selectedCandidateA.resumeMatchScore}%</span>
                </div>
              </div>
            </div>

            {/* Candidate B Card */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="flex items-center space-x-3">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={selectedCandidateB.avatarUrl} alt={selectedCandidateB.name} className="w-10 h-10 rounded-full object-cover ring-2 ring-purple-500/30" />
                <div>
                  <h4 className="font-bold text-white">{selectedCandidateB.name}</h4>
                  <span className="text-xs text-purple-400 font-mono">{selectedCandidateB.appliedRole}</span>
                </div>
              </div>

              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between p-2 rounded bg-slate-950">
                  <span className="text-slate-400">Technical Competency:</span>
                  <span className="font-bold text-blue-400">{selectedCandidateB.technicalScore}%</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-950">
                  <span className="text-slate-400">Communication Clarity:</span>
                  <span className="font-bold text-emerald-400">{selectedCandidateB.communicationScore}%</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-950">
                  <span className="text-slate-400">Resume Match:</span>
                  <span className="font-bold text-purple-400">{selectedCandidateB.resumeMatchScore}%</span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </main>
    </div>
  );
}
