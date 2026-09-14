'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Clock,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Video,
} from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { useInterviewStore } from '@/store/useInterviewStore';
import { interviewService, Evaluation } from '@/services/interviewService';
import { getApiErrorMessage } from '@/services/apiClient';

export default function LiveInterviewPage() {
  const router = useRouter();
  const {
    activeInterview,
    currentQuestion,
    latestEvaluation,
    setActiveInterview,
    addQuestion,
    setLatestEvaluation,
    reset,
  } = useInterviewStore();

  const [answerText, setAnswerText] = useState('');
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [isFinishing, setIsFinishing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState(0);

  // Redirect to setup when there is no active interview (e.g. page refresh).
  useEffect(() => {
    if (!activeInterview) {
      router.replace('/dashboard/interview-setup');
    }
  }, [activeInterview, router]);

  useEffect(() => {
    const t = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, []);

  const totalQuestions = activeInterview?.number_of_questions || 0;
  const answered = activeInterview?.completed_question_count ?? 0;

  const formatTimer = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handleSubmitAnswer = async () => {
    if (!activeInterview || !currentQuestion || !answerText.trim()) return;
    setIsEvaluating(true);
    setError(null);
    try {
      const evaluation = await interviewService.submitAnswer(
        activeInterview.id,
        currentQuestion.id,
        answerText.trim()
      );
      setLatestEvaluation(evaluation);
      setAnswerText('');
    } catch (err) {
      setError(getApiErrorMessage(err, 'Answer evaluation failed. Please try again.'));
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleNextQuestion = async () => {
    if (!activeInterview) return;
    setError(null);

    // If this was the last planned question, complete the interview.
    if (answered + 1 >= totalQuestions) {
      await handleFinish();
      return;
    }

    try {
      const next = await interviewService.nextQuestion(activeInterview.id);
      addQuestion(next);
      setLatestEvaluation(null);
    } catch {
      // No more questions available -> finish the interview.
      await handleFinish();
    }
  };

  const handleFinish = async () => {
    if (!activeInterview) return;
    setIsFinishing(true);
    setError(null);
    try {
      await interviewService.complete(activeInterview.id);
      const id = activeInterview.id;
      reset();
      router.push(`/dashboard/interview-summary?interview_id=${id}`);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not finish the interview.'));
      setIsFinishing(false);
    }
  };

  if (!activeInterview || !currentQuestion) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-6 pb-12">
      <DashboardHeader
        title={`AI Interview — ${activeInterview.company}`}
        subtitle={`${activeInterview.job_role} • Question ${answered + (latestEvaluation ? 1 : 0)} of ${totalQuestions} • Adaptive difficulty: ${activeInterview.current_difficulty}`}
      />

      <main className="p-6 max-w-4xl mx-auto space-y-6">
        {/* Progress */}
        <Card className="p-4">
          <div className="flex items-center justify-between mb-2 text-xs text-slate-500">
            <span className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-blue-600" /> Elapsed {formatTimer(elapsed)}
            </span>
            <span className="flex items-center gap-1.5">
              <Video className="w-3.5 h-3.5 text-blue-600" /> {activeInterview.job_role} @ {activeInterview.company}
            </span>
          </div>
          <ProgressBar
            progress={totalQuestions ? (answered / totalQuestions) * 100 : 0}
            color="blue"
            showPercentage={false}
          />
        </Card>

        {error && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Question */}
        <Card className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-[11px] uppercase font-mono text-blue-700 font-bold flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" /> Resume-Grounded Question
            </span>
            <div className="flex items-center gap-2">
              <Badge variant="outline">Q{currentQuestion.question_index}</Badge>
              <Badge variant="primary">{currentQuestion.difficulty}</Badge>
            </div>
          </div>
          <p className="text-base text-slate-900 font-medium leading-relaxed">
            {currentQuestion.question_text}
          </p>
        </Card>

        {/* Answer */}
        {!latestEvaluation ? (
          <Card className="p-6 space-y-4">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
              Your Answer
            </label>
            <textarea
              rows={8}
              value={answerText}
              onChange={(e) => setAnswerText(e.target.value)}
              placeholder="Type your technical response. Explain your reasoning, trade-offs and concrete details."
              className="w-full rounded-2xl bg-white border border-slate-300 p-4 text-sm text-slate-900 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 font-sans leading-relaxed"
            />
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400 font-mono">
                {answerText.trim() ? `${answerText.trim().split(/\s+/).length} words` : ''}
              </span>
              <Button
                variant="primary"
                size="md"
                onClick={handleSubmitAnswer}
                disabled={!answerText.trim() || isEvaluating}
                isLoading={isEvaluating}
                loadingText="Evaluating your answer..."
                className="gap-2"
              >
                <span>Submit Answer</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </Card>
        ) : (
          /* Evaluation feedback */
          <Card className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-600" /> Answer Evaluation
              </h3>
              <span className="text-2xl font-extrabold text-blue-700 font-mono">
                {Math.round(latestEvaluation.score)}/100
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: 'Correctness', value: latestEvaluation.correctness },
                { label: 'Depth', value: latestEvaluation.technical_depth },
                { label: 'Clarity', value: latestEvaluation.clarity },
                { label: 'Confidence', value: latestEvaluation.confidence },
              ].map((m) => (
                <div key={m.label} className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                  <span className="text-[10px] text-slate-500 block">{m.label}</span>
                  <span className="text-lg font-bold text-slate-900 font-mono">{Math.round(m.value)}</span>
                </div>
              ))}
            </div>

            <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-sm text-slate-700">
              {latestEvaluation.feedback}
            </div>

            {latestEvaluation.knowledge_gap && (
              <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-sm text-amber-800">
                <strong className="block text-xs font-bold uppercase tracking-wider mb-1">Missing concept</strong>
                {latestEvaluation.knowledge_gap}
              </div>
            )}

            <div className="flex items-center justify-between pt-2">
              <Badge variant="secondary">
                Next question difficulty: {latestEvaluation.next_difficulty}
              </Badge>
              <Button
                variant="primary"
                size="md"
                onClick={handleNextQuestion}
                className="gap-2"
                disabled={isFinishing}
              >
                <span>{answered + 1 >= totalQuestions ? 'Finish Interview' : 'Next Question'}</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </Card>
        )}

        {isFinishing && (
          <Card className="p-4 text-sm text-slate-600 flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
            Generating your final interview report...
          </Card>
        )}
      </main>
    </div>
  );
}
