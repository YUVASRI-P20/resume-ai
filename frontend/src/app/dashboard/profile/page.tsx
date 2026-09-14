'use client';

import React, { useState } from 'react';
import {
  User,
  Mail,
  Building2,
  Briefcase,
  Award,
  Save,
  Sparkles,
  Code2,
  Link2,
  Globe,
  Phone,
  MapPin,
  FileText,
  CheckCircle2,
} from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { useAuthStore } from '@/store/useAuthStore';
import { useResumeStore } from '@/store/useResumeStore';

export default function ProfilePage() {
  const { user, updateProfile } = useAuthStore();
  const { currentAnalysis } = useResumeStore();

  const [name, setName] = useState(user?.name || 'Alex Chen');
  const [email, setEmail] = useState(user?.email || 'alex.chen@interviewiq.ai');
  const [role, setRole] = useState(user?.role || 'Fullstack');
  const [targetCompany, setTargetCompany] = useState(user?.targetCompany || 'Vercel');
  const [githubUrl, setGithubUrl] = useState(user?.githubUrl || 'https://github.com/alexchen-dev');
  const [linkedinUrl, setLinkedinUrl] = useState(user?.linkedinUrl || 'https://linkedin.com/in/alexchen-fullstack');
  const [portfolioUrl, setPortfolioUrl] = useState(user?.portfolioUrl || 'https://alexchen.dev');
  const [phone, setPhone] = useState(user?.phone || '+1-555-019-4821');
  const [location, setLocation] = useState(user?.location || 'San Francisco, CA');
  const [bio, setBio] = useState(user?.bio || 'Senior Software Engineer specializing in scalable fullstack architectures.');
  const [isSaved, setIsSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfile({
      name,
      email,
      role: role as any,
      targetCompany,
      githubUrl,
      linkedinUrl,
      portfolioUrl,
      phone,
      location,
      bio,
    });
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
  };

  return (
    <div className="flex-1 space-y-6 pb-12">
      <DashboardHeader
        title="Candidate Profile & Social Verification"
        subtitle="Manage your personal information, technical links (GitHub, LinkedIn, Portfolio), and target company focus."
      />

      <main className="p-6 max-w-4xl mx-auto space-y-8">
        <Card className="glass-panel p-8 space-y-6 bg-slate-900/90 border-slate-800 shadow-2xl">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
            <div className="flex items-center space-x-4">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={user?.avatarUrl || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250'}
                alt={name}
                className="w-20 h-20 rounded-2xl object-cover ring-4 ring-blue-500/30"
              />
              <div className="space-y-1">
                <h2 className="text-xl font-bold text-white">{name}</h2>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-blue-400 font-mono">{role} Engineer • Target: {targetCompany}</span>
                  <Badge variant="success" className="text-[10px] font-mono">Profile Verified</Badge>
                </div>
                <span className="text-[11px] text-slate-500 font-mono block">Joined {user?.joinedDate || 'August 2026'}</span>
              </div>
            </div>

            <div className="text-right space-y-1 self-end sm:self-auto font-mono text-xs">
              <span className="text-slate-400">Readiness Index:</span>
              <div className="text-2xl font-extrabold text-emerald-400">{user?.readinessScore || 88}%</div>
            </div>
          </div>

          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                icon={<User className="w-4 h-4" />}
                required
              />
              <Input
                label="Work Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                icon={<Mail className="w-4 h-4" />}
                required
              />
            </div>

            {/* Social & Professional Links */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="GitHub Profile URL"
                placeholder="https://github.com/your-username"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                icon={<Code2 className="w-4 h-4 text-purple-400" />}
              />
              <Input
                label="LinkedIn Profile URL"
                placeholder="https://linkedin.com/in/your-profile"
                value={linkedinUrl}
                onChange={(e) => setLinkedinUrl(e.target.value)}
                icon={<Link2 className="w-4 h-4 text-blue-400" />}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Portfolio Website URL"
                placeholder="https://yourportfolio.dev"
                value={portfolioUrl}
                onChange={(e) => setPortfolioUrl(e.target.value)}
                icon={<Globe className="w-4 h-4 text-emerald-400" />}
              />
              <Input
                label="Phone Number"
                placeholder="+1-555-019-2834"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                icon={<Phone className="w-4 h-4 text-amber-400" />}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Target Dream Company"
                value={targetCompany}
                onChange={(e) => setTargetCompany(e.target.value)}
                icon={<Building2 className="w-4 h-4 text-blue-400" />}
              />
              <Input
                label="Location"
                placeholder="San Francisco, CA / Remote"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                icon={<MapPin className="w-4 h-4 text-red-400" />}
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 font-mono">
                Professional Summary &amp; Bio
              </label>
              <textarea
                rows={3}
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                className="w-full rounded-xl bg-slate-950 border border-slate-700/80 p-3 text-xs text-slate-100 focus:outline-none focus:border-blue-500 font-sans"
              />
            </div>

            {/* Active Resume Link Preview */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs font-mono">
              <div className="flex items-center gap-2.5">
                <FileText className="w-4 h-4 text-blue-400" />
                <span className="text-slate-300">Active Resume: <strong className="text-white">{currentAnalysis.fileName}</strong> ({currentAnalysis.matchPercentage}% ATS Match)</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                type="button"
                onClick={() => window.location.href = '/dashboard/resume-upload'}
                className="text-[11px] font-mono"
              >
                Manage Resumes
              </Button>
            </div>

            <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
              {isSaved ? (
                <span className="text-xs text-emerald-400 font-mono font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4" /> Profile &amp; links saved successfully!
                </span>
              ) : (
                <span className="text-xs text-slate-500 font-mono">Changes persist automatically to your user profile.</span>
              )}
              <Button type="submit" variant="glow" size="md" className="gap-2 font-mono">
                <Save className="w-4 h-4" /> Save Profile Details
              </Button>
            </div>
          </form>
        </Card>
      </main>
    </div>
  );
}
