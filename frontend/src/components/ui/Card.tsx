import React from 'react';
import { cn } from '@/utils/cn';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hoverEffect?: boolean;
  glass?: boolean;
}

export const Card: React.FC<CardProps> = ({
  className,
  hoverEffect = true,
  glass = true,
  children,
  ...props
}) => {
  return (
    <div
      className={cn(
        'rounded-2xl border p-6 transition-all duration-200',
        glass
          ? 'bg-white border-slate-200 shadow-sm'
          : 'bg-slate-50 border-slate-200 text-slate-900',
        hoverEffect && 'hover:border-blue-300 hover:shadow-md hover:shadow-blue-100',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
