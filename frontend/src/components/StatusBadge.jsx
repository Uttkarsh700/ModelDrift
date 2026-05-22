import React from 'react'

const StatusBadge = ({ status, label }) => {
  let backgroundColor = '#6b7280'
  let textColor = '#ffffff'

  if (status === 'online' || status === 'low') {
    backgroundColor = '#10b981'
  } else if (status === 'medium') {
    backgroundColor = '#f59e0b'
  } else if (status === 'high' || status === 'offline') {
    backgroundColor = '#ef4444'
  }

  return (
    <span
      className="status-badge"
      style={{
        backgroundColor,
        color: textColor,
      }}
    >
      {label || status}
    </span>
  )
}

export default StatusBadge
