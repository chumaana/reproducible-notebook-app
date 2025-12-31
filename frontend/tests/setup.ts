// frontend/tests/setup.ts
import { vi } from 'vitest'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock as any

// Mock window.fs (for file operations in artifacts)
global.window.fs = {
  readFile: vi.fn(),
} as any
