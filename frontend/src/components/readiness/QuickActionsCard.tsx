'use client';

import React from 'react';
import Link from 'next/link';
import { Video, FileText, Sparkles, Map, TrendingUp, Zap } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export const QuickActionsCard: React.FC = () => {
  return (
    <Card className="p-6 space-y-4 bg-slate-900/80 border-slate-800 backdrop-blur-xl">
      <div className="flex items-center gap-2">
        <Zap className="w-5 h-5 text-amber-400" />
        <h3 className="text-lg font-bold text-white">Next Steps & Quick Actions</h3>
      </div>
      <p className="text-xs text-slate-400">
        Jump straight into action to accelerate your preparation trajectory.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 pt-2">
        <Link href="/dashboard/interview-setup">
          <Button variant="glow" className="w-full justify-center gap-2 text-xs py-3">
            <Video className="w-4 h-4 text-blue-300" /> Start AI Interview
          </Button>
        </Link>

        <Link href="/dashboard/resume-analysis">
          <Button variant="secondary" className="w-full justify-center gap-2 text-xs py-3">
            <FileText className="w-4 h-4 text-emerald-400" /> View Resume Analysis
          </Button>
        </Link>

        <Link href="/dashboard/resume-optimizer">
          <Button variant="secondary" className="w-full justify-center gap-2 text-xs py-3">
            <Sparkles className="w-4 h-4 text-purple-400" /> View Resume Optimizer
          </Button>
        </Link>

        <Link href="/dashboard/roadmap">
          <Button variant="secondary" className="w-full justify-center gap-2 text-xs py-3">
            <Map className="w-4 h-4 text-indigo-400" /> Open Learning Roadmap
          </Button>
        </Link>

        <Link href="/dashboard/progress">
          <Button variant="secondary" className="w-full justify-center gap-2 text-xs py-3">
            <TrendingUp className="w-4 h-4 text-amber-400" /> View Progress Dashboard
          </Button>
        </Link>
      </div>
    </Card>
  );
};
