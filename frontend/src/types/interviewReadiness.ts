export type SkillLevel = 'strong' | 'average' | 'weak' | 'missing';
export type PriorityLevel = 'Critical' | 'High' | 'Medium' | 'Low';
export type DifficultyLevel = 'Easy' | 'Medium' | 'Hard';

export interface CompanyMatch {
  id: string;
  name: string;
  matchScore: number; // e.g. 91 (for 91%)
  role: string;
  hiringDifficulty: string;
  keySkillsMatched: string[];
  missingCriticalSkills: string[];
  averagePackage: string;
  accentColor: string;
}

export interface SkillCategoryBreakdown {
  strong: string[];
  average: string[];
  weak: string[];
  missing: string[];
}

export interface SkillAnalysisItem {
  id: string;
  name: string;
  level: SkillLevel;
  score: number;
  category: string;
  industryBenchmark: number;
}

export interface TechnicalKnowledgeCategory {
  id: string;
  name: string;
  currentLevel: number; // 0 - 100
  targetLevel: number;  // 0 - 100
  progressPercentage: number;
  topicsCovered: number;
  totalTopics: number;
  iconName: string;
}

export interface InterviewConfidence {
  id: string;
  roundName: string;
  score: number; // 0 - 100
  description: string;
  keyStrengths: string;
  areaToImprove: string;
}

export interface MissingTopic {
  id: string;
  topic: string;
  category: string;
  importance: PriorityLevel;
  estimatedHours: number;
  difficulty: DifficultyLevel;
  priority: PriorityLevel;
  recommendedResource: string;
}

export interface ActionPlanStep {
  id: string;
  stepNumber: number;
  title: string;
  description: string;
  estimatedHours: number;
  status: 'completed' | 'in_progress' | 'upcoming';
  category: string;
  actionRoute?: string;
}

export interface ReadinessTimeframe {
  days: 7 | 14 | 21;
  predictedScore: number;
  hoursPerDay: number;
  milestone: string;
  recommendedPace: string;
}

export interface ReadinessComparison {
  currentReadiness: number;
  predictedReadiness: number;
  daysToAchieve: number;
  confidenceInterval: string;
  historyData: { day: string; current: number; predicted: number }[];
}

export interface PreparationChecklistItem {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  category: string;
  estimatedMinutes: number;
  actionRoute?: string;
}

export interface CareerInsight {
  id: string;
  type: 'technology' | 'certification' | 'project' | 'portfolio' | 'github' | 'linkedin';
  title: string;
  description: string;
  impactScore: string;
  actionText: string;
  tags: string[];
}

export interface InterviewReadinessData {
  overallScore: number;
  maxScore: number;
  readinessTier: 'Interview Ready' | 'Near Ready' | 'Needs Preparation';
  summary: string;
  lastUpdated: string;
  companies: CompanyMatch[];
  skills: SkillAnalysisItem[];
  skillCategoryBreakdown: SkillCategoryBreakdown;
  technicalKnowledge: TechnicalKnowledgeCategory[];
  confidenceDashboard: InterviewConfidence[];
  missingTopics: MissingTopic[];
  actionPlan: ActionPlanStep[];
  preparationTimeframes: ReadinessTimeframe[];
  comparison: ReadinessComparison;
  checklist: PreparationChecklistItem[];
  careerInsights: CareerInsight[];
}
