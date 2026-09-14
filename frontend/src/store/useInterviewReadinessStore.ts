import { create } from 'zustand';
import { InterviewReadinessData } from '@/types/interviewReadiness';
import { mockReadinessData } from '@/services/readinessDummyData';
import { fetchInterviewReadinessData, updateChecklistItemApi } from '@/services/interviewReadinessService';

interface InterviewReadinessState {
  data: InterviewReadinessData;
  isLoading: boolean;
  selectedCompanyId: string;
  selectedCategory: string;
  activeTimeframeDays: 7 | 14 | 21;
  fetchData: () => Promise<void>;
  toggleChecklistItem: (id: string) => Promise<void>;
  setSelectedCompany: (companyId: string) => void;
  setSelectedCategory: (category: string) => void;
  setActiveTimeframeDays: (days: 7 | 14 | 21) => void;
}

export const useInterviewReadinessStore = create<InterviewReadinessState>((set, get) => ({
  data: mockReadinessData,
  isLoading: false,
  selectedCompanyId: 'all',
  selectedCategory: 'all',
  activeTimeframeDays: 14,

  fetchData: async () => {
    set({ isLoading: true });
    try {
      const data = await fetchInterviewReadinessData();
      set({ data, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  toggleChecklistItem: async (id: string) => {
    const currentChecklist = get().data.checklist;
    const targetItem = currentChecklist.find((item) => item.id === id);
    if (!targetItem) return;

    const updatedChecklist = currentChecklist.map((item) =>
      item.id === id ? { ...item, completed: !item.completed } : item
    );

    set((state) => ({
      data: {
        ...state.data,
        checklist: updatedChecklist,
      },
    }));

    await updateChecklistItemApi(id, !targetItem.completed);
  },

  setSelectedCompany: (companyId: string) => {
    set({ selectedCompanyId: companyId });
  },

  setSelectedCategory: (category: string) => {
    set({ selectedCategory: category });
  },

  setActiveTimeframeDays: (days: 7 | 14 | 21) => {
    set({ activeTimeframeDays: days });
  },
}));
