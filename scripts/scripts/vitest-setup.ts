import { vi } from 'vitest';

vi.mock('electron-log', () => ({
  default: {
    scope: () => ({
      info: console.info,
      error: console.error,
      warn: console.warn,
      debug: console.debug,
    }),
    initialize: vi.fn(),
    transports: {
      file: {
        level: 'info',
      },
    },
  },
}));

// Mock electron
vi.mock('electron', () => ({
  app: {
    on: vi.fn(),
  },
  shell: {
    openPath: vi.fn(),
  },
}));
