export type ResumeOptimizerSuggestionStatus = 'pending' | 'accepted' | 'rejected';

export interface ResumeOptimizerSuggestion {
  id: string;
  title: string;
  category: string;
  original: string;
  optimized: string;
  impact: string;
  status: ResumeOptimizerSuggestionStatus;
}

export interface ResumeOptimizerTimelineItem {
  title: string;
  detail: string;
  time: string;
}

export interface ResumeOptimizerData {
  profileName: string;
  currentResumeScore: number;
  optimizedResumeScore: number;
  currentAtsScore: number;
  optimizedAtsScore: number;
  summary: {
    original: string;
    optimized: string;
  };
  projectHighlights: {
    original: string;
    optimized: string;
  }[];
  bulletPoints: {
    original: string;
    optimized: string;
  }[];
  technicalKeywords: string[];
  missingSkills: string[];
  missingSections: string[];
  suggestions: ResumeOptimizerSuggestion[];
  timeline: ResumeOptimizerTimelineItem[];
}
