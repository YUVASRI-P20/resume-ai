import React from 'react';
import Link from 'next/link';
import { Calendar, Clock, ArrowRight, CheckCircle2, Award, Zap } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { InterviewSession } from '@/types/interview';

interface InterviewCardProps {
  interview: InterviewSession;
}

export const InterviewCard: React.FC<InterviewCardProps> = ({ interview }) => {
  const isCompleted = interview.status === 'Completed';

  return (
    <Card className="flex flex-col justify-between group">
      <div className="space-y-4">
        {/* Header Badge & Title */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-slate-900 border border-slate-700 flex items-center justify-center text-xl shadow-inner">
              {interview.companyLogo || '💼'}
            </div>
            <div>
              <span className="text-xs font-semibold text-blue-400 font-mono">{interview.companyName}</span>
              <h3 className="font-bold text-base text-white group-hover:text-blue-300 transition-colors line-clamp-1">
                {interview.title}
              </h3>
            </div>
          </div>
          <Badge variant={isCompleted ? 'success' : 'primary'}>
            {interview.status}
          </Badge>
        </div>

        {/* Domain & Level Info */}
        <div className="flex items-center space-x-2 text-xs text-slate-400 font-medium">
          <span className="px-2 py-0.5 rounded-lg bg-slate-900 border border-slate-700">{interview.domain}</span>
          <span>•</span>
          <span className="px-2 py-0.5 rounded-lg bg-slate-900 border border-slate-700">{interview.difficulty}</span>
        </div>

        {/* Scores Gauge if completed */}
        {isCompleted && interview.overallScore !== undefined && (
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-700/60 grid grid-cols-3 gap-2 text-center">
            <div>
              <span className="text-[10px] text-slate-400 font-mono block">Overall</span>
              <span className="text-base font-bold text-blue-400 font-mono">{interview.overallScore}%</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-mono block">Technical</span>
              <span className="text-base font-bold text-purple-400 font-mono">{interview.technicalScore}%</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-mono block">Readiness</span>
              <span className="text-base font-bold text-emerald-400 font-mono">{interview.readinessScore}%</span>
            </div>
          </div>
        )}
      </div>

      {/* Footer Info & CTA */}
      <div className="pt-4 mt-4 border-t border-slate-700/50 flex items-center justify-between">
        <div className="flex items-center space-x-3 text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" /> {interview.durationMinutes}m
          </span>
          <span className="flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5" /> {new Date(interview.createdAt).toLocaleDateString()}
          </span>
        </div>

        <Link href={isCompleted ? `/dashboard/ai-feedback` : `/dashboard/live-interview`}>
          <Button variant={isCompleted ? 'secondary' : 'glow'} size="sm" className="gap-1 text-xs">
            <span>{isCompleted ? 'View Analysis' : 'Resume Mock'}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Button>
        </Link>
      </div>
    </Card>
  );
};
