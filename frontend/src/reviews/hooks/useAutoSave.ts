import { useEffect, useRef } from 'react'
import { apiClient } from '../../api/client'

interface AutoSaveOptions {
  data: any
  canvasId: string
  interval?: number
  onSave?: (success: boolean) => void
}

export const useAutoSave = ({ data, canvasId, interval = 30000, onSave }: AutoSaveOptions) => {
  const timeoutRef = useRef<NodeJS.Timeout>()
  const lastSavedRef = useRef<string>('')
  
  const saveDraft = async () => {
    const currentData = JSON.stringify(data)
    if (currentData === lastSavedRef.current) return
    
    try {
      await apiClient.post(`/api/canvases/${canvasId}/reviews/draft`, data)
      lastSavedRef.current = currentData
      onSave?.(true)
    } catch (error) {
      onSave?.(false)
    }
  }
  
  useEffect(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    timeoutRef.current = setTimeout(saveDraft, interval)
    
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [data, interval])
  
  return { saveDraft }
}