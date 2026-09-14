'use client';

import { create } from 'zustand';
import {
  resumeService,
  ResumeDetail,
  ResumeListItem,
} from '@/services/resumeService';

interface ResumeState {
  resumes: ResumeListItem[];
  activeResumeId: string | null;
  currentDetail: ResumeDetail | null;
  isLoadingList: boolean;
  isUploading: boolean;
  uploadMessage: string | null;
  error: string | null;

  loadResumes: () => Promise<void>;
  uploadResume: (file: File) => Promise<ResumeDetail | null>;
  setActiveResume: (id: string) => Promise<void>;
  deleteResume: (id: string) => Promise<void>;
  clearError: () => void;
}

export const useResumeStore = create<ResumeState>((set, get) => ({
  resumes: [],
  activeResumeId: null,
  currentDetail: null,
  isLoadingList: false,
  isUploading: false,
  uploadMessage: null,
  error: null,

  loadResumes: async () => {
    set({ isLoadingList: true, error: null });
    try {
      const resumes = await resumeService.list();
      const activeResumeId = get().activeResumeId;
      const stillValid = activeResumeId && resumes.some((r) => r.id === activeResumeId);
      set({
        resumes,
        activeResumeId: stillValid ? activeResumeId : resumes[0]?.id ?? null,
        isLoadingList: false,
      });
      if (resumes.length > 0) {
        await get().setActiveResume(stillValid ? (activeResumeId as string) : resumes[0].id);
      } else {
        set({ currentDetail: null });
      }
    } catch (err) {
      set({ isLoadingList: false, error: 'Could not load your resumes. Is the backend running?' });
    }
  },

  uploadResume: async (file: File) => {
    set({ isUploading: true, error: null, uploadMessage: null });
    try {
      const result = await resumeService.upload(file);
      set({
        uploadMessage: result.message || 'Resume uploaded successfully.',
        isUploading: false,
      });
      await get().loadResumes();
      // Return the freshly-parsed detail for immediate display.
      if (result.id) {
        const detail = await resumeService.get(result.id);
        set({ activeResumeId: detail.id, currentDetail: detail });
        return detail;
      }
      return null;
    } catch (err) {
      const { getApiErrorMessage } = await import('@/services/apiClient');
      set({
        isUploading: false,
        error: getApiErrorMessage(err, 'Please upload a valid PDF resume.'),
      });
      return null;
    }
  },

  setActiveResume: async (id: string) => {
    set({ activeResumeId: id, currentDetail: null });
    try {
      const detail = await resumeService.get(id);
      set({ currentDetail: detail });
    } catch {
      set({ error: 'Could not load the selected resume.' });
    }
  },

  deleteResume: async (id: string) => {
    try {
      await resumeService.remove(id);
      await get().loadResumes();
    } catch (err) {
      const { getApiErrorMessage } = await import('@/services/apiClient');
      set({ error: getApiErrorMessage(err, 'Could not delete the resume.') });
    }
  },

  clearError: () => set({ error: null }),
}));
