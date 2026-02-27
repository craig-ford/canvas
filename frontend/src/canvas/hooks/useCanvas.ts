import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  getCanvas, 
  getVbu,
  updateCanvas as apiUpdateCanvas,
  createThesis as apiCreateThesis,
  updateThesis as apiUpdateThesis,
  deleteThesis as apiDeleteThesis,
  reorderTheses as apiReorderTheses,
  createProofPoint as apiCreateProofPoint,
  updateProofPoint as apiUpdateProofPoint,
  deleteProofPoint as apiDeleteProofPoint,
  uploadAttachment as apiUploadAttachment,
  deleteAttachment as apiDeleteAttachment,
  Canvas,
  Thesis,
  ProofPoint
} from '../../api/canvas';

interface UseCanvasOptions {
  vbuId: string;
  autoSave?: boolean;
  debounceMs?: number;
}

interface UseCanvasReturn {
  canvas: Canvas | null;
  vbuName: string;
  loading: boolean;
  error: string | null;
  saving: boolean;
  lastSaved: Date | null;
  updateCanvas: (updates: Partial<Canvas>) => Promise<void>;
  addThesis: (text: string) => Promise<string | undefined>;
  updateThesis: (thesisId: string, updates: Partial<Thesis>) => Promise<void>;
  removeThesis: (thesisId: string) => Promise<void>;
  reorderTheses: (thesisOrders: Array<{id: string, order: number}>) => Promise<void>;
  addProofPoint: (thesisId: string, description: string) => Promise<string | undefined>;
  updateProofPoint: (proofPointId: string, updates: Partial<ProofPoint>) => Promise<void>;
  removeProofPoint: (proofPointId: string) => Promise<void>;
  uploadAttachment: (proofPointId: string, file: File, label?: string) => Promise<void>;
  deleteAttachment: (attachmentId: string) => Promise<void>;
  setCurrentlyTesting: (type: 'thesis' | 'proof_point' | null, id: string | null) => Promise<void>;
}

export const useCanvas = (options: UseCanvasOptions): UseCanvasReturn => {
  const { vbuId, autoSave = true, debounceMs = 2000 } = options;
  
  const [canvas, setCanvas] = useState<Canvas | null>(null);
  const [vbuName, setVbuName] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pendingUpdatesRef = useRef<Partial<Canvas>>({});
  const canvasRef = useRef<Canvas | null>(null);

  // Keep ref in sync
  useEffect(() => { canvasRef.current = canvas; }, [canvas]);

  // Load canvas data on mount
  useEffect(() => {
    const loadCanvas = async () => {
      try {
        setLoading(true);
        setError(null);
        const [canvasData, vbuData] = await Promise.all([getCanvas(vbuId), getVbu(vbuId)]);
        setCanvas(canvasData);
        setVbuName(vbuData.name);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load canvas');
      } finally {
        setLoading(false);
      }
    };

    loadCanvas();
  }, [vbuId]);

  // Flush pending saves
  const flushSave = useCallback(async () => {
    const updates = pendingUpdatesRef.current;
    if (Object.keys(updates).length === 0) return;
    pendingUpdatesRef.current = {};
    try {
      setSaving(true);
      const updatedCanvas = await apiUpdateCanvas(vbuId, updates);
      setCanvas(updatedCanvas);
      setLastSaved(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save changes');
    } finally {
      setSaving(false);
    }
  }, [vbuId]);

  const updateCanvas = useCallback(async (updates: Partial<Canvas>) => {
    if (!canvasRef.current) return;

    // Optimistic update
    setCanvas(prev => prev ? { ...prev, ...updates } : null);
    
    if (autoSave) {
      // Merge with pending
      pendingUpdatesRef.current = { ...pendingUpdatesRef.current, ...updates };
      if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
      saveTimeoutRef.current = setTimeout(flushSave, debounceMs);
    } else {
      try {
        setSaving(true);
        const updatedCanvas = await apiUpdateCanvas(vbuId, updates);
        setCanvas(updatedCanvas);
        setLastSaved(new Date());
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update canvas');
        setCanvas(canvasRef.current);
      } finally {
        setSaving(false);
      }
    }
  }, [vbuId, autoSave, debounceMs, flushSave]);

  const updateThesis = useCallback(async (thesisId: string, updates: Partial<Thesis>) => {
    if (!canvas) return;

    // Optimistic update
    setCanvas(prev => {
      if (!prev) return null;
      return {
        ...prev,
        theses: prev.theses.map(thesis => 
          thesis.id === thesisId ? { ...thesis, ...updates } : thesis
        )
      };
    });

    try {
      setSaving(true);
      await apiUpdateThesis(thesisId, updates);
      setLastSaved(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update thesis');
      // Reload canvas to revert optimistic update
      const canvasData = await getCanvas(vbuId);
      setCanvas(canvasData);
    } finally {
      setSaving(false);
    }
  }, [canvas, vbuId]);

  const reorderTheses = useCallback(async (thesisOrders: Array<{id: string, order: number}>) => {
    if (!canvas) return;

    // Optimistic update
    const reorderedTheses = [...canvas.theses].sort((a, b) => {
      const orderA = thesisOrders.find(o => o.id === a.id)?.order || a.order;
      const orderB = thesisOrders.find(o => o.id === b.id)?.order || b.order;
      return orderA - orderB;
    });

    setCanvas(prev => prev ? { ...prev, theses: reorderedTheses } : null);

    try {
      setSaving(true);
      await apiReorderTheses(canvas.id, thesisOrders);
      setLastSaved(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reorder theses');
      // Reload canvas to revert optimistic update
      const canvasData = await getCanvas(vbuId);
      setCanvas(canvasData);
    } finally {
      setSaving(false);
    }
  }, [canvas, vbuId]);

  const updateProofPoint = useCallback(async (proofPointId: string, updates: Partial<ProofPoint>) => {
    if (!canvas) return;

    // Optimistic update
    setCanvas(prev => {
      if (!prev) return null;
      return {
        ...prev,
        theses: prev.theses.map(thesis => ({
          ...thesis,
          proof_points: thesis.proof_points.map(pp => 
            pp.id === proofPointId ? { ...pp, ...updates } : pp
          )
        }))
      };
    });

    try {
      setSaving(true);
      await apiUpdateProofPoint(proofPointId, updates);
      setLastSaved(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update proof point');
      // Reload canvas to revert optimistic update
      const canvasData = await getCanvas(vbuId);
      setCanvas(canvasData);
    } finally {
      setSaving(false);
    }
  }, [canvas, vbuId]);

  const uploadAttachment = useCallback(async (proofPointId: string, file: File, label?: string) => {
    try {
      setSaving(true);
      const attachment = await apiUploadAttachment(file, { proof_point_id: proofPointId, label });
      
      // Update canvas with new attachment
      setCanvas(prev => {
        if (!prev) return null;
        return {
          ...prev,
          theses: prev.theses.map(thesis => ({
            ...thesis,
            proof_points: thesis.proof_points.map(pp => 
              pp.id === proofPointId 
                ? { ...pp, attachments: [...pp.attachments, attachment] }
                : pp
            )
          }))
        };
      });
      
      setLastSaved(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload attachment');
    } finally {
      setSaving(false);
    }
  }, []);

  const deleteAttachment = useCallback(async (attachmentId: string) => {
    if (!canvas) return;

    // Optimistic removal
    setCanvas(prev => {
      if (!prev) return null;
      return {
        ...prev,
        theses: prev.theses.map(thesis => ({
          ...thesis,
          proof_points: thesis.proof_points.map(pp => ({
            ...pp,
            attachments: pp.attachments.filter(att => att.id !== attachmentId)
          }))
        }))
      };
    });

    try {
      setSaving(true);
      await apiDeleteAttachment(attachmentId);
      setLastSaved(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete attachment');
      // Reload canvas to revert optimistic update
      const canvasData = await getCanvas(vbuId);
      setCanvas(canvasData);
    } finally {
      setSaving(false);
    }
  }, [canvas, vbuId]);

  const addThesis = useCallback(async (text: string): Promise<string | undefined> => {
    if (!canvas) return;
    try {
      setSaving(true);
      const nextOrder = canvas.theses.length > 0 ? Math.max(...canvas.theses.map(t => t.order)) + 1 : 1;
      const newThesis = await apiCreateThesis(canvas.id, { text, order: nextOrder });
      setCanvas(prev => prev ? { ...prev, theses: [...prev.theses, { ...newThesis, proof_points: newThesis.proof_points || [] }] } : null);
      setLastSaved(new Date());
      return newThesis.id;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add thesis');
    } finally {
      setSaving(false);
    }
  }, [canvas]);

  const removeThesis = useCallback(async (thesisId: string) => {
    if (!canvas) return;
    setCanvas(prev => prev ? { ...prev, theses: prev.theses.filter(t => t.id !== thesisId) } : null);
    try {
      setSaving(true);
      await apiDeleteThesis(thesisId);
      setLastSaved(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete thesis');
      const canvasData = await getCanvas(vbuId);
      setCanvas(canvasData);
    } finally {
      setSaving(false);
    }
  }, [canvas, vbuId]);

  const addProofPoint = useCallback(async (thesisId: string, description: string): Promise<string | undefined> => {
    if (!canvas) return;
    try {
      setSaving(true);
      const newPP = await apiCreateProofPoint(thesisId, { description });
      setCanvas(prev => {
        if (!prev) return null;
        return {
          ...prev,
          theses: prev.theses.map(t =>
            t.id === thesisId ? { ...t, proof_points: [...t.proof_points, { ...newPP, attachments: newPP.attachments || [] }] } : t
          )
        };
      });
      setLastSaved(new Date());
      return newPP.id;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add proof point');
    } finally {
      setSaving(false);
    }
  }, [canvas]);

  const removeProofPoint = useCallback(async (proofPointId: string) => {
    if (!canvas) return;
    setCanvas(prev => {
      if (!prev) return null;
      return {
        ...prev,
        theses: prev.theses.map(t => ({
          ...t,
          proof_points: t.proof_points.filter(pp => pp.id !== proofPointId)
        }))
      };
    });
    try {
      setSaving(true);
      await apiDeleteProofPoint(proofPointId);
      setLastSaved(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete proof point');
      const canvasData = await getCanvas(vbuId);
      setCanvas(canvasData);
    } finally {
      setSaving(false);
    }
  }, [canvas, vbuId]);

  const setCurrentlyTesting = useCallback(async (type: 'thesis' | 'proof_point' | null, id: string | null) => {
    if (!canvas) return;

    const updates = {
      currently_testing_type: type,
      currently_testing_id: id
    };

    await updateCanvas(updates);
  }, [canvas, updateCanvas]);

  // Cleanup timeout on unmount and when dependencies change
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
        saveTimeoutRef.current = null;
      }
    };
  }, []);

  return {
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
    setCurrentlyTesting
  };
};