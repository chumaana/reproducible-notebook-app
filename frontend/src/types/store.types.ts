import type { User, Notebook } from './models.types'

export interface AuthState {
  token: string | null
  user: User | null
  loading: boolean
  error: string | null
}

export interface NotebookState {
  notebooks: Notebook[]
  currentNotebook: Notebook | null
  loading: boolean
  error: string | null
}
