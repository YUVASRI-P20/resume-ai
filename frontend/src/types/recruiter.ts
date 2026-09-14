export interface CandidateProfile {
  id: string;
  name: string;
  avatarUrl: string;
  appliedRole: string;
  overallScore: number;
  technicalScore: number;
  communicationScore: number;
  confidenceScore: number;
  resumeMatchScore: number;
  interviewDate: string;
  recommendation: 'Strong Hire' | 'Hire' | 'Leaning Hire' | 'No Hire';
  keyStrengths: string[];
  flaggedGaps: string[];
  reportPdfUrl?: string;
}

export interface CandidateComparison {
  candidateA: CandidateProfile;
  candidateB: CandidateProfile;
  metrics: {
    category: string;
    candidateAScore: number;
    candidateBScore: number;
  }[];
}
