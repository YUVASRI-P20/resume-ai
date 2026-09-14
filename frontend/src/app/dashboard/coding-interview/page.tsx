'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  Code2,
  Play,
  CheckCircle2,
  XCircle,
  Terminal,
  RotateCcw,
  ArrowRight,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { useResumeStore } from '@/store/useResumeStore';
import { codingService, CodingQuestion, CodingSubmission, CodingReview } from '@/services/codingService';
import { getApiErrorMessage } from '@/services/apiClient';

export default function CodingInterviewPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { resumes, activeResumeId, loadResumes } = useResumeStore();

  const [question, setQuestion] = useState<CodingQuestion | null>(null);
  const [pageMessage, setPageMessage] = useState<string | null>(null);
  const [language, setLanguage] = useState('Python');
  const [code, setCode] = useState('');
  const [isStarting, setIsStarting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submission, setSubmission] = useState<CodingSubmission | null>(null);
  const [review, setReview] = useState<CodingReview | null>(null);
  const [isReviewing, setIsReviewing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadResumes();
  }, [loadResumes]);

  const handleStart = async () => {
    if (!activeResumeId) {
      setError('Please upload your resume before starting the personalized coding test.');
      return;
    }
    setIsStarting(true);
    setError(null);
    setPageMessage(null);
    setSubmission(null);
    setReview(null);
    try {
      const result = await codingService.start(activeResumeId);
      if (result.question) {
        setQuestion(result.question);
        setCode('# Read the input from stdin and print your answer.\n');
        setLanguage(result.question.supported_languages?.[0] || 'Python');
      } else {
        setPageMessage(result.message || 'No coding questions are available yet.');
      }
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not start the coding test.'));
    } finally {
      setIsStarting(false);
    }
  };

  const handleSubmit = async () => {
    if (!question || !code.trim()) return;
    setIsSubmitting(true);
    setError(null);
    setReview(null);
    try {
      const sub = await codingService.submit(question.id, language, code);
      setSubmission(sub);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Submission failed. Please try again.'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReview = async () => {
    if (!submission) return;
    setIsReviewing(true);
    setError(null);
    try {
      const r = await codingService.requestReview(submission.id);
      setReview(r);
    } catch (err) {
      setError(getApiErrorMessage(err, 'AI code review is temporarily unavailable. Please try again.'));
    } finally {
      setIsReviewing(false);
    }
  };

  const exec = submission?.execution;

  return (
    <div className="flex-1 space-y-6">
      <DashboardHeader
        title="Coding Test"
        subtitle="A coding problem selected from your actual resume skills, executed against real test cases."
      />

      <main className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Start panel */}
        {!question && (
          <Card className="p-10 text-center space-y-4">
            <Code2 className="w-10 h-10 text-blue-600 mx-auto" />
            <h2 className="text-xl font-bold text-slate-900">Start Personalized Coding Test</h2>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              We select a problem based on the skills actually present in your resume. Your code runs
              in a sandbox against real test cases.
            </p>
            {error && (
              <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-start gap-2 text-left">
                <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}
            {pageMessage && <p className="text-sm text-slate-500">{pageMessage}</p>}
            <Button
              variant="primary"
              size="lg"
              onClick={handleStart}
              disabled={isStarting}
              isLoading={isStarting}
              loadingText="Selecting problem from your resume..."
              className="gap-2"
            >
              <span>Start Coding Test</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Card>
        )}

        {question && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[650px]">
            {/* Left Pane: Problem description */}
            <Card className="lg:col-span-5 p-6 flex flex-col justify-between space-y-6 overflow-y-auto max-h-[700px]">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Badge variant="primary" className="font-mono">{question.difficulty.toUpperCase()}</Badge>
                  <span className="text-xs text-slate-400 font-mono">{question.domain}</span>
                </div>

                <h2 className="text-xl font-bold text-slate-900 tracking-tight">{question.title}</h2>

                <p className="text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">{question.description}</p>

                <div className="space-y-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">Constraints</h4>
                  <pre className="text-xs text-slate-600 whitespace-pre-wrap">{question.constraints}</pre>
                </div>

                <div className="space-y-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">Examples</h4>
                  {question.examples.map((ex, i) => (
                    <div key={i} className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs font-mono space-y-1">
                      <p className="text-slate-500 font-bold">Input</p>
                      <pre className="text-slate-700 whitespace-pre-wrap">{ex.input}</pre>
                      <p className="text-slate-500 font-bold">Output</p>
                      <pre className="text-slate-700 whitespace-pre-wrap">{ex.output}</pre>
                    </div>
                  ))}
                </div>

                <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-xs text-blue-800">
                  Expected complexity: time {question.expected_time_complexity}, space {question.expected_space_complexity}
                </div>
              </div>
            </Card>

            {/* Right Pane: Editor & results */}
            <div className="lg:col-span-7 flex flex-col space-y-4">
              {/* Editor toolbar */}
              <div className="p-3 rounded-2xl bg-white border border-slate-200 flex items-center justify-between gap-4">
                <div className="flex items-center space-x-3">
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="h-9 rounded-lg bg-slate-50 border border-slate-300 px-3 text-xs text-slate-800 focus:outline-none focus:border-blue-500"
                  >
                    {question.supported_languages.map((l) => (
                      <option key={l} value={l}>{l}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => setCode('')}
                    title="Reset Code"
                    className="p-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-400 hover:text-slate-700"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="flex items-center space-x-2">
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={handleSubmit}
                    disabled={isSubmitting || !code.trim()}
                    isLoading={isSubmitting}
                    loadingText="Running tests..."
                    className="gap-1.5 text-xs"
                  >
                    <Play className="w-3.5 h-3.5" /> Submit &amp; Run Tests
                  </Button>
                </div>
              </div>

              {/* Code editor */}
              <div className="flex-1 rounded-2xl bg-slate-900 border border-slate-800 p-4 font-mono text-xs relative overflow-hidden flex shadow-inner min-h-[320px]">
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  spellCheck={false}
                  className="w-full h-full bg-transparent text-slate-100 focus:outline-none resize-none font-mono text-xs leading-relaxed"
                />
              </div>

              {/* Results console */}
              <div className="rounded-2xl bg-slate-900 border border-slate-800 p-4 space-y-3 font-mono text-xs">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-400 font-bold flex items-center gap-1.5">
                    <Terminal className="w-4 h-4 text-blue-400" /> Execution Results
                  </span>
                  {exec && (
                    <Badge variant={exec.execution_status === 'PASSED' ? 'success' : 'error'} className="text-[10px]">
                      {exec.passed_tests}/{exec.total_tests} {exec.execution_status}
                    </Badge>
                  )}
                </div>

                {error && <p className="text-red-400">{error}</p>}

                {exec ? (
                  <div className="space-y-2">
                    <p className="text-slate-300">
                      Runtime: {exec.runtime_ms}ms • Status: {exec.execution_status}
                    </p>
                    {exec.error_message && (
                      <pre className="p-3 rounded-lg bg-slate-800 text-red-300 text-[11px] overflow-x-auto whitespace-pre-wrap">
                        {exec.error_message}
                      </pre>
                    )}
                    {exec.execution_status === 'PASSED' && (
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={handleReview}
                        disabled={isReviewing}
                        isLoading={isReviewing}
                        loadingText="Generating AI review..."
                        className="gap-1.5 text-xs"
                      >
                        Get AI Code Review
                      </Button>
                    )}
                    {review && (
                      <div className="p-3 rounded-lg bg-slate-800 text-slate-200 space-y-2">
                        <p>
                          <strong>Score:</strong> {Math.round(review.score)}/100 • <strong>Complexity:</strong>{' '}
                          {review.time_complexity} time, {review.space_complexity} space
                        </p>
                        {review.issues.length > 0 && (
                          <div>
                            <strong>Issues:</strong>
                            <ul className="list-disc list-inside text-[11px] text-amber-300">
                              {review.issues.map((i, k) => <li key={k}>{i}</li>)}
                            </ul>
                          </div>
                        )}
                        {review.suggestions.length > 0 && (
                          <div>
                            <strong>Suggestions:</strong>
                            <ul className="list-disc list-inside text-[11px] text-blue-300">
                              {review.suggestions.map((s, k) => <li key={k}>{s}</li>)}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-slate-500 text-[11px] italic">
                    Submit your solution to run it against the test cases.
                  </p>
                )}
              </div>

              {submission && (
                <Button
                  variant="primary"
                  size="md"
                  className="gap-2 self-end"
                  onClick={() => router.push(`/dashboard/interview-summary?interview_id=${searchParams.get('interview_id') ?? ''}&from_coding=1`)}
                >
                  <span>Continue to Report</span>
                  <ArrowRight className="w-4 h-4" />
                </Button>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
