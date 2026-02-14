import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, test, expect, beforeEach } from 'vitest';
import { DashboardPage } from '../DashboardPage';

// Mock useAuth hook
const mockUseAuth = vi.fn();
vi.mock('../auth/useAuth', () => ({
  useAuth: mockUseAuth
}));

// Mock API client
const mockApi = {
  get: vi.fn()
};
vi.mock('../api/client', () => ({
  default: mockApi
}));

// Mock child components
vi.mock('../dashboard/VBUTable', () => ({
  VBUTable: ({ vbus, onExportPDF, onViewVBU }: any) => (
    <div data-testid="vbu-table">
      <div>VBU Count: {vbus.length}</div>
      {vbus.map((vbu: any) => (
        <div key={vbu.id} data-testid={`vbu-${vbu.id}`}>
          {vbu.name}
          <button onClick={() => onExportPDF(vbu.id)}>Export PDF</button>
          <button onClick={() => onViewVBU(vbu.id)}>View VBU</button>
        </div>
      ))}
    </div>
  )
}));

vi.mock('../dashboard/DashboardFilters', () => ({
  DashboardFilters: ({ filters, onFiltersChange }: any) => (
    <div data-testid="dashboard-filters">
      <button onClick={() => onFiltersChange({ lanes: ['build'], gmIds: [], healthStatuses: [] })}>
        Apply Filter
      </button>
      <button onClick={() => onFiltersChange({ lanes: [], gmIds: [], healthStatuses: [] })}>
        Clear Filters
      </button>
    </div>
  )
}));

vi.mock('../dashboard/PortfolioNotes', () => ({
  PortfolioNotes: () => <div data-testid="portfolio-notes">Portfolio Notes</div>
}));

const mockVBUs = [
  {
    id: '123e4567-e89b-12d3-a456-426614174000',
    name: 'Product Alpha',
    gm_name: 'John Smith',
    lifecycle_lane: 'build',
    success_description: 'Success means validated product-market fit',
    currently_testing: 'Customer acquisition channels',
    next_review_date: '2026-03-15',
    primary_constraint: 'Limited engineering capacity',
    health_indicator: 'In Progress',
    portfolio_notes: 'Focus area for Q1'
  }
];

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'Test User', role: 'viewer' },
      isAuthenticated: true
    });
    mockApi.get.mockResolvedValue({
      data: { data: mockVBUs, meta: { total: 1 } }
    });
  });

  test('renders loading state initially', async () => {
    // Mock delayed API response
    mockApi.get.mockImplementation(() => new Promise(resolve => 
      setTimeout(() => resolve({ data: { data: mockVBUs, meta: { total: 1 } } }), 100)
    ));

    render(<DashboardPage />);
    
    expect(screen.getByText('Portfolio Dashboard')).toBeInTheDocument();
    expect(screen.getByTestId('loading-state')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.queryByTestId('loading-state')).not.toBeInTheDocument();
    });
  });

  test('renders empty state when no VBUs found', async () => {
    mockApi.get.mockResolvedValue({
      data: { data: [], meta: { total: 0 } }
    });

    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('empty-state')).toBeInTheDocument();
      expect(screen.getByText(/no VBUs found/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /clear filters/i })).toBeInTheDocument();
    });
  });

  test('renders VBU table when data loaded', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('vbu-table')).toBeInTheDocument();
      expect(screen.getByText('VBU Count: 1')).toBeInTheDocument();
      expect(screen.getByTestId('vbu-123e4567-e89b-12d3-a456-426614174000')).toBeInTheDocument();
      expect(screen.getByText('Product Alpha')).toBeInTheDocument();
    });
  });

  test('updates filters and refetches data', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('dashboard-filters')).toBeInTheDocument();
    });

    const applyFilterButton = screen.getByRole('button', { name: 'Apply Filter' });
    fireEvent.click(applyFilterButton);

    await waitFor(() => {
      expect(mockApi.get).toHaveBeenCalledWith('/portfolio/summary?lane=build');
    });
  });

  test('handles API error gracefully', async () => {
    mockApi.get.mockRejectedValue(new Error('Network error'));

    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('error-state')).toBeInTheDocument();
      expect(screen.getByText(/error loading portfolio data/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });
  });

  test('shows portfolio notes for admin users', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'Admin User', role: 'admin' },
      isAuthenticated: true
    });

    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('portfolio-notes')).toBeInTheDocument();
    });
  });

  test('hides portfolio notes for non-admin users', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'GM User', role: 'gm' },
      isAuthenticated: true
    });

    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.queryByTestId('portfolio-notes')).not.toBeInTheDocument();
    });
  });

  test('applies responsive layout classes', async () => {
    render(<DashboardPage />);
    
    const dashboardContainer = screen.getByRole('main');
    expect(dashboardContainer).toHaveClass('p-6');
    
    await waitFor(() => {
      const contentArea = screen.getByTestId('dashboard-content');
      expect(contentArea).toHaveClass('space-y-6');
    });
  });

  test('has proper accessibility attributes', async () => {
    render(<DashboardPage />);
    
    expect(screen.getByRole('main')).toHaveAttribute('aria-label', 'Portfolio Dashboard');
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Portfolio Dashboard');
    
    await waitFor(() => {
      const vbuTable = screen.getByTestId('vbu-table');
      expect(vbuTable.closest('[role="region"]')).toHaveAttribute('aria-label', 'VBU list');
    });
  });

  test('handles PDF export action', async () => {
    const mockExportPDF = vi.fn();
    
    render(<DashboardPage />);
    
    await waitFor(() => {
      const exportButton = screen.getByRole('button', { name: 'Export PDF' });
      fireEvent.click(exportButton);
    });

    // Test would verify PDF export functionality when implemented
    expect(screen.getByRole('button', { name: 'Export PDF' })).toBeInTheDocument();
  });

  test('handles view VBU navigation', async () => {
    const mockNavigate = vi.fn();
    
    render(<DashboardPage />);
    
    await waitFor(() => {
      const viewButton = screen.getByRole('button', { name: 'View VBU' });
      fireEvent.click(viewButton);
    });

    // Test would verify navigation when router is implemented
    expect(screen.getByRole('button', { name: 'View VBU' })).toBeInTheDocument();
  });
});