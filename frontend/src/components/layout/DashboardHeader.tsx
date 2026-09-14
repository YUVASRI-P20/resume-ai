'use client';

import React from 'react';
import Link from 'next/link';
import { Search, Bell, Plus } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface DashboardHeaderProps {
  title?: string;
  subtitle?: string;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  title = 'Dashboard Overview',
  subtitle = '',
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/90 backdrop-blur px-6 py-4 flex items-center justify-between">
      {/* Title & Subtitle */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          {title}
        </h1>
        {subtitle && (
          <p className="text-xs text-slate-500 font-medium hidden sm:block">{subtitle}</p>
        )}
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-4">
        {/* Search Bar */}
        <div className="relative hidden lg:block w-64">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search topics, questions..."
            className="w-full h-9 pl-9 pr-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-500 transition-all"
          />
        </div>

        {/* Notifications Icon */}
        <Link href="/dashboard/notifications" className="relative p-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-600 hover:text-blue-700 hover:border-blue-300 transition-colors">
          <Bell className="w-4 h-4" />
        </Link>

        {/* Start Interview Quick Action */}
        <Link href="/dashboard/interview-setup">
          <Button variant="primary" size="sm" className="gap-1.5">
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Start Interview</span>
          </Button>
        </Link>
      </div>
    </header>
  );
};
