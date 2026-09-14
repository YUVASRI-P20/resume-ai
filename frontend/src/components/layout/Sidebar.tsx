'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  LayoutDashboard,
  FileText,
  Video,
  Code2,
  BrainCircuit,
  Network,
  Map,
  PlaySquare,
  History,
  TrendingUp,
  Users,
  Settings,
  Bell,
  User,
  LogOut,
  Cpu,
  Sparkles,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { useAuthStore } from '@/store/useAuthStore';

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  badge?: string;
  section?: string;
}

const navItems: NavItem[] = [
  { label: 'Overview', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Resume Analyzer', href: '/dashboard/resume-upload', icon: FileText, section: 'INTERVIEW PREP' },
  { label: 'Readiness Predictor', href: '/dashboard/interview-readiness', icon: Sparkles },
  { label: 'AI Technical Interview', href: '/dashboard/interview-setup', icon: Video },
  { label: 'Coding Interview', href: '/dashboard/coding-interview', icon: Code2 },
  { label: 'AI Feedback & Scores', href: '/dashboard/ai-feedback', icon: BrainCircuit, section: 'ANALYTICS' },
  { label: 'Knowledge Graph', href: '/dashboard/knowledge-graph', icon: Network },
  { label: 'Learning Roadmap', href: '/dashboard/roadmap', icon: Map },
  { label: 'Interview Replay', href: '/dashboard/replay', icon: PlaySquare },
  { label: 'Interview History', href: '/dashboard/history', icon: History, section: 'PROGRESS' },
  { label: 'Progress Analytics', href: '/dashboard/progress', icon: TrendingUp },
  { label: 'Recruiter Portal', href: '/dashboard/recruiter', icon: Users },
  { label: 'Profile', href: '/dashboard/profile', icon: User, section: 'ACCOUNT' },
  { label: 'Notifications', href: '/dashboard/notifications', icon: Bell },
  { label: 'Settings', href: '/dashboard/settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuthStore();

  return (
    <aside className="w-64 border-r border-slate-200 bg-white flex flex-col justify-between shrink-0 h-screen sticky top-0">
      <div className="flex flex-col flex-1 overflow-y-auto px-4 py-6 scrollbar-none">
        {/* Brand */}
        <Link href="/dashboard" className="flex items-center space-x-3 px-2 mb-6 group">
          <div className="h-9 w-9 rounded-xl bg-blue-600 flex items-center justify-center shadow-sm">
            <Cpu className="h-4 w-4 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-base tracking-tight text-slate-900 flex items-center gap-1">
              InterviewIQ <span className="text-[10px] px-1.5 py-0.2 rounded bg-blue-50 text-blue-700 font-mono border border-blue-200">AI</span>
            </span>
          </div>
        </Link>

        {/* Navigation Items */}
        <nav className="space-y-1">
          {navItems.map((item, idx) => {
            const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
            const Icon = item.icon;

            return (
              <React.Fragment key={item.href}>
                {item.section && idx !== 0 && (
                  <div className="pt-4 pb-2 px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                    {item.section}
                  </div>
                )}
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all group',
                    isActive
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  )}
                >
                  <div className="flex items-center space-x-3">
                    <Icon
                      className={cn(
                        'h-4 w-4 transition-colors',
                        isActive ? 'text-blue-600' : 'text-slate-400 group-hover:text-slate-600'
                      )}
                    />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                      {item.badge}
                    </span>
                  )}
                </Link>
              </React.Fragment>
            );
          })}
        </nav>
      </div>

      {/* User Footer Bar */}
      <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
        <div className="flex items-center space-x-3 overflow-hidden">
          <div className="h-9 w-9 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center shrink-0">
            {(user?.name || 'U').charAt(0).toUpperCase()}
          </div>
          <div className="flex flex-col truncate">
            <span className="text-xs font-semibold text-slate-900 truncate">{user?.name || 'Account'}</span>
            <span className="text-[11px] text-slate-500 truncate">{user?.email || ''}</span>
          </div>
        </div>
        <button
          onClick={async () => {
            await logout();
            router.push('/login');
          }}
          title="Sign Out"
          className="p-2 rounded-lg text-slate-400 hover:text-red-600 hover:bg-white transition-colors"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </aside>
  );
};
