/**
 * RetrainingRunsTable Component
 * Displays historical retraining runs in a clean table format.
 */

import React from 'react'

const RetrainingRunsTable = ({ runs = [] }) => {
  if (!runs || runs.length === 0) {
    return (
      <div className="retraining-table-container">
        <p className="empty-state">No retraining runs yet.</p>
      </div>
    )
  }

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'pending':
        return 'status-badge status-pending'
      case 'running':
        return 'status-badge status-running'
      case 'completed':
        return 'status-badge status-completed'
      case 'failed':
        return 'status-badge status-failed'
      default:
        return 'status-badge'
    }
  }

  const formatDateTime = (isoString) => {
    if (!isoString) return '-'
    const date = new Date(isoString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="retraining-table-container">
      <table className="retraining-table">
        <thead>
          <tr>
            <th>Status</th>
            <th>Model</th>
            <th>Version</th>
            <th>Reason</th>
            <th>Started</th>
            <th>Finished</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.id} className="retraining-row">
              <td>
                <span className={getStatusBadgeClass(run.status)}>
                  {run.status.charAt(0).toUpperCase() + run.status.slice(1)}
                </span>
              </td>
              <td>{run.model_name}</td>
              <td>{run.model_version}</td>
              <td>{run.trigger_reason}</td>
              <td className="datetime-cell">{formatDateTime(run.started_at)}</td>
              <td className="datetime-cell">{formatDateTime(run.finished_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default RetrainingRunsTable
