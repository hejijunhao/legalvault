// src/types/supabase.ts

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      virtual_paralegals: {
        Row: {
          id: string
          user_id: string
          name: string
          email: string
          phone_number: string | null
          profile_picture_url: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          name: string
          email: string
          phone_number?: string | null
          profile_picture_url?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          name?: string
          email?: string
          phone_number?: string | null
          profile_picture_url?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      abilities: {
        Row: {
          id: string
          paralegal_id: string
          name: string
          description: string
          status: 'active' | 'inactive' | 'pending'
          configuration: Json
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          paralegal_id: string
          name: string
          description: string
          status?: 'active' | 'inactive' | 'pending'
          configuration?: Json
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          paralegal_id?: string
          name?: string
          description?: string
          status?: 'active' | 'inactive' | 'pending'
          configuration?: Json
          created_at?: string
          updated_at?: string
        }
      }
      behaviors: {
        Row: {
          id: string
          paralegal_id: string
          name: string
          description: string
          configuration: Json
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          paralegal_id: string
          name: string
          description: string
          configuration?: Json
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          paralegal_id?: string
          name?: string
          description?: string
          configuration?: Json
          created_at?: string
          updated_at?: string
        }
      }
    }
  }
}