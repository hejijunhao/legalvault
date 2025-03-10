// src/services/research/research-api.ts

import { supabase } from '@/lib/supabase'
import { Message, ResearchSession } from '@/contexts/research/research-context'

export async function getAuthHeader() {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}

export async function fetchSessions(): Promise<ResearchSession[]> {
  const headers = await getAuthHeader()
  const response = await fetch('/api/research/sessions', { headers })
  
  if (!response.ok) throw response
  return await response.json()
}

export async function fetchSession(sessionId: string): Promise<ResearchSession> {
  const headers = await getAuthHeader()
  const response = await fetch(`/api/research/sessions/${sessionId}`, { headers })
  
  if (!response.ok) throw response
  return await response.json()
}

export async function createNewSession(query: string): Promise<ResearchSession> {
  const headers = await getAuthHeader()
  const response = await fetch('/api/research/sessions', {
    method: 'POST',
    headers,
    body: JSON.stringify({ query })
  })
  
  if (!response.ok) throw response
  return await response.json()
}

export async function sendSessionMessage(sessionId: string, content: string): Promise<ResearchSession> {
  const headers = await getAuthHeader()
  const response = await fetch(`/api/research/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ content })
  })
  
  if (!response.ok) throw response
  return await response.json()
}