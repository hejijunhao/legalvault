// src/services/user/user-api-types.ts

/**
 * Represents a user profile, matching the backend UserProfile schema.
 */
export interface UserProfile {
    /**
     * Unique identifier for the user (UUID).
     */
    id: string;
  
    /**
     * User's email address.
     * Non-nullable in schema, but may be null in database (handled by backend fallback).
     */
    email: string;
  
    /**
     * User's first name, may be null if not provided.
     */
    first_name: string | null;
  
    /**
     * User's last name, may be null if not provided.
     */
    last_name: string | null;
  
    /**
     * User's full name, may be null if not provided.
     */
    name: string | null;
  
    /**
     * User's role in the system (e.g., "lawyer", "admin").
     */
    role: string;
  
    /**
     * ID of the assigned virtual paralegal, may be null.
     */
    virtual_paralegal_id: string | null;
  
    /**
     * ID of the user's enterprise, may be null.
     */
    enterprise_id: string | null;
  
    /**
     * Timestamp of user creation (ISO string).
     */
    created_at: string;
  
    /**
     * Timestamp of last update (ISO string).
     */
    updated_at: string;
  
    /**
     * Timestamp of last login (ISO string), may be null.
     */
    last_login: string | null;
  }