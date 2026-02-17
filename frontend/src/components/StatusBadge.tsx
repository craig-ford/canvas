import React, { useState, useRef, useEffect } from 'react';
import { ChevronDownIcon } from '@heroicons/react/20/solid';

interface StatusBadgeProps {
  status: 'not_started' | 'in_progress' | 'observed' | 'stalled';
  onChange?: (status: string) => void;
  readonly?: boolean;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status, onChange, readonly = false }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const statusConfig = {
    not_started: { color: 'bg-gray-100 text-gray-800', text: 'Not Started' },
    in_progress: { color: 'bg-teal-100 text-teal-800', text: 'In Progress' },
    observed: { color: 'bg-green-100 text-green-800', text: 'Observed' },
    stalled: { color: 'bg-yellow-100 text-yellow-800', text: 'Stalled' }
  };

  const allStatuses: Array<keyof typeof statusConfig> = ['not_started', 'in_progress', 'observed', 'stalled'];

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleStatusSelect = (newStatus: string) => {
    if (onChange) {
      onChange(newStatus);
    }
    setIsOpen(false);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Escape') {
      setIsOpen(false);
    } else if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      if (!readonly && onChange) {
        setIsOpen(!isOpen);
      }
    } else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      if (!isOpen && !readonly && onChange) {
        setIsOpen(true);
      }
    }
  };

  const canInteract = !readonly && onChange;
  const currentConfig = statusConfig[status];

  return (
    <div className="relative" ref={dropdownRef}>
      <div
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          currentConfig.color
        } ${canInteract ? 'cursor-pointer hover:opacity-80' : 'cursor-default'}`}
        onClick={() => canInteract && setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        tabIndex={canInteract ? 0 : -1}
        role={canInteract ? 'button' : undefined}
        aria-haspopup={canInteract ? 'listbox' : undefined}
        aria-expanded={canInteract ? isOpen : undefined}
        aria-label={`Status: ${currentConfig.text}${canInteract ? '. Click to change status' : ''}`}
      >
        {currentConfig.text}
        {canInteract && (
          <ChevronDownIcon 
            className={`ml-1 h-3 w-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} 
          />
        )}
      </div>

      {isOpen && canInteract && (
        <div className="absolute z-10 mt-1 w-32 bg-white border border-gray-200 rounded-md shadow-lg">
          <div className="py-1" role="listbox">
            {allStatuses.map((statusOption) => {
              const config = statusConfig[statusOption];
              return (
                <button
                  key={statusOption}
                  className={`w-full text-left px-3 py-2 text-xs hover:bg-gray-50 ${
                    statusOption === status ? 'bg-gray-50' : ''
                  }`}
                  onClick={() => handleStatusSelect(statusOption)}
                  role="option"
                  aria-selected={statusOption === status}
                >
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
                    {config.text}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default StatusBadge;