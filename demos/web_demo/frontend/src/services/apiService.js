import axios from 'axios';

// Configure axios defaults
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? window.location.origin 
  : 'https://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    
    if (error.response?.status === 500) {
      throw new Error('Server error. Please check the backend logs.');
    } else if (error.response?.status === 404) {
      throw new Error('API endpoint not found.');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timed out. Please try again.');
    } else if (error.code === 'NETWORK_ERROR' || !error.response) {
      throw new Error('Network error. Please check your connection and ensure the backend is running.');
    }
    
    throw error;
  }
);

export const apiService = {
  // System health and status
  async getSystemStatus() {
    const response = await api.get('/health');
    return response.data;
  },

  // Chat functionality
  async sendChatMessage(message) {
    const response = await api.post('/chat', message);
    return response.data;
  },

  // Conversation management
  async getConversationInfo() {
    const response = await api.get('/conversation');
    return response.data;
  },

  async resetConversation() {
    const response = await api.post('/conversation/reset');
    return response.data;
  },

  // Guardrail settings
  async getGuardrailSettings() {
    const response = await api.get('/guardrails');
    return response.data;
  },

  async updateGuardrailSettings(settings) {
    const response = await api.post('/guardrails', settings);
    return response.data;
  },

  // Presets
  async getAvailablePresets() {
    const response = await api.get('/presets');
    return response.data;
  },

  async loadPreset(presetData) {
    const response = await api.post('/preset', presetData);
    return response.data;
  },

  // Audit log
  async getAuditLog() {
    const response = await api.get('/audit_log');
    return response.data;
  },
};

export default apiService;