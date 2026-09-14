import axios from 'axios';

// Use 127.0.0.1 instead of "localhost": on Windows the browser resolves
// localhost to ::1 (IPv6) first, and a uvicorn bound to 127.0.0.1 only would
// refuse that connection — surfacing as "Cannot reach the server".
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // AI generation can take a while
});

// Request Interceptor: Attach JWT Token if present
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('interviewiq_access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: on 401 try one silent refresh, else clear the session.
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (
      error.response?.status === 401 &&
      !original._retry &&
      typeof window !== 'undefined'
    ) {
      original._retry = true;
      const refreshToken = localStorage.getItem('interviewiq_refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem('interviewiq_access_token', data.access_token);
          localStorage.setItem('interviewiq_refresh_token', data.refresh_token);
          original.headers.Authorization = `Bearer ${data.access_token}`;
          return apiClient(original);
        } catch {
          localStorage.removeItem('interviewiq_access_token');
          localStorage.removeItem('interviewiq_refresh_token');
          localStorage.removeItem('interviewiq_user');
          if (window.location.pathname.startsWith('/dashboard')) {
            window.location.href = '/login';
          }
        }
      }
    }

    // Normalize the error message from the backend (never expose raw tracebacks).
    const data = error.response?.data;
    let message: string;
    if (typeof data?.detail === 'string') {
      // FastAPI default: { detail: "..." }
      message = data.detail;
    } else if (Array.isArray(data?.detail)) {
      // FastAPI validation: { detail: [{ msg: "..." }, ...] }
      message = data.detail.map((d: { msg?: string }) => d.msg || 'Invalid input.').join('. ');
    } else if (data?.error?.message) {
      // Backend error envelope: { success: false, error: { code, message, details? } }
      const fieldErrors = data.error.details?.errors;
      message = Array.isArray(fieldErrors) && fieldErrors.length > 0
        ? fieldErrors
            .map((e: { msg?: string }) => e.msg?.replace(/^Value error,\s*/i, '') || 'Invalid input.')
            .join('. ')
        : data.error.message;
    } else if (typeof data?.error === 'string') {
      // Legacy/flat shape: { error: "<string>" }
      message = data.error;
    } else if (error.response?.status === 429) {
      message = 'Too many attempts. Please wait a minute and try again.';
    } else if (!error.response) {
      // Request never reached the backend (down, wrong port, or CORS-blocked).
      message = 'Cannot reach the server. Please make sure the backend is running and try again.';
    } else {
      message = 'Something went wrong. Please try again.';
    }
    error.userMessage = message;
    return Promise.reject(error);
  }
);

/** Extract a user-friendly message from an API error. */
export function getApiErrorMessage(error: unknown, fallback = 'Something went wrong. Please try again.'): string {
  const err = error as { userMessage?: string; message?: string };
  return err?.userMessage || err?.message || fallback;
}
