import { apiClient } from './client';
import type {
  LoginPayload,
  RegisterPayload,
  UserProfile,
} from '../reproducible-notebook-app/frontend/src/types/api.types';

interface AuthResponse {
  token: string;
  user: UserProfile;
}

export class AuthService {
  async login(credentials: LoginPayload): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      '/auth/login/',
      credentials,
    );
    return response.data;
  }

  async register(credentials: RegisterPayload): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      '/auth/register/',
      credentials,
    );
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout/');
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  }

  async getUser(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>('/auth/user/');
    return response.data;
  }
}

export const authService = new AuthService();
