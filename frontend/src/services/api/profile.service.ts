import { apiClient } from './client';
import type { UserProfile } from '../reproducible-notebook-app/frontend/src/types/api.types';

export class ProfileService {
  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get('/profile/');
    return response.data;
  }

  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    const response = await apiClient.patch('/profile/', data);
    return response.data;
  }
}

export const profileService = new ProfileService();
