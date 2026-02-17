import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  getCanvas, 
  updateCanvas as apiUpdateCanvas,
  updateThesis as apiUpdateThesis,
  reorderTheses as apiReorderTheses,
  updateProofPoint as apiUpdateProofPoint,
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
  loading: boolean;
  error: string | null;
  saving: boolean;
  lastSaved: Date | null;
  updateCanvas: (updates: Partial<Canvas>) => Promise<void>;
  updateThesis: (thesisId: string, updates: Partial<Thesis>) => Promise<void>;
  reorderTheses: (thesisOrders: Array<{id: string, order: number}>) => Promise<void>;
  updateProofPoint: (proofPointId: string, updates: Partial<ProofPoint>) => Promise<void>;
  uploadAttachment: (proofPointId: string, file: File, label?: string) => Promise<void>;
  deleteAttachment: (attachmentId: string) => Promise<void>;
  setCurrentlyTesting: (type: 'thesis' | 'proof_point' | null, id: string | null) => Promise<void>;
}

export const useCanvas = (options: UseCanvasOptions): UseCanvasReturn => {
  const { vbuId, autoSave = true, debounceMs = 2000 } = options;
  
  const [canvas, setCanvas] = useState<Canvas | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pendingUpdatesRef = useRef<Partial<Canvas>>({});

  // Load canvas data on mount
  useEffect(() => {
    const loadCanvas = async () => {
      try {
        setLoading(true);
        setError(null);
        const canvasData = await getCanvas(vbuId);
        setCanvas(canvasData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load canvas');
      } finally {
        setLoading(false);
      }
    };

    loadCanvas();
  }, [vbuId]);

  // Debounced save function
  const debouncedSave = useCallback(async (updates: Partial<Canvas>) => {
    if (!autoSave || !canvas) return;

    // Clear existing timeout
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    // Merge with pending updates
    pendingUpdatesRef.current = { ...pendingUpdatesRef.current, ...updates };

    // Set new timeout
    saveTimeoutRef.current = setTimeout(async () => {
      try {
        setSaving(true);
        const updatedCanvas = await apiUpdateCanvas(vbuId, pendingUpdatesRef.current);
        setCanvas(updatedCanvas);
        setLastSaved(new Date());
        pendingUpdatesRef.current = {};
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to save changes');
      } finally {
        setSaving(false);
      }
    }, debounceMs);
  }, [vbuId, autoSave, debounceMs, canvas]);

  const updateCanvas = useCallback(async (updates: Partial<Canvas>) => {
    if (!canvas) return;

    // Optimistic update
    setCanvas(prev => prev ? { ...prev, ...updates } : null);
    
    if (autoSave) {
      await debouncedSave(updates);
    } else {
      try {
        setSaving(true);
        const updatedCanvas = await apiUpdateCanvas(vbuId, updates);
        setCanvas(updatedCanvas);
        setLastSaved(new Date());
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update canvas');
        // Revert optimistic update on error
        setCanvas(canvas);
      } finally {
        setSaving(false);
      }
    }
  }, [canvas, vbuId, autoSave, debouncedSave]);

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
  }, [vbuId, autoSave, debounceMs]);

  return {
    canvas,
    loading,
    error,
    saving,
    lastSaved,
    updateCanvas,
    updateThesis,
    reorderTheses,
    updateProofPoint,
    uploadAttachment,
    deleteAttachment,
    setCurrentlyTesting
  };
};