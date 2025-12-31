import { describe, it, expect } from 'vitest'
import { getErrorMessage, formatDate, truncate, generateId } from '@/utils/helpers'

describe('Utils - helpers', () => {
  describe('getErrorMessage', () => {
    it('extracts error from axios error with detail', () => {
      const error = {
        isAxiosError: true,
        response: {
          data: { detail: 'Authentication failed' },
        },
      }

      expect(getErrorMessage(error)).toBe('Authentication failed')
    })

    it('extracts error from axios error with error field', () => {
      const error = {
        isAxiosError: true,
        response: {
          data: { error: 'Invalid input' },
        },
      }

      expect(getErrorMessage(error)).toBe('Invalid input')
    })

    it('handles non-axios errors', () => {
      const error = new Error('Something went wrong')
      expect(getErrorMessage(error)).toBe('Something went wrong')
    })
  })

  describe('formatDate', () => {
    it('formats ISO date string', () => {
      const date = '2024-03-15T10:30:00Z'
      const formatted = formatDate(date)

      expect(formatted).toContain('Mar')
      expect(formatted).toContain('15')
      expect(formatted).toContain('2024')
    })

    it('returns "Unknown" for undefined', () => {
      expect(formatDate(undefined)).toBe('Unknown')
    })
  })

  describe('truncate', () => {
    it('truncates long text', () => {
      const text = 'This is a very long text that should be truncated'
      const result = truncate(text, 20)

      expect(result.length).toBeLessThanOrEqual(23)
      expect(result).toContain('...')
    })

    it('does not truncate short text', () => {
      const text = 'Short'
      const result = truncate(text, 20)

      expect(result).toBe('Short')
    })
  })

  describe('generateId', () => {
    it('generates unique IDs', () => {
      const id1 = generateId()
      const id2 = generateId()

      expect(id1).not.toBe(id2)
      expect(id1).toContain('-')
    })
  })
})
