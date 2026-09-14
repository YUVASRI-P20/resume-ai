import React from 'react';
import { cn } from '@/utils/cn';

interface ProgressBarProps {
  progress: number;
  label?: string;
  showPercentage?: boolean;
  color?: 'blue' | 'purple' | 'emerald' | 'gradient';
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  label,
  showPercentage = true,
  color = 'blue',
  className,
}) => {
  const cappedProgress = Math.min(Math.max(progress, 0), 100);

  const colorVariants = {
    blue: 'bg-blue-600',
    purple: 'bg-indigo-600',
    emerald: 'bg-emerald-500',
    gradient: 'bg-gradient-to-r from-blue-600 to-sky-500',
  };

  return (
    <div className={cn('w-full space-y-1.5', className)}>
      {(label || showPercentage) && (
        <div className="flex justify-between items-center text-xs font-medium text-slate-600">
          {label && <span>{label}</span>}
          {showPercentage && <span className="text-slate-500 font-mono">{cappedProgress}%</span>}
        </div>
      )}
      <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden border border-slate-200">
        <div
          className={cn('h-full rounded-full transition-all duration-500 ease-out', colorVariants[color])}
          style={{ width: `${cappedProgress}%` }}
        />
      </div>
    </div>
  );
};
