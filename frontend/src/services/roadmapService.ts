import { apiClient } from './apiClient';

export interface RoadmapTask {
  id: string;
  day_number: number;
  task_title: string;
  description: string;
  study_time_hours: number;
  priority: 'Low' | 'Medium' | 'High' | 'Critical';
  difficulty: string;
  resources: string[];
  is_completed: boolean;
}

export interface RoadmapWeek {
  id: string;
  week_number: number;
  theme: string;
  objectives: string;
  tasks: RoadmapTask[];
}

export interface Roadmap {
  id: string;
  user_id: string;
  title: string;
  summary: string;
  total_weeks: number;
  completion_percentage: number;
  created_at: string;
  weeks: RoadmapWeek[];
}

export const roadmapService = {
  /** 15-day personalized plan from real weaknesses, job gaps and resume skills. */
  async getByInterview(interviewId: string): Promise<Roadmap> {
    const response = await apiClient.get<Roadmap>(`/interviews/${interviewId}/roadmap`);
    return response.data;
  },

  async getMine(): Promise<Roadmap> {
    const response = await apiClient.get<Roadmap>(`/roadmap/${(await import('@/store/useAuthStore')).useAuthStore.getState().user?.id ?? ''}`);
    return response.data;
  },

  async regenerate(): Promise<Roadmap> {
    const response = await apiClient.post<Roadmap>('/roadmap/regenerate');
    return response.data;
  },

  async setTaskCompleted(taskId: string, isCompleted: boolean): Promise<RoadmapTask> {
    const response = await apiClient.patch<RoadmapTask>(`/roadmap/tasks/${taskId}`, { is_completed: isCompleted });
    return response.data;
  },
};
