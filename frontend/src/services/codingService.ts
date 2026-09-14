import { apiClient, getApiErrorMessage } from './apiClient';

export interface CodingQuestion {
  id: string;
  title: string;
  description: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  domain: string;
  constraints: string;
  examples: { input: string; output: string }[];
  expected_time_complexity: string;
  expected_space_complexity: string;
  supported_languages: string[];
}

export interface CodingExecution {
  id: string;
  passed_tests: number;
  total_tests: number;
  runtime_ms: number;
  memory_mb: number;
  error_message: string | null;
  execution_status: string;
}

export interface CodingReview {
  id: string;
  score: number;
  correctness: number;
  code_quality: number;
  time_complexity: string;
  space_complexity: string;
  strengths: string[];
  issues: string[];
  suggestions: string[];
  better_approach: string;
}

export interface CodingSubmission {
  id: string;
  question_id: string;
  language: string;
  source_code: string;
  status: 'PENDING' | 'RUNNING' | 'PASSED' | 'FAILED' | 'TIMEOUT' | 'COMPILATION_ERROR' | 'RUNTIME_ERROR';
  submission_time: string;
  execution: CodingExecution | null;
  review: CodingReview | null;
}

export const codingService = {
  /** Start a coding test grounded in the candidate's actual resume skills. */
  async start(resumeId: string): Promise<{ question: CodingQuestion | null; message: string | null }> {
    try {
      const response = await apiClient.post('/coding/start', { resume_id: resumeId });
      return response.data;
    } catch (err) {
      throw new Error(getApiErrorMessage(err, 'Could not start the coding test.'));
    }
  },

  async submit(questionId: string, language: string, sourceCode: string): Promise<CodingSubmission> {
    const response = await apiClient.post<CodingSubmission>('/coding/submissions', {
      question_id: questionId,
      language,
      source_code: sourceCode,
    });
    return response.data;
  },

  async requestReview(submissionId: string): Promise<CodingReview> {
    const response = await apiClient.post<CodingReview>(`/coding/submissions/${submissionId}/review`);
    return response.data;
  },

  async mySubmissions(): Promise<CodingSubmission[]> {
    const response = await apiClient.get<CodingSubmission[]>('/coding/submissions');
    return response.data;
  },
};
