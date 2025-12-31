import { describe, it, expect } from 'vitest'
import { ref } from 'vue'
import { useMarkdown } from './useMarkdown'

describe('useMarkdown', () => {
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

  it('generates a full Rmd string with YAML header and fences', () => {
    const title = ref('My Notebook')
    const content = ref('x <- 10\nprint(x)')
    const { generateFullRmd } = useMarkdown(title, content)

    const result = generateFullRmd()

    expect(result).toContain('title: "My Notebook"')
    expect(result).toContain('output: html_document')
    expect(result).toContain('\`\`\`{r}\nx <- 10\nprint(x)\n\`\`\`')
  })

  it('does not double-wrap if fences are already present', () => {
    const title = ref('Existing Fences')
    const content = ref('\`\`\`{r}\nprint("stay")\n\`\`\`')
    const { generateFullRmd } = useMarkdown(title, content)

    const result = generateFullRmd()

    const fenceCount = (result.match(/\`\`\`\{r\}/g) || []).length
    expect(fenceCount).toBe(1)
  })

  it('returns empty string if extractCleanContent is called with nothing', () => {
    const title = ref('')
    const content = ref('')
    const { extractCleanContent } = useMarkdown(title, content)

    expect(extractCleanContent('')).toBe('')
  })
})
