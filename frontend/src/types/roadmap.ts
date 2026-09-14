export interface DailyTask {
  id: string;
  day: string;
  title: string;
  description: string;
  estimatedMinutes: number;
  completed: boolean;
  type: 'Reading' | 'Coding Practice' | 'System Design' | 'Mock Quiz';
}

export interface WeeklyPlan {
  weekNumber: number;
  theme: string;
  focusArea: string;
  status: 'Completed' | 'In Progress' | 'Upcoming';
  dailyTasks: DailyTask[];
}

export interface KnowledgeGraphNode {
  id: string;
  label: string;
  category: 'Frontend' | 'Backend' | 'System Design' | 'Algorithms' | 'Security' | 'DevOps & Cloud';
  masteryPercentage: number; // 0 - 100
  status: 'Strong' | 'Needs Improvement' | 'Weak';
  connections: string[]; // Connected Node IDs
  description?: string;
  prerequisites?: string[];
  recommendedQuestions?: string[];
  x?: number;
  y?: number;
}

export interface LearningRoadmap {
  id: string;
  title: string;
  targetRole: string;
  overallProgressPercentage: number;
  weeklyPlans: WeeklyPlan[];
  graphNodes: KnowledgeGraphNode[];
}
