import React, { useState, useEffect } from 'react';

interface VBUSummary {
  id: string;
  name: string;
  gm_name: string;
  lifecycle_lane: string;
  success_description?: string;
  currently_testing?: string;
  next_review_date?: string;
  primary_constraint?: string;
  health_indicator: string;
  portfolio_notes?: string;
}

interface FilterState {
  lanes: string[];
  gmIds: string[];
  healthStatuses: string[];
}

export const DashboardPage: React.FC = () => {
  const [vbus, setVBUs] = useState<VBUSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterState>({
    lanes: [],
    gmIds: [],
    healthStatuses: []
  });

  // Mock useAuth hook result
  const user = { id: '1', name: 'Test User', role: 'viewer' };

  useEffect(() => {
    const fetchPortfolio = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Mock API call - will be replaced with actual implementation
        const params = new URLSearchParams();
        if (filters.lanes.length) params.set('lane', filters.lanes.join(','));
        if (filters.gmIds.length) params.set('gm_id', filters.gmIds.join(','));
        if (filters.healthStatuses.length) params.set('health_status', filters.healthStatuses.join(','));
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 100));
        setVBUs([]);
      } catch (err) {
        setError('Error loading portfolio data');
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolio();
  }, [filters]);

  const handleFiltersChange = (newFilters: FilterState) => {
    setFilters(newFilters);
  };

  const handleExportPDF = (vbuId: string) => {
    // PDF export functionality will be implemented
    console.log('Export PDF for VBU:', vbuId);
  };

  const handleViewVBU = (vbuId: string) => {
    // Navigation functionality will be implemented
    console.log('View VBU:', vbuId);
  };

  const handleClearFilters = () => {
    setFilters({ lanes: [], gmIds: [], healthStatuses: [] });
  };

  if (loading) {
    return (
      <main className="p-6" aria-label="Portfolio Dashboard">
        <h1 className="text-2xl font-bold mb-6">Portfolio Dashboard</h1>
        <div data-testid="loading-state">Loading...</div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="p-6" aria-label="Portfolio Dashboard">
        <h1 className="text-2xl font-bold mb-6">Portfolio Dashboard</h1>
        <div data-testid="error-state">
          <p>Error loading portfolio data</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </main>
    );
  }

  if (vbus.length === 0) {
    return (
      <main className="p-6" aria-label="Portfolio Dashboard">
        <h1 className="text-2xl font-bold mb-6">Portfolio Dashboard</h1>
        <div data-testid="empty-state">
          <p>No VBUs found</p>
          <button onClick={handleClearFilters}>Clear Filters</button>
        </div>
      </main>
    );
  }

  return (
    <main className="p-6" aria-label="Portfolio Dashboard">
      <h1 className="text-2xl font-bold mb-6">Portfolio Dashboard</h1>
      
      <div data-testid="dashboard-content" className="space-y-6">
        <div data-testid="dashboard-filters">
          <button onClick={() => handleFiltersChange({ lanes: ['build'], gmIds: [], healthStatuses: [] })}>
            Apply Filter
          </button>
          <button onClick={() => handleFiltersChange({ lanes: [], gmIds: [], healthStatuses: [] })}>
            Clear Filters
          </button>
        </div>

        <div role="region" aria-label="VBU list">
          <div data-testid="vbu-table">
            <div>VBU Count: {vbus.length}</div>
            {vbus.map((vbu) => (
              <div key={vbu.id} data-testid={`vbu-${vbu.id}`}>
                {vbu.name}
                <button onClick={() => handleExportPDF(vbu.id)}>Export PDF</button>
                <button onClick={() => handleViewVBU(vbu.id)}>View VBU</button>
              </div>
            ))}
          </div>
        </div>

        {user.role === 'admin' && (
          <div data-testid="portfolio-notes">Portfolio Notes</div>
        )}
      </div>
    </main>
  );
};