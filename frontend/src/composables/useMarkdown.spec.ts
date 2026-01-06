import { describe, it, expect } from 'vitest'
import { ref } from 'vue'
import { useMarkdown } from './useMarkdown'

/**
 * Test suite for the useMarkdown composable.
 * Verifies the parsing logic that converts between raw R code (editor view)
 * and valid R Markdown files (backend storage format).
 */
describe('useMarkdown', () => {
  /**
   * Tests the extraction logic:
   * It should strip the YAML header and markdown fences (```),
   * returning only the raw R code for the CodeMirror editor.
   */
  it('extracts clean content from a full Rmd string', () => {
    const title = ref('Test')
    const content = ref('')
    const { extractCleanContent } = useMarkdown(title, content)

    const fullRmd = `---
title: "Sample Notebook"
output: html_document
---
\`\`\`{r}
print("Hello World")
\`\`\`
`
    const result = extractCleanContent(fullRmd)
    expect(result).toBe('print("Hello World")')
  })

  /**
   * Tests the file assembly logic:
   * It should construct a valid .Rmd file by injecting the title into the YAML header
   * and wrapping the raw code in an R execution block.
   */
  it('generates a full Rmd string with YAML header and fences', () => {
    const title = ref('My Notebook')
    const content = ref('x <- 10\nprint(x)')
    const { generateFullRmd } = useMarkdown(title, content)

    const result = generateFullRmd()

    expect(result).toContain('title: "My Notebook"')
    expect(result).toContain('output: html_document')
    expect(result).toContain('\`\`\`{r}\nx <- 10\nprint(x)\n\`\`\`')
  })

  /**
   * Verifies idempotency:
   * If the content is already wrapped in fences (e.g., loaded from an existing file),
   * the generator should not add a second layer of wrapping.
   */
  it('does not double-wrap if fences are already present', () => {
    const title = ref('Existing Fences')
    const content = ref('\`\`\`{r}\nprint("stay")\n\`\`\`')
    const { generateFullRmd } = useMarkdown(title, content)

    const result = generateFullRmd()

    const fenceCount = (result.match(/\`\`\`\{r\}/g) || []).length
    expect(fenceCount).toBe(1)
  })

  /**
   * Edge case handling:
   * Ensures the parser returns an empty string gracefully when input is missing.
   */
  it('returns empty string if extractCleanContent is called with nothing', () => {
    const title = ref('')
    const content = ref('')
    const { extractCleanContent } = useMarkdown(title, content)

    expect(extractCleanContent('')).toBe('')
  })
})
