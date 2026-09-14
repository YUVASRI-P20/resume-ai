'use client';

import React from 'react';
import { Bell, CheckCircle2, Sparkles, AlertCircle, Clock, Calendar } from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export default function NotificationsPage() {
  const notifications = [
    {
      id: 'n_1',
      title: 'AI Feedback Report Ready',
      desc: 'Your Vercel Senior Frontend session feedback has been generated with a 91% overall score.',
      time: '10 minutes ago',
      type: 'feedback',
      unread: true,
    },
    {
      id: 'n_2',
      title: 'Weekly Roadmap Milestone Due',
      desc: 'Complete Task #5: Sliding Window Rate Limiters in Module 2.',
      time: '2 hours ago',
      type: 'roadmap',
      unread: true,
    },
    {
      id: 'n_3',
      title: 'Upcoming Mock Session Reminder',
      desc: 'Linear UI Design Systems mock scheduled for tomorrow at 3:00 PM.',
      time: '1 day ago',
      type: 'reminder',
      unread: false,
    },
  ];

  return (
    <div className="flex-1 space-y-6">
      <DashboardHeader
        title="Notifications & Activity Feed"
        subtitle="Stay updated on interview feedback reports, roadmap deadlines, and session reminders."
      />

      <main className="p-6 max-w-4xl mx-auto space-y-4">
        {notifications.map((n) => (
          <Card key={n.id} className={`p-4 flex items-start justify-between space-x-4 ${n.unread ? 'border-blue-500/40 bg-blue-950/20' : ''}`}>
            <div className="flex items-start space-x-3">
              <div className="p-2.5 rounded-xl bg-blue-600/10 text-blue-400 shrink-0">
                <Bell className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <h4 className="text-sm font-bold text-white">{n.title}</h4>
                  {n.unread && <Badge variant="primary" className="text-[9px]">UNREAD</Badge>}
                </div>
                <p className="text-xs text-slate-300">{n.desc}</p>
                <span className="text-[10px] text-slate-500 font-mono block">{n.time}</span>
              </div>
            </div>
          </Card>
        ))}
      </main>
    </div>
  );
}
