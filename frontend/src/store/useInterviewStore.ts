import { create } from 'zustand';
import { Interview, Question, Evaluation } from '@/services/interviewService';

interface InterviewState {
  activeInterview: Interview | null;
  questions: Question[];
  currentQuestion: Question | null;
  latestEvaluation: Evaluation | null;
  isGeneratingQuestion: boolean;

  setActiveInterview: (interview: Interview, question: Question | null) => void;
  setCurrentQuestion: (question: Question | null) => void;
  addQuestion: (question: Question) => void;
  setLatestEvaluation: (evaluation: Evaluation | null) => void;
  setGenerating: (generating: boolean) => void;
  reset: () => void;
}

export const useInterviewStore = create<InterviewState>((set) => ({
  activeInterview: null,
  questions: [],
  currentQuestion: null,
  latestEvaluation: null,
  isGeneratingQuestion: false,

  setActiveInterview: (interview, question) =>
    set({
      activeInterview: interview,
      questions: question ? [question] : [],
      currentQuestion: question,
      latestEvaluation: null,
    }),

  setCurrentQuestion: (question) => set({ currentQuestion: question }),

  addQuestion: (question) =>
    set((state) => ({
      questions: [...state.questions, question],
      currentQuestion: question,
    })),

  setLatestEvaluation: (evaluation) => set({ latestEvaluation: evaluation }),

  setGenerating: (generating) => set({ isGeneratingQuestion: generating }),

  reset: () =>
    set({
      activeInterview: null,
      questions: [],
      currentQuestion: null,
      latestEvaluation: null,
      isGeneratingQuestion: false,
    }),
}));
