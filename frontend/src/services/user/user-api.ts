// src/services/user/user-api.ts

import { apiClient } from '@/lib/api-client';
import { UserProfile } from './user-api-types';

export class UserService {
  private baseUrl = '/api/users';

  async getUserProfile(userId: string): Promise<UserProfile> {
    return apiClient.get<UserProfile>(`${this.baseUrl}/${userId}`);
  }

  async getCurrentUserProfile(): Promise<UserProfile> {
    return apiClient.get<UserProfile>(`${this.baseUrl}/me`);
  }

  async updateCurrentUserEmail(email: string): Promise<UserProfile> {
    return apiClient.patch<UserProfile>(`${this.baseUrl}/me/email`, { email });
  }
}

export const userService = new UserService();
