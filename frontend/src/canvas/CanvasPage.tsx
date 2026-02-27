import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeftIcon, CalendarIcon, PlusIcon, TrashIcon, ChevronDownIcon, ChevronRightIcon, InformationCircleIcon } from '@heroicons/react/24/outline';
import ErrorBoundary from '../components/ErrorBoundary';
import InlineEdit from '../components/InlineEdit';
import StatusBadge from '../components/StatusBadge';
import FileUpload from '../components/FileUpload';
import ReviewHistory from '../reviews/ReviewHistory';
import RichTextEditor from '../components/RichTextEditor';
import { useCanvas } from './hooks/useCanvas';
import { listThesisCategories, ThesisCategory } from '../api/canvas';
import { useAuth } from '../auth/useAuth';
import { exportCanvasPdf } from '../utils/exportPdf';

const colorStyle = (color: string | null | undefined) => {
  if (!color) return { backgroundColor: '#f3f4f6', color: '#6b7280' };
  const [bg, fg] = color.split(',');
  return { backgroundColor: bg, color: fg };
};

const InfoTip: React.FC<{ text: string }> = ({ text }) => {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  return (
    <div className="relative inline-flex" ref={ref}>
      <button
        type="button"
        onClick={(e) => { e.stopPropagation(); setOpen(!open); }}
        className="text-neutral-400 hover:text-primary transition-colors"
        aria-label="More info"
      >
        <InformationCircleIcon className="h-4 w-4" />
      </button>
      {open && (
        <div className="absolute z-20 bottom-full mb-2 left-1/2 -translate-x-1/2 w-72 bg-navy text-white text-xs leading-relaxed rounded-lg shadow-lg p-3">
          {text}
          <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-[#001641]" />
        </div>
      )}
    </div>
  );
};

const ThesisTypeBadge: React.FC<{
  categoryId: string | null;
  categories: ThesisCategory[];
  onChange: (id: string | null) => void;
}> = ({ categoryId, categories, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const cat = categories.find(c => c.id === categoryId);

  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setIsOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [isOpen]);

  return (
    <div className="relative flex items-center gap-1.5 flex-shrink-0" ref={ref} onClick={(e) => e.stopPropagation()}>
      <span className="text-[11px] text-neutral-400 hidden sm:inline">Type:</span>
      <div
        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium cursor-pointer transition-all hover:ring-2 hover:ring-offset-1 hover:ring-gray-300"
        style={colorStyle(cat?.color)}
        onClick={() => setIsOpen(!isOpen)}
      >
        {cat?.name || 'No Type'}
        <ChevronDownIcon className={`ml-1 h-3 w-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </div>
      {isOpen && (
        <div className="absolute z-10 mt-1 right-0 w-80 bg-white border border-gray-200 rounded-md shadow-lg py-1">
          <button
            className={`w-full text-left px-3 py-2 text-xs hover:bg-gray-50 ${!categoryId ? 'bg-gray-50' : ''}`}
            onClick={() => { onChange(null); setIsOpen(false); }}
          >
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium" style={colorStyle(null)}>No Type</span>
          </button>
          {categories.map(c => (
            <button
              key={c.id}
              className={`w-full text-left px-3 py-2 text-xs hover:bg-gray-50 ${c.id === categoryId ? 'bg-gray-50' : ''}`}
              onClick={() => { onChange(c.id); setIsOpen(false); }}
              title={c.description || ''}
            >
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium" style={colorStyle(c.color)}>{c.name}</span>
              {c.description && <p className="mt-1 text-[11px] text-gray-400 leading-tight pl-2">{c.description}</p>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

const CanvasPage: React.FC = () => {
  const { vbuId } = useParams<{ vbuId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const [draggedThesis, setDraggedThesis] = useState<string | null>(null);
  const [categories, setCategories] = useState<ThesisCategory[]>([]);
  const [expandedTheses, setExpandedTheses] = useState<Set<string>>(new Set());
  const [expandedPPs, setExpandedPPs] = useState<Set<string>>(new Set());

  const toggleThesis = (id: string) => setExpandedTheses(prev => {
    const next = new Set(prev);
    next.has(id) ? next.delete(id) : next.add(id);
    return next;
  });
  const togglePP = (id: string) => setExpandedPPs(prev => {
    const next = new Set(prev);
    next.has(id) ? next.delete(id) : next.add(id);
    return next;
  });

  useEffect(() => { listThesisCategories().then(setCategories).catch(() => {}); }, []);

  const { user } = useAuth();
  const canEdit = user?.role === 'admin' || user?.role === 'gm' || user?.role === 'group_leader';

  const {
    canvas,
    vbuName,
    loading,
    error,
    saving,
    lastSaved,
    updateCanvas,
    addThesis,
    updateThesis,
    removeThesis,
    reorderTheses,
    addProofPoint,
    updateProofPoint,
    removeProofPoint,
    uploadAttachment,
    deleteAttachment,
    setCurrentlyTesting,
  } = useCanvas({ vbuId: vbuId || '' });

  const handleThesisDrop = (targetThesisId: string) => {
    if (!draggedThesis || draggedThesis === targetThesisId || !canvas) return;
    const draggedIndex = canvas.theses.findIndex(t => t.id === draggedThesis);
    const targetIndex = canvas.theses.findIndex(t => t.id === targetThesisId);
    if (draggedIndex === -1 || targetIndex === -1) return;

    const newTheses = [...canvas.theses];
    const [draggedItem] = newTheses.splice(draggedIndex, 1);
    newTheses.splice(targetIndex, 0, draggedItem);

    reorderTheses(newTheses.map((t, i) => ({ id: t.id, order: i + 1 })));
    setDraggedThesis(null);
  };

  // Scroll to proof point if hash is present (e.g. #pp-uuid)
  useEffect(() => {
    if (loading || !location.hash || !canvas) return;
    const ppId = location.hash.slice(1).replace('pp-', '');
    // Find the thesis that owns this proof point
    const parentThesis = canvas.theses.find(t => t.proof_points.some(p => p.id === ppId));
    if (!parentThesis) return;

    // Expand the parent thesis and the proof point
    setExpandedTheses(prev => new Set(prev).add(parentThesis.id));
    setExpandedPPs(prev => new Set(prev).add(ppId));
  }, [loading, location.hash, canvas]);

  // After expansions render, scroll to the element
  useEffect(() => {
    if (loading || !location.hash) return;
    const elId = location.hash.slice(1);
    const timer = setTimeout(() => {
      const el = document.getElementById(elId);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.classList.add('ring-2', 'ring-primary', 'ring-offset-2');
        setTimeout(() => el.classList.remove('ring-2', 'ring-primary', 'ring-offset-2'), 3000);
      }
    }, 100);
    return () => clearTimeout(timer);
  }, [loading, location.hash, expandedTheses, expandedPPs]);

  if (loading) {
    return <div className="flex justify-center items-center h-64 text-neutral-500">Loading canvas…</div>;
  }

  if (error || !canvas) {
    return (
      <div className="text-center py-12">
        <p className="text-neutral-800 font-medium mb-2">{error || 'Canvas not found'}</p>
        <button onClick={() => navigate('/')} className="text-sm text-primary hover:text-primary-dark">
          Back to Dashboard
        </button>
      </div>
    );
  }

  const lifecycleLanes = [
    { value: 'build', label: 'Build', color: 'bg-primary-pale text-primary-dark' },
    { value: 'sell', label: 'Sell', color: 'bg-success-pale text-success-dark' },
    { value: 'milk', label: 'Milk', color: 'bg-warning-pale text-warning-dark' },
    { value: 'reframe', label: 'Reframe', color: 'bg-accent-pale text-accent' },
  ];

  return (
    <ErrorBoundary>
      <div className="max-w-6xl mx-auto p-6 space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {user?.role !== 'gm' && (
              <button onClick={() => navigate('/')} className="p-2 hover:bg-neutral-50 rounded-lg">
                <ArrowLeftIcon className="h-5 w-5 text-neutral-500" />
              </button>
            )}
            <h1 className="text-2xl font-semibold text-navy">
              {vbuName || canvas.product_name || 'VBU Canvas'}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => vbuId && exportCanvasPdf(vbuId)}
              className="flex items-center space-x-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
            >
              <span>Export PDF</span>
            </button>
            <button
              onClick={() => navigate(`/vbus/${vbuId}/review/new`)}
              className="flex items-center space-x-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
            >
              <CalendarIcon className="h-4 w-4" />
              <span>Start Review</span>
            </button>
          </div>
        </div>

        {/* Autosave Status */}
        <div className="bg-neutral-50 px-4 py-2 rounded-lg text-sm text-neutral-500">
          {saving ? 'Saving…' : lastSaved ? `Last saved: ${lastSaved.toLocaleString()}` : 'No changes yet'}
        </div>

        {/* Context Section */}
        <div className="bg-white border border-neutral-100 rounded-lg p-6">
          <h2 className="text-lg font-medium text-navy mb-4">Context</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-neutral-800 mb-2">Product Name</label>
              <InlineEdit
                value={canvas.product_name || ''}
                onSave={(v) => updateCanvas({ product_name: v })}
                placeholder="Enter product name…"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-800 mb-2">Lifecycle Lane <InfoTip text="Which behavioural mode is this VBU in? Build = invest to prove the model. Sell = replicate what works. Milk = maximise cash and manage risk. Reframe = the current model is exhausted, pivot required." /></label>
              <div className="flex space-x-2">
                {lifecycleLanes.map((lane) => (
                  <button
                    key={lane.value}
                    onClick={() => updateCanvas({ lifecycle_lane: lane.value as any })}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      canvas.lifecycle_lane === lane.value ? lane.color : 'bg-neutral-50 text-neutral-500 hover:bg-neutral-100'
                    }`}
                  >
                    {lane.label}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-800 mb-2">Health</label>
              <div className="flex space-x-2">
                {[
                  { value: 'Not Started', icon: '⚪', color: 'bg-gray-100 text-gray-600' },
                  { value: 'In Progress', icon: '🟡', color: 'bg-teal-100 text-teal-700' },
                  { value: 'On Track', icon: '🟢', color: 'bg-green-100 text-green-700' },
                  { value: 'At Risk', icon: '🔴', color: 'bg-yellow-100 text-yellow-700' },
                ].map((h) => (
                  <button
                    key={h.value}
                    onClick={() => updateCanvas({ health_indicator: h.value })}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      canvas.health_indicator === h.value ? h.color : 'bg-neutral-50 text-neutral-500 hover:bg-neutral-100'
                    }`}
                  >
                    {h.icon} {h.value}
                  </button>
                ))}
              </div>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-neutral-800 mb-2">Success Description <InfoTip text="Complete the sentence: 'In this lane, success over 12–24 months means…' This should describe the observable outcome, not activities. What does the world look like if this VBU succeeds?" /></label>
              <InlineEdit
                value={canvas.success_description || ''}
                onSave={(v) => updateCanvas({ success_description: v })}
                multiline
                placeholder="In this lane, success over 12-24 months means…"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-neutral-800 mb-2">Future State Intent <InfoTip text="The 3–5 year vision. Describe the 'new normal' you are working toward — not a project plan, but what the world looks like when the strategy has played out." /></label>
              <InlineEdit
                value={canvas.future_state_intent || ''}
                onSave={(v) => updateCanvas({ future_state_intent: v })}
                multiline
                placeholder="3-5 year vision statement…"
              />
            </div>
          </div>
        </div>

        {/* Strategic Focus Section */}
        <div className="bg-white border border-neutral-100 rounded-lg p-6">
          <h2 className="text-lg font-medium text-navy mb-4">Strategic Focus <InfoTip text="These fields capture the behavioural discipline for this lifecycle lane — what to focus on, what to resist, and what the single biggest blocker is." /></h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-neutral-800 mb-2">Primary Focus <InfoTip text="What is the dominant mode for this VBU right now? Learning (testing hypotheses), Replication (scaling what works), or Cash & Risk (protecting margin and managing downside)." /></label>
              <InlineEdit
                value={canvas.primary_focus || ''}
                onSave={(v) => updateCanvas({ primary_focus: v })}
                placeholder="Learning / Replication / Cash & Risk"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-800 mb-2">Primary Constraint <InfoTip text="The single biggest blocker preventing the next proof point from appearing. Not a risk register — just the one thing that, if removed, would most accelerate progress." /></label>
              <InlineEdit
                value={canvas.primary_constraint || ''}
                onSave={(v) => updateCanvas({ primary_constraint: v })}
                placeholder="Single biggest blocker…"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-800 mb-2">Resist Doing <InfoTip text="What must this VBU actively resist? Each lifecycle lane has temptations — e.g. Build must resist premature scaling, Sell must resist custom one-offs, Milk must resist starving the cash cow of maintenance." /></label>
              <InlineEdit
                value={canvas.resist_doing || ''}
                onSave={(v) => updateCanvas({ resist_doing: v })}
                multiline
                placeholder="What we must resist doing…"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-800 mb-2">Good Discipline <InfoTip text="What does good execution look like in this lane? Describe the habits and behaviours that signal the team is operating with the right discipline for their lifecycle stage." /></label>
              <InlineEdit
                value={canvas.good_discipline || ''}
                onSave={(v) => updateCanvas({ good_discipline: v })}
                multiline
                placeholder="What good discipline looks like…"
              />
            </div>
          </div>
        </div>

        {/* Strategic Theses Section */}
        <div className="bg-white border border-neutral-100 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-navy">Strategic Theses <InfoTip text="A thesis is a strategic hypothesis about what must become true over 12–36 months. Phrase it as a 'new normal', not a project — e.g. 'Enterprise buyers will consolidate from 5 vendors to 2' rather than 'Launch enterprise sales program'. Max 5 per canvas." /></h2>
            <button
              onClick={async () => {
                if (canvas.theses.length >= 5) {
                  alert('Maximum 5 theses per canvas');
                  return;
                }
                const newId = await addThesis('');
                if (newId) {
                  setExpandedTheses(prev => new Set(prev).add(newId));
                  setTimeout(() => document.getElementById(`thesis-${newId}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' }), 100);
                }
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-primary hover:bg-primary-pale rounded-lg transition-colors"
            >
              <PlusIcon className="h-4 w-4" /> Add Thesis
            </button>
          </div>
          {canvas.theses.length === 0 ? (
            <p className="text-neutral-500 text-sm">No theses yet. Add one to get started.</p>
          ) : (
            <div className="space-y-3">
              {canvas.theses.map((thesis) => {
                const isExpanded = expandedTheses.has(thesis.id);
                const cat = categories.find(c => c.id === thesis.category_id);
                return (
                <ErrorBoundary key={thesis.id} fallback={<div className="text-red-600 text-sm">Thesis error. Please refresh.</div>}>
                  <div
                    id={`thesis-${thesis.id}`}
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={() => handleThesisDrop(thesis.id)}
                    className="border border-neutral-100 rounded-lg hover:shadow-md transition-shadow"
                  >
                    {/* Collapsed header — always visible */}
                    <div className="flex items-center gap-3 p-4 cursor-pointer" onClick={() => toggleThesis(thesis.id)}>
                      <div
                        draggable
                        onDragStart={(e) => { e.stopPropagation(); setDraggedThesis(thesis.id); }}
                        className="flex-shrink-0 w-6 h-6 bg-primary-pale text-primary-dark rounded-full flex items-center justify-center text-sm font-medium cursor-grab active:cursor-grabbing"
                        title="Drag to reorder"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {thesis.order}
                      </div>
                      {isExpanded
                        ? <ChevronDownIcon className="h-4 w-4 text-neutral-400 flex-shrink-0" />
                        : <ChevronRightIcon className="h-4 w-4 text-neutral-400 flex-shrink-0" />
                      }
                      <span className={`flex-1 text-sm font-medium truncate ${thesis.text?.trim() ? 'text-navy' : 'text-gray-400 italic'}`}>{thesis.text?.trim() || 'New thesis'}</span>
                      <ThesisTypeBadge
                        categoryId={thesis.category_id}
                        categories={categories}
                        onChange={(id) => updateThesis(thesis.id, { category_id: id })}
                      />
                      <button
                        onClick={(e) => { e.stopPropagation(); removeThesis(thesis.id); }}
                        className="p-1 text-neutral-300 hover:text-red-500 transition-colors"
                        title="Delete thesis"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>

                    {/* Expanded content */}
                    {isExpanded && (
                      <div className="px-4 pb-4 pt-0 ml-[3.25rem]">
                        <div className="mb-3">
                          <InlineEdit
                            value={thesis.text}
                            onSave={(v) => updateThesis(thesis.id, { text: v })}
                            placeholder="Enter thesis statement…"
                          />
                        </div>

                        <div className="mb-3">
                          <label className="block text-xs font-medium text-neutral-500 mb-1">Description</label>
                          <RichTextEditor
                            content={thesis.description || ''}
                            onUpdate={(html) => updateThesis(thesis.id, { description: html })}
                            placeholder="Add supporting detail…"
                          />
                        </div>

                        {/* Proof Points */}
                        <div className="mt-6 space-y-2">
                          <div className="mb-2">
                            <h3 className="text-xs font-semibold text-neutral-500 uppercase tracking-wide">Proof Points <span className="normal-case tracking-normal"><InfoTip text="Observable signals (not activities) that this thesis is strengthening or weakening. Think 'what would we see in the real world?' — e.g. 'Win rate against Competitor X exceeds 40%' or 'Three enterprise customers renew without discount'. Aim for 3–6 month horizon." /></span></h3>
                          </div>
                          {thesis.proof_points.map((pp) => {
                            const ppExpanded = expandedPPs.has(pp.id);
                            return (
                            <div key={pp.id} id={`pp-${pp.id}`} className="bg-neutral-50 rounded-lg">
                              {/* PP collapsed row */}
                              <div className="flex items-center gap-2 px-3 py-2 cursor-pointer" onClick={() => togglePP(pp.id)}>
                                {ppExpanded
                                  ? <ChevronDownIcon className="h-3.5 w-3.5 text-neutral-400 flex-shrink-0" />
                                  : <ChevronRightIcon className="h-3.5 w-3.5 text-neutral-400 flex-shrink-0" />
                                }
                                <span className={`flex-1 text-sm truncate ${pp.description.trim() ? 'text-gray-800' : 'text-gray-400 italic'}`}>{pp.description.trim() || 'New proof point'}</span>
                                <StatusBadge
                                  status={pp.status}
                                  onChange={(status) => updateProofPoint(pp.id, { status: status as any })}
                                />
                                <button
                                  onClick={(e) => { e.stopPropagation(); removeProofPoint(pp.id); }}
                                  className="p-1 text-neutral-300 hover:text-red-500 transition-colors"
                                  title="Delete proof point"
                                >
                                  <TrashIcon className="h-3.5 w-3.5" />
                                </button>
                              </div>

                              {/* PP expanded content */}
                              {ppExpanded && (
                                <div className="px-3 pb-3 pt-1 ml-6">
                                  <div className="mb-2">
                                    <InlineEdit
                                      value={pp.description}
                                      onSave={(v) => updateProofPoint(pp.id, { description: v })}
                                      placeholder="Observable signal description…"
                                    />
                                  </div>
                                  <div className="mb-2">
                                    <label className="block text-xs font-medium text-neutral-500 mb-1">Notes</label>
                                    <RichTextEditor
                                      content={pp.notes || ''}
                                      onUpdate={(html) => updateProofPoint(pp.id, { notes: html })}
                                      placeholder="Proof point notes…"
                                    />
                                  </div>
                                  <ErrorBoundary fallback={<div className="text-red-600 text-sm">File upload error.</div>}>
                                    <FileUpload
                                      onUpload={(file, label) => uploadAttachment(pp.id, file, label)}
                                      attachments={pp.attachments}
                                      onDelete={(attachmentId) => deleteAttachment(attachmentId)}
                                      maxSize={10485760}
                                      allowedTypes={['image/jpeg', 'image/png', 'image/gif', 'application/pdf']}
                                    />
                                  </ErrorBoundary>
                                </div>
                              )}
                            </div>
                            );
                          })}
                          <button
                            onClick={async () => {
                              const newPPId = await addProofPoint(thesis.id, '');
                              if (newPPId) {
                                setExpandedPPs(prev => new Set(prev).add(newPPId));
                                setTimeout(() => {
                                  document.getElementById(`pp-${newPPId}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                }, 100);
                              }
                            }}
                            className="flex items-center gap-1 text-xs font-medium text-primary hover:text-primary-dark transition-colors mt-2"
                          >
                            <PlusIcon className="h-3.5 w-3.5" /> Add Proof Point
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </ErrorBoundary>
                );
              })}
            </div>
          )}
        </div>

        {/* Currently Testing Section */}
        {canvas.currently_testing_type && (
          <div className="bg-white border border-neutral-100 rounded-lg p-6">
            <h2 className="text-lg font-medium text-navy mb-4">Currently Testing</h2>
            <div className="text-sm text-neutral-500">
              Focus: {canvas.currently_testing_type === 'thesis' ? 'Thesis' : 'Proof Point'} —{' '}
              {canvas.currently_testing_type === 'thesis'
                ? canvas.theses.find(t => t.id === canvas.currently_testing_id)?.text
                : 'Selected proof point'}
            </div>
          </div>
        )}

        {/* Review History */}
        <ReviewHistory canvasId={canvas.id} vbuId={vbuId || ''} />
      </div>
    </ErrorBoundary>
  );
};

export default CanvasPage;
