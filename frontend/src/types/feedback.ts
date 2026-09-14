export interface RadarScorePoint {
  subject: string;
  A: number; // Candidate Score
  B: number; // Target Benchmark
  fullMark: number;
}

export interface HallucinationItem {
  id: string;
  statement: string;
  explanation: string;
  correction: string;
  severity: 'Low' | 'Medium' | 'High';
}

export interface KnowledgeGapItem {
  id: string;
  topic: string;
  description: string;
  recommendedAction: string;
}

export interface AIFeedbackReport {
  interviewId: string;
  overallScore: number;
  technicalScore: number;
  communicationScore: number;
  confidenceScore: number;
  readinessScore: number;
  radarData: RadarScorePoint[];
  strengths: string[];
  weaknesses: string[];
  hallucinations: HallucinationItem[];
  knowledgeGaps: KnowledgeGapItem[];
  suggestions: string[];
  resumeClaimVerification: {
    claim: string;
    verdict: 'Verified' | 'Partial Knowledge' | 'Inaccurate';
    notes: string;
  }[];
}
