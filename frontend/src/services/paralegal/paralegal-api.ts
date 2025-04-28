// src/services/paralegal/paralegal-api.ts

import {
  VirtualParalegalCreate,
  VirtualParalegalUpdate,
  VirtualParalegalResponse,
  ParalegalError,
  ParalegalNotFoundError,
  ParalegalConflictError,
} from './paralegal-api-types';

export class ParalegalService {
  private baseUrl = '/api/paralegals';

  private getHeaders(): HeadersInit {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('Not authenticated');
    }
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      
      if (response.status === 404) {
        throw new ParalegalNotFoundError(error.detail);
      }
      if (response.status === 409) {
        throw new ParalegalConflictError(error.detail);
      }
      
      throw new ParalegalError(
        error.detail || 'An error occurred',
        response.status
      );
    }
    return response.json();
  }

  /**
   * Get the current user's Virtual Paralegal
   */
  async getMyParalegal(): Promise<VirtualParalegalResponse> {
    const response = await fetch(`${this.baseUrl}/me`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<VirtualParalegalResponse>(response);
  }

  /**
   * Create a new Virtual Paralegal and assign it to the current user
   */
  async createParalegal(data: VirtualParalegalCreate): Promise<VirtualParalegalResponse> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse<VirtualParalegalResponse>(response);
  }

  /**
   * Update the current user's Virtual Paralegal
   */
  async updateMyParalegal(data: VirtualParalegalUpdate): Promise<VirtualParalegalResponse> {
    const response = await fetch(`${this.baseUrl}/me`, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse<VirtualParalegalResponse>(response);
  }

  /**
   * Check if the current user has a Virtual Paralegal assigned
   */
  async hasParalegal(): Promise<boolean> {
    try {
      await this.getMyParalegal();
      return true;
    } catch (error) {
      if (error instanceof ParalegalNotFoundError) {
        return false;
      }
      throw error;
    }
  }
}

// Export a singleton instance
export const paralegalService = new ParalegalService();