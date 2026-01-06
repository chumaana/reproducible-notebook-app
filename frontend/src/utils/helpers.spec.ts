import { describe, it, expect, vi } from 'vitest'
import { getErrorMessage, formatDateTime, debounce } from '@/utils/helpers'

/**
 * Test suite for utility functions.
 * Validates error parsing logic, date formatting, and performance optimization helpers.
 */
describe('Utils - helpers', () => {
  describe('getErrorMessage', () => {
    /**
     * Test extraction of DRF 'detail' style errors.
     * Common for authentication and permission exceptions (e.g., 401/403).
     */
    it('extracts error from axios error with detail field', () => {
      const error = {
        isAxiosError: true,
        response: {
          data: { detail: 'Authentication failed' },
        },
      }
      expect(getErrorMessage(error)).toBe('Authentication failed')
    })

    /**
     * Test extraction of standard 'error' field.
     * Common for generic API exceptions.
     */
    it('extracts error from axios error with error field', () => {
      const error = {
        isAxiosError: true,
        response: {
          data: { error: 'Invalid input' },
        },
      }
      expect(getErrorMessage(error)).toBe('Invalid input')
    })

    /**
     * Test parsing of Django form validation errors.
     * Should flatten object-based field errors into a readable string.
     */
    it('extracts and joins multiple Django field errors', () => {
      const error = {
        isAxiosError: true,
        response: {
          data: {
            username: ['This field is required.'],
            password: ['Too short.'],
          },
        },
      }

      const msg = getErrorMessage(error)

      expect(msg).toContain('username: This field is required.')
      expect(msg).toContain('password: Too short.')
    })

    /**
     * Fallback mechanism check for generic JavaScript errors.
     */
    it('handles generic JS errors (non-axios)', () => {
      const error = new Error('Something went wrong')
      expect(getErrorMessage(error)).toBe('Something went wrong')
    })
  })

  describe('formatDateTime', () => {
    /**
     * Verifies correct parsing of ISO strings into locale-aware formats.
     */
    it('formats ISO date string into readable text', () => {
      const date = '2024-03-15T10:30:00Z'
      const formatted = formatDateTime(date)

      expect(formatted).not.toBe('Invalid Date')
      expect(formatted).not.toBe('Unknown')
      expect(formatted).toContain('2024')
    })

    /**
     * Edge case: Handling missing input gracefully.
     */
    it('handles undefined input gracefully', () => {
      expect(formatDateTime(undefined)).toBe('Unknown')
    })

    /**
     * Edge case: Handling malformed date strings.
     */
    it('handles malformed date strings', () => {
      expect(formatDateTime('not-a-date')).toBe('Invalid Date')
    })
  })

  describe('debounce', () => {
    /**
     * Verifies execution limiting using fake timers.
     * Critical for performance (e.g., preventing API calls on every keystroke).
     */
    it('delays execution and coalesces multiple calls', () => {
      vi.useFakeTimers()
      const func = vi.fn()
      const debouncedFunc = debounce(func, 100)

      // Call multiple times rapidly
      debouncedFunc()
      debouncedFunc()
      debouncedFunc()

      // Should not be called yet due to delay
      expect(func).not.toHaveBeenCalled()

      // Fast-forward time
      vi.advanceTimersByTime(100)

      // Should execute exactly once
      expect(func).toHaveBeenCalledTimes(1)

      vi.useRealTimers()
    })
  })
})
