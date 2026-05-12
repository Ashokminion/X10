import axios from 'axios';

// AI Service runs on port 8000 - this is the main backend now
const AI_URL = process.env.REACT_APP_AI_SERVICE_URL || 'http://localhost:8000';

// Create axios instance for AI service
const api = axios.create({
    baseURL: AI_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add JWT token to requests
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Handle errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Authentication API
export const authAPI = {
    login: (credentials) => api.post('/api/auth/login', credentials),
};

// Employee API
export const employeeAPI = {
    getAll: (params = {}) => api.get('/api/employees', { params }),
    getById: (code) => api.get(`/api/employees/${code}`),
    create: (employee) => api.post('/api/employees', employee),
    update: (code, employee) => api.put(`/api/employees/${code}`, employee),
    delete: (code) => api.delete(`/api/employees/${code}`),
    uploadCSV: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/api/employees/upload-csv', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },
    getUploadHistory: () => api.get('/api/employees/upload-history'),
};

// Company API
export const companyAPI = {
    getAll: () => api.get('/api/companies'),
    getDetail: (name) => api.get(`/api/companies/${encodeURIComponent(name)}`),
    compareAll: () => api.get('/api/companies/compare/all'),
    create: (company) => api.post('/api/companies', company),
    update: (name, company) => api.put(`/api/companies/${encodeURIComponent(name)}`, company),
    delete: (name) => api.delete(`/api/companies/${encodeURIComponent(name)}`),
};

// Dashboard API
export const dashboardAPI = {
    getStats: () => api.get('/api/dashboard/stats'),
};

// Chatbot API
export const chatbotAPI = {
    sendMessage: (message, userId) =>
        api.post('/api/chatbot/query', { user_id: userId, message }),
    getHistory: (userId) => api.get(`/api/chatbot/history/${userId}`),
};

// Optimization API
export const optimizationAPI = {
    optimize: (data) => api.post('/api/optimization/optimize', data),
    reassignRisk: (data) => api.post('/api/optimization/reassign-risk', data),
};

// Reports API
export const reportsAPI = {
    generatePDF: () => api.get('/api/reports/generate-pdf', { responseType: 'blob' }),
};

// Scenario API
export const scenarioAPI = {
    simulate: (data) => api.post('/api/scenario/simulate', data),
};

export default api;
