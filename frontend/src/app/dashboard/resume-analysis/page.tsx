'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';
import {
  FileText,
  Award,
  ArrowRight,
  Briefcase,
  GraduationCap,
  FolderGit2,
  Sparkles,
  AlertTriangle,
  NotListedLocation,
} from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useResumeStore } from '@/store/useResumeStore';

function SectionList({
  title,
  icon: Icon,
  items,
  emptyText,
  renderItem,
}: {
  title: string;
  icon: React.ElementType;
  items: unknown[];
  emptyText: string;
  renderItem: (item: any) => React.ReactNode;
}) {
  return (
    <Card className="p-6 space-y-4">
      <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
        <Icon className="w-5 h-5 text-blue-600" /> {title}
      </h3>
      {items.length === 0 ? (
        <p className="text-xs text-slate-400 italic flex items-center gap-1.5">
          <NotListedLocation className="w-3.5 h-3.5" /> {emptyText}
        </p>
      ) : (
        <div className="space-y-3">
          {items.map((item, idx) => (
            <div key={idx}>{renderItem(item)}</div>
          ))}
        </div>
      )}
    </Card>
  );
}

export default function ResumeAnalysisPage() {
  const {
    resumes,
    activeResumeId,
    currentDetail,
    setActiveResume,
    loadResumes,
  } = useResumeStore();

  useEffect(() => {
    if (resumes.length === 0) {
      loadResumes();
    }
  }, [resumes.length, loadResumes]);

  const data = currentDetail;
  const skillsSection = data?.sections?.find((s) => s.section_type === 'skills');
  const projectsSection = data?.sections?.find((s) => s.section_type === 'projects');
  const experienceSection = data?.sections?.find((s) => s.section_type === 'experience');
  const educationSection = data?.sections?.find((s) => s.section_type === 'education');
  const certificationsSection = data?.sections?.find((s) => s.section_type === 'certifications');

  const projects = Array.isArray(projectsSection?.content_json) ? (projectsSection!.content_json as any[]) : [];
  const experience = Array.isArray(experienceSection?.content_json) ? (experienceSection!.content_json as any[]) : [];
  const education = Array.isArray(educationSection?.content_json) ? (educationSection!.content_json as any[]) : [];
  const certifications = Array.isArray(certificationsSection?.content_json) ? (certificationsSection!.content_json as any[]) : [];

  if (resumes.length === 0 && !data) {
    return (
      <div className="flex-1 space-y-6 pb-12">
        <DashboardHeader title="Resume Analysis" subtitle="Extracted skills, projects and experience from your uploaded resume." />
        <main className="p-6 max-w-5xl mx-auto">
          <Card className="p-10 text-center space-y-3">
            <FileText className="w-10 h-10 text-slate-300 mx-auto" />
            <p className="text-base font-semibold text-slate-700">No resume uploaded</p>
            <p className="text-sm text-slate-500">Upload your resume to see your extracted profile here.</p>
            <Link href="/dashboard/resume-upload" className="inline-block pt-2">
              <Button variant="primary" size="md">Upload Resume</Button>
            </Link>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-6 pb-12">
      <DashboardHeader
        title="Resume Analysis"
        subtitle={data ? `Extracted profile for ${data.original_filename}` : 'Loading…'}
      />

      <main className="p-6 max-w-6xl mx-auto space-y-8">
        {/* Resume switcher */}
        {resumes.length > 1 && (
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl bg-white border border-slate-200">
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <span className="text-slate-500">Resume:</span>
              <select
                value={activeResumeId ?? ''}
                onChange={(e) => setActiveResume(e.target.value)}
                className="bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-sm text-slate-900 font-semibold focus:outline-none focus:border-blue-500"
              >
                {resumes.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.original_filename}
                  </option>
                ))}
              </select>
            </div>

            <Link
              href="/dashboard/resume-upload"
              className="text-sm text-blue-600 hover:text-blue-700 underline"
            >
              + Upload Another Resume
            </Link>
          </div>
        )}

        {/* Candidate header */}
        <Card className="p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <Badge variant="primary" className="font-mono text-[10px]">EXTRACTED PROFILE</Badge>
            <h2 className="text-xl font-bold text-slate-900">{data?.full_name || data?.original_filename || '—'}</h2>
            <p className="text-xs text-slate-500">
              {[data?.email, data?.phone, data?.location].filter(Boolean).join(' • ') || 'Contact details not found in resume'}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant={data?.status === 'parsed' ? 'success' : 'warning'}>
              {data?.status === 'parsed' ? 'Parsed successfully' : data?.status === 'parse_failed' ? 'Parse failed' : data?.status || ''}
            </Badge>
            <Link href="/dashboard/interview-setup">
              <Button variant="primary" size="sm" className="gap-2 text-xs">
                <span>Job Matching</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </Card>

        {data?.status !== 'parsed' && (
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-800 flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
            <span>
              This resume has not been parsed successfully yet. Job matching and interviews need a
              parsed resume{data?.parse_error ? ` (error: ${data.parse_error})` : ''}.
            </span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Extracted Skills — ONLY what the resume contains */}
          <Card className="p-6 space-y-4">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Award className="w-5 h-5 text-blue-600" /> Extracted Skills
            </h3>
            {!data || data.skills.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No skills were detected in this resume.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {data.skills.map((skill) => (
                  <span
                    key={skill.id}
                    className="px-3 py-1.5 rounded-lg bg-blue-50 border border-blue-200 text-xs font-semibold text-blue-800"
                    title={skill.proficiency_hint || 'Mentioned in resume'}
                  >
                    {skill.name}
                  </span>
                ))}
              </div>
            )}
            <p className="text-[11px] text-slate-400">
              Only technologies actually mentioned in your resume are listed here.
            </p>
          </Card>

          <SectionList
            title="Projects"
            icon={FolderGit2}
            items={projects}
            emptyText="No projects were detected in this resume."
            renderItem={(p: any) => (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <h4 className="text-sm font-bold text-slate-900">{p.title || p.name || 'Project'}</h4>
                  <div className="flex flex-wrap gap-1">
                    {(Array.isArray(p.technologies) ? p.technologies : Array.isArray(p.tech_stack) ? p.tech_stack : [])
                      .slice(0, 6)
                      .map((t: string, i: number) => (
                        <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-600 font-mono">
                          {t}
                        </span>
                      ))}
                  </div>
                </div>
                {p.description && <p className="text-xs text-slate-600">{p.description}</p>}
              </div>
            )}
          />

          <SectionList
            title="Experience"
            icon={Briefcase}
            items={experience}
            emptyText="No work experience or internships were detected in this resume."
            renderItem={(e: any) => (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">{e.title || e.role || e.company || 'Role'}</h4>
                    <span className="text-xs text-blue-700 font-mono">
                      {[e.company, e.organization, e.duration, e.period].filter(Boolean).join(' • ')}
                    </span>
                  </div>
                </div>
                {e.description && <p className="text-xs text-slate-600">{e.description}</p>}
                {Array.isArray(e.highlights) &&
                  e.highlights.map((h: string, i: number) => (
                    <li key={i} className="list-disc list-inside text-xs text-slate-500">{h}</li>
                  ))}
              </div>
            )}
          />

          <SectionList
            title="Education"
            icon={GraduationCap}
            items={education}
            emptyText="No education details were detected in this resume."
            renderItem={(ed: any) => (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <h4 className="text-sm font-bold text-slate-900">{ed.degree || ed.title || 'Degree'}</h4>
                <span className="text-xs text-slate-500">
                  {[ed.institution, ed.university, ed.college, ed.year, ed.graduation_year].filter(Boolean).join(' • ')}
                </span>
              </div>
            )}
          />

          <SectionList
            title="Certifications"
            icon={Sparkles}
            items={certifications}
            emptyText="No certifications were detected in this resume."
            renderItem={(c: any) => (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <h4 className="text-sm font-bold text-slate-900">{c.title || c.name || 'Certification'}</h4>
                <span className="text-xs text-slate-500">{[c.issuer, c.organization, c.year].filter(Boolean).join(' • ')}</span>
              </div>
            )}
          />
        </div>

        {/* Raw text reference (traceability) */}
        {data && (
          <details className="group">
            <summary className="cursor-pointer text-xs font-semibold text-blue-600 hover:text-blue-700">
              View extracted resume text (source of truth)
            </summary>
            <pre className="mt-3 p-4 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-slate-600 overflow-x-auto max-h-72 whitespace-pre-wrap">
              {/* raw text isn't sent to the client by default; sections above are the structured source */}
              {`Sections above are extracted verbatim from your uploaded document.`}
            </pre>
          </details>
        )}
      </main>
    </div>
  );
}
