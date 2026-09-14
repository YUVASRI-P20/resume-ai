'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Video,
  Building2,
  ArrowRight,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Loader2,
  Briefcase,
} from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { useResumeStore } from '@/store/useResumeStore';
import { useInterviewStore } from '@/store/useInterviewStore';
import {
  careerService,
  Company,
  JobRole,
  RoleMatchResult,
  RoleRequirementsResponse,
} from '@/services/careerService';
import { interviewService } from '@/services/interviewService';
import { getApiErrorMessage } from '@/services/apiClient';

export default function InterviewSetupPage() {
  const router = useRouter();
  const { resumes, activeResumeId, loadResumes } = useResumeStore();
  const { setActiveInterview, setCurrentQuestion } = useInterviewStore();

  const [companies, setCompanies] = useState<Company[]>([]);
  const [roles, setRoles] = useState<JobRole[]>([]);
  const [requirements, setRequirements] = useState<RoleRequirementsResponse | null>(null);
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null);
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [match, setMatch] = useState<RoleMatchResult | null>(null);
  const [isLoadingCompanies, setIsLoadingCompanies] = useState(true);
  const [isLoadingMatch, setIsLoadingMatch] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [numberOfQuestions, setNumberOfQuestions] = useState(5);

  useEffect(() => {
    loadResumes();
    careerService
      .listCompanies()
      .then((cs) => {
        setCompanies(cs);
        if (cs.length > 0) setSelectedCompany((prev) => prev ?? cs[0].id);
      })
      .catch(() => setError('Could not load companies. Is the backend running?'))
      .finally(() => setIsLoadingCompanies(false));
  }, [loadResumes]);

  useEffect(() => {
    setRoles([]);
    setSelectedRole(null);
    setRequirements(null);
    setMatch(null);
    if (!selectedCompany) return;
    careerService
      .listCompanyRoles(selectedCompany)
      .then((rs) => {
        setRoles(rs);
        if (rs.length > 0) setSelectedRole(rs[0].id);
      })
      .catch(() => setError('Could not load job roles for this company.'));
  }, [selectedCompany]);

  useEffect(() => {
    setRequirements(null);
    if (!selectedRole) return;
    careerService
      .getRoleRequirements(selectedRole)
      .then(setRequirements)
      .catch(() => setError('Could not load the job requirements.'));
  }, [selectedRole]);

  const handleCheckMatch = async () => {
    if (!activeResumeId || !selectedCompany || !selectedRole) return;
    setIsLoadingMatch(true);
    setError(null);
    try {
      const result = await careerService.createRoleMatch(activeResumeId, selectedCompany, selectedRole);
      setMatch(result);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Job matching failed. Make sure your resume is parsed first.'));
    } finally {
      setIsLoadingMatch(false);
    }
  };

  const handleStartInterview = async () => {
    if (!activeResumeId) {
      setError('Please upload your resume before starting the personalized interview.');
      return;
    }
    if (!selectedCompany || !selectedRole) {
      setError('Please select a job role before starting the interview.');
      return;
    }
    setIsStarting(true);
    setError(null);
    try {
      const company = companies.find((c) => c.id === selectedCompany);
      const role = roles.find((r) => r.id === selectedRole);
      const interview = await interviewService.start({
        company: company?.name || 'Target Company',
        job_role: role?.title || 'Software Engineer',
        domain: role?.domain || 'Software Engineering',
        resume_id: activeResumeId,
        number_of_questions: numberOfQuestions,
      });
      // Generate the first resume-grounded question.
      const question = await interviewService.nextQuestion(interview.id);
      setActiveInterview(interview, question);
      setCurrentQuestion(question);
      router.push('/dashboard/live-interview');
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not start the interview. Please try again.'));
      setIsStarting(false);
    }
  };

  return (
    <div className="flex-1 space-y-6 pb-12">
      <DashboardHeader
        title="Job Matching & Interview Setup"
        subtitle="Select a real job role, compare it against your resume, then start a resume-grounded AI interview."
      />

      <main className="p-6 max-w-5xl mx-auto space-y-8">
        {/* Resume status */}
        <Card className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600">
              <Briefcase className="w-5 h-5" />
            </div>
            <div>
              <span className="text-sm font-bold text-slate-900">Active resume</span>
              <p className="text-xs text-slate-500">
                {resumes.find((r) => r.id === activeResumeId)?.original_filename || 'None selected'}
                {' • '}
                {resumes.find((r) => r.id === activeResumeId)?.status || ''}
              </p>
            </div>
          </div>
          {(!activeResumeId || resumes.length === 0) && (
            <Button variant="outline" size="sm" onClick={() => router.push('/dashboard/resume-upload')}>
              Upload Resume First
            </Button>
          )}
        </Card>

        {error && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <Card className="p-8 space-y-8">
          {/* Step 1: Company */}
          <div className="space-y-3">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
              1. Select Target Company
            </label>
            {isLoadingCompanies ? (
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <Loader2 className="w-4 h-4 animate-spin" /> Loading companies…
              </div>
            ) : companies.length === 0 ? (
              <p className="text-sm text-slate-500">No companies available yet.</p>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {companies.map((c) => (
                  <div
                    key={c.id}
                    onClick={() => setSelectedCompany(c.id)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all ${
                      selectedCompany === c.id
                        ? 'bg-blue-50 border-blue-400 ring-1 ring-blue-200'
                        : 'bg-white border-slate-200 hover:border-blue-300'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-blue-600" />
                      <h4 className="text-sm font-bold text-slate-900">{c.name}</h4>
                    </div>
                    {c.industry && <span className="text-[10px] text-slate-500">{c.industry}</span>}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Step 2: Role */}
          <div className="space-y-3">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
              2. Select Job Role
            </label>
            {roles.length === 0 ? (
              <p className="text-sm text-slate-500">
                {selectedCompany ? 'No roles available for this company.' : 'Select a company first.'}
              </p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {roles.map((r) => (
                  <div
                    key={r.id}
                    onClick={() => setSelectedRole(r.id)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all ${
                      selectedRole === r.id
                        ? 'bg-blue-50 border-blue-400 ring-1 ring-blue-200'
                        : 'bg-white border-slate-200 hover:border-blue-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-bold text-slate-900">{r.title}</h4>
                      {r.seniority && <Badge variant="outline">{r.seniority}</Badge>}
                    </div>
                    {r.description && <p className="text-xs text-slate-500 mt-1 line-clamp-2">{r.description}</p>}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Step 3: Job requirements + match */}
          {requirements && (
            <div className="space-y-3">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
                3. Job Requirements vs Your Resume
              </label>
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <h4 className="text-sm font-bold text-slate-900">
                  {requirements.role.title} at {requirements.company.name}
                </h4>
                <div className="flex flex-wrap gap-2">
                  {requirements.requirements.map((req) => (
                    <span key={req.requirement} className="px-2 py-0.5 rounded bg-white border border-slate-200 text-[11px] text-slate-700" title={`Importance: ${req.importance}/5`}>
                      {req.requirement}
                    </span>
                  ))}
                </div>
              </div>

              <Button
                variant="secondary"
                size="md"
                onClick={handleCheckMatch}
                disabled={!activeResumeId || isLoadingMatch}
                isLoading={isLoadingMatch}
                loadingText="Checking job compatibility..."
                className="gap-2"
              >
                <span>Compare My Resume</span>
              </Button>

              {match && (
                <div className="space-y-4 pt-2">
                  <div className="p-5 rounded-xl bg-blue-50 border border-blue-200 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-slate-900">Job-fit score</span>
                      <span className="text-2xl font-extrabold text-blue-700 font-mono">{match.match_percentage}%</span>
                    </div>
                    <ProgressBar progress={match.match_percentage} color="blue" showPercentage={false} />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 space-y-2">
                      <h4 className="text-xs font-bold text-emerald-800 flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4" /> Matching skills
                      </h4>
                      {match.evidence.filter((e) => e.status === 'strong' || e.status === 'moderate').length === 0 ? (
                        <p className="text-xs text-emerald-700 italic">None found in your resume.</p>
                      ) : (
                        <ul className="space-y-1.5">
                          {match.evidence
                            .filter((e) => e.status === 'strong' || e.status === 'moderate')
                            .map((e) => (
                              <li key={e.requirement} className="text-xs text-emerald-900 flex items-start gap-1.5">
                                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                                <span>
                                  <strong>{e.requirement}</strong>
                                  {e.evidence && <span className="block text-[11px] text-emerald-700">{e.evidence}</span>}
                                </span>
                              </li>
                            ))}
                        </ul>
                      )}
                    </div>

                    <div className="p-4 rounded-xl bg-red-50 border border-red-200 space-y-2">
                      <h4 className="text-xs font-bold text-red-800 flex items-center gap-1.5">
                        <XCircle className="w-4 h-4" /> Missing / not mentioned in resume
                      </h4>
                      {match.evidence.filter((e) => e.status === 'weak' || e.status === 'missing').length === 0 ? (
                        <p className="text-xs text-red-700 italic">All requirements covered.</p>
                      ) : (
                        <ul className="space-y-1.5">
                          {match.evidence
                            .filter((e) => e.status === 'weak' || e.status === 'missing')
                            .map((e) => (
                              <li key={e.requirement} className="text-xs text-red-900 flex items-start gap-1.5">
                                <XCircle className="w-3.5 h-3.5 text-red-500 shrink-0 mt-0.5" />
                                <span>
                                  <strong>{e.requirement}</strong>
                                  <span className="block text-[11px] text-red-600">Not mentioned in resume</span>
                                </span>
                              </li>
                            ))}
                        </ul>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 4: Interview config + start */}
          <div className="space-y-4 pt-2 border-t border-slate-200">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
              4. Start Personalized AI Interview
            </label>
            <div className="flex flex-col sm:flex-row sm:items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-slate-600">
                <span>Questions:</span>
                <select
                  value={numberOfQuestions}
                  onChange={(e) => setNumberOfQuestions(Number(e.target.value))}
                  className="bg-slate-50 border border-slate-300 rounded-lg px-3 py-1.5 text-sm text-slate-900 focus:outline-none focus:border-blue-500"
                >
                  {[3, 5, 8, 10].map((n) => (
                    <option key={n} value={n}>{n}</option>
                  ))}
                </select>
              </div>

              <Button
                variant="primary"
                size="lg"
                className="gap-2 sm:ml-auto"
                onClick={handleStartInterview}
                disabled={isStarting || !activeResumeId || !selectedRole}
                isLoading={isStarting}
                loadingText="Generating personalized interview..."
              >
                <span>Start Interview</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-[11px] text-slate-400">
              Questions are generated from your uploaded resume and the selected role — the AI never
              asks about technologies that are not in your resume.
            </p>
          </div>
        </Card>
      </main>
    </div>
  );
}
