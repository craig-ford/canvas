import React, { useState, useEffect } from 'react';
import { ArrowLeftIcon, CalendarIcon } from '@heroicons/react/24/outline';
import InlineEdit from '../components/InlineEdit';
import StatusBadge from '../components/StatusBadge';
import FileUpload from '../components/FileUpload';

interface CanvasPageProps {
  vbuId: string;
}

interface Attachment {
  id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  label?: string;
  uploaded_by: string;
  created_at: string;
}

interface ProofPoint {
  id: string;
  description: string;
  status: 'not_started' | 'in_progress' | 'observed' | 'stalled';
  evidence_note?: string;
  target_review_month?: string;
  attachments: Attachment[];
}

interface Thesis {
  id: string;
  order: number;
  text: string;
  proof_points: ProofPoint[];
}

interface Canvas {
  id: string;
  vbu_id: string;
  product_name?: string;
  lifecycle_lane: 'build' | 'sell' | 'milk' | 'reframe';
  success_description?: string;
  future_state_intent?: string;
  primary_focus?: string;
  resist_doing?: string;
  good_discipline?: string;
  primary_constraint?: string;
  currently_testing_type?: 'thesis' | 'proof_point';
  currently_testing_id?: string;
  theses: Thesis[];
}

const CanvasPage: React.FC<CanvasPageProps> = ({ vbuId }) => {
  const [canvas, setCanvas] = useState<Canvas | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [draggedThesis, setDraggedThesis] = useState<string | null>(null);

  // Mock data loading
  useEffect(() => {
    const loadCanvas = async () => {
      try {
        // Mock API call - will be replaced in T-024
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const mockCanvas: Canvas = {
          id: 'canvas-1',
          vbu_id: vbuId,
          product_name: 'Strategic Product Alpha',
          lifecycle_lane: 'build',
          success_description: 'We will have validated product-market fit with 1000+ active users',
          future_state_intent: 'Become the leading solution in our market segment',
          primary_focus: 'Learning',
          resist_doing: 'Building features without user validation',
          good_discipline: 'Weekly user interviews and data review',
          primary_constraint: 'Limited engineering resources',
          currently_testing_type: 'thesis',
          currently_testing_id: 'thesis-1',
          theses: [
            {
              id: 'thesis-1',
              order: 1,
              text: 'Users will pay for premium features',
              proof_points: [
                {
                  id: 'pp-1',
                  description: 'Survey shows 60%+ willingness to pay',
                  status: 'in_progress',
                  evidence_note: 'Initial survey completed',
                  target_review_month: '2024-03',
                  attachments: []
                }
              ]
            }
          ]
        };
        
        setCanvas(mockCanvas);
      } catch (err) {
        setError('Failed to load canvas');
      } finally {
        setLoading(false);
      }
    };

    loadCanvas();
  }, [vbuId]);

  const handleSave = async (field: string, value: string) => {
    // Mock save - will be replaced with API call
    await new Promise(resolve => setTimeout(resolve, 500));
    setLastUpdated(new Date());
  };

  const handleLifecycleLaneChange = (lane: string) => {
    if (canvas) {
      setCanvas({
        ...canvas,
        lifecycle_lane: lane as Canvas['lifecycle_lane']
      });
      setLastUpdated(new Date());
    }
  };

  const handleStatusChange = (proofPointId: string, status: string) => {
    if (canvas) {
      const updatedTheses = canvas.theses.map(thesis => ({
        ...thesis,
        proof_points: thesis.proof_points.map(pp =>
          pp.id === proofPointId ? { ...pp, status: status as ProofPoint['status'] } : pp
        )
      }));
      setCanvas({ ...canvas, theses: updatedTheses });
      setLastUpdated(new Date());
    }
  };

  const handleFileUpload = async (proofPointId: string, file: File, label?: string) => {
    // Mock upload
    await new Promise(resolve => setTimeout(resolve, 1000));
    const newAttachment: Attachment = {
      id: `att-${Date.now()}`,
      filename: file.name,
      content_type: file.type,
      size_bytes: file.size,
      label,
      uploaded_by: 'current-user',
      created_at: new Date().toISOString()
    };

    if (canvas) {
      const updatedTheses = canvas.theses.map(thesis => ({
        ...thesis,
        proof_points: thesis.proof_points.map(pp =>
          pp.id === proofPointId 
            ? { ...pp, attachments: [...pp.attachments, newAttachment] }
            : pp
        )
      }));
      setCanvas({ ...canvas, theses: updatedTheses });
    }
  };

  const handleFileDelete = async (proofPointId: string, attachmentId: string) => {
    if (canvas) {
      const updatedTheses = canvas.theses.map(thesis => ({
        ...thesis,
        proof_points: thesis.proof_points.map(pp =>
          pp.id === proofPointId 
            ? { ...pp, attachments: pp.attachments.filter(att => att.id !== attachmentId) }
            : pp
        )
      }));
      setCanvas({ ...canvas, theses: updatedTheses });
    }
  };

  const handleThesisDragStart = (thesisId: string) => {
    setDraggedThesis(thesisId);
  };

  const handleThesisDrop = (targetThesisId: string) => {
    if (!draggedThesis || draggedThesis === targetThesisId || !canvas) return;

    const draggedIndex = canvas.theses.findIndex(t => t.id === draggedThesis);
    const targetIndex = canvas.theses.findIndex(t => t.id === targetThesisId);

    if (draggedIndex === -1 || targetIndex === -1) return;

    const newTheses = [...canvas.theses];
    const [draggedItem] = newTheses.splice(draggedIndex, 1);
    newTheses.splice(targetIndex, 0, draggedItem);

    // Update order numbers
    const reorderedTheses = newTheses.map((thesis, index) => ({
      ...thesis,
      order: index + 1
    }));

    setCanvas({ ...canvas, theses: reorderedTheses });
    setDraggedThesis(null);
    setLastUpdated(new Date());
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  if (error || !canvas) {
    return <div className="text-red-600 text-center">{error || 'Canvas not found'}</div>;
  }

  const lifecycleLanes = [
    { value: 'build', label: 'Build', color: 'bg-blue-100 text-blue-800' },
    { value: 'sell', label: 'Sell', color: 'bg-green-100 text-green-800' },
    { value: 'milk', label: 'Milk', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'reframe', label: 'Reframe', color: 'bg-purple-100 text-purple-800' }
  ];

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeftIcon className="h-5 w-5" />
          </button>
          <h1 className="text-2xl font-semibold">VBU Canvas</h1>
        </div>
        <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          <CalendarIcon className="h-4 w-4" />
          <span>Monthly Review</span>
        </button>
      </div>

      {/* Autosave Status */}
      <div className="bg-gray-50 px-4 py-2 rounded-lg text-sm text-gray-600">
        Last updated: {lastUpdated.toLocaleString()}
      </div>

      {/* Context Section */}
      <div className="bg-white border rounded-lg p-6">
        <h2 className="text-lg font-medium mb-4">Context</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Product Name</label>
            <InlineEdit
              value={canvas.product_name || ''}
              onSave={(value) => handleSave('product_name', value)}
              placeholder="Enter product name..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Lifecycle Lane</label>
            <div className="flex space-x-2">
              {lifecycleLanes.map((lane) => (
                <button
                  key={lane.value}
                  onClick={() => handleLifecycleLaneChange(lane.value)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    canvas.lifecycle_lane === lane.value
                      ? lane.color
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {lane.label}
                </button>
              ))}
            </div>
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">Success Description</label>
            <InlineEdit
              value={canvas.success_description || ''}
              onSave={(value) => handleSave('success_description', value)}
              multiline
              placeholder="In this lane, success over 12-24 months means..."
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">Future State Intent</label>
            <InlineEdit
              value={canvas.future_state_intent || ''}
              onSave={(value) => handleSave('future_state_intent', value)}
              multiline
              placeholder="3-5 year vision statement..."
            />
          </div>
        </div>
      </div>

      {/* Strategic Focus Section */}
      <div className="bg-white border rounded-lg p-6">
        <h2 className="text-lg font-medium mb-4">Strategic Focus</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Primary Focus</label>
            <InlineEdit
              value={canvas.primary_focus || ''}
              onSave={(value) => handleSave('primary_focus', value)}
              placeholder="Learning / Replication / Cash & Risk"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Primary Constraint</label>
            <InlineEdit
              value={canvas.primary_constraint || ''}
              onSave={(value) => handleSave('primary_constraint', value)}
              placeholder="Single biggest blocker..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Resist Doing</label>
            <InlineEdit
              value={canvas.resist_doing || ''}
              onSave={(value) => handleSave('resist_doing', value)}
              multiline
              placeholder="What we must resist doing..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Good Discipline</label>
            <InlineEdit
              value={canvas.good_discipline || ''}
              onSave={(value) => handleSave('good_discipline', value)}
              multiline
              placeholder="What good discipline looks like..."
            />
          </div>
        </div>
      </div>

      {/* Strategic Theses Section */}
      <div className="bg-white border rounded-lg p-6">
        <h2 className="text-lg font-medium mb-4">Strategic Theses</h2>
        <div className="space-y-6">
          {canvas.theses.map((thesis) => (
            <div
              key={thesis.id}
              draggable
              onDragStart={() => handleThesisDragStart(thesis.id)}
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => handleThesisDrop(thesis.id)}
              className="border rounded-lg p-4 cursor-move hover:shadow-md transition-shadow"
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center text-sm font-medium">
                  {thesis.order}
                </div>
                <div className="flex-1">
                  <InlineEdit
                    value={thesis.text}
                    onSave={(value) => handleSave(`thesis_${thesis.id}`, value)}
                    placeholder="Enter thesis statement..."
                  />
                  
                  {/* Proof Points */}
                  <div className="mt-4 space-y-3">
                    {thesis.proof_points.map((proofPoint) => (
                      <div key={proofPoint.id} className="bg-gray-50 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <InlineEdit
                              value={proofPoint.description}
                              onSave={(value) => handleSave(`proof_point_${proofPoint.id}`, value)}
                              placeholder="Observable signal description..."
                            />
                          </div>
                          <StatusBadge
                            status={proofPoint.status}
                            onChange={(status) => handleStatusChange(proofPoint.id, status)}
                          />
                        </div>
                        
                        {proofPoint.evidence_note && (
                          <div className="mb-3">
                            <label className="block text-xs font-medium text-gray-600 mb-1">Evidence Note</label>
                            <InlineEdit
                              value={proofPoint.evidence_note}
                              onSave={(value) => handleSave(`evidence_${proofPoint.id}`, value)}
                              multiline
                              placeholder="Evidence supporting status..."
                            />
                          </div>
                        )}
                        
                        <FileUpload
                          onUpload={(file, label) => handleFileUpload(proofPoint.id, file, label)}
                          attachments={proofPoint.attachments}
                          onDelete={(attachmentId) => handleFileDelete(proofPoint.id, attachmentId)}
                          maxSize={10485760} // 10MB
                          allowedTypes={['image/jpeg', 'image/png', 'image/gif', 'application/pdf']}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Currently Testing Section */}
      <div className="bg-white border rounded-lg p-6">
        <h2 className="text-lg font-medium mb-4">Currently Testing</h2>
        <div className="text-sm text-gray-600">
          Focus: {canvas.currently_testing_type === 'thesis' ? 'Thesis' : 'Proof Point'} - 
          {canvas.currently_testing_type === 'thesis' 
            ? canvas.theses.find(t => t.id === canvas.currently_testing_id)?.text
            : 'Selected proof point'
          }
        </div>
      </div>
    </div>
  );
};

export default CanvasPage;