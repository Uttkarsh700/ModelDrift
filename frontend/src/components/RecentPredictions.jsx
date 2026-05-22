import React from 'react'

const RecentPredictions = ({ predictions = [] }) => {
  if (!predictions || predictions.length === 0) {
    return (
      <div className="card">
        <h3>Recent Predictions</h3>
        <div className="empty-state">
          <p>No predictions available yet.</p>
          <p className="hint">Predictions will appear here as the model makes them.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h3>Recent Predictions</h3>
      <table className="predictions-table">
        <thead>
          <tr>
            <th>Prediction ID</th>
            <th>Model</th>
            <th>Prediction</th>
            <th>Confidence</th>
            <th>Created At</th>
          </tr>
        </thead>
        <tbody>
          {predictions.slice(0, 20).map((pred) => (
            <tr key={pred.prediction_id}>
              <td className="pred-id">{pred.prediction_id}</td>
              <td>{pred.model_name}</td>
              <td>
                <span className={`prediction-badge pred-${pred.prediction?.replace(/_/g, '-')}`}>
                  {pred.prediction}
                </span>
              </td>
              <td className="confidence">
                {(pred.confidence * 100).toFixed(1)}%
              </td>
              <td className="timestamp">
                {new Date(pred.created_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default RecentPredictions
