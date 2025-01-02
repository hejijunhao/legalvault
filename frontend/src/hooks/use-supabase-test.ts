import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'

export const useSupabaseTest = () => {
  const [isConnected, setIsConnected] = useState<boolean | null>(null)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const testConnection = async () => {
      try {
        const { error } = await supabase.from('virtual_paralegals').select('id').limit(1)

        if (error) {
          throw error
        }

        setIsConnected(true)
      } catch (e) {
        setError(e instanceof Error ? e : new Error('Failed to connect to Supabase'))
        setIsConnected(false)
      }
    }

    testConnection()
  }, [])

  return { isConnected, error }
}