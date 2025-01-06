// components/MetricCard.js
import React from 'react';

const MetricCard = ({ title, value, color }) => {
  return (
    <div className="rounded-xl p-6 bg-opacity-60 backdrop-blur-md">
      <h3 className="text-lg font-medium mb-2">{title}</h3>
      <div className={`text-3xl font-bold ${color}`}>{value}</div>
      <div className="text-sm text-gray-600">Avg. Engagement</div>
    </div>
  );
};

export default MetricCard;
