'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Route, CheckCircle2, Clock, ArrowRight, PlayCircle } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { ActionPlanStep } from '@/types/interviewReadiness';

interface PreparationTimelineProps {
  actionPlan: ActionPlanStep[];
}

export const PreparationTimeline: React.FC<PreparationTimelineProps> = ({ actionPlan }) => {
  return (
    <Card className="p-6 space-y-6 bg-slate-900/80 border-slate-800 backdrop-blur-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Route className="w-5 h-5 text-indigo-400" />
            <h3 className="text-lg font-bold text-white">Personalized AI Action Plan Roadmap</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Step-by-step preparation path optimized by AI to reach your target readiness score.
          </p>
        </div>

        <Badge variant="primary" className="text-xs">
          {actionPlan.length} Milestone Steps
        </Badge>
      </div>

      {/* Timeline List */}
      <div className="relative pl-6 sm:pl-8 space-y-8 before:absolute before:left-3 sm:before:left-4 before:top-3 before:bottom-3 before:w-0.5 before:bg-gradient-to-b before:from-emerald-500 before:via-blue-500 before:to-slate-800">
        {actionPlan.map((step, idx) => {
          const isCompleted = step.status === 'completed';
          const isInProgress = step.status === 'in_progress';

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4, delay: idx * 0.1 }}
              className="relative space-y-2"
            >
              {/* Timeline Bullet Node */}
              <div
                className={`absolute -left-6 sm:-left-8 top-1.5 h-6 w-6 rounded-full flex items-center justify-center border-2 transition-all ${
                  isCompleted
                    ? 'bg-emerald-500 border-emerald-400 text-slate-950 shadow-md shadow-emerald-500/20'
                    : isInProgress
                    ? 'bg-blue-600 border-blue-400 text-white animate-pulse shadow-md shadow-blue-500/20'
                    : 'bg-slate-950 border-slate-700 text-slate-500'
                }`}
              >
                {isCompleted ? (
                  <CheckCircle2 className="w-3.5 h-3.5" />
                ) : (
                  <span className="text-[10px] font-bold font-mono">{step.stepNumber}</span>
                )}
              </div>

              {/* Step Card Content */}
              <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 space-y-3 hover:border-slate-700 transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-slate-500 uppercase tracking-wider">Step {step.stepNumber}</span>
                    <Badge
                      variant={isCompleted ? 'success' : isInProgress ? 'primary' : 'outline'}
                      className="text-[10px]"
                    >
                      {isCompleted ? 'Completed' : isInProgress ? 'In Progress' : 'Upcoming'}
                    </Badge>
                    <Badge variant="secondary" className="text-[10px]">
                      {step.category}
                    </Badge>
                  </div>

                  <span className="text-xs font-mono text-slate-400 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-blue-400" /> Est: {step.estimatedHours} Hours
                  </span>
                </div>

                <div>
                  <h4 className="text-base font-bold text-white">{step.title}</h4>
                  <p className="text-xs text-slate-300 mt-1 leading-relaxed">{step.description}</p>
                </div>

                {step.actionRoute && (
                  <div className="pt-2 flex justify-end">
                    <Link href={step.actionRoute}>
                      <Button size="sm" variant={isInProgress ? 'glow' : 'outline'} className="gap-1.5 text-xs">
                        {isInProgress ? <PlayCircle className="w-3.5 h-3.5" /> : null}
                        <span>{isInProgress ? 'Continue Action' : 'View Details'}</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Button>
                    </Link>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </Card>
  );
};
