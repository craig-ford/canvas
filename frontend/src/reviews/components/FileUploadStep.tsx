import React, { useState, useEffect } from 'react'
import FileUpload from '../../components/FileUpload'
import { apiClient } from '../../api/client'

interface Attachment {
  id: string
  filename: string
  content_type: string
  size_bytes: number
  label?: string
  uploaded_by: string
  created_at: string
}

interface FileUploadStepProps {
  attachmentIds: string[]
  onAttachmentsChange: (ids: string[]) => void
}

export const FileUploadStep: React.FC<FileUploadStepProps> = ({ 
  attachmentIds, 
  onAttachmentsChange 
}) => {
  const [attachments, setAttachments] = useState<Attachment[]>([])

  useEffect(() => {
    const fetchAttachments = async () => {
      if (attachmentIds.length === 0) {
        setAttachments([])
        return
      }
      
      try {
        const promises = attachmentIds.map(id => 
          apiClient.get(`/api/attachments/${id}`)
        )
        const responses = await Promise.all(promises)
        setAttachments(responses.map(r => r.data.data))
      } catch (error) {
        console.error('Failed to fetch attachments:', error)
      }
    }
    
    fetchAttachments()
  }, [attachmentIds])

  const handleFileUpload = async (file: File, label?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (label) formData.append('label', label)
    
    try {
      const response = await apiClient.post('/api/attachments', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      const newAttachment = response.data.data
      onAttachmentsChange([...attachmentIds, newAttachment.id])
    } catch (error) {
      throw error
    }
  }
  
  const handleFileRemove = async (attachmentId: string) => {
    try {
      await apiClient.delete(`/api/attachments/${attachmentId}`)
      onAttachmentsChange(attachmentIds.filter(id => id !== attachmentId))
    } catch (error) {
      throw error
    }
  }
  
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium">Attachments (optional)</h3>
      <FileUpload
        onUpload={handleFileUpload}
        attachments={attachments}
        onDelete={handleFileRemove}
        maxSize={10 * 1024 * 1024}
        allowedTypes={['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/png', 'image/jpeg']}
      />
    </div>
  )
}