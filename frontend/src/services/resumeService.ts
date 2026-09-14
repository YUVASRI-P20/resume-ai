import { apiClient } from './apiClient';

export interface ExtractedSkill {
  id: string;
  name: string;
  category: string;
  proficiency_hint: string | null;
}

export interface ResumeSection {
  id: string;
  section_type: string;
  order_index: number;
  content_text: string | null;
  content_json: unknown;
}

export interface ResumeListItem {
  id: string;
  original_filename: string;
  status: 'uploaded' | 'parsing' | 'parsed' | 'parse_failed';
  full_name: string | null;
  email: string | null;
  file_size_bytes: number;
  created_at: string;
  updated_at: string;
}

export interface ResumeDetail extends ResumeListItem {
  parse_error: string | null;
  phone: string | null;
  location: string | null;
  linkedin_url: string | null;
  github_url: string | null;
  portfolio_url: string | null;
  sections: ResumeSection[];
  skills: ExtractedSkill[];
}

export const resumeService = {
  async upload(file: File): Promise<{ id: string; status: string; message: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/resumes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 180000, // parsing + AI extraction can be slow
    });
    return response.data;
  },

  async list(): Promise<ResumeListItem[]> {
    const response = await apiClient.get<ResumeListItem[]>('/resumes');
    return response.data;
  },

  async get(resumeId: string): Promise<ResumeDetail> {
    const response = await apiClient.get<ResumeDetail>(`/resumes/${resumeId}`);
    return response.data;
  },

  async remove(resumeId: string): Promise<void> {
    await apiClient.delete(`/resumes/${resumeId}`);
  },
};
