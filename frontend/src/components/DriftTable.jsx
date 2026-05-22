import React from 'react'

const DriftTable = ({ features = [] }) => {
  if (!features || features.length === 0) {
    return (
      <div className="card">
        <h3>Feature Drift Analysis</h3>
        <div className="empty-state">
          <p>No drift metrics available yet.</p>
          <p className="hint">Run drift calculation to see feature-level analysis.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h3>Feature Drift Analysis</h3>
      <table className="drift-table">
        <thead>
          <tr>
            <th>Feature</th>
            <th>PSI</th>
            <th>KS Statistic</th>
            <th>KS P-Value</th>
            <th>Drift Level</th>
          </tr>
        </thead>
        <tbody>
          {features.map((feature) => (
            <tr key={feature.feature_name}>
              <td className="feature-name">{feature.feature_name}</td>
              <td className="psi-value">{feature.psi_score?.toFixed(3) || 'N/A'}</td>
              <td>{feature.ks_statistic?.toFixed(3) || 'N/A'}</td>
              <td>{feature.ks_p_value?.toFixed(4) || 'N/A'}</td>
              <td>
                <span className={`drift-badge drift-${feature.drift_level}`}>
                  {feature.drift_level?.toUpperCase()}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default DriftTable
