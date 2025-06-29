// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock styled-components completely inline
jest.mock('styled-components', () => {
  const mockStyledFunction = (tag) => (styles) => (props) => {
    const React = require('react');
    const { children, ...otherProps } = props || {};
    return React.createElement(tag, otherProps, children);
  };

  const mockStyled = new Proxy(mockStyledFunction, {
    get: (target, prop) => {
      if (typeof prop === 'string') {
        return target(prop);
      }
      return target;
    }
  });

  // Add common HTML elements
  mockStyled.div = mockStyledFunction('div');
  mockStyled.button = mockStyledFunction('button');
  mockStyled.input = mockStyledFunction('input');
  mockStyled.textarea = mockStyledFunction('textarea');
  mockStyled.span = mockStyledFunction('span');
  mockStyled.p = mockStyledFunction('p');
  mockStyled.h1 = mockStyledFunction('h1');
  mockStyled.h2 = mockStyledFunction('h2');
  mockStyled.h3 = mockStyledFunction('h3');
  mockStyled.select = mockStyledFunction('select');
  mockStyled.option = mockStyledFunction('option');
  mockStyled.label = mockStyledFunction('label');
  mockStyled.form = mockStyledFunction('form');
  mockStyled.header = mockStyledFunction('header');
  mockStyled.footer = mockStyledFunction('footer');
  mockStyled.nav = mockStyledFunction('nav');
  mockStyled.section = mockStyledFunction('section');
  mockStyled.article = mockStyledFunction('article');
  mockStyled.aside = mockStyledFunction('aside');
  mockStyled.main = mockStyledFunction('main');

  return {
    __esModule: true,
    default: mockStyled,
    css: jest.fn(() => ''),
    keyframes: jest.fn(() => ''),
    ThemeProvider: ({ children }) => children,
    createGlobalStyle: jest.fn(() => () => null)
  };
});

// Mock react-icons
jest.mock('react-icons/fa', () => ({
  FaPaperPlane: () => 'FaPaperPlane-icon',
  FaRobot: () => 'FaRobot-icon', 
  FaUser: () => 'FaUser-icon',
  FaExclamationTriangle: () => 'FaExclamationTriangle-icon',
  FaShieldAlt: () => 'FaShieldAlt-icon',
  FaCog: () => 'FaCog-icon',
  FaToggleOn: () => 'FaToggleOn-icon',
  FaToggleOff: () => 'FaToggleOff-icon',
  FaClipboardList: () => 'FaClipboardList-icon',
  FaRefresh: () => 'FaRefresh-icon',
  FaFilter: () => 'FaFilter-icon',
  FaDownload: () => 'FaDownload-icon',
  FaExclamationCircle: () => 'FaExclamationCircle-icon',
  FaEye: () => 'FaEye-icon'
}));

jest.mock('react-icons/fi', () => ({
  FiSend: () => 'FiSend-icon',
  FiUser: () => 'FiUser-icon',
  FiCpu: () => 'FiCpu-icon', 
  FiShield: () => 'FiShield-icon',
  FiAlertTriangle: () => 'FiAlertTriangle-icon',
  FiSettings: () => 'FiSettings-icon',
  FiRefreshCw: () => 'FiRefreshCw-icon',
  FiMessageSquare: () => 'FiMessageSquare-icon'
}));

// Mock date-fns
jest.mock('date-fns', () => ({
  format: jest.fn((date, formatStr) => {
    if (date instanceof Date) {
      return date.toISOString().split('T')[0];
    }
    return '2023-01-01';
  }),
  parseISO: jest.fn((dateString) => new Date(dateString)),
  isValid: jest.fn(() => true)
}));

// Suppress console warnings in tests
const originalError = console.error;
const originalWarn = console.warn;

beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' && 
      (args[0].includes('Warning: ReactDOM.render is deprecated') ||
       args[0].includes('Warning: componentWillReceiveProps') ||
       args[0].includes('Warning: componentWillUpdate') ||
       args[0].includes('Warning: `ReactDOMTestUtils.act` is deprecated') ||
       args[0].includes('Warning: React does not recognize') ||
       args[0].includes('Warning: Received') ||
       args[0].includes('Warning: An update to') ||
       args[0].includes('Failed to initialize app: Error: Network error') ||
       args[0].includes('act(...)'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
  
  console.warn = (...args) => {
    if (
      typeof args[0] === 'string' && 
      (args[0].includes('styled-components') ||
       args[0].includes('deprecated') ||
       args[0].includes('act(...)'))
    ) {
      return;
    }
    originalWarn.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
  console.warn = originalWarn;
});

// Mock window.matchMedia for responsive tests
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));