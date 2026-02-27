import React, { useState, useEffect } from 'react'
import { apiClient } from '../api/client'

interface ReviewHistoryProps {
  canvasId: string
  vbuId: string
}

interface ReviewData {
  id: string
  canvas_id: string
  review_date: string
  what_moved: string | null
  what_learned: string | null
  what_threatens: string | null
  currently_testing_type: string | null
  currently_testing_id: string | null
  created_by: string
  created_at: string
  commitments: Array<{
    id: string
    text: string
    order: number
  }>
  attachments: Array<{
    id: string
    filename: string
    label: string | null
    size_bytes: number
  }>
}

const ReviewHistory: React.FC<ReviewHistoryProps> = ({ canvasId, vbuId }) => {
  const [reviews, setReviews] = useState<ReviewData[]>([])
  const [expandedReviews, setExpandedReviews] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        setLoading(true)
        const response = await apiClient.get(`/canvases/${canvasId}/reviews`)
        setReviews(response.data.data)
      } catch (err: any) {
        setError(err.response?.data?.error?.message || 'Failed to load reviews')
      } finally {
        setLoading(false)
      }
    }

    fetchReviews()
  }, [canvasId])

  const toggleExpanded = (reviewId: string) => {
    const newExpanded = new Set(expandedReviews)
    if (newExpanded.has(reviewId)) {
      newExpanded.delete(reviewId)
    } else {
      newExpanded.add(reviewId)
    }
    setExpandedReviews(newExpanded)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getExcerpt = (text: string | null, maxLength: number = 100) => {
    if (!text) return ''
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
  }

  const retryFetch = () => {
    setError(null)
    const fetchReviews = async () => {
      try {
        setLoading(true)
        const response = await apiClient.get(`/canvases/${canvasId}/reviews`)
        setReviews(response.data.data)
      } catch (err: any) {
        setError(err.response?.data?.error?.message || 'Failed to load reviews')
      } finally {
        setLoading(false)
      }
    }
    fetchReviews()
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Review History</h3>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Review History</h3>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700 mb-2">{error}</p>
          <button
            onClick={retryFetch}
            className="text-red-600 hover:text-red-500 text-sm font-medium"
          >
            Try again
          </button>
        </div>
      </div>
    )
  }

  if (reviews.length === 0) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Review History</h3>
        <div className="text-center py-8 text-gray-500">
          <p>No reviews yet</p>
          <p className="text-sm mt-1">Start your first monthly review to see history here</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Review History</h3>
        <a
          href={`/vbus/${vbuId}/review/new`}
          className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark text-sm"
        >
          Start Review
        </a>
      </div>

      <div className="space-y-3">
        {reviews.map((review) => {
          const isExpanded = expandedReviews.has(review.id)
          
          return (
            <div key={review.id} className="border rounded-lg bg-white">
              <div className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <span className="text-lg">📅</span>
                    <div>
                      <h4 className="font-medium">{formatDate(review.review_date)}</h4>
                      {!isExpanded && review.what_moved && (
                        <p className="text-sm text-gray-600 mt-1">
                          What moved: "{getExcerpt(review.what_moved)}"
                        </p>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-3 text-sm text-gray-500">
                      <span>💼 {review.commitments.length} commitments</span>
                      <span>📎 {review.attachments.length} attachments</span>
                    </div>
                    <button
                      onClick={() => toggleExpanded(review.id)}
                      className="text-blue-600 hover:text-blue-700 p-1"
                    >
                      {isExpanded ? '▲' : '▼'}
                    </button>
                  </div>
                </div>

                {isExpanded && (
                  <div className="mt-6 space-y-4 border-t pt-4">
                    {review.what_moved && (
                      <div>
                        <h5 className="font-medium text-gray-900 mb-2">📝 What moved:</h5>
                        <p className="text-gray-700 text-sm">{review.what_moved}</p>
                      </div>
                    )}

                    {review.what_learned && (
                      <div>
                        <h5 className="font-medium text-gray-900 mb-2">🧠 What learned:</h5>
                        <p className="text-gray-700 text-sm">{review.what_learned}</p>
                      </div>
                    )}

                    {review.what_threatens && (
                      <div>
                        <h5 className="font-medium text-gray-900 mb-2">⚠️ What threatens:</h5>
                        <p className="text-gray-700 text-sm">{review.what_threatens}</p>
                      </div>
                    )}

                    {review.commitments.length > 0 && (
                      <div>
                        <h5 className="font-medium text-gray-900 mb-2">💼 Commitments:</h5>
                        <ol className="list-decimal list-inside space-y-1">
                          {review.commitments
                            .sort((a, b) => a.order - b.order)
                            .map((commitment) => (
                              <li key={commitment.id} className="text-gray-700 text-sm">
                                {commitment.text}
                              </li>
                            ))}
                        </ol>
                      </div>
                    )}

                    {review.currently_testing_type && (
                      <div>
                        <h5 className="font-medium text-gray-900 mb-2">🎯 Currently Testing:</h5>
                        <p className="text-gray-700 text-sm">
                          {review.currently_testing_type === 'thesis' ? 'Thesis' : 'Proof Point'}
                        </p>
                      </div>
                    )}

                    {review.attachments.length > 0 && (
                      <div>
                        <h5 className="font-medium text-gray-900 mb-2">📎 Attachments:</h5>
                        <div className="space-y-2">
                          {review.attachments.map((attachment) => (
                            <div
                              key={attachment.id}
                              className="flex items-center justify-between p-2 bg-gray-50 rounded"
                            >
                              <div className="flex items-center space-x-2">
                                <span className="text-sm">📄</span>
                                <span className="text-sm font-medium">
                                  {attachment.label || attachment.filename}
                                </span>
                                <span className="text-xs text-gray-500">
                                  ({formatFileSize(attachment.size_bytes)})
                                </span>
                              </div>
                              <a
                                href={`/api/attachments/${attachment.id}`}
                                download={attachment.filename}
                                className="text-blue-600 hover:text-blue-500 text-sm font-medium"
                              >
                                Download
                              </a>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ReviewHistory