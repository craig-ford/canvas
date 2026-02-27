import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';
import { usePortfolio } from './hooks/usePortfolio';
import { DashboardFilters } from './DashboardFilters';
import VBUTable from './VBUTable';
import { PortfolioNotes } from './PortfolioNotes';
import { ThesisHealthTile } from './ThesisHealthTile';

import { exportCanvasPdf } from '../utils/exportPdf';

interface FilterState {
  lanes: string[];
  gmIds: string[];
  healthStatuses: string[];
  vbuIds: string[];
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
    healthStatuses: searchParams.get('healthStatuses')?.split(',').filter(Boolean) || [],
    vbuIds: searchParams.get('vbuIds')?.split(',').filter(Boolean) || []
  });

  const { vbus, loading, error, refetch } = usePortfolio(filters);

  // GMs with a single VBU go straight to their canvas
  useEffect(() => {
    if (!loading && user?.role === 'gm' && vbus.length === 1) {
      navigate(`/vbus/${vbus[0].id}/canvas`, { replace: true });
    }
  }, [loading, user, vbus, navigate]);

  // Build VBU options for filter (from all VBUs the user can see)
  const vbuOptions = vbus.map(v => ({ id: v.id, name: v.name }));

  // Filter VBU table by selected VBU IDs
  const filteredVbus = filters.vbuIds.length > 0
    ? vbus.filter(v => filters.vbuIds.includes(v.id))
    : vbus;

  // Sync filters with URL parameters
  useEffect(() => {
    const params = new URLSearchParams();
    if (filters.lanes.length) params.set('lanes', filters.lanes.join(','));
    if (filters.gmIds.length) params.set('gmIds', filters.gmIds.join(','));
    if (filters.healthStatuses.length) params.set('healthStatuses', filters.healthStatuses.join(','));
    if (filters.vbuIds.length) params.set('vbuIds', filters.vbuIds.join(','));
    setSearchParams(params);
  }, [filters, setSearchParams]);

  const handleFiltersChange = (newFilters: FilterState) => {
    setFilters(newFilters);
  };

  const handleClearFilters = () => {
    setFilters({ lanes: [], gmIds: [], healthStatuses: [], vbuIds: [] });
  };

  const handleExportPDF = (vbuId: string) => {
    exportCanvasPdf(vbuId);
  };

  const handleViewVBU = (vbuId: string) => {
    navigate(`/vbus/${vbuId}/canvas`);
  };

  if (loading) {
    return (
      <main className="p-6" aria-label="Portfolio Dashboard">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-navy mb-6">Portfolio Dashboard</h1>
          <div data-testid="loading-state" className="flex items-center justify-center h-64">
            <div className="animate-pulse space-y-4 w-full">
              <div className="h-4 bg-neutral-100 rounded w-1/4"></div>
              <div className="space-y-2">
                <div className="h-4 bg-neutral-100 rounded"></div>
                <div className="h-4 bg-neutral-100 rounded w-5/6"></div>
                <div className="h-4 bg-neutral-100 rounded w-4/6"></div>
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
          <h1 className="text-2xl font-bold text-navy mb-6">Portfolio Dashboard</h1>
          <div data-testid="error-state" className="text-center py-12">
            <p className="text-neutral-800 font-medium mb-2">Error loading portfolio data</p>
            <p className="text-neutral-500 mb-4">Please try again or contact support if the problem persists.</p>
            <button
              onClick={refetch}
              className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-lg text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </main>
    );
  }

  if (filteredVbus.length === 0 && vbus.length === 0) {
    return (
      <main className="p-6" aria-label="Portfolio Dashboard">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-navy mb-6">Portfolio Dashboard</h1>
          
          <div className="flex gap-4">
            <DashboardFilters filters={filters} onFiltersChange={handleFiltersChange} vbuOptions={vbuOptions} />
            <div className="flex-1 min-w-0">
              <div data-testid="empty-state" className="text-center py-12">
                <p className="text-neutral-800 font-medium mb-2">No VBUs found</p>
                <p className="text-neutral-500 mb-4">Try adjusting your filters or check back later.</p>
                <button
                  onClick={handleClearFilters}
                  className="inline-flex items-center px-4 py-2 border border-neutral-100 text-sm font-medium rounded-lg text-neutral-800 bg-white hover:bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="p-6" aria-label="Portfolio Dashboard">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold text-navy mb-6">Portfolio Dashboard</h1>
        
        <div data-testid="dashboard-content" className="flex gap-4">
          {/* Left sidebar — filters */}
          <DashboardFilters filters={filters} onFiltersChange={handleFiltersChange} vbuOptions={vbuOptions} />

          {/* Main content */}
          <div className="flex-1 min-w-0 space-y-6">
            <div role="region" aria-label="VBU list" className="bg-white rounded-lg border border-neutral-100">
              <VBUTable 
                vbus={filteredVbus}
                onExportPDF={handleExportPDF}
                onViewVBU={handleViewVBU}
              />
            </div>

            <ThesisHealthTile vbuIds={filters.vbuIds} />

            {(user?.role === 'admin' || user?.role === 'group_leader') && <PortfolioNotes />}
          </div>
        </div>
      </div>
    </main>
  );
};