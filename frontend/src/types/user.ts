export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatarUrl: string;
  role: 'Frontend' | 'Backend' | 'Fullstack' | 'AI/ML' | 'DevOps' | 'System Architect';
  targetCompany: string;
  experienceLevel: 'Entry' | 'Mid-Level' | 'Senior' | 'Lead' | 'Principal';
  readinessScore: number;
  completedInterviewsCount: number;
  studyStreakDays: number;
  joinedDate: string;
  isRecruiter?: boolean;
  githubUrl?: string;
  linkedinUrl?: string;
  portfolioUrl?: string;
  phone?: string;
  location?: string;
  bio?: string;
  isOnboarded?: boolean;
}

export interface AuthState {
  user: UserProfile | null;
  isAuthenticated: boolean;
  token: string | null;
}
