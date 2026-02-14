import { useState, useEffect } from 'react';
import { apiClient } from '../../api/client';

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

interface UsePortfolioResult {
  vbus: VBUSummary[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export const usePortfolio = (filters: FilterState): UsePortfolioResult => {
  const [vbus, setVBUs] = useState<VBUSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPortfolio = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (filters.lanes.length) params.set('lane', filters.lanes.join(','));
      if (filters.gmIds.length) params.set('gm_id', filters.gmIds.join(','));
      if (filters.healthStatuses.length) params.set('health_status', filters.healthStatuses.join(','));
      
      const response = await apiClient.get(`/portfolio/summary?${params.toString()}`);
      setVBUs(response.data.data);
    } catch (err) {
      setError('Error loading portfolio data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolio();
  }, [filters.lanes, filters.gmIds, filters.healthStatuses]);

  return {
    vbus,
    loading,
    error,
    refetch: fetchPortfolio
  };
};