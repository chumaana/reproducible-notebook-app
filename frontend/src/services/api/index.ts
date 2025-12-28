// ==================== Services ====================
export { authService } from './auth.service'
export { profileService } from './profile.service'
export { notebookService } from './notebook.service'

// ==================== Service Classes (if needed for typing) ====================
export { AuthService } from './auth.service'
export { ProfileService } from './profile.service'
export { NotebookService } from './notebook.service'

// ==================== Types ====================
export type {
  // Models
  User,
  Notebook,
  Execution,

  // API
  LoginPayload,
  RegisterPayload,
  AuthResponse,
  ReproducibilityAnalysis,
  ApiError,
  ErrorResponse,

  // Aliases
  UserProfile,
} from '@/types'

// ==================== Client ====================
export { apiClient } from './client'

// ==================== Default API Object ====================
import { authService } from './auth.service'
import { profileService } from './profile.service'
import { notebookService } from './notebook.service'

const api = {
  // ==================== Auth ====================
  auth: {
    login: authService.login.bind(authService),
    register: authService.register.bind(authService),
    logout: authService.logout.bind(authService),
    getUser: authService.getUser.bind(authService),
  },

  // ==================== Profile ====================
  profile: {
    get: profileService.getProfile.bind(profileService),
    update: profileService.updateProfile.bind(profileService),
  },

  // ==================== Notebooks ====================
  notebooks: {
    getAll: notebookService.getAll.bind(notebookService),
    getById: notebookService.getById.bind(notebookService),
    create: notebookService.create.bind(notebookService),
    update: notebookService.update.bind(notebookService),
    delete: notebookService.delete.bind(notebookService),
    execute: notebookService.execute.bind(notebookService),
    getExecutions: notebookService.getExecutions.bind(notebookService),
    getReproducibilityAnalysis: notebookService.getReproducibilityAnalysis.bind(notebookService),
    generatePackage: notebookService.generatePackage.bind(notebookService),
    generateDiff: notebookService.generateDiff.bind(notebookService),
    download: notebookService.download.bind(notebookService),
    downloadPackage: notebookService.downloadPackage.bind(notebookService),
  },
}

export default api
