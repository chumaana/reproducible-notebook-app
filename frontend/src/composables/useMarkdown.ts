import type { Ref } from 'vue'

/**
 * Composable for converting between clean R code and full R Markdown (.Rmd) format.
 * Handles YAML header and code fence wrapping/unwrapping.
 *
 * @param title - Ref containing the notebook title
 * @param content - Ref containing the clean R code content
 * @returns Object with extractCleanContent and generateFullRmd functions
 */
export function useMarkdown(title: Ref<string>, content: Ref<string>) {
  /**
   * Extracts clean R code from full Rmd file by removing YAML header and code fences.
   *
   * @param fullRmd - Full R Markdown content
   * @returns Clean R code without YAML header and fences
   */
  const extractCleanContent = (fullRmd: string): string => {
    if (!fullRmd) return ''

    // Remove YAML header (between --- and ---)
    const yamlRegex = /^---\s*\n[\s\S]*?\n---\s*\n/
    let clean = fullRmd.replace(yamlRegex, '').trim()

    // Remove R code block fences if they exist
    if (clean.startsWith('```{r}') && clean.endsWith('```')) {
      clean = clean.replace(/^```\{r\}\n/, '').replace(/\n```$/, '')
    }

    return clean
  }

  /**
   * Generates full Rmd file from clean R code by adding YAML header and code fences.
   *
   * @returns Complete R Markdown file content
   */
  const generateFullRmd = (): string => {
    const header = `---
title: "${title.value || 'Untitled Notebook'}"
output: html_document
---
`
    // Check if user manually added fences
    const hasFences = content.value.trim().startsWith('```{r}')

    if (hasFences) {
      return header + content.value
    } else {
      return header + '```{r}\n' + content.value + '\n```'
    }
  }

  return {
    extractCleanContent,
    generateFullRmd,
  }
}
