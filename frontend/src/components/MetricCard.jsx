import React from 'react'

const MetricCard = ({ label, value, unit = '', color = '#3b82f6' }) => {
  return (
    <div className="metric-card" style={{ borderLeftColor: color }}>
      <div className="metric-label">{label}</div>
      <div className="metric-value">
        {value}
        {unit && <span className="metric-unit">{unit}</span>}
      </div>
    </div>
  )
}

export default MetricCard
