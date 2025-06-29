import { apiService } from './apiService';

// Mock axios
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: jest.fn(),
    post: jest.fn(),
    defaults: { headers: { common: {} } },
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() }
    }
  })),
  get: jest.fn(),
  post: jest.fn()
}));

describe('ApiService', () => {
  let mockAxios;

  beforeEach(() => {
    const axios = require('axios');
    mockAxios = axios.create();
    jest.clearAllMocks();
  });

  describe('getHealth', () => {
    test('returns health data successfully', async () => {
      const mockHealthData = {
        status: 'healthy',
        pipeline_loaded: true,
        audit_enabled: true,
        enabled_guardrails: 5,
        total_guardrails: 5
      };

      mockAxios.get.mockResolvedValue({ data: mockHealthData });

      const result = await apiService.getHealth();

      expect(mockAxios.get).toHaveBeenCalledWith('/api/health');
      expect(result).toEqual(mockHealthData);
    });

    test('handles health check error', async () => {
      mockAxios.get.mockRejectedValue(new Error('Network error'));

      await expect(apiService.getHealth()).rejects.toThrow('Network error');
    });
  });

  describe('getGuardrails', () => {
    test('returns guardrail settings successfully', async () => {
      const mockGuardrailData = {
        input_guardrails: [
          { name: 'length_check', enabled: true },
          { name: 'pii_detection', enabled: false }
        ],
        output_guardrails: [
          { name: 'content_filter', enabled: true }
        ],
        preset: 'customer_service',
        use_conversation_aware_prompt_injection: false
      };

      mockAxios.get.mockResolvedValue({ data: mockGuardrailData });

      const result = await apiService.getGuardrails();

      expect(mockAxios.get).toHaveBeenCalledWith('/api/guardrails');
      expect(result).toEqual(mockGuardrailData);
    });

    test('handles guardrails fetch error', async () => {
      mockAxios.get.mockRejectedValue(new Error('Unauthorized'));

      await expect(apiService.getGuardrails()).rejects.toThrow('Unauthorized');
    });
  });

  describe('updateGuardrails', () => {
    test('updates guardrail settings successfully', async () => {
      const settingsUpdate = {
        input_guardrails: [
          { name: 'length_check', enabled: false }
        ],
        output_guardrails: [],
        preset: 'customer_service',
        use_conversation_aware_prompt_injection: true
      };

      const mockResponse = { status: 'success', message: 'Settings updated' };
      mockAxios.post.mockResolvedValue({ data: mockResponse });

      const result = await apiService.updateGuardrails(settingsUpdate);

      expect(mockAxios.post).toHaveBeenCalledWith('/api/guardrails', settingsUpdate);
      expect(result).toEqual(mockResponse);
    });

    test('handles guardrails update error', async () => {
      const settingsUpdate = { invalid: 'data' };
      mockAxios.post.mockRejectedValue(new Error('Validation error'));

      await expect(apiService.updateGuardrails(settingsUpdate)).rejects.toThrow('Validation error');
    });
  });

  describe('getPresets', () => {
    test('returns available presets successfully', async () => {
      const mockPresets = {
        presets: {
          'customer_service': 'Customer Service',
          'content_moderation': 'Content Moderation',
          'basic_pipeline': 'Basic Pipeline'
        }
      };

      mockAxios.get.mockResolvedValue({ data: mockPresets });

      const result = await apiService.getPresets();

      expect(mockAxios.get).toHaveBeenCalledWith('/api/presets');
      expect(result).toEqual(mockPresets);
    });
  });

  describe('loadPreset', () => {
    test('loads preset successfully', async () => {
      const presetName = 'content_moderation';
      const mockResponse = { status: 'success', message: 'Preset loaded' };

      mockAxios.post.mockResolvedValue({ data: mockResponse });

      const result = await apiService.loadPreset(presetName);

      expect(mockAxios.post).toHaveBeenCalledWith('/api/preset', { preset: presetName });
      expect(result).toEqual(mockResponse);
    });

    test('handles invalid preset error', async () => {
      const presetName = 'nonexistent_preset';
      mockAxios.post.mockRejectedValue(new Error('Preset not found'));

      await expect(apiService.loadPreset(presetName)).rejects.toThrow('Preset not found');
    });
  });

  describe('sendMessage', () => {
    test('sends message successfully', async () => {
      const message = 'Hello world';
      const mockResponse = {
        content: 'Hello! How can I help you?',
        blocked: false,
        warnings: [],
        reasons: [],
        conversation_id: 'conv-123',
        processing_details: { time_ms: 250 }
      };

      mockAxios.post.mockResolvedValue({ data: mockResponse });

      const result = await apiService.sendMessage(message);

      expect(mockAxios.post).toHaveBeenCalledWith('/api/chat', { content: message });
      expect(result).toEqual(mockResponse);
    });

    test('handles blocked message', async () => {
      const message = 'My SSN is 123-45-6789';
      const mockResponse = {
        content: 'Message blocked due to PII',
        blocked: true,
        warnings: ['PII detected'],
        reasons: ['Social Security Number found'],
        conversation_id: 'conv-123',
        processing_details: { time_ms: 340 }
      };

      mockAxios.post.mockResolvedValue({ data: mockResponse });

      const result = await apiService.sendMessage(message);

      expect(result.blocked).toBe(true);
      expect(result.warnings).toContain('PII detected');
    });

    test('handles message send error', async () => {
      const message = 'Test message';
      mockAxios.post.mockRejectedValue(new Error('Server error'));

      await expect(apiService.sendMessage(message)).rejects.toThrow('Server error');
    });

    test('handles empty message', async () => {
      const message = '';
      mockAxios.post.mockRejectedValue(new Error('Content is required'));

      await expect(apiService.sendMessage(message)).rejects.toThrow('Content is required');
    });
  });

  describe('getConversation', () => {
    test('returns conversation info successfully', async () => {
      const mockConversation = {
        active: true,
        conversation_id: 'conv-123',
        message_count: 5,
        started_at: '2023-01-01T10:00:00Z'
      };

      mockAxios.get.mockResolvedValue({ data: mockConversation });

      const result = await apiService.getConversation();

      expect(mockAxios.get).toHaveBeenCalledWith('/api/conversation');
      expect(result).toEqual(mockConversation);
    });
  });

  describe('resetConversation', () => {
    test('resets conversation successfully', async () => {
      const mockResponse = { status: 'success', message: 'Conversation reset' };
      mockAxios.post.mockResolvedValue({ data: mockResponse });

      const result = await apiService.resetConversation();

      expect(mockAxios.post).toHaveBeenCalledWith('/api/conversation/reset');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getAuditLog', () => {
    test('returns audit log data successfully', async () => {
      const mockAuditData = {
        status: 'active',
        total_records: 100,
        recent_records: [
          {
            id: 1,
            timestamp: '2023-01-01T10:00:00Z',
            event_type: 'chat_message',
            content: 'Hello world',
            blocked: false
          }
        ]
      };

      mockAxios.get.mockResolvedValue({ data: mockAuditData });

      const result = await apiService.getAuditLog();

      expect(mockAxios.get).toHaveBeenCalledWith('/api/audit_log');
      expect(result).toEqual(mockAuditData);
    });

    test('handles audit log with query parameters', async () => {
      const params = { limit: 50, event_type: 'chat_message' };
      const mockAuditData = { status: 'active', recent_records: [] };

      mockAxios.get.mockResolvedValue({ data: mockAuditData });

      const result = await apiService.getAuditLog(params);

      expect(mockAxios.get).toHaveBeenCalledWith('/api/audit_log', { params });
      expect(result).toEqual(mockAuditData);
    });
  });

  describe('error handling', () => {
    test('handles network errors', async () => {
      mockAxios.get.mockRejectedValue({
        code: 'NETWORK_ERROR',
        message: 'Network Error'
      });

      await expect(apiService.getHealth()).rejects.toMatchObject({
        code: 'NETWORK_ERROR'
      });
    });

    test('handles HTTP error responses', async () => {
      mockAxios.post.mockRejectedValue({
        response: {
          status: 422,
          data: { detail: 'Validation error' }
        }
      });

      await expect(apiService.sendMessage('test')).rejects.toMatchObject({
        response: {
          status: 422
        }
      });
    });

    test('handles timeout errors', async () => {
      mockAxios.get.mockRejectedValue({
        code: 'ECONNABORTED',
        message: 'timeout of 5000ms exceeded'
      });

      await expect(apiService.getHealth()).rejects.toMatchObject({
        code: 'ECONNABORTED'
      });
    });
  });

  describe('request configuration', () => {
    test('sets correct base URL', () => {
      const axios = require('axios');
      expect(axios.create).toHaveBeenCalledWith({
        baseURL: 'https://localhost:8000',
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json'
        }
      });
    });

    test('sets correct timeout', () => {
      const axios = require('axios');
      const createCall = axios.create.mock.calls[0][0];
      expect(createCall.timeout).toBe(10000);
    });

    test('sets correct headers', () => {
      const axios = require('axios');
      const createCall = axios.create.mock.calls[0][0];
      expect(createCall.headers['Content-Type']).toBe('application/json');
    });
  });

  describe('concurrent requests', () => {
    test('handles multiple concurrent requests', async () => {
      const mockHealthData = { status: 'healthy' };
      const mockGuardrailData = { input_guardrails: [] };

      mockAxios.get
        .mockResolvedValueOnce({ data: mockHealthData })
        .mockResolvedValueOnce({ data: mockGuardrailData });

      const [healthResult, guardrailResult] = await Promise.all([
        apiService.getHealth(),
        apiService.getGuardrails()
      ]);

      expect(healthResult).toEqual(mockHealthData);
      expect(guardrailResult).toEqual(mockGuardrailData);
      expect(mockAxios.get).toHaveBeenCalledTimes(2);
    });
  });
});