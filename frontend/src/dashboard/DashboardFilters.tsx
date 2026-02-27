import React, { useState } from 'react';
import { FunnelIcon, ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

interface FilterState {
  lanes: string[];
  gmIds: string[];
  healthStatuses: string[];
  vbuIds: string[];
}

interface VBUOption {
  id: string;
  name: string;
}

interface DashboardFiltersProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  vbuOptions?: VBUOption[];
}

export const DashboardFilters: React.FC<DashboardFiltersProps> = ({ filters, onFiltersChange, vbuOptions = [] }) => {
  const [open, setOpen] = useState(true);
  const activeCount = filters.lanes.length + filters.gmIds.length + filters.healthStatuses.length + filters.vbuIds.length;

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="flex flex-col items-center gap-1 p-2 bg-white rounded-lg border border-neutral-100 hover:bg-gray-50"
        title="Show filters"
      >
        <FunnelIcon className="h-5 w-5 text-gray-500" />
        {activeCount > 0 && (
          <span className="bg-primary text-white text-xs rounded-full px-1.5 py-0.5 leading-none">{activeCount}</span>
        )}
        <ChevronRightIcon className="h-3 w-3 text-gray-400" />
      </button>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-neutral-100 w-48 shrink-0">
      <div className="flex items-center justify-between p-3 border-b border-neutral-50">
        <span className="flex items-center gap-1.5 text-sm font-medium text-gray-700">
          <FunnelIcon className="h-4 w-4" />
          Filters
          {activeCount > 0 && (
            <span className="bg-primary text-white text-xs rounded-full px-1.5 py-0.5 leading-none">{activeCount}</span>
          )}
        </span>
        <button onClick={() => setOpen(false)} className="p-0.5 hover:bg-gray-100 rounded" title="Collapse filters">
          <ChevronLeftIcon className="h-4 w-4 text-gray-400" />
        </button>
      </div>

      <div className="p-3 space-y-4">
        <div>
          <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1.5">Lane</label>
          <div className="space-y-1">
            {['build', 'sell', 'milk', 'reframe'].map(lane => (
              <label key={lane} className="flex items-center gap-2 text-sm cursor-pointer hover:bg-gray-50 rounded px-1 py-0.5">
                <input
                  type="checkbox"
                  checked={filters.lanes.includes(lane)}
                  onChange={(e) => {
                    const newLanes = e.target.checked
                      ? [...filters.lanes, lane]
                      : filters.lanes.filter(l => l !== lane);
                    onFiltersChange({ ...filters, lanes: newLanes });
                  }}
                  className="rounded border-gray-300 text-primary focus:ring-primary h-3.5 w-3.5"
                />
                <span className="capitalize">{lane}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1.5">Health</label>
          <div className="space-y-1">
            {['On Track', 'At Risk', 'Behind'].map(status => (
              <label key={status} className="flex items-center gap-2 text-sm cursor-pointer hover:bg-gray-50 rounded px-1 py-0.5">
                <input
                  type="checkbox"
                  checked={filters.healthStatuses.includes(status)}
                  onChange={(e) => {
                    const newStatuses = e.target.checked
                      ? [...filters.healthStatuses, status]
                      : filters.healthStatuses.filter(s => s !== status);
                    onFiltersChange({ ...filters, healthStatuses: newStatuses });
                  }}
                  className="rounded border-gray-300 text-primary focus:ring-primary h-3.5 w-3.5"
                />
                <span>{status}</span>
              </label>
            ))}
          </div>
        </div>

        {vbuOptions.length > 1 && (
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1.5">VBU</label>
            <div className="space-y-1 max-h-40 overflow-y-auto">
              {vbuOptions.map(vbu => (
                <label key={vbu.id} className="flex items-center gap-2 text-sm cursor-pointer hover:bg-gray-50 rounded px-1 py-0.5">
                  <input
                    type="checkbox"
                    checked={filters.vbuIds.includes(vbu.id)}
                    onChange={(e) => {
                      const newIds = e.target.checked
                        ? [...filters.vbuIds, vbu.id]
                        : filters.vbuIds.filter(id => id !== vbu.id);
                      onFiltersChange({ ...filters, vbuIds: newIds });
                    }}
                    className="rounded border-gray-300 text-primary focus:ring-primary h-3.5 w-3.5"
                  />
                  <span className="truncate" title={vbu.name}>{vbu.name}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {activeCount > 0 && (
          <button
            onClick={() => onFiltersChange({ lanes: [], gmIds: [], healthStatuses: [], vbuIds: [] })}
            className="text-xs text-gray-500 hover:text-gray-700 underline"
          >
            Clear all
          </button>
        )}
      </div>
    </div>
  );
};
