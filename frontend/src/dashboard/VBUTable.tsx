import React, { useState, useMemo } from 'react';
import HealthIndicator from './HealthIndicator';

interface VBUSummary {
  id: string;
  name: string;
  gm_name: string;
  lifecycle_lane: 'build' | 'sell' | 'milk' | 'reframe';
  success_description: string | null;
  currently_testing: string | null;
  next_review_date: string | null;
  primary_constraint: string | null;
  health_indicator: string;
  portfolio_notes: string | null;
}

interface VBUTableProps {
  vbus: VBUSummary[];
  onExportPDF: (vbuId: string) => void;
  onViewVBU: (vbuId: string) => void;
}

interface SortConfig {
  key: keyof VBUSummary;
  direction: 'asc' | 'desc';
}

const VBUTable: React.FC<VBUTableProps> = ({ vbus, onExportPDF, onViewVBU }) => {
  const [sortConfig, setSortConfig] = useState<SortConfig | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 25;

  const sortedVBUs = useMemo(() => {
    if (!sortConfig) return vbus;

    return [...vbus].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      if (aValue === null && bValue === null) return 0;
      if (aValue === null) return 1;
      if (bValue === null) return -1;

      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [vbus, sortConfig]);

  const paginatedVBUs = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return sortedVBUs.slice(startIndex, startIndex + itemsPerPage);
  }, [sortedVBUs, currentPage]);

  const totalPages = Math.ceil(vbus.length / itemsPerPage);

  const handleSort = (key: keyof VBUSummary) => {
    setSortConfig(current => ({
      key,
      direction: current?.key === key && current.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const getSortIndicator = (key: keyof VBUSummary) => {
    if (!sortConfig || sortConfig.key !== key) return '';
    return sortConfig.direction === 'asc' ? ' ↑' : ' ↓';
  };

  if (vbus.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No VBUs found
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200" aria-label="VBU portfolio table">
        <thead className="bg-gray-50">
          <tr>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              onClick={() => handleSort('name')}
              aria-sort={sortConfig?.key === 'name' ? sortConfig.direction : undefined}
            >
              VBU Name{getSortIndicator('name')}
            </th>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              onClick={() => handleSort('lifecycle_lane')}
              aria-sort={sortConfig?.key === 'lifecycle_lane' ? sortConfig.direction : undefined}
            >
              Lane{getSortIndicator('lifecycle_lane')}
            </th>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              onClick={() => handleSort('gm_name')}
              aria-sort={sortConfig?.key === 'gm_name' ? sortConfig.direction : undefined}
            >
              GM{getSortIndicator('gm_name')}
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Testing
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Next Review
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Health
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {paginatedVBUs.map((vbu, index) => (
            <tr 
              key={vbu.id} 
              className="hover:bg-gray-50 focus-within:bg-gray-50 focus:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onViewVBU(vbu.id);
                }
              }}
              aria-label={`VBU: ${vbu.name}, GM: ${vbu.gm_name}, Lane: ${vbu.lifecycle_lane}, Health: ${vbu.health_indicator}${vbu.currently_testing ? `, Testing: ${vbu.currently_testing}` : ''}${vbu.next_review_date ? `, Next Review: ${vbu.next_review_date}` : ''}`}
            >
              <td className="px-6 py-4 whitespace-nowrap">
                <div>
                  <div className="text-sm font-medium text-gray-900">{vbu.name}</div>
                  {vbu.success_description && (
                    <div className="text-sm text-gray-500 truncate max-w-xs">
                      {vbu.success_description}
                    </div>
                  )}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  vbu.lifecycle_lane === 'build' ? 'bg-blue-100 text-blue-800' :
                  vbu.lifecycle_lane === 'sell' ? 'bg-green-100 text-green-800' :
                  vbu.lifecycle_lane === 'milk' ? 'bg-purple-100 text-purple-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {vbu.lifecycle_lane.toUpperCase()}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {vbu.gm_name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {vbu.currently_testing || '—'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {vbu.next_review_date || '—'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <HealthIndicator status={vbu.health_indicator} />
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onViewVBU(vbu.id)}
                    className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-lg text-white bg-primary hover:bg-primary-dark transition-colors"
                  >
                    View
                  </button>
                  <button
                    onClick={() => onExportPDF(vbu.id)}
                    className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-lg text-primary border border-primary hover:bg-primary hover:text-white transition-colors"
                  >
                    Export PDF
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 bg-white border-t border-gray-200 sm:px-6">
          <div className="flex justify-between flex-1 sm:hidden">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="relative inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="relative ml-3 inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
          <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Showing <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span> to{' '}
                <span className="font-medium">
                  {Math.min(currentPage * itemsPerPage, vbus.length)}
                </span>{' '}
                of <span className="font-medium">{vbus.length}</span> VBUs
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`relative inline-flex items-center px-4 py-2 text-sm font-medium ${
                      page === currentPage
                        ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600'
                        : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                    } border`}
                  >
                    {page}
                  </button>
                ))}
                {currentPage < totalPages && (
                  <button
                    onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                    className="relative inline-flex items-center px-2 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-r-md hover:bg-gray-50"
                  >
                    Next
                  </button>
                )}
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VBUTable;