import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { apiClient } from '../api/client'
import { StepIndicator } from './components/StepIndicator'
import { WhatMovedStep } from './components/WhatMovedStep'
import { CommitmentsStep } from './components/CommitmentsStep'
import { FileUploadStep } from './components/FileUploadStep'
import { useAutoSave } from './hooks/useAutoSave'

interface ReviewData {
  what_moved: string
  what_learned: string
  what_threatens: string
  currently_testing_type: 'thesis' | 'proof_point'
  currently_testing_id: string
  commitments: Array<{ text: string; order: number }>
  attachment_ids: string[]
}

interface CanvasOptions {
  theses: Array<{
    id: string
    text: string
    proof_points: Array<{
      id: string
      description: string
    }>
  }>
}

export const ReviewWizard: React.FC = () => {
  const { vbuId } = useParams<{ vbuId: string }>()
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(1)
  const [reviewData, setReviewData] = useState<ReviewData>({
    what_moved: '',
    what_learned: '',
    what_threatens: '',
    currently_testing_type: 'thesis',
    currently_testing_id: '',
    commitments: [{ text: '', order: 1 }],
    attachment_ids: []
  })
  const [canvasOptions, setCanvasOptions] = useState<CanvasOptions | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')

  const { saveDraft } = useAutoSave({
    data: reviewData,
    canvasId: vbuId!,
    onSave: (success) => setSaveStatus(success ? 'saved' : 'error')
  })

  const handleManualSave = async () => {
    setSaveStatus('saving')
    await saveDraft()
  }

  useEffect(() => {
    const fetchCanvasOptions = async () => {
      try {
        const response = await apiClient.get(`/canvases/${vbuId}/options`)
        setCanvasOptions(response.data.data)
      } catch (err) {
        setError('Failed to load canvas options')
      }
    }
    
    if (vbuId) {
      fetchCanvasOptions()
    }
  }, [vbuId])

  const handleNext = () => {
    if (currentStep < 4) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    
    try {
      await apiClient.post(`/canvases/${vbuId}/reviews`, {
        review_date: new Date().toISOString().split('T')[0],
        ...reviewData
      })
      navigate(`/vbus/${vbuId}`)
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to submit review')
    } finally {
      setLoading(false)
    }
  }

  const isStepValid = () => {
    switch (currentStep) {
      case 4:
        return reviewData.commitments.length > 0 && 
               reviewData.commitments.every(c => c.text.trim().length > 0) &&
               reviewData.currently_testing_id.length > 0
      default:
        return true
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <WhatMovedStep data={reviewData} onChange={setReviewData} />
            <FileUploadStep 
              attachmentIds={reviewData.attachment_ids}
              onAttachmentsChange={(ids) => setReviewData({...reviewData, attachment_ids: ids})}
            />
          </div>
        )
      case 2:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold">What did we learn that changes our beliefs?</h2>
            <textarea
              value={reviewData.what_learned}
              onChange={(e) => setReviewData({ ...reviewData, what_learned: e.target.value })}
              className="w-full h-32 p-4 border rounded-lg"
              maxLength={5000}
              placeholder="Focus on insights that challenge assumptions or change strategy..."
            />
            <div className="text-sm text-gray-500">{reviewData.what_learned.length}/5000 characters</div>
          </div>
        )
      case 3:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold">What now threatens the next proof point?</h2>
            <textarea
              value={reviewData.what_threatens}
              onChange={(e) => setReviewData({ ...reviewData, what_threatens: e.target.value })}
              className="w-full h-32 p-4 border rounded-lg"
              maxLength={5000}
              placeholder="Identify risks, blockers, or changes that could impact progress..."
            />
            <div className="text-sm text-gray-500">{reviewData.what_threatens.length}/5000 characters</div>
          </div>
        )
      case 4:
        return <CommitmentsStep data={reviewData} onChange={setReviewData} options={canvasOptions} />
      default:
        return null
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <button
            onClick={() => navigate(`/vbus/${vbuId}`)}
            className="text-blue-600 hover:text-blue-500 text-sm"
          >
            ← Back to Canvas
          </button>
          <h1 className="text-3xl font-bold mt-2">Monthly Review</h1>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            {saveStatus === 'saving' && <span className="text-blue-600">Saving...</span>}
            {saveStatus === 'saved' && <span className="text-green-600">Saved</span>}
            {saveStatus === 'error' && <span className="text-red-600">Save failed</span>}
          </div>
          <button onClick={handleManualSave} className="px-4 py-2 border rounded">
            Save Draft
          </button>
        </div>
      </div>

      <StepIndicator currentStep={currentStep} totalSteps={4} />
      
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      <div className="mb-8">
        {renderStep()}
      </div>

      <div className="flex justify-between">
        <div>
          {currentStep > 1 && (
            <button
              onClick={handlePrevious}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              ← Previous
            </button>
          )}
        </div>
        
        <div className="space-x-4">
          <button
            onClick={() => navigate(`/vbus/${vbuId}`)}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            Cancel
          </button>
          
          {currentStep < 4 ? (
            <button
              onClick={handleNext}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Next Step →
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={!isStepValid() || loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Submitting...' : 'Submit Review'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}