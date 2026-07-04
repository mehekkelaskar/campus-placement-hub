import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const tokens = JSON.parse(localStorage.getItem('tokens'));
  if (tokens?.access) {
    config.headers.Authorization = `Bearer ${tokens.access}`;
  }
  return config;
});

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const tokens = JSON.parse(localStorage.getItem('tokens'));

      if (tokens?.refresh) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: tokens.refresh,
          });
          const newTokens = response.data;
          localStorage.setItem('tokens', JSON.stringify(newTokens));
          originalRequest.headers.Authorization = `Bearer ${newTokens.access}`;
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('tokens');
          localStorage.removeItem('user');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  getMe: () => api.get('/auth/me/'),
  updateMe: (data) => api.put('/auth/me/', data),
  refreshToken: (refresh) => api.post('/auth/token/refresh/', { refresh }),
  forgotPassword: (email) => api.post('/auth/forgot-password/', { email }),
  resetPassword: (token, password, password2) => api.post('/auth/reset-password/', { token, password, password2 }),
};

// Company API
export const companyAPI = {
  list: (params) => api.get('/companies/', { params }),
  detail: (id) => api.get(`/companies/${id}/`),
  adminList: () => api.get('/companies/admin/'),
  adminCreate: (data) => api.post('/companies/admin/create/', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  adminUpdate: (id, data) => api.put(`/companies/admin/${id}/update/`, data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  adminDelete: (id) => api.delete(`/companies/admin/${id}/delete/`),
  adminTogglePublish: (id) => api.patch(`/companies/admin/${id}/publish/`),
};

// Bookmark API
export const bookmarkAPI = {
  list: () => api.get('/bookmarks/'),
  toggle: (companyId) => api.post(`/bookmarks/${companyId}/`),
};

// Dashboard API
export const dashboardAPI = {
  student: () => api.get('/dashboard/'),
  admin: () => api.get('/dashboard/admin/'),
};

// Placement Drive API
export const driveAPI = {
  list: (params) => api.get('/companies/drives/', { params }),
};

// Admin Student API
export const studentAdminAPI = {
  list: (params) => api.get('/auth/admin/students/', { params }),
  verify: (id) => api.patch(`/auth/admin/students/${id}/verify/`),
  toggleActive: (id) => api.patch(`/auth/admin/students/${id}/toggle-active/`),
};

// AI Chatbot API
export const chatbotAPI = {
  ask: (question) => api.post('/auth/chatbot/', { question }),
};

export default api;
