import React from 'react';
import { Cpu } from 'lucide-react';

export default function GlobalLoading() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col items-center justify-center p-4 bg-grid-pattern space-y-4">
      <div className="h-16 w-16 rounded-3xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 p-1 shadow-2xl shadow-blue-500/30 animate-pulse">
        <div className="h-full w-full bg-slate-950 rounded-[22px] flex items-center justify-center">
          <Cpu className="h-8 w-8 text-blue-400 animate-spin" />
        </div>
      </div>
      <div className="space-y-1 text-center font-mono">
        <h3 className="text-base font-bold text-white tracking-wider">InterviewIQ AI</h3>
        <p className="text-xs text-slate-400">Loading Technical Interview Environment...</p>
      </div>
    </div>
  );
}
