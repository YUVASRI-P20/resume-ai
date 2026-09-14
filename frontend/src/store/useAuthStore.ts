'use client';

import { create } from 'zustand';
import { UserProfile } from '@/types/user';
import { authService, mapBackendUser } from '@/services/authService';

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

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
  role?: 'STUDENT' | 'RECRUITER';
}

interface AuthStore {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isInitialized: boolean;
  /** Raw backend user for fields the mapped profile doesn't carry. */
  backendUser: BackendUser | null;
  accessToken: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (payload: RegisterPayload) => Promise<UserProfile>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => void;
}

export const TOKEN_KEY = 'interviewiq_access_token';
export const REFRESH_KEY = 'interviewiq_refresh_token';
export const USER_KEY = 'interviewiq_user';

const getStoredUser = (): UserProfile | null => {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem(USER_KEY);
    const token = localStorage.getItem(TOKEN_KEY);
    if (raw && token) return JSON.parse(raw);
  } catch (_) {}
  return null;
};

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: getStoredUser(),
  isAuthenticated: Boolean(getStoredUser()),
  isInitialized: false,
  backendUser: null,
  accessToken: null,

  login: async (email: string, password: string) => {
    try {
      const res = await authService.login(email.trim(), password);
      if (typeof window !== 'undefined') {
        localStorage.setItem(TOKEN_KEY, res.tokens.access_token);
        localStorage.setItem(REFRESH_KEY, res.tokens.refresh_token);
      }
      const profile = mapBackendUser(res.user);
      if (typeof window !== 'undefined') {
        localStorage.setItem(USER_KEY, JSON.stringify(profile));
      }
      set({ user: profile, isAuthenticated: true, backendUser: res.user, accessToken: res.tokens.access_token });
      return true;
    } catch {
      return false;
    }
  },

  register: async (payload: RegisterPayload) => {
    const res = await authService.register({
      email: payload.email.trim(),
      password: payload.password,
      full_name: payload.name.trim(),
      role: payload.role || 'STUDENT',
    });
    if (typeof window !== 'undefined') {
      localStorage.setItem(TOKEN_KEY, res.tokens.access_token);
      localStorage.setItem(REFRESH_KEY, res.tokens.refresh_token);
    }
    const profile = mapBackendUser(res.user);
    if (typeof window !== 'undefined') {
      localStorage.setItem(USER_KEY, JSON.stringify(profile));
    }
    set({ user: profile, isAuthenticated: true, backendUser: res.user, accessToken: res.tokens.access_token });
    return profile;
  },

  logout: async () => {
    const refreshToken = typeof window !== 'undefined' ? localStorage.getItem(REFRESH_KEY) : null;
    if (refreshToken) {
      await authService.logout(refreshToken);
    }
    if (typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(REFRESH_KEY);
      localStorage.removeItem(USER_KEY);
    }
    set({ user: null, isAuthenticated: false, backendUser: null, accessToken: null });
  },

  refreshUser: async () => {
    try {
      const profile = await authService.me();
      if (typeof window !== 'undefined') {
        localStorage.setItem(USER_KEY, JSON.stringify(profile));
      }
      set({ user: profile, isAuthenticated: true, isInitialized: true });
    } catch {
      set({ isInitialized: true });
    }
  },

  updateProfile: (data) => {
    set((state) => {
      if (!state.user) return state;
      const updated = { ...state.user, ...data };
      if (typeof window !== 'undefined') {
        localStorage.setItem(USER_KEY, JSON.stringify(updated));
      }
      return { user: updated };
    });
  },
}));
