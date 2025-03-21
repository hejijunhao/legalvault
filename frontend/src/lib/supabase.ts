// src/lib/supabase.ts

import { createClient } from '@supabase/supabase-js'
import { Database } from '@/types/supabase'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
    storage: typeof window !== 'undefined' ? window.localStorage : undefined,
    storageKey: 'legalvault-auth',
  },
  global: {
    headers: {
      'x-application-name': 'legalvault',
    },
  },
})

// Helper function to handle Supabase errors
export const handleSupabaseError = (error: Error) => {
  console.error('Supabase operation failed:', error.message)
  // Add your error reporting service here if needed
  throw error
}

// Typed database helper functions
export const getVirtualParalegal = async (userId: string) => {
  const { data, error } = await supabase
    .from('virtual_paralegals')
    .select('*')
    .eq('user_id', userId)
    .single()

  if (error) {
    handleSupabaseError(error)
  }

  return data
}

export const updateVirtualParalegal = async (id: string, updates: Partial<Database['public']['Tables']['virtual_paralegals']['Update']>) => {
  const { data, error } = await supabase
    .from('virtual_paralegals')
    .update(updates)
    .eq('id', id)
    .select()
    .single()

  if (error) {
    handleSupabaseError(error)
  }

  return data
}

// Additional helper functions can be added here as needed