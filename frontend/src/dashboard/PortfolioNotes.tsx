import React, { useState, useCallback } from 'react';
import { useAuth } from '../auth/useAuth';
import { apiClient } from '../api/client';

// Simple debounce utility since lodash is not available
const debounce = (fn: Function, delay: number) => {
  let timeoutId: NodeJS.Timeout;
  return (...args: any[]) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};

type SaveStatus = 'saved' | 'saving' | 'error';

export const PortfolioNotes: React.FC = () => {
  const { user } = useAuth();
  const [notes, setNotes] = useState('');
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('saved');

  // Debounced autosave function
  const debouncedSave = useCallback(
    debounce(async (value: string) => {
      if (user?.role !== 'admin' && user?.role !== 'group_leader') return;

      setSaveStatus('saving');
      try {
        await apiClient.patch('/portfolio/notes', { notes: value });
        setSaveStatus('saved');
      } catch (error) {
        setSaveStatus('error');
      }
    }, 500),
    [user]
  );

  const handleNotesChange = (value: string) => {
    setNotes(value);
    debouncedSave(value);
  };

  // Don't render for non-admin users
  if (user?.role !== 'admin' && user?.role !== 'group_leader') return null;

  return (
    <div className="mt-6" role="region" aria-label="Portfolio notes">
      <h2 className="text-lg font-semibold mb-2">Portfolio Notes</h2>
      <textarea
        value={notes}
        onChange={(e) => handleNotesChange(e.target.value)}
        className="w-full h-32 p-3 border rounded-md"
        placeholder="Add portfolio-level notes..."
        aria-label="Portfolio notes (admin only)"
        aria-describedby="notes-status"
        maxLength={10000}
      />
      <div id="notes-status" aria-live="polite" className="text-sm text-gray-500 mt-1">
        {saveStatus === 'saved' && '✓ Saved'}
        {saveStatus === 'saving' && '⟳ Saving...'}
        {saveStatus === 'error' && '⚠ Error saving'}
      </div>
    </div>
  );
};