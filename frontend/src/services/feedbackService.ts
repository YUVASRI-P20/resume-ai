import { apiClient } from './apiClient';

export interface FeedbackReport {
  id: string;
  interview_id: string;
  user_id: string;
  overall_score: number;
  technical_score: number;
  communication_score: number;
  confidence_score: number;
  coding_score: number;
  interview_summary: string;
  detailed_feedback: string;
  created_at: string;
  categories: { id: string; category_name: string; score: number; comments: string }[];
  strengths: { id: string; title: string; description: string }[];
  weaknesses: { id: string; title: string; description: string }[];
  hallucinations: {
    id: string;
    concept: string;
    candidate_claim: string;
    correct_explanation: string;
    severity: string;
    confidence: number;
  }[];
}

export const feedbackService = {
  /** Final report for an interview — derived from real evaluation records. */
  async getReport(interviewId: string): Promise<FeedbackReport> {
    const response = await apiClient.get<FeedbackReport>(`/feedback/${interviewId}/report`);
    return response.data;
  },
};
