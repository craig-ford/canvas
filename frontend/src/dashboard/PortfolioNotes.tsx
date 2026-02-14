import React, { useState, useCallback } from 'react';

interface User {
  id: string;
  name: string;
  role: string;
}

interface UseAuthResult {
  user: User | null;
  isAuthenticated: boolean;
}

// Mock useAuth hook - will be replaced with actual implementation
const useAuth = (): UseAuthResult => ({
  user: { id: '1', name: 'Test User', role: 'viewer' },
  isAuthenticated: true
});

// Mock debounce function - will be replaced with actual lodash.debounce
const debounce = (fn: Function, delay: number) => {
  let timeoutId: NodeJS.Timeout;
  return (...args: any[]) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};

// Mock API client - will be replaced with actual implementation
const api = {
  patch: async (url: string, data: any) => {
    // Simulate API call
    return { data: { success: true } };
  }
};

type SaveStatus = 'saved' | 'saving' | 'error';

export const PortfolioNotes: React.FC = () => {
  const { user } = useAuth();
  const [notes, setNotes] = useState('');
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('saved');

  // Debounced autosave function
  const debouncedSave = useCallback(
    debounce(async (value: string) => {
      if (user?.role !== 'admin') return;

      setSaveStatus('saving');
      try {
        await api.patch('/portfolio/notes', { notes: value });
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
  if (user?.role !== 'admin') return null;

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