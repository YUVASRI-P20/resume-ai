import { apiClient, getApiErrorMessage } from './apiClient';

export interface Question {
  id: string;
  question_index: number;
  question_text: string;
  question_type: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
}

export interface Interview {
  id: string;
  company: string;
  job_role: string;
  domain: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  interview_type: string;
  duration_minutes: number;
  number_of_questions: number;
  status: 'CREATED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  current_difficulty: 'Easy' | 'Medium' | 'Hard';
  question_count: number;
  completed_question_count: number;
  start_time: string | null;
  end_time: string | null;
  created_at: string;
}

export interface Evaluation {
  id: string;
  score: number;
  correctness: number;
  technical_depth: number;
  clarity: number;
  confidence: number;
  feedback: string;
  knowledge_gap: string | null;
  next_difficulty: 'Easy' | 'Medium' | 'Hard';
}

export interface InterviewSummary {
  overall_performance: string;
  technical_performance: string;
  strong_topics: string[];
  weak_topics: string[];
  average_score: number;
  difficulty_progression: string[];
  knowledge_gaps: string[] | null;
  improvement_suggestions: string[];
}

export const interviewService = {
  /** Start an interview. Requires a parsed resume; the backend grounds every question in it. */
  async start(payload: {
    company: string;
    job_role: string;
    domain: string;
    difficulty?: 'Easy' | 'Medium' | 'Hard';
    number_of_questions?: number;
    duration_minutes?: number;
    resume_id: string;
  }): Promise<Interview> {
    try {
      const response = await apiClient.post<Interview>('/interviews/start', {
        difficulty: 'Medium',
        interview_type: 'Resume Based',
        ...payload,
      });
      return response.data;
    } catch (err) {
      throw new Error(getApiErrorMessage(err, 'Could not start the interview. Please try again.'));
    }
  },

  /** Get the current question (fetches all questions; the last one is current). */
  async getQuestions(interviewId: string): Promise<Question[]> {
    const response = await apiClient.get<Question[]>(`/interviews/${interviewId}/questions`);
    return response.data;
  },

  async submitAnswer(interviewId: string, questionId: string, answerText: string): Promise<Evaluation> {
    const response = await apiClient.post<Evaluation>(`/interviews/${interviewId}/answer`, {
      question_id: questionId,
      answer_text: answerText,
    });
    return response.data;
  },

  /** Ask the AI for the next adaptive question (follow-up on the last answer). */
  async nextQuestion(interviewId: string): Promise<Question> {
    const response = await apiClient.post<Question>(`/interviews/${interviewId}/next-question`);
    return response.data;
  },

  async complete(interviewId: string): Promise<InterviewSummary> {
    await apiClient.post(`/interviews/${interviewId}/complete`);
    const response = await apiClient.get<InterviewSummary>(`/interviews/${interviewId}/results`);
    return response.data;
  },

  async get(interviewId: string): Promise<Interview> {
    const response = await apiClient.get<Interview>(`/interviews/${interviewId}`);
    return response.data;
  },

  async history(): Promise<Interview[]> {
    const response = await apiClient.get<Interview[]>('/interviews/history');
    return response.data;
  },

  async cancel(interviewId: string): Promise<void> {
    await apiClient.post(`/interviews/${interviewId}/cancel`);
  },
};
