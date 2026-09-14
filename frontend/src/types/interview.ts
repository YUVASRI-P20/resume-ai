export type QuestionCategory = 'Technical' | 'System Design' | 'Coding' | 'Behavioral' | 'Resume Deep Dive';

export interface TestCase {
  id: string;
  input: string;
  expectedOutput: string;
  actualOutput?: string;
  passed?: boolean;
  isHidden?: boolean;
}

export interface InterviewQuestion {
  id: string;
  category: QuestionCategory;
  title: string;
  prompt: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  starterCode?: string;
  language?: string;
  testCases?: TestCase[];
  timeLimitSeconds?: number;
  hints?: string[];
  expectedKeywords?: string[];
}

export interface InterviewAnswer {
  questionId: string;
  answerText: string;
  codeSolution?: string;
  audioRecordingUrl?: string;
  timeSpentSeconds: number;
  aiCritique?: string;
  score?: number;
  hallucinationsDetected?: string[];
}

export interface InterviewSession {
  id: string;
  title: string;
  companyName: string;
  companyLogo?: string;
  domain: string;
  difficulty: 'Junior' | 'Mid' | 'Senior' | 'Staff';
  createdAt: string;
  durationMinutes: number;
  status: 'Upcoming' | 'In Progress' | 'Completed';
  questions: InterviewQuestion[];
  answers: Record<string, InterviewAnswer>;
  overallScore?: number;
  technicalScore?: number;
  communicationScore?: number;
  confidenceScore?: number;
  readinessScore?: number;
}
