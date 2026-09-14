'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  Cpu,
  User,
  Mail,
  Globe,
  Phone,
  MapPin,
  Building2,
  FileUp,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Video,
  Code2,
  LayoutDashboard,
  ShieldCheck,
  Check,
  Plus,
  Link2,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { useAuthStore } from '@/store/useAuthStore';
import { useResumeStore } from '@/store/useResumeStore';
import { useInterviewStore } from '@/store/useInterviewStore';
import { interviewService } from '@/services/interviewService';

export default function OnboardingPage() {
  const router = useRouter();
  const { user, register, updateProfile } = useAuthStore();
  const { parseAndSetResume, currentAnalysis } = useResumeStore();
  const { setActiveSession } = useInterviewStore();

  const [step, setStep] = useState<1 | 2 | 3>(1);

  // Step 1: Personal & Professional Links
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [githubUrl, setGithubUrl] = useState(user?.githubUrl || 'https://github.com/');
  const [linkedinUrl, setLinkedinUrl] = useState(user?.linkedinUrl || 'https://linkedin.com/in/');
  const [portfolioUrl, setPortfolioUrl] = useState(user?.portfolioUrl || '');
  const [phone, setPhone] = useState(user?.phone || '+1-555-019-8800');
  const [location, setLocation] = useState(user?.location || 'San Francisco, CA');
  const [role, setRole] = useState(user?.role || 'Fullstack');
  const [company, setCompany] = useState(user?.targetCompany || 'Vercel');

  // Step 2: Resume Upload State
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [resumeParsed, setResumeParsed] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  // Step 3: Launching Action State
  const [isLaunching, setIsLaunching] = useState(false);

  // Handle Step 1 Save
  const handleStep1Submit = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfile({
      name: name.trim() || 'Candidate Engineer',
      email: email.trim() || user?.email,
      githubUrl: githubUrl.trim(),
      linkedinUrl: linkedinUrl.trim(),
      portfolioUrl: portfolioUrl.trim(),
      phone: phone.trim(),
      location: location.trim(),
      role: role as any,
      targetCompany: company.trim(),
      isOnboarded: true,
    });
    setStep(2);
  };

  // Handle Resume File Selection & Parsing
  const handleProcessResume = async (selectedFile: File) => {
    setFile(selectedFile);
    setIsUploading(true);
    setUploadProgress(25);

    let extractedText = '';
    try {
      if (selectedFile.type.includes('text') || selectedFile.name.endsWith('.txt')) {
        extractedText = await selectedFile.text();
      } else {
        const arrayBuffer = await selectedFile.arrayBuffer();
        const bytes = new Uint8Array(arrayBuffer);
        let str = '';
        for (let i = 0; i < Math.min(bytes.length, 50000); i++) {
          const charCode = bytes[i];
          if ((charCode >= 32 && charCode <= 126) || charCode === 10 || charCode === 13) {
            str += String.fromCharCode(charCode);
          }
        }
        extractedText = str;
      }
    } catch {
      extractedText = selectedFile.name;
    }

    setUploadProgress(65);

    // Parse into reactive resume store
    await parseAndSetResume(selectedFile, extractedText);

    setUploadProgress(100);
    setIsUploading(false);
    setResumeParsed(true);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleProcessResume(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleProcessResume(e.dataTransfer.files[0]);
    }
  };

  // Step 3 Launch Handlers
  const handleLaunchVoiceInterview = async () => {
    setIsLaunching(true);
    const session = await interviewService.createSession({
      company,
      difficulty: 'Senior',
      domain: 'Technical Architecture',
      instructions: `Targeting candidate ${name} with GitHub profile ${githubUrl} and verified resume skills: ${currentAnalysis.extractedSkills.slice(0, 4).map((s) => s.name).join(', ')}.`,
    });
    setActiveSession(session);
    setTimeout(() => {
      setIsLaunching(false);
      router.push('/dashboard/live-interview');
    }, 600);
  };

  const handleLaunchCodingTest = () => {
    router.push('/dashboard/coding-interview');
  };

  const handleGoDashboard = () => {
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-4 sm:p-6 bg-grid-pattern relative">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[160px] pointer-events-none" />

      <div className="w-full max-w-2xl relative z-10 space-y-6">
        {/* Brand & Header */}
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex items-center space-x-3 group">
            <div className="h-12 w-12 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 p-0.5 shadow-lg shadow-blue-500/20">
              <div className="h-full w-full bg-slate-950 rounded-[14px] flex items-center justify-center">
                <Cpu className="h-6 w-6 text-blue-400" />
              </div>
            </div>
          </Link>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
            Welcome to InterviewIQ
          </h1>
          <p className="text-xs text-slate-400">
            Set up your candidate profile, connect your technical links &amp; resume, and launch your first AI mock interview.
          </p>
        </div>

        {/* 3-Step Progress Indicator */}
        <div className="grid grid-cols-3 gap-2 sm:gap-4 p-3 rounded-2xl bg-slate-900/90 border border-slate-800 backdrop-blur-xl">
          <div
            className={`flex items-center gap-2 p-2 rounded-xl text-xs font-mono transition-colors ${
              step === 1 ? 'bg-blue-600 text-white font-bold' : step > 1 ? 'text-emerald-400' : 'text-slate-500'
            }`}
          >
            <span className="w-5 h-5 rounded-full bg-slate-950/80 flex items-center justify-center text-[10px]">
              {step > 1 ? <Check className="w-3 h-3" /> : '1'}
            </span>
            <span className="hidden sm:inline">Profile Links</span>
          </div>

          <div
            className={`flex items-center gap-2 p-2 rounded-xl text-xs font-mono transition-colors ${
              step === 2 ? 'bg-blue-600 text-white font-bold' : step > 2 ? 'text-emerald-400' : 'text-slate-500'
            }`}
          >
            <span className="w-5 h-5 rounded-full bg-slate-950/80 flex items-center justify-center text-[10px]">
              {step > 2 ? <Check className="w-3 h-3" /> : '2'}
            </span>
            <span className="hidden sm:inline">Upload Resume</span>
          </div>

          <div
            className={`flex items-center gap-2 p-2 rounded-xl text-xs font-mono transition-colors ${
              step === 3 ? 'bg-blue-600 text-white font-bold' : 'text-slate-500'
            }`}
          >
            <span className="w-5 h-5 rounded-full bg-slate-950/80 flex items-center justify-center text-[10px]">
              3
            </span>
            <span className="hidden sm:inline">Start Interview</span>
          </div>
        </div>

        {/* Step 1: Personal Profile & Professional Links */}
        {step === 1 && (
          <Card className="glass-panel p-6 sm:p-8 space-y-6 bg-slate-900/90 border-slate-800 shadow-2xl">
            <div className="space-y-1 border-b border-slate-800 pb-3">
              <Badge variant="primary" className="font-mono text-[10px] uppercase">
                STEP 1 OF 3
              </Badge>
              <h3 className="text-lg font-bold text-white">Personal Information &amp; Social Links</h3>
              <p className="text-xs text-slate-400">
                Connect your GitHub, LinkedIn, and portfolio to customize AI technical questions to your public repositories and career history.
              </p>
            </div>

            <form onSubmit={handleStep1Submit} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label="Full Name"
                  placeholder="Alex Chen"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  icon={<User className="w-4 h-4" />}
                  required
                />
                <Input
                  label="Work Email"
                  type="email"
                  placeholder="alex@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  icon={<Mail className="w-4 h-4" />}
                  required
                />
              </div>

              {/* GitHub & LinkedIn URLs */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label="GitHub Profile URL"
                  placeholder="https://github.com/your-username"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  icon={<Code2 className="w-4 h-4 text-purple-400" />}
                  required
                />
                <Input
                  label="LinkedIn Profile URL"
                  placeholder="https://linkedin.com/in/your-profile"
                  value={linkedinUrl}
                  onChange={(e) => setLinkedinUrl(e.target.value)}
                  icon={<Link2 className="w-4 h-4 text-blue-400" />}
                  required
                />
              </div>

              {/* Portfolio & Phone */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label="Portfolio / Website URL (Optional)"
                  placeholder="https://yourportfolio.dev"
                  value={portfolioUrl}
                  onChange={(e) => setPortfolioUrl(e.target.value)}
                  icon={<Globe className="w-4 h-4 text-emerald-400" />}
                />
                <Input
                  label="Phone Number (Optional)"
                  placeholder="+1-555-019-2834"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  icon={<Phone className="w-4 h-4 text-amber-400" />}
                />
              </div>

              {/* Target Domain & Dream Company */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 font-mono">
                    Target Engineering Domain
                  </label>
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value as any)}
                    className="w-full h-11 rounded-xl bg-slate-950 border border-slate-700/80 px-3 text-xs text-slate-100 focus:outline-none focus:border-blue-500 font-sans"
                  >
                    <option value="Fullstack">Senior Fullstack (React / Python / Node)</option>
                    <option value="System Architect">Distributed Systems Architect</option>
                    <option value="Backend">Backend &amp; Cloud (Go / FastAPI / Rust)</option>
                    <option value="Frontend">Frontend Architecture (Next.js / React 19)</option>
                    <option value="AI/ML">AI &amp; LLM Systems Engineer</option>
                    <option value="DevOps">DevOps &amp; Kubernetes Infrastructure</option>
                  </select>
                </div>

                <Input
                  label="Target Dream Company"
                  placeholder="e.g. Vercel, OpenAI, Stripe, Google"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  icon={<Building2 className="w-4 h-4 text-blue-400" />}
                  required
                />
              </div>

              <div className="pt-2">
                <Button type="submit" variant="glow" size="lg" className="w-full gap-2 font-mono">
                  <span>Continue to Resume Upload</span>
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </div>
            </form>
          </Card>
        )}

        {/* Step 2: Resume Upload & Instant Parser */}
        {step === 2 && (
          <Card className="glass-panel p-6 sm:p-8 space-y-6 bg-slate-900/90 border-slate-800 shadow-2xl">
            <div className="space-y-1 border-b border-slate-800 pb-3">
              <Badge variant="primary" className="font-mono text-[10px] uppercase">
                STEP 2 OF 3
              </Badge>
              <h3 className="text-lg font-bold text-white">Upload Your Technical Resume</h3>
              <p className="text-xs text-slate-400">
                Upload your resume (PDF, DOCX, TXT). InterviewIQ extracts verified skills and audits project claims.
              </p>
            </div>

            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragActive(true);
              }}
              onDragLeave={() => setDragActive(false)}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-3xl p-8 text-center transition-all flex flex-col items-center justify-center space-y-4 ${
                dragActive
                  ? 'border-blue-500 bg-blue-950/20 scale-[1.01]'
                  : 'border-slate-700/80 bg-slate-950/40 hover:border-slate-600'
              }`}
            >
              <div className="h-16 w-16 rounded-2xl bg-blue-600/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
                <FileUp className="w-8 h-8" />
              </div>

              <div className="space-y-1">
                <h3 className="text-base font-semibold text-white">
                  Drag &amp; Drop your resume here, or{' '}
                  <label
                    htmlFor="onboarding-resume-input"
                    className="text-blue-400 hover:text-blue-300 cursor-pointer font-bold underline"
                  >
                    browse file
                  </label>
                </h3>
                <p className="text-xs text-slate-400 font-mono">PDF, DOCX, TXT up to 10MB</p>
              </div>

              <input
                id="onboarding-resume-input"
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileChange}
                className="hidden"
              />

              <Button
                variant="outline"
                size="sm"
                onClick={() => document.getElementById('onboarding-resume-input')?.click()}
                className="mt-2 text-xs font-mono gap-2"
              >
                <Plus className="w-3.5 h-3.5" /> Select Resume File
              </Button>
            </div>

            {/* Uploading Progress */}
            {isUploading && (
              <div className="space-y-2 p-4 rounded-xl bg-slate-950 border border-slate-800 animate-pulse">
                <div className="flex justify-between text-xs text-slate-300 font-mono">
                  <span>Parsing Skills &amp; Auditing Claims...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <ProgressBar progress={uploadProgress} color="blue" />
              </div>
            )}

            {/* Extracted Skills Summary if Parsed */}
            {resumeParsed && (
              <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/40 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>Parsed {file?.name || currentAnalysis.fileName}</span>
                  </span>
                  <Badge variant="success" className="font-mono text-[10px]">
                    {currentAnalysis.matchPercentage}% ATS Match
                  </Badge>
                </div>

                <div className="flex flex-wrap gap-1.5 pt-1">
                  {currentAnalysis.extractedSkills.slice(0, 8).map((s) => (
                    <span
                      key={s.name}
                      className="px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-[10px] font-mono text-emerald-300"
                    >
                      {s.name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between pt-2 border-t border-slate-800">
              <Button variant="outline" size="md" onClick={() => setStep(1)} className="gap-2 text-xs font-mono">
                <ArrowLeft className="w-4 h-4" /> Back
              </Button>

              <Button
                variant="glow"
                size="md"
                onClick={() => setStep(3)}
                className="gap-2 text-xs font-mono shadow-xl"
              >
                <span>Continue to Mock Interviews</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </Card>
        )}

        {/* Step 3: Launch Mock Interview or Coding Test */}
        {step === 3 && (
          <Card className="glass-panel p-6 sm:p-8 space-y-6 bg-slate-900/90 border-slate-800 shadow-2xl">
            <div className="space-y-1 border-b border-slate-800 pb-3">
              <Badge variant="primary" className="font-mono text-[10px] uppercase">
                STEP 3 OF 3 • READY TO PRACTICE
              </Badge>
              <h3 className="text-lg font-bold text-white">Your Profile is Ready! Choose Your Starting Mode</h3>
              <p className="text-xs text-slate-400">
                AI has ingested your resume skills and GitHub profile. Choose where you want to start.
              </p>
            </div>

            {/* Candidate Summary Box */}
            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3 text-xs font-mono">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                <span className="text-slate-400">Candidate Name:</span>
                <span className="font-bold text-white">{name || user?.name}</span>
              </div>
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                <span className="text-slate-400">GitHub &amp; LinkedIn:</span>
                <span className="text-blue-400 truncate max-w-[280px]">{githubUrl}</span>
              </div>
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                <span className="text-slate-400">Target Role &amp; Company:</span>
                <span className="text-purple-400 font-bold">{role} @ {company}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Active Resume:</span>
                <span className="text-emerald-400 font-bold">{file?.name || currentAnalysis.fileName} ({currentAnalysis.matchPercentage}% Match)</span>
              </div>
            </div>

            {/* 3 Action Launch Cards */}
            <div className="space-y-3 pt-2">
              {/* Option 1: Live Voice Mock Interview */}
              <button
                type="button"
                onClick={handleLaunchVoiceInterview}
                disabled={isLaunching}
                className="w-full p-4 rounded-2xl bg-gradient-to-r from-blue-900/60 to-indigo-950/60 border border-blue-500/50 hover:border-blue-400 transition-all text-left flex items-center justify-between group shadow-xl"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-12 h-12 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 group-hover:scale-110 transition-transform">
                    <Video className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-sm font-bold text-white group-hover:text-blue-300">
                        Start Live AI Voice Mock Interview
                      </h4>
                      <Badge variant="primary" className="text-[10px]">RECOMMENDED</Badge>
                    </div>
                    <p className="text-xs text-slate-300 mt-0.5">
                      Adaptive speech interview with live mic transcription and AI voice feedback for {company}.
                    </p>
                  </div>
                </div>
                <ArrowRight className="w-5 h-5 text-blue-400 group-hover:translate-x-1 transition-transform shrink-0" />
              </button>

              {/* Option 2: Live Monaco Coding Test */}
              <button
                type="button"
                onClick={handleLaunchCodingTest}
                className="w-full p-4 rounded-2xl bg-slate-950 border border-slate-800 hover:border-purple-500/50 transition-all text-left flex items-center justify-between group"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-12 h-12 rounded-xl bg-purple-600/20 border border-purple-500/40 flex items-center justify-center text-purple-400 group-hover:scale-110 transition-transform">
                    <Code2 className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white group-hover:text-purple-300">
                      Start Monaco Live Coding Simulator
                    </h4>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Solve company-targeted algorithm and system problems with automated test case runners.
                    </p>
                  </div>
                </div>
                <ArrowRight className="w-5 h-5 text-slate-400 group-hover:translate-x-1 transition-transform shrink-0" />
              </button>

              {/* Option 3: Full Dashboard */}
              <button
                type="button"
                onClick={handleGoDashboard}
                className="w-full p-3.5 rounded-xl bg-slate-950 border border-slate-800/80 hover:border-slate-700 text-left flex items-center justify-between group"
              >
                <div className="flex items-center gap-3">
                  <LayoutDashboard className="w-5 h-5 text-slate-400" />
                  <span className="text-xs font-semibold text-slate-300 group-hover:text-white">
                    Go to Full AI Dashboard Overview
                  </span>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-500 group-hover:translate-x-1 transition-transform shrink-0" />
              </button>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
