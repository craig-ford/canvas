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

interface CommitmentsStepProps {
  data: ReviewData
  onChange: (data: ReviewData) => void
  options: CanvasOptions | null
}

export const CommitmentsStep: React.FC<CommitmentsStepProps> = ({ data, onChange, options }) => {
  const getCommitmentError = (commitment: { text: string }) => {
    if (!commitment.text.trim()) return 'Commitment is required';
    if (commitment.text.length > 1000) return 'Commitment must be 1000 characters or less';
    return null;
  };

  const getCurrentlyTestingError = () => {
    if (!data.currently_testing_id) return 'Please select what you are currently testing';
    return null;
  };

  const allErrors = [
    ...data.commitments.map(getCommitmentError).filter(Boolean),
    getCurrentlyTestingError()
  ].filter(Boolean);
  const addCommitment = () => {
    if (data.commitments.length < 3) {
      const newCommitments = [...data.commitments, { 
        text: '', 
        order: data.commitments.length + 1 
      }]
      onChange({ ...data, commitments: newCommitments })
    }
  }

  const removeCommitment = (index: number) => {
    const newCommitments = data.commitments
      .filter((_, i) => i !== index)
      .map((commitment, i) => ({ ...commitment, order: i + 1 }))
    onChange({ ...data, commitments: newCommitments })
  }

  const updateCommitment = (index: number, text: string) => {
    const newCommitments = data.commitments.map((commitment, i) => 
      i === index ? { ...commitment, text } : commitment
    )
    onChange({ ...data, commitments: newCommitments })
  }

  const handleCurrentlyTestingChange = (value: string) => {
    const [type, id] = value.split(':')
    onChange({
      ...data,
      currently_testing_type: type as 'thesis' | 'proof_point',
      currently_testing_id: id
    })
  }

  return (
    <div className="space-y-8">
      {allErrors.length > 0 && (
        <div aria-live="polite" aria-atomic="true" className="sr-only">
          {allErrors.length} validation error{allErrors.length > 1 ? 's' : ''} found
        </div>
      )}
      <div>
        <h2 className="text-2xl font-semibold mb-4">Commitments & Focus</h2>
        
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-4">Commitments (1-3 required)</h3>
          <div className="space-y-3">
            {data.commitments.map((commitment, index) => {
              const error = getCommitmentError(commitment);
              return (
                <div key={index} className="space-y-1">
                  <div className="flex items-center space-x-3">
                    <span className="text-sm font-medium text-gray-600 w-6">
                      {index + 1}.
                    </span>
                    <input
                      type="text"
                      value={commitment.text}
                      onChange={(e) => updateCommitment(index, e.target.value)}
                      className={`flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                        error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : ''
                      }`}
                      maxLength={1000}
                      placeholder="Enter a specific commitment..."
                      aria-invalid={error ? 'true' : 'false'}
                      aria-describedby={error ? `commitment-error-${index}` : undefined}
                    />
                    {data.commitments.length > 1 && (
                      <button
                        onClick={() => removeCommitment(index)}
                        className="text-red-600 hover:text-red-700 p-2"
                        title="Remove commitment"
                      >
                        ×
                      </button>
                    )}
                  </div>
                  {error && (
                    <p id={`commitment-error-${index}`} className="text-sm text-red-600 ml-9">
                      {error}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
          
          {data.commitments.length < 3 && (
            <button
              onClick={addCommitment}
              className="mt-3 text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              + Add Commitment ({3 - data.commitments.length} remaining)
            </button>
          )}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium mb-4">What are we currently testing? (required)</h3>
        {getCurrentlyTestingError() && (
          <p className="text-sm text-red-600 mb-2" role="alert">
            {getCurrentlyTestingError()}
          </p>
        )}
        {options ? (
          <div className="space-y-3 border rounded-lg p-4 max-h-64 overflow-y-auto">
            {options.theses.map((thesis) => (
              <div key={thesis.id} className="space-y-2">
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="radio"
                    name="currently_testing"
                    value={`thesis:${thesis.id}`}
                    checked={data.currently_testing_type === 'thesis' && data.currently_testing_id === thesis.id}
                    onChange={(e) => handleCurrentlyTestingChange(e.target.value)}
                    className="mt-1"
                  />
                  <span className="text-sm font-medium">{thesis.text}</span>
                </label>
                
                {thesis.proof_points?.map((proofPoint) => (
                  <label key={proofPoint.id} className="flex items-start space-x-3 ml-6 cursor-pointer">
                    <input
                      type="radio"
                      name="currently_testing"
                      value={`proof_point:${proofPoint.id}`}
                      checked={data.currently_testing_type === 'proof_point' && data.currently_testing_id === proofPoint.id}
                      onChange={(e) => handleCurrentlyTestingChange(e.target.value)}
                      className="mt-1"
                    />
                    <span className="text-sm text-gray-700">{proofPoint.description}</span>
                  </label>
                ))}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-gray-500 text-sm">Loading options...</div>
        )}
      </div>
    </div>
  )
}