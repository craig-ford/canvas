import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';
import { usePortfolio } from './hooks/usePortfolio';
import { DashboardFilters } from './DashboardFilters';
import VBUTable from './VBUTable';
import { PortfolioNotes } from './PortfolioNotes';

interface FilterState {
  lanes: string[];
  gmIds: string[];
  healthStatuses: string[];
}

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

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  const [filters, setFilters] = useState<FilterState>({
    lanes: searchParams.get('lanes')?.split(',').filter(Boolean) || [],
    gmIds: searchParams.get('gmIds')?.split(',').filter(Boolean) || [],
    healthStatuses: searchParams.get('healthStatuses')?.split(',').filter(Boolean) || []
  });

  const { vbus, loading, error, refetch } = usePortfolio(filters);

  // Sync filters with URL parameters
  useEffect(() => {
    const params = new URLSearchParams();
    if (filters.lanes.length) params.set('lanes', filters.lanes.join(','));
    if (filters.gmIds.length) params.set('gmIds', filters.gmIds.join(','));
    if (filters.healthStatuses.length) params.set('healthStatuses', filters.healthStatuses.join(','));
    setSearchParams(params);
  }, [filters, setSearchParams]);

  const handleFiltersChange = (newFilters: FilterState) => {
    setFilters(newFilters);
  };

  const handleClearFilters = () => {
    setFilters({ lanes: [], gmIds: [], healthStatuses: [] });
  };

  const handleExportPDF = (vbuId: string) => {
    // PDF export functionality will be implemented
    console.log('Export PDF for VBU:', vbuId);
  };

  const handleViewVBU = (vbuId: string) => {
    navigate(`/vbus/${vbuId}`);
  };

  if (loading) {
    return (
      <main className="p-6" aria-label="Portfolio Dashboard">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Portfolio Dashboard</h1>
          <div data-testid="loading-state" className="flex items-center justify-center h-64">
            <div className="animate-pulse space-y-4 w-full">
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
              <div className="space-y-2">
                <div className="h-4 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                <div className="h-4 bg-gray-200 rounded w-4/6"></div>
              </div>
            </div>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="p-6" aria-label="Portfolio Dashboard">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Portfolio Dashboard</h1>
          <div data-testid="error-state" className="text-center py-12">
            <div className="text-red-600 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <p className="text-gray-900 font-medium mb-2">Error loading portfolio data</p>
            <p className="text-gray-500 mb-4">Please try again or contact support if the problem persists.</p>
            <button
              onClick={refetch}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Retry
            </button>
          </div>
        </div>
      </main>
    );
  }

  if (vbus.length === 0) {
    return (
      <main className="p-6" aria-label="Portfolio Dashboard">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Portfolio Dashboard</h1>
          
          <div className="space-y-6">
            <DashboardFilters filters={filters} onFiltersChange={handleFiltersChange} />
            
            <div data-testid="empty-state" className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <p className="text-gray-900 font-medium mb-2">No VBUs found</p>
              <p className="text-gray-500 mb-4">Try adjusting your filters or check back later.</p>
              <button
                onClick={handleClearFilters}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="p-6" aria-label="Portfolio Dashboard">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Portfolio Dashboard</h1>
        
        <div data-testid="dashboard-content" className="space-y-6">
          <DashboardFilters filters={filters} onFiltersChange={handleFiltersChange} />
          
          <div role="region" aria-label="VBU list" className="bg-white rounded-lg border">
            <VBUTable 
              vbus={vbus}
              onExportPDF={handleExportPDF}
              onViewVBU={handleViewVBU}
            />
          </div>

          {user?.role === 'admin' && <PortfolioNotes />}
        </div>
      </div>
    </main>
  );
};