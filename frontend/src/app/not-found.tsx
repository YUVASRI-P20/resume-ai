import React from 'react';
import Link from 'next/link';
import { Cpu, ArrowLeft, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex items-center justify-center p-4 bg-grid-pattern relative">
      <div className="w-full max-w-md space-y-6 text-center relative z-10">
        <div className="w-20 h-20 rounded-3xl bg-red-500/10 border border-red-500/30 flex items-center justify-center mx-auto text-red-400 shadow-xl">
          <AlertTriangle className="w-10 h-10 animate-bounce" />
        </div>

        <div className="space-y-2">
          <span className="text-4xl font-extrabold text-white font-mono">404</span>
          <h1 className="text-2xl font-bold text-white tracking-tight">Question Route Not Found</h1>
          <p className="text-xs text-slate-400">The technical interview route you were looking for does not exist or has been archived.</p>
        </div>

        <div className="pt-2">
          <Link href="/dashboard">
            <Button variant="glow" size="md" className="gap-2">
              <ArrowLeft className="w-4 h-4" /> Return to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
