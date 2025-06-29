// Mock axios first
jest.mock('axios', () => {
  const mockAxiosInstance = {
    get: jest.fn(),
    post: jest.fn(),
    defaults: { headers: { common: {} } },
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() }
    }
  };
  
  return {
    create: jest.fn(() => mockAxiosInstance),
    get: jest.fn(),
    post: jest.fn()
  };
});

import { apiService } from './apiService';

// Get the mocked axios instance
const axios = require('axios');
const mockAxiosInstance = axios.create();

describe('ApiService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getSystemStatus', () => {
    test('returns system status successfully', async () => {
      const mockSystemStatus = {
        status: 'healthy',
        pipeline_loaded: true,
        audit_enabled: true,
        enabled_guardrails: 5,
        total_guardrails: 5
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockSystemStatus });

      const result = await apiService.getSystemStatus();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/health');
      expect(result).toEqual(mockSystemStatus);
    });

    test('handles system status error', async () => {
      mockAxiosInstance.get.mockRejectedValue(new Error('Network error'));

      await expect(apiService.getSystemStatus()).rejects.toThrow('Network error');
    });
  });

  describe('getGuardrailSettings', () => {
    test('returns guardrail settings successfully', async () => {
      const mockGuardrailData = {
        input_guardrails: [
          { name: 'pii_check', enabled: true },
          { name: 'toxicity_check', enabled: false }
        ],
        output_guardrails: [
          { name: 'code_generation_check', enabled: true }
        ],
        preset: 'customer_service'
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockGuardrailData });

      const result = await apiService.getGuardrailSettings();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/guardrails');
      expect(result).toEqual(mockGuardrailData);
    });

    test('handles guardrails fetch error', async () => {
      mockAxiosInstance.get.mockRejectedValue(new Error('Unauthorized'));

      await expect(apiService.getGuardrailSettings()).rejects.toThrow('Unauthorized');
    });
  });

  describe('updateGuardrailSettings', () => {
    test('updates guardrail settings successfully', async () => {
      const settingsUpdate = {
        input_guardrails: [{ name: 'pii_check', enabled: false }],
        output_guardrails: [{ name: 'code_generation_check', enabled: true }]
      };

      const mockResponse = { status: 'success', message: 'Settings updated' };
      mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

      const result = await apiService.updateGuardrailSettings(settingsUpdate);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/guardrails', settingsUpdate);
      expect(result).toEqual(mockResponse);
    });

    test('handles guardrails update error', async () => {
      const settingsUpdate = { invalid: 'data' };
      mockAxiosInstance.post.mockRejectedValue(new Error('Validation error'));

      await expect(apiService.updateGuardrailSettings(settingsUpdate)).rejects.toThrow('Validation error');
    });
  });

  describe('getAvailablePresets', () => {
    test('returns available presets successfully', async () => {
      const mockPresets = {
        presets: {
          'customer_service': 'Customer service configuration',
          'medical': 'Medical application configuration'
        }
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockPresets });

      const result = await apiService.getAvailablePresets();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/presets');
      expect(result).toEqual(mockPresets);
    });
  });

  describe('loadPreset', () => {
    test('loads preset successfully', async () => {
      const presetData = { preset: 'customer_service' };
      const mockResponse = { status: 'success', message: 'Preset loaded' };

      mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

      const result = await apiService.loadPreset(presetData);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/preset', presetData);
      expect(result).toEqual(mockResponse);
    });

    test('handles invalid preset error', async () => {
      const presetData = { preset: 'nonexistent_preset' };
      mockAxiosInstance.post.mockRejectedValue(new Error('Preset not found'));

      await expect(apiService.loadPreset(presetData)).rejects.toThrow('Preset not found');
    });
  });

  describe('sendChatMessage', () => {
    test('sends message successfully', async () => {
      const message = { content: 'Hello world' };
      const mockResponse = {
        content: 'Hello! How can I help you?',
        blocked: false,
        warnings: [],
        reasons: [],
        conversation_id: 'conv_123'
      };

      mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

      const result = await apiService.sendChatMessage(message);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/chat', message);
      expect(result).toEqual(mockResponse);
    });

    test('handles blocked message', async () => {
      const message = { content: 'Blocked content' };
      const mockResponse = {
        content: '',
        blocked: true,
        warnings: [],
        reasons: ['Content contains PII'],
        conversation_id: 'conv_123'
      };

      mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

      const result = await apiService.sendChatMessage(message);

      expect(result.blocked).toBe(true);
      expect(result.reasons).toContain('Content contains PII');
    });

    test('handles server error', async () => {
      const message = { content: 'Test' };
      mockAxiosInstance.post.mockRejectedValue(new Error('Server error'));

      await expect(apiService.sendChatMessage(message)).rejects.toThrow('Server error');
    });
  });

  describe('getAuditLog', () => {
    test('returns audit log successfully', async () => {
      const mockAuditData = {
        status: 'enabled',
        recent_records: [
          {
            timestamp: '2023-01-01T10:00:00Z',
            event_type: 'guardrail_decision',
            filter_name: 'pii_check',
            decision: 'block'
          }
        ],
        total_records: 1
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockAuditData });

      const result = await apiService.getAuditLog();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/audit_log');
      expect(result).toEqual(mockAuditData);
    });

    test('handles audit log error', async () => {
      mockAxiosInstance.get.mockRejectedValue(new Error('Audit log not available'));

      await expect(apiService.getAuditLog()).rejects.toThrow('Audit log not available');
    });
  });

  describe('resetConversation', () => {
    test('resets conversation successfully', async () => {
      const mockResponse = { status: 'success', message: 'Conversation reset' };
      mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

      const result = await apiService.resetConversation();

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/conversation/reset');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getConversationInfo', () => {
    test('returns conversation info successfully', async () => {
      const mockConversationInfo = {
        active: true,
        conversation_id: 'conv_123',
        turn_count: 5
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockConversationInfo });

      const result = await apiService.getConversationInfo();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/conversation');
      expect(result).toEqual(mockConversationInfo);
    });
  });

  describe('initialization', () => {
    test('axios is configured correctly', () => {
      // Test passes if the module loads without errors
      expect(apiService).toBeDefined();
      expect(apiService.getSystemStatus).toBeDefined();
      expect(apiService.sendChatMessage).toBeDefined();
    });
  });

  describe('concurrent requests', () => {
    test('handles multiple concurrent requests', async () => {
      const mockHealthData = { status: 'healthy' };
      const mockGuardrailData = { input_guardrails: [] };

      mockAxiosInstance.get
        .mockResolvedValueOnce({ data: mockHealthData })
        .mockResolvedValueOnce({ data: mockGuardrailData });

      const promises = [
        apiService.getSystemStatus(),
        apiService.getGuardrailSettings()
      ];

      const results = await Promise.all(promises);

      expect(results[0]).toEqual(mockHealthData);
      expect(results[1]).toEqual(mockGuardrailData);
      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(2);
    });
  });
});