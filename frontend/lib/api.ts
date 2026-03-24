import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor — attach JWT token if present
api.interceptors.request.use(
    (config) => {
        const token = typeof window !== 'undefined' ? localStorage.getItem(TOKEN_KEY) : null;
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Auto-logout on 401 Unauthorized
        if (error.response?.status === 401) {
            if (typeof window !== 'undefined') {
                localStorage.removeItem(TOKEN_KEY);
                localStorage.removeItem(USER_KEY);
                window.location.href = '/auth/login';
            }
        }
        return Promise.reject(error);
    }
);

export const authService = {
    login: async (username: string, password: string) => {
        // OAuth2 password flow expects form-encoded body
        const params = new URLSearchParams();
        params.append('username', username);
        params.append('password', password);

        const response = await api.post('/auth/login', params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });

        const { access_token, user } = response.data;

        localStorage.setItem(TOKEN_KEY, access_token);
        localStorage.setItem(USER_KEY, JSON.stringify(user ?? { username }));

        return response.data;
    },

    register: async (username: string, email: string, password: string) => {
        const response = await api.post('/auth/register', { username, email, password });

        const { access_token, user } = response.data;

        if (access_token) {
            localStorage.setItem(TOKEN_KEY, access_token);
            localStorage.setItem(USER_KEY, JSON.stringify(user ?? { username, email }));
        }

        return response.data;
    },

    logout: () => {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        window.location.href = '/auth/login';
    },

    getToken: (): string | null => {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem(TOKEN_KEY);
    },

    getUser: (): any | null => {
        if (typeof window === 'undefined') return null;
        const raw = localStorage.getItem(USER_KEY);
        if (!raw) return null;
        try {
            return JSON.parse(raw);
        } catch {
            return null;
        }
    },

    isAuthenticated: (): boolean => {
        return !!authService.getToken();
    },
};

export const searchService = {
    search: async (query: string, top_k: number = 5, mode: string = "research") => {
        const response = await api.post('/search', { query, top_k, mode });
        return response.data;
    },
};

export const chatService = {
    chat: async (query: string, top_k: number = 3, mode: string = "advice") => {
        const response = await api.post('/chat', { query, top_k, mode });
        return response.data;
    },
};

export const historyService = {
    getHistory: async (limit: number = 30) => {
        const response = await api.get('/history', { params: { limit } });
        return response.data;
    },

    deleteHistory: async (id: string) => {
        const response = await api.delete(`/history/${id}`);
        return response.data;
    },

    clearAllHistory: async () => {
        const response = await api.delete('/history');
        return response.data;
    },
};

export const profileService = {
    getProfile: async () => {
        const response = await api.get('/profile');
        return response.data;
    },
};

export default api;
