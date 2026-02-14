import React from 'react'

interface ReviewData {
  what_moved: string
  what_learned: string
  what_threatens: string
  currently_testing_type: 'thesis' | 'proof_point'
  currently_testing_id: string
  commitments: Array<{ text: string; order: number }>
  attachment_ids: string[]
}

interface WhatMovedStepProps {
  data: ReviewData
  onChange: (data: ReviewData) => void
}

export const WhatMovedStep: React.FC<WhatMovedStepProps> = ({ data, onChange }) => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">What moved since last month?</h2>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-700">
          Focus on measurable outcomes, customer feedback, and concrete progress. 
          What evidence do you have that things are moving forward?
        </p>
      </div>
      <textarea
        value={data.what_moved}
        onChange={(e) => onChange({ ...data, what_moved: e.target.value })}
        className="w-full h-32 p-4 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        maxLength={5000}
        placeholder="Describe the concrete progress, metrics, customer feedback, or other evidence of movement..."
      />
      <div className="text-sm text-gray-500">{data.what_moved.length}/5000 characters</div>
    </div>
  )
}