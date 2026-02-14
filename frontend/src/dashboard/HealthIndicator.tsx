import React from 'react';

interface HealthIndicatorProps {
  status: string;
}

const HealthIndicator: React.FC<HealthIndicatorProps> = ({ status }) => {
  const statusConfig = {
    "Not Started": { color: "bg-gray-100 text-gray-600", icon: "⚪", label: "Not Started" },
    "In Progress": { color: "bg-teal-100 text-teal-700", icon: "🟡", label: "In Progress" },
    "On Track": { color: "bg-green-100 text-green-700", icon: "🟢", label: "On Track" },
    "At Risk": { color: "bg-yellow-100 text-yellow-700", icon: "🔴", label: "At Risk" }
  };

  const config = statusConfig[status as keyof typeof statusConfig] || statusConfig["Not Started"];

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`} aria-label={config.label}>
      <span className="sr-only">Health status: </span>
      <span>{config.icon} {config.label}</span>
    </span>
  );
};

export default HealthIndicator;