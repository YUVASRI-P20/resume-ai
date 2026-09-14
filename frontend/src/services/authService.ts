import { apiClient } from './apiClient';
import type { UserProfile } from '@/types/user';

interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface AuthResponse {
  user: BackendUser;
  tokens: TokenPair;
}

interface BackendUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_email_verified: boolean;
  created_at: string;
  updated_at: string;
}

export function mapBackendUser(u: BackendUser): UserProfile {
  return {
    id: u.id,
    name: u.full_name,
    email: u.email,
    avatarUrl: '',
    role: 'Fullstack',
    targetCompany: '',
    experienceLevel: 'Entry',
    readinessScore: 0,
    completedInterviewsCount: 0,
    studyStreakDays: 0,
    joinedDate: u.created_at ? new Date(u.created_at).toLocaleDateString(undefined, { month: 'long', year: 'numeric' }) : '',
    isRecruiter: u.role === 'RECRUITER',
    isOnboarded: false,
  };
}

export const authService = {
  async register(payload: {
    email: string;
    password: string;
    full_name: string;
    role?: 'STUDENT' | 'RECRUITER';
  }): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register', payload);
    return response.data;
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', { email, password });
    return response.data;
  },

  async logout(refreshToken: string): Promise<void> {
    try {
      await apiClient.post('/auth/logout', { refresh_token: refreshToken });
    } catch {
      // Logout client-side regardless; server token will expire naturally.
    }
  },

  async refresh(refreshToken: string): Promise<TokenPair> {
    const response = await apiClient.post<TokenPair>('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },

  async me(): Promise<UserProfile> {
    const response = await apiClient.get<BackendUser>('/auth/me');
    return mapBackendUser(response.data);
  },
};
