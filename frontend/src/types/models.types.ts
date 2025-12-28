export interface User {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
  bio?: string
  created_at?: string
}

export interface Notebook {
  id?: number
  title: string
  content: string
  author?: string
  created_at?: string
  updated_at?: string
  is_public?: boolean
}

export interface Execution {
  id: number
  notebook: number
  html_output: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at: string
  completed_at?: string
  error_message?: string
}
