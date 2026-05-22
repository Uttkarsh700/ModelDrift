import React, { useState, useEffect } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import {
  getDriftSummary,
  getLatestDriftMetrics,
  runDriftCalculation,
} from '../api/client'
import MetricCard from '../components/MetricCard'
import StatusBadge from '../components/StatusBadge'
import DriftTable from '../components/DriftTable'

const DriftAnalysis = () => {
  const [driftSummary, setDriftSummary] = useState(null)
  const [driftMetrics, setDriftMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [runLoading, setRunLoading] = useState(false)
  const [actionMessage, setActionMessage] = useState(null)

  useEffect(() => {
    fetchDriftData()
    const interval = setInterval(fetchDriftData, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchDriftData = async () => {
    try {
      setError(null)
      const [summary, metrics] = await Promise.all([
        getDriftSummary(),
        getLatestDriftMetrics(),
      ])

      setDriftSummary(summary)
      setDriftMetrics(metrics)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching drift data:', err)
      setError('Failed to fetch drift analysis data.')
      setLoading(false)
    }
  }

  const handleRunDriftCheck = async () => {
    try {
      setRunLoading(true)
      setActionMessage(null)
      await runDriftCalculation()
      setActionMessage({ type: 'success', text: 'Drift check completed! Refreshing data...' })
      setTimeout(() => {
        fetchDriftData()
        setActionMessage(null)
      }, 1500)
    } catch (err) {
      console.error('Error running drift check:', err)
      setActionMessage({ type: 'error', text: 'Failed to run drift check. See console for details.' })
    } finally {
      setRunLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="page-content">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading drift analysis...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-content">
        <div className="error-state">
          <p>⚠️ {error}</p>
        </div>
      </div>
    )
  }

  // Check if drift data exists
  if (!driftSummary || !driftMetrics) {
    return (
      <div className="page-content">
        <div className="page-header">
          <h2>Drift Analysis</h2>
          <p className="page-subtitle">Compare baseline data with current production data using PSI and KS-test.</p>
        </div>
        <div className="empty-state">
          <p>No drift metrics yet.</p>
          <p className="hint">Generate demo data and run drift check to see analysis.</p>
        </div>
      </div>
    )
  }

  const driftLevel = driftSummary?.overall_drift_level || 'unknown'
  const accuracyDrop = driftSummary?.accuracy_drop || 0
  const highDriftFeatures = driftMetrics?.features?.filter(
    (f) => f.drift_level === 'high'
  )?.length || 0

  const isRetrainingRecommended =
    driftLevel === 'high' || accuracyDrop >= 0.10

  const retrainingReason = driftLevel === 'high'
    ? 'high drift detected'
    : accuracyDrop >= 0.10
      ? `accuracy dropped by ${(accuracyDrop * 100).toFixed(1)}%`
      : 'drift below threshold'

  // Prepare PSI chart data
  const psiChartData = driftMetrics?.features?.map((f) => ({
    name: f.feature_name,
    psi: parseFloat(f.psi_score?.toFixed(3)),
  })) || []

  // Prepare KS-test chart data
  const ksChartData = driftMetrics?.features?.map((f) => ({
    name: f.feature_name,
    ks: parseFloat(f.ks_statistic?.toFixed(3)),
  })) || []

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Drift Analysis</h2>
        <p className="page-subtitle">Compare baseline data with current production data using PSI and KS-test.</p>
      </div>

      {/* Action Message */}
      {actionMessage && (
        <div className={`action-message ${actionMessage.type}`}>
          {actionMessage.type === 'success' ? '✅' : '❌'} {actionMessage.text}
        </div>
      )}

      {/* KPI Cards */}
      <div className="kpi-grid">
        <MetricCard
          label="Overall Drift Level"
          value={driftLevel.toUpperCase()}
          color={driftLevel === 'high' ? '#ef4444' : driftLevel === 'medium' ? '#f59e0b' : '#10b981'}
        />
        <MetricCard
          label="Average PSI"
          value={(driftSummary?.average_psi || 0).toFixed(4)}
          color="#3b82f6"
        />
        <MetricCard
          label="Maximum PSI"
          value={(driftSummary?.max_psi || 0).toFixed(4)}
          color="#8b5cf6"
        />
        <MetricCard
          label="Current Accuracy"
          value={((driftSummary?.current_accuracy || 0) * 100).toFixed(1)}
          unit="%"
          color="#10b981"
        />
        <MetricCard
          label="Accuracy Drop"
          value={((driftSummary?.accuracy_drop || 0) * 100).toFixed(1)}
          unit="%"
          color={accuracyDrop >= 0.10 ? '#ef4444' : '#10b981'}
        />
        <MetricCard
          label="High Drift Features"
          value={highDriftFeatures}
          color={highDriftFeatures > 0 ? '#ef4444' : '#10b981'}
        />
      </div>

      {/* Explanation Card */}
      <div className="card explanation-card">
        <h3>How to Read This Page</h3>
        <div className="explanation-content">
          <p>
            <strong>PSI (Population Stability Index)</strong> checks how much a feature's distribution changed
            between the baseline and current data. Higher values indicate more drift.
          </p>
          <p>
            <strong>KS-Test (Kolmogorov-Smirnov Test)</strong> checks whether baseline and current values are
            statistically different. The p-value tells you if the difference is significant.
          </p>
          <p>
            <strong>High PSI or Big Accuracy Drop</strong> means the model may need retraining to stay accurate
            on current data.
          </p>
        </div>
      </div>

      {/* PSI Interpretation Card */}
      <div className="card psi-interpretation-card">
        <h3>PSI Score Interpretation</h3>
        <div className="interpretation-grid">
          <div className="interpretation-item low">
            <span className="level-label">Low Drift</span>
            <span className="level-range">PSI &lt; 0.10</span>
          </div>
          <div className="interpretation-item medium">
            <span className="level-label">Medium Drift</span>
            <span className="level-range">0.10 ≤ PSI &lt; 0.25</span>
          </div>
          <div className="interpretation-item high">
            <span className="level-label">High Drift</span>
            <span className="level-range">PSI ≥ 0.25</span>
          </div>
        </div>
      </div>

      {/* PSI Chart */}
      <div className="card">
        <h3>PSI Scores by Feature</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={psiChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="psi" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* KS-Test Chart */}
      <div className="card">
        <h3>KS-Test Statistics by Feature</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={ksChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="ks" fill="#8b5cf6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Feature Drift Table */}
      <DriftTable features={driftMetrics?.features || []} />

      {/* Retraining Recommendation */}
      <div className={`card recommendation-card ${isRetrainingRecommended ? 'recommended' : 'monitoring'}`}>
        <h3>Retraining Recommendation</h3>
        <div className="recommendation-content">
          <div className="recommendation-status">
            {isRetrainingRecommended ? (
              <>
                <span className="recommendation-badge critical">⚠️ RECOMMENDED</span>
                <p className="recommendation-reason">
                  Retraining recommended because {retrainingReason}
                </p>
              </>
            ) : (
              <>
                <span className="recommendation-badge monitoring">✅ MONITORING ONLY</span>
                <p className="recommendation-reason">
                  {retrainingReason}
                </p>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Run Drift Check Button */}
      <div className="action-section">
        <button
          className="btn btn-primary"
          onClick={handleRunDriftCheck}
          disabled={runLoading}
        >
          {runLoading ? 'Running Drift Check...' : 'Run Drift Check'}
        </button>
      </div>
    </div>
  )
}

export default DriftAnalysis
