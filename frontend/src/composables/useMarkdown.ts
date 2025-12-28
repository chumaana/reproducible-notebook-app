import { computed, type Ref } from 'vue'

export function useMarkdown(title: Ref<string>, content: Ref<string>) {
  const extractCleanContent = (fullRmd: string): string => {
    if (!fullRmd) return ''

    const yamlRegex = /^---\s*\n[\s\S]*?\n---\s*\n/
    let clean = fullRmd.replace(yamlRegex, '').trim()

    if (clean.startsWith('```{r}') && clean.endsWith('```')) {
      clean = clean.replace(/^```\{r\}\n/, '').replace(/\n```$/, '')
    }

    return clean
  }

  const generateFullRmd = (): string => {
    const header = `---
title: "${title.value || 'Untitled Notebook'}"
output: html_document
---

`
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
