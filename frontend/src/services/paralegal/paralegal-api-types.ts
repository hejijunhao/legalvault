// src/services/paralegal/paralegal-api-types.ts

/**
 * Base interface for Virtual Paralegal data
 */
export interface VirtualParalegalBase {
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  whatsapp?: string;
  gender?: string;
  profile_picture_id?: string;
}

/**
 * Interface for creating a new Virtual Paralegal
 */
export type VirtualParalegalCreate = VirtualParalegalBase;

/**
 * Interface for updating a Virtual Paralegal
 * All fields are optional
 */
export type VirtualParalegalUpdate = Partial<VirtualParalegalBase>;

/**
 * Interface for Virtual Paralegal responses from the API
 * Extends the base interface with system fields
 */
export interface VirtualParalegalResponse extends VirtualParalegalBase {
  id: string;
  created_at: string;
  updated_at: string;
}

/**
 * Custom error types that match backend exceptions
 */
export class ParalegalError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ParalegalError';
  }
}

export class ParalegalNotFoundError extends ParalegalError {
  constructor(message: string = 'Virtual Paralegal not found') {
    super(message, 404, 'PARALEGAL_NOT_FOUND');
    this.name = 'ParalegalNotFoundError';
  }
}

export class ParalegalConflictError extends ParalegalError {
  constructor(message: string = 'User already has a Virtual Paralegal assigned') {
    super(message, 409, 'PARALEGAL_CONFLICT');
    this.name = 'ParalegalConflictError';
  }
}