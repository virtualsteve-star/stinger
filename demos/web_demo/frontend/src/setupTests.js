// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock styled-components for testing
jest.mock('styled-components', () => ({
  __esModule: true,
  default: jest.fn().mockImplementation((component) => {
    return jest.fn().mockImplementation(({ children, ...props }) => {
      const React = require('react');
      return React.createElement(component, props, children);
    });
  }),
  css: jest.fn(),
  keyframes: jest.fn(),
  ThemeProvider: ({ children }) => children
}));

// Mock react-icons
jest.mock('react-icons/fa', () => ({
  FaPaperPlane: () => 'FaPaperPlane',
  FaRobot: () => 'FaRobot', 
  FaUser: () => 'FaUser',
  FaExclamationTriangle: () => 'FaExclamationTriangle',
  FaShieldAlt: () => 'FaShieldAlt',
  FaCog: () => 'FaCog',
  FaToggleOn: () => 'FaToggleOn',
  FaToggleOff: () => 'FaToggleOff',
  FaClipboardList: () => 'FaClipboardList',
  FaRefresh: () => 'FaRefresh',
  FaFilter: () => 'FaFilter',
  FaDownload: () => 'FaDownload',
  FaExclamationCircle: () => 'FaExclamationCircle',
  FaEye: () => 'FaEye'
}));

jest.mock('react-icons/fi', () => ({
  FiSend: () => 'FiSend',
  FiUser: () => 'FiUser',
  FiCpu: () => 'FiCpu', 
  FiShield: () => 'FiShield',
  FiAlertTriangle: () => 'FiAlertTriangle'
}));

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
  }))
}));

// Mock date-fns
jest.mock('date-fns', () => ({
  format: jest.fn((date) => '2023-01-01 10:00:00'),
  parseISO: jest.fn((dateString) => new Date(dateString))
}));

// Suppress console warnings in tests
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' && 
      args[0].includes('Warning: ReactDOM.render is deprecated')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});