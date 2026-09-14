'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  FileUp,
  CheckCircle2,
  FileText,
  ArrowRight,
  Trash2,
  Check,
  Layers,
  AlertCircle,
  AlertTriangle,
} from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { useResumeStore } from '@/store/useResumeStore';

export default function ResumeUploadPage() {
  const router = useRouter();
  const {
    resumes,
    activeResumeId,
    isLoadingList,
    isUploading,
    uploadMessage,
    error,
    loadResumes,
    uploadResume,
    setActiveResume,
    deleteResume,
    clearError,
  } = useResumeStore();

  const [dragActive, setDragActive] = useState(false);
  const [showLib, setShowLib] = useState(false);

  useEffect(() => {
    loadResumes();
  }, [loadResumes]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleProcessFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleProcessFile(e.dataTransfer.files[0]);
    }
  };

  const handleProcessFile = async (selectedFile: File) => {
    clearError();
    const detail = await uploadResume(selectedFile);
    if (detail) {
      setShowLib(true);
    }
  };

  return (
    <div className="flex-1 space-y-6 pb-12">
      <DashboardHeader
        title="Resume"
        subtitle="Upload your real resume (PDF). We extract only the skills that actually appear in it."
      />

      <main className="p-6 max-w-5xl mx-auto space-y-8">
        {/* Upload Card */}
        <Card className="p-8 space-y-6">
          <div className="text-center space-y-2">
            <h2 className="text-2xl font-bold text-slate-900">Upload Your Resume</h2>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              PDF, DOCX or TXT up to 10MB. Skills, projects and experience are extracted from the
              actual document text — nothing is invented.
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
                ? 'border-blue-500 bg-blue-50'
                : 'border-slate-300 bg-slate-50 hover:border-blue-400'
            }`}
          >
            <div className="h-16 w-16 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600">
              <FileUp className="w-8 h-8" />
            </div>

            <div className="space-y-1">
              <h3 className="text-base font-semibold text-slate-900">
                Drag &amp; drop your resume here, or{' '}
                <label
                  htmlFor="resume-file-input"
                  className="text-blue-600 hover:text-blue-700 cursor-pointer font-bold underline"
                >
                  browse file
                </label>
              </h3>
              <p className="text-xs text-slate-500 font-mono">PDF, DOCX, TXT up to 10MB</p>
            </div>

            <input
              id="resume-file-input"
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={handleFileChange}
              disabled={isUploading}
              className="hidden"
            />

            <Button
              variant="outline"
              size="sm"
              onClick={() => document.getElementById('resume-file-input')?.click()}
              disabled={isUploading}
              className="mt-2 text-xs gap-2"
            >
              Select Resume File
            </Button>
          </div>

          {/* Loading states */}
          {isUploading && (
            <div className="space-y-2 p-4 rounded-xl bg-blue-50 border border-blue-200">
              <div className="flex justify-between text-xs text-blue-800 font-mono">
                <span>Uploading resume &amp; extracting content...</span>
              </div>
              <ProgressBar progress={70} color="blue" showPercentage={false} />
              <p className="text-[11px] text-blue-600">
                This can take up to a minute — we're parsing the PDF and analyzing your skills with AI.
              </p>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Upload Complete Banner */}
          {uploadMessage && !isUploading && !error && (
            <div className="p-5 rounded-2xl bg-emerald-50 border border-emerald-200 space-y-4">
              <div className="flex items-start space-x-3">
                <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <h4 className="text-sm font-bold text-slate-900">Resume processed</h4>
                  <p className="text-xs text-slate-600">{uploadMessage}</p>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3 pt-2">
                <Button
                  variant="primary"
                  size="md"
                  onClick={() => router.push('/dashboard/resume-analysis')}
                  className="gap-2 text-xs"
                >
                  <span>View Extracted Skills</span>
                  <ArrowRight className="w-4 h-4" />
                </Button>
                <Button
                  variant="outline"
                  size="md"
                  onClick={() => router.push('/dashboard/interview-setup')}
                  className="gap-2 text-xs"
                >
                  <span>Continue to Job Matching</span>
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </Card>

        {/* Uploaded Resumes Library */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Layers className="w-5 h-5 text-blue-600" />
                <span>Your Resumes</span>
              </h3>
              <p className="text-xs text-slate-500">
                Select the resume you want to use for job matching and interviews.
              </p>
            </div>
          </div>

          {isLoadingList ? (
            <Card className="p-8 text-center text-sm text-slate-500">Loading your resumes…</Card>
          ) : resumes.length === 0 ? (
            <Card className="p-8 text-center space-y-2">
              <FileText className="w-8 h-8 text-slate-300 mx-auto" />
              <p className="text-sm font-semibold text-slate-700">No resume uploaded</p>
              <p className="text-xs text-slate-500">
                Upload your first resume above to unlock job matching and personalized interviews.
              </p>
            </Card>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {resumes.map((res) => {
                const isActive = res.id === activeResumeId;
                return (
                  <Card
                    key={res.id}
                    className={`p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
                      isActive ? 'border-blue-400 ring-1 ring-blue-200' : ''
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <div
                        className={`h-12 w-12 rounded-2xl flex items-center justify-center shrink-0 ${
                          isActive
                            ? 'bg-blue-50 border border-blue-300 text-blue-600'
                            : 'bg-slate-50 border border-slate-200 text-slate-400'
                        }`}
                      >
                        <FileText className="w-6 h-6" />
                      </div>

                      <div className="space-y-1.5">
                        <div className="flex items-center flex-wrap gap-2">
                          <h4 className="text-sm font-bold text-slate-900">{res.original_filename}</h4>
                          {isActive && (
                            <span className="px-2 py-0.5 rounded-md bg-blue-50 border border-blue-200 text-blue-700 text-[10px] font-mono font-bold flex items-center gap-1">
                              <Check className="w-3 h-3" /> Active
                            </span>
                          )}
                          <Badge
                            variant={
                              res.status === 'parsed'
                                ? 'success'
                                : res.status === 'parse_failed'
                                ? 'error'
                                : 'warning'
                            }
                          >
                            {res.status === 'parsed'
                              ? 'Parsed'
                              : res.status === 'parse_failed'
                              ? 'Parse failed'
                              : res.status === 'parsing'
                              ? 'Parsing…'
                              : 'Uploaded'}
                          </Badge>
                        </div>

                        {res.full_name && (
                          <span className="text-[11px] text-slate-500 block">{res.full_name}</span>
                        )}

                        <span className="text-[11px] text-slate-400 font-mono block">
                          Uploaded {new Date(res.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 self-end md:self-auto shrink-0">
                      {!isActive ? (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setActiveResume(res.id)}
                          className="text-xs"
                        >
                          Set as Active
                        </Button>
                      ) : null}

                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => {
                          setActiveResume(res.id);
                          router.push('/dashboard/resume-analysis');
                        }}
                        className="text-xs"
                      >
                        View Analysis &rarr;
                      </Button>

                      <button
                        type="button"
                        onClick={() => deleteResume(res.id)}
                        className="p-2 rounded-lg text-slate-400 hover:text-red-600 hover:bg-slate-50 transition-colors"
                        title="Delete Resume"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </Card>
                );
              })}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
