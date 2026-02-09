// src/components/MetricsCard.jsx
// Metrics Display Card

import React from 'react';

const MetricsCard = ({ icon: Icon, title, value, subtitle, color = 'blue' }) => {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    yellow: 'from-yellow-500 to-yellow-600',
    red: 'from-red-500 to-red-600',
  };

  return (
    <div className={`p-6 rounded-xl bg-gradient-to-br ${colorClasses[color]} shadow-lg`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-white/80 text-sm font-medium mb-1">{title}</p>
          <h3 className="text-3xl font-bold text-white mb-1">{value}</h3>
          {subtitle && <p className="text-white/60 text-xs">{subtitle}</p>}
        </div>
        {Icon && (
          <div className="bg-white/20 p-3 rounded-lg">
            <Icon className="w-8 h-8 text-white" />
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricsCard;