import React from 'react';

interface FilterState {
  lanes: string[];
  gmIds: string[];
  healthStatuses: string[];
}

interface DashboardFiltersProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
}

export const DashboardFilters: React.FC<DashboardFiltersProps> = ({ filters, onFiltersChange }) => {
  return (
    <div className="bg-white p-4 rounded-lg border space-y-4">
      <h3 className="font-medium text-gray-900">Filters</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Lifecycle Lanes</label>
          <div className="space-y-2">
            {['build', 'sell', 'milk', 'reframe'].map(lane => (
              <label key={lane} className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.lanes.includes(lane)}
                  onChange={(e) => {
                    const newLanes = e.target.checked
                      ? [...filters.lanes, lane]
                      : filters.lanes.filter(l => l !== lane);
                    onFiltersChange({ ...filters, lanes: newLanes });
                  }}
                  className="mr-2"
                />
                <span className="text-sm capitalize">{lane}</span>
              </label>
            ))}
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Health Status</label>
          <div className="space-y-2">
            {['On Track', 'At Risk', 'Behind'].map(status => (
              <label key={status} className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.healthStatuses.includes(status)}
                  onChange={(e) => {
                    const newStatuses = e.target.checked
                      ? [...filters.healthStatuses, status]
                      : filters.healthStatuses.filter(s => s !== status);
                    onFiltersChange({ ...filters, healthStatuses: newStatuses });
                  }}
                  className="mr-2"
                />
                <span className="text-sm">{status}</span>
              </label>
            ))}
          </div>
        </div>
        
        <div className="flex items-end">
          <button
            onClick={() => onFiltersChange({ lanes: [], gmIds: [], healthStatuses: [] })}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
          >
            Clear All Filters
          </button>
        </div>
      </div>
    </div>
  );
};