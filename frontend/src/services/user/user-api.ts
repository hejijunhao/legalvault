// src/services/user.ts

import { UserProfile } from './user-api-types';

export class UserService {
  private baseUrl = '/api/users';
  
  private getHeaders(): HeadersInit {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('Not authenticated');
    }
    return {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }

  async getUserProfile(userId: string): Promise<UserProfile> {
    const response = await fetch(`${this.baseUrl}/${userId}`, {
      headers: this.getHeaders(),
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Not authenticated');
      }
      throw new Error(`Failed to fetch profile: ${response.statusText}`);
    }
    return response.json();
  }

  async getCurrentUserProfile(): Promise<UserProfile> {
    const response = await fetch(`${this.baseUrl}/me`, {
      headers: this.getHeaders(),
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Not authenticated');
      }
      throw new Error(`Failed to fetch current user profile: ${response.statusText}`);
    }
    return response.json();
  }

  async updateCurrentUserEmail(email: string): Promise<UserProfile> {
    const response = await fetch(`${this.baseUrl}/me/email`, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: JSON.stringify({ email }),
    });
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Not authenticated');
      }
      throw new Error(`Failed to update email: ${response.statusText}`);
    }
    return response.json();
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  }
}

export const userService = new UserService();