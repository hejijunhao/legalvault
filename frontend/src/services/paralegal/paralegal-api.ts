// src/services/paralegal/paralegal-api.ts

import { apiClient, ApiError } from '@/lib/api-client';
import {
  VirtualParalegalCreate,
  VirtualParalegalUpdate,
  VirtualParalegalResponse,
  ParalegalNotFoundError,
  ParalegalConflictError,
  ParalegalError,
} from './paralegal-api-types';

export class ParalegalService {
  private baseUrl = '/api/paralegals';

  private handleError(error: unknown): never {
    if (error instanceof ApiError) {
      if (error.status === 404) {
        throw new ParalegalNotFoundError(error.details || error.message);
      }
      if (error.status === 409) {
        throw new ParalegalConflictError(error.details || error.message);
      }
      throw new ParalegalError(error.message, error.status || 500, error.code);
    }
    throw error;
  }

  /**
   * Get the current user's Virtual Paralegal
   */
  async getMyParalegal(): Promise<VirtualParalegalResponse> {
    try {
      return await apiClient.get<VirtualParalegalResponse>(`${this.baseUrl}/me`);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Create a new Virtual Paralegal and assign it to the current user
   */
  async createParalegal(data: VirtualParalegalCreate): Promise<VirtualParalegalResponse> {
    try {
      return await apiClient.post<VirtualParalegalResponse>(this.baseUrl, data);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Update the current user's Virtual Paralegal
   */
  async updateMyParalegal(data: VirtualParalegalUpdate): Promise<VirtualParalegalResponse> {
    try {
      return await apiClient.patch<VirtualParalegalResponse>(`${this.baseUrl}/me`, data);
    } catch (error) {
      this.handleError(error);
    }
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
