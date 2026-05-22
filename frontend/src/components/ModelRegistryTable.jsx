import React from 'react'

const ModelRegistryTable = ({ models = [] }) => {
  const getStageColor = (stage) => {
    switch (stage) {
      case 'production':
        return '#10b981' // green
      case 'staging':
        return '#3b82f6' // blue
      case 'archived':
        return '#6b7280' // gray
      default:
        return '#64748b'
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: '2-digit' })
  }

  const formatTime = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true })
  }

  if (!models || models.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>
        No models in registry yet.
      </div>
    )
  }

  return (
    <table className="retraining-table" style={{ width: '100%' }}>
      <thead>
        <tr>
          <th>Model</th>
          <th>Version</th>
          <th>Stage</th>
          <th>Accuracy</th>
          <th>F1 Score</th>
          <th>Drift</th>
          <th>Created</th>
          <th>Promoted</th>
        </tr>
      </thead>
      <tbody>
        {models.map((model) => (
          <tr key={model.id}>
            <td>{model.model_name}</td>
            <td>{model.model_version}</td>
            <td>
              <span
                className="status-badge"
                style={{
                  backgroundColor: getStageColor(model.stage),
                  color: '#fff',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: '600',
                }}
              >
                {model.stage}
              </span>
            </td>
            <td>{(model.accuracy * 100).toFixed(1)}%</td>
            <td>{(model.f1_score * 100).toFixed(1)}%</td>
            <td>{model.drift_score !== null ? (model.drift_score * 100).toFixed(1) + '%' : '-'}</td>
            <td>{formatDate(model.created_at)}</td>
            <td>{model.promoted_at ? formatDate(model.promoted_at) : '-'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default ModelRegistryTable
