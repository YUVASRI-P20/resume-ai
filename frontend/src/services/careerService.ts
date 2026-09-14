import { apiClient } from './apiClient';

export interface Company {
  id: string;
  name: string;
  description: string | null;
  industry: string | null;
}

export interface JobRole {
  id: string;
  company_id: string;
  title: string;
  description: string | null;
  domain: string | null;
  seniority: string | null;
  job_description: string | null;
}

export interface RoleRequirement {
  requirement: string;
  category: string;
  importance: number;
}

export interface RoleRequirementsResponse {
  role: JobRole;
  company: Company;
  requirements: RoleRequirement[];
}

export interface MatchEvidence {
  requirement: string;
  category: string | null;
  importance: number | null;
  evidence: string | null;
  status: 'strong' | 'moderate' | 'weak' | 'missing';
  confidence: number;
  reason: string | null;
}

export interface RoleMatchResult {
  id: string;
  resume_id: string;
  company_id: string;
  job_role_id: string;
  match_percentage: number;
  strong_areas: string[];
  weak_areas: string[];
  requirements_matched: string[];
  requirements_missing: string[];
  evidence: MatchEvidence[];
  created_at: string;
}

export interface DashboardData {
  user_name: string;
  email: string;
  streak: { streak_days: number; longest_streak_days: number; last_activity_date: string | null };
  resume: { id: string; original_filename: string; status: string; uploaded_at: string } | null;
  selected_company: string | null;
  selected_role: string | null;
  match_percentage: number | null;
  strong_areas: string[];
  weak_areas: string[];
  interview_progress: { total: number; completed: number; in_progress: number; last_score: number | null };
  knowledge_gaps: { topic: string; description: string }[];
  roadmap_progress: number | null;
}

export const careerService = {
  async listCompanies(): Promise<Company[]> {
    const response = await apiClient.get<Company[]>('/companies');
    return response.data;
  },

  async listCompanyRoles(companyId: string): Promise<JobRole[]> {
    const response = await apiClient.get<JobRole[]>(`/companies/${companyId}/roles`);
    return response.data;
  },

  async getRoleRequirements(roleId: string): Promise<RoleRequirementsResponse> {
    const response = await apiClient.get<RoleRequirementsResponse>(`/job-roles/${roleId}`);
    return response.data;
  },

  async createRoleMatch(resumeId: string, companyId: string, jobRoleId: string): Promise<RoleMatchResult> {
    const response = await apiClient.post<RoleMatchResult>(`/resumes/${resumeId}/role-match`, {
      company_id: companyId,
      job_role_id: jobRoleId,
    });
    return response.data;
  },

  async listRoleMatches(resumeId: string): Promise<RoleMatchResult[]> {
    const response = await apiClient.get<RoleMatchResult[]>(`/resumes/${resumeId}/role-match`);
    return response.data;
  },

  async getDashboard(): Promise<DashboardData> {
    const response = await apiClient.get<DashboardData>('/dashboard');
    return response.data;
  },

  async getStreak(): Promise<{ streak_days: number; longest_streak_days: number }> {
    const response = await apiClient.get('/streak');
    return response.data;
  },
};
