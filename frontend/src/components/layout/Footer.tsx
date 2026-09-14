import React from 'react';
import Link from 'next/link';
import { Cpu, Globe, Code2, Share2 } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800 bg-slate-950 text-slate-400 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-5 gap-10">
        {/* Brand Column */}
        <div className="md:col-span-2 space-y-4">
          <Link href="/" className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-blue-600 to-purple-600 p-0.5">
              <div className="h-full w-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Cpu className="h-4 w-4 text-blue-400" />
              </div>
            </div>
            <span className="font-bold text-lg text-white">InterviewIQ AI</span>
          </Link>
          <p className="text-sm text-slate-400 max-w-sm">
            Your personal AI Technical Interview Coach. Adaptive mock interviews, knowledge gap detection, hallucination verification, and real-time coding assessments.
          </p>
          <div className="flex space-x-4 pt-2">
            <a href="#" className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors">
              <Code2 className="w-4 h-4" />
            </a>
            <a href="#" className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors">
              <Globe className="w-4 h-4" />
            </a>
            <a href="#" className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors">
              <Share2 className="w-4 h-4" />
            </a>
          </div>
        </div>

        {/* Product Links */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">Product</h4>
          <ul className="space-y-2 text-sm">
            <li><Link href="#features" className="hover:text-white transition-colors">AI Interview Engine</Link></li>
            <li><Link href="/dashboard/coding-interview" className="hover:text-white transition-colors">Coding Simulator</Link></li>
            <li><Link href="/dashboard/knowledge-graph" className="hover:text-white transition-colors">Knowledge Graph</Link></li>
            <li><Link href="/dashboard/roadmap" className="hover:text-white transition-colors">Learning Roadmap</Link></li>
            <li><Link href="/dashboard/recruiter" className="hover:text-white transition-colors">Recruiter Suite</Link></li>
          </ul>
        </div>

        {/* Target Companies */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">Prep Tracks</h4>
          <ul className="space-y-2 text-sm">
            <li><Link href="/dashboard/interview-setup" className="hover:text-white transition-colors">Vercel & Next.js</Link></li>
            <li><Link href="/dashboard/interview-setup" className="hover:text-white transition-colors">Stripe System Design</Link></li>
            <li><Link href="/dashboard/interview-setup" className="hover:text-white transition-colors">OpenAI AI/ML</Link></li>
            <li><Link href="/dashboard/interview-setup" className="hover:text-white transition-colors">Linear UI Systems</Link></li>
            <li><Link href="/dashboard/interview-setup" className="hover:text-white transition-colors">Apple Web Client</Link></li>
          </ul>
        </div>

        {/* Legal & System */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">Company</h4>
          <ul className="space-y-2 text-sm">
            <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
            <li><a href="#" className="hover:text-white transition-colors">FastAPI Specs</a></li>
            <li><span className="inline-flex items-center gap-1.5 text-xs text-emerald-400 font-mono"><span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> All Systems Operational</span></li>
          </ul>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12 pt-8 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500">
        <p>© 2026 InterviewIQ AI. Built for Final Year Project demonstration.</p>
        <p className="font-mono">API Ready for FastAPI Backend Integration</p>
      </div>
    </footer>
  );
};
