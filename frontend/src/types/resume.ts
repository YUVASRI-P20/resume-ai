export interface SkillItem {
  name: string;
  category: 'Frontend' | 'Backend' | 'Database' | 'DevOps' | 'AI/ML' | 'Core CS';
  proficiency: 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert';
  verifiedInResume: boolean;
  matchScore: number;
}

export interface WorkExperienceItem {
  company: string;
  role: string;
  duration: string;
  highlights: string[];
  verificationStatus: 'Verified' | 'Needs Deep-Dive' | 'Exaggerated Claim';
}

export interface ResumeAnalysis {
  id: string;
  fileName: string;
  parsedAt: string;
  matchPercentage: number;
  extractedSkills: SkillItem[];
  missingRecommendedSkills: string[];
  experience: WorkExperienceItem[];
  education: {
    degree: string;
    institution: string;
    year: string;
    gpa?: string;
  }[];
  projectClaims: {
    title: string;
    description: string;
    techStack: string[];
    aiVerificationNotes: string;
  }[];
}
