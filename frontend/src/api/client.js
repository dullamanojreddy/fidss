import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('fidss_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  login: async (username, password) => {
    const res = await api.post('/auth/login', { username, password });
    return res.data;
  },
  getProfile: async () => {
    const res = await api.get('/auth/me');
    return res.data;
  },
};

export const screeningApi = {
  list: async (limit = 20, offset = 0) => {
    const res = await api.get('/screenings', { params: { limit, offset } });
    return res.data;
  },
  getById: async (id) => {
    const res = await api.get(`/screenings/${id}`);
    return res.data;
  },
  create: async (formData) => {
    const res = await api.post('/screenings', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  getEvidence: async (id) => {
    const res = await api.get(`/screenings/${id}/evidence`);
    return res.data;
  },
  submitReview: async (id, payload) => {
    const res = await api.post(`/screenings/${id}/review`, payload);
    return res.data;
  },
  getReview: async (id) => {
    const res = await api.get(`/screenings/${id}/review`);
    return res.data;
  },
};

export const auditApi = {
  getLogs: async (limit = 50) => {
    const res = await api.get('/audit/logs', { params: { limit } });
    return res.data;
  },
  verifyChain: async (screeningId) => {
    const res = await api.post(`/audit/${screeningId}/verify`);
    return res.data;
  },
  tamperDemo: async (screeningId) => {
    const res = await api.post('/audit/tamper-demo', null, { params: { screening_id: screeningId } });
    return res.data;
  },
};

export const dashboardApi = {
  getStats: async () => {
    const res = await api.get('/dashboard');
    return res.data;
  },
};

export const watchlistApi = {
  search: async (query) => {
    const res = await api.get('/watchlist/search', { params: { query } });
    return res.data;
  },
};

export const settingsApi = {
  get: async () => {
    const res = await api.get('/settings');
    return res.data;
  },
  update: async (settings) => {
    const res = await api.put('/settings', { settings });
    return res.data;
  },
  getModels: async () => {
    const res = await api.get('/settings/models');
    return res.data;
  },
};

export default api;
