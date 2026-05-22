import React from 'react'

const AlertCard = ({ alert, onResolve, isResolving }) => {
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return '#ef4444' // red
      case 'warning':
        return '#f59e0b' // amber/yellow
      case 'info':
        return '#3b82f6' // blue
      default:
        return '#6b7280' // gray
    }
  }

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return '🔴'
      case 'warning':
        return '🟡'
      case 'info':
        return '🔵'
      default:
        return '⚪'
    }
  }

  const getSourceLabel = (source) => {
    switch (source) {
      case 'drift':
        return '📊 Drift'
      case 'retraining':
        return '🔄 Retraining'
      case 'github_actions':
        return '🔷 GitHub Actions'
      case 'system':
        return '⚙️ System'
      default:
        return source
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: '2-digit' }) +
           ' ' +
           date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true })
  }

  return (
    <div
      style={{
        backgroundColor: '#1e293b',
        border: `2px solid ${getSeverityColor(alert.severity)}`,
        borderRadius: '8px',
        padding: '16px',
        marginBottom: '12px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        gap: '16px',
      }}
    >
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <span style={{ fontSize: '18px' }}>{getSeverityIcon(alert.severity)}</span>
          <span
            style={{
              fontWeight: '600',
              fontSize: '14px',
              color: getSeverityColor(alert.severity),
              textTransform: 'uppercase',
            }}
          >
            {alert.severity}
          </span>
          <span style={{ fontSize: '12px', color: '#94a3b8', marginLeft: 'auto' }}>
            {getSourceLabel(alert.source)}
          </span>
        </div>

        <div style={{ fontSize: '15px', fontWeight: '600', marginBottom: '4px', color: '#f1f5f9' }}>
          {alert.title}
        </div>

        <div style={{ fontSize: '13px', color: '#cbd5e1', marginBottom: '8px', lineHeight: '1.5' }}>
          {alert.message}
        </div>

        <div style={{ fontSize: '12px', color: '#64748b' }}>
          Created: {formatDate(alert.created_at)}
          {alert.resolved_at && ` • Resolved: ${formatDate(alert.resolved_at)}`}
        </div>
      </div>

      {alert.status === 'active' && (
        <button
          onClick={() => onResolve(alert.id)}
          disabled={isResolving}
          style={{
            padding: '8px 16px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: '600',
            cursor: isResolving ? 'not-allowed' : 'pointer',
            opacity: isResolving ? 0.5 : 1,
            whiteSpace: 'nowrap',
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => {
            if (!isResolving) e.target.style.backgroundColor = '#2563eb'
          }}
          onMouseLeave={(e) => {
            if (!isResolving) e.target.style.backgroundColor = '#3b82f6'
          }}
        >
          {isResolving ? 'Resolving...' : 'Resolve'}
        </button>
      )}

      {alert.status === 'resolved' && (
        <span
          style={{
            padding: '8px 12px',
            backgroundColor: '#10b981',
            color: 'white',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: '600',
            whiteSpace: 'nowrap',
          }}
        >
          ✓ Resolved
        </span>
      )}
    </div>
  )
}

export default AlertCard
