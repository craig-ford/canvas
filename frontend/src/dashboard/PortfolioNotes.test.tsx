import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, test, expect, beforeEach } from 'vitest';
import { PortfolioNotes } from '../PortfolioNotes';

// Mock useAuth hook
const mockUseAuth = vi.fn();
vi.mock('../auth/useAuth', () => ({
  useAuth: mockUseAuth
}));

// Mock API client
const mockApi = {
  patch: vi.fn()
};
vi.mock('../api/client', () => ({
  default: mockApi
}));

// Mock debounce utility
const mockDebounce = vi.fn((fn, delay) => {
  let timeoutId: NodeJS.Timeout;
  return (...args: any[]) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
});
vi.mock('lodash.debounce', () => ({
  default: mockDebounce
}));

describe('PortfolioNotes', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.patch.mockResolvedValue({ data: { success: true } });
  });

  test('renders nothing for non-admin users', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'GM User', role: 'gm' },
      isAuthenticated: true
    });

    const { container } = render(<PortfolioNotes />);
    
    expect(container.firstChild).toBeNull();
  });

  test('renders textarea and save status for admin users', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'Admin User', role: 'admin' },
      isAuthenticated: true
    });

    render(<PortfolioNotes />);
    
    expect(screen.getByRole('region', { name: /portfolio notes/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Portfolio Notes');
    expect(screen.getByRole('textbox', { name: /portfolio notes/i })).toBeInTheDocument();
    expect(screen.getByText(/saved/i)).toBeInTheDocument();
  });

  test('calls API with debounced autosave on text change', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'Admin User', role: 'admin' },
      isAuthenticated: true
    });

    render(<PortfolioNotes />);
    
    const textarea = screen.getByRole('textbox', { name: /portfolio notes/i });
    
    fireEvent.change(textarea, { target: { value: 'New portfolio notes' } });
    
    // Wait for debounce delay (500ms)
    await waitFor(() => {
      expect(mockApi.patch).toHaveBeenCalledWith('/portfolio/notes', {
        notes: 'New portfolio notes'
      });
    }, { timeout: 1000 });
  });

  test('shows saving status during API call', async () => {
    // Mock API with delayed response
    mockApi.patch.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ data: { success: true } }), 200))
    );

    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'Admin User', role: 'admin' },
      isAuthenticated: true
    });

    render(<PortfolioNotes />);
    
    const textarea = screen.getByRole('textbox', { name: /portfolio notes/i });
    
    fireEvent.change(textarea, { target: { value: 'New notes' } });
    
    // Should show saving status
    await waitFor(() => {
      expect(screen.getByText(/saving/i)).toBeInTheDocument();
    });
    
    // Should show saved status after API completes
    await waitFor(() => {
      expect(screen.getByText(/saved/i)).toBeInTheDocument();
    }, { timeout: 1000 });
  });

  test('shows error status on API failure', async () => {
    mockApi.patch.mockRejectedValue(new Error('Network error'));

    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'Admin User', role: 'admin' },
      isAuthenticated: true
    });

    render(<PortfolioNotes />);
    
    const textarea = screen.getByRole('textbox', { name: /portfolio notes/i });
    
    fireEvent.change(textarea, { target: { value: 'New notes' } });
    
    await waitFor(() => {
      expect(screen.getByText(/error saving/i)).toBeInTheDocument();
    }, { timeout: 1000 });
  });

  test('respects maxLength constraint', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'Admin User', role: 'admin' },
      isAuthenticated: true
    });

    render(<PortfolioNotes />);
    
    const textarea = screen.getByRole('textbox', { name: /portfolio notes/i });
    
    expect(textarea).toHaveAttribute('maxLength', '10000');
  });

  test('has proper accessibility attributes', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'Admin User', role: 'admin' },
      isAuthenticated: true
    });

    render(<PortfolioNotes />);
    
    const region = screen.getByRole('region', { name: /portfolio notes/i });
    expect(region).toBeInTheDocument();
    
    const textarea = screen.getByRole('textbox', { name: /portfolio notes/i });
    expect(textarea).toHaveAttribute('aria-label', 'Portfolio notes (admin only)');
    expect(textarea).toHaveAttribute('aria-describedby', 'notes-status');
    
    const status = screen.getByText(/saved/i);
    expect(status).toHaveAttribute('id', 'notes-status');
    expect(status).toHaveAttribute('aria-live', 'polite');
  });

  test('initializes with empty notes', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'Admin User', role: 'admin' },
      isAuthenticated: true
    });

    render(<PortfolioNotes />);
    
    const textarea = screen.getByRole('textbox', { name: /portfolio notes/i });
    expect(textarea).toHaveValue('');
  });

  test('updates textarea value on user input', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'Admin User', role: 'admin' },
      isAuthenticated: true
    });

    render(<PortfolioNotes />);
    
    const textarea = screen.getByRole('textbox', { name: /portfolio notes/i });
    
    fireEvent.change(textarea, { target: { value: 'Test notes' } });
    
    expect(textarea).toHaveValue('Test notes');
  });

  test('has correct placeholder text', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'Admin User', role: 'admin' },
      isAuthenticated: true
    });

    render(<PortfolioNotes />);
    
    const textarea = screen.getByRole('textbox', { name: /portfolio notes/i });
    expect(textarea).toHaveAttribute('placeholder', 'Add portfolio-level notes...');
  });

  test('applies correct CSS classes', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'Admin User', role: 'admin' },
      isAuthenticated: true
    });

    render(<PortfolioNotes />);
    
    const textarea = screen.getByRole('textbox', { name: /portfolio notes/i });
    expect(textarea).toHaveClass('w-full', 'h-32', 'p-3', 'border', 'rounded-md');
  });
});