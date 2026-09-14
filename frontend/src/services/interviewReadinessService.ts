import { apiClient } from './apiClient';
import { mockReadinessData } from './readinessDummyData';
import { InterviewReadinessData, PreparationChecklistItem } from '@/types/interviewReadiness';

export const fetchInterviewReadinessData = async (): Promise<InterviewReadinessData> => {
  try {
    const response = await apiClient.get<InterviewReadinessData>('/interview-readiness');
    return response.data;
  } catch {
    // Return realistic mock data when API is offline or during frontend development
    await new Promise((resolve) => setTimeout(resolve, 300));
    return mockReadinessData;
  }
};

export const updateChecklistItemApi = async (id: string, completed: boolean): Promise<{ success: boolean }> => {
  try {
    const response = await apiClient.patch<{ success: boolean }>(`/interview-readiness/checklist/${id}`, { completed });
    return response.data;
  } catch {
    return { success: true };
  }
};

export const recalculateReadinessScoreApi = async (companyIds: string[]): Promise<Partial<InterviewReadinessData>> => {
  try {
    const response = await apiClient.post<Partial<InterviewReadinessData>>('/interview-readiness/recalculate', { companyIds });
    return response.data;
  } catch {
    return {
      overallScore: companyIds.length > 0 ? 89 : 87,
    };
  }
};
