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
  getRecentPredictions,
} from '../api/client'
import MetricCard from '../components/MetricCard'
import StatusBadge from '../components/StatusBadge'
import DriftTable from '../components/DriftTable'
import RecentPredictions from '../components/RecentPredictions'

const Overview = () => {
  const [driftSummary, setDriftSummary] = useState(null)
  const [driftMetrics, setDriftMetrics] = useState(null)
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)

        const [summary, metrics, preds] = await Promise.all([
          getDriftSummary(),
          getLatestDriftMetrics(),
          getRecentPredictions(20),
        ])

        setDriftSummary(summary)
        setDriftMetrics(metrics)
        setPredictions(preds)
      } catch (err) {
        console.error('Error fetching data:', err)
        setError('Failed to fetch dashboard data. Ensure backend is running.')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  // Prepare chart data
  const chartData =
    driftMetrics?.features?.map((f) => ({
      name: f.feature_name,
      PSI: parseFloat(f.psi_score?.toFixed(3)),
    })) || []

  if (loading) {
    return (
      <div className="page-content">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-content">
        <div className="error-state">
          <p>⚠️ {error}</p>
          <div className="hint">
            <p>Quick setup:</p>
            <ol>
              <li>Start backend: <code>cd backend && python -m uvicorn app.main:app --reload</code></li>
              <li>Generate demo data: <code>python scripts/generate_demo_data.py</code></li>
              <li>Run drift calculation: <code>python scripts/test_drift.py</code></li>
              <li>Refresh this page</li>
            </ol>
          </div>
        </div>
      </div>
    )
  }

  const driftLevel = driftSummary?.overall_drift_level || 'unknown'

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Overview</h2>
        <p className="page-subtitle">Real-time model monitoring and drift detection</p>
      </div>

      {/* KPI Cards */}
      <div className="metrics-grid">
        <MetricCard
          label="Model Name"
          value={driftSummary?.model_name || 'N/A'}
          color="#3b82f6"
        />
        <MetricCard
          label="Overall Drift Level"
          value={
            <StatusBadge
              status={driftLevel}
              label={driftLevel?.toUpperCase()}
            />
          }
          color="#8b5cf6"
        />
        <MetricCard
          label="Average PSI"
          value={(driftSummary?.avg_psi?.toFixed(3)) || 'N/A'}
          color="#06b6d4"
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
          color="#ef4444"
        />
        <MetricCard
          label="High Drift Features"
          value={driftSummary?.high_drift_features || 0}
          color="#f59e0b"
        />
      </div>

      {/* Drift Summary */}
      {driftSummary && (
        <div className="card">
          <h3>Drift Summary Statistics</h3>
          <div className="summary-grid">
            <div className="summary-item">
              <div className="summary-label">Max PSI</div>
              <div className="summary-value">{driftSummary.max_psi?.toFixed(3)}</div>
            </div>
            <div className="summary-item">
              <div className="summary-label">Min PSI</div>
              <div className="summary-value">{driftSummary.min_psi?.toFixed(3)}</div>
            </div>
            <div className="summary-item">
              <div className="summary-label">Baseline Accuracy</div>
              <div className="summary-value">
                {((driftSummary.baseline_accuracy || 0) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="summary-item">
              <div className="summary-label">Medium Drift Features</div>
              <div className="summary-value">{driftSummary.medium_drift_features}</div>
            </div>
            <div className="summary-item">
              <div className="summary-label">Low Drift Features</div>
              <div className="summary-value">{driftSummary.low_drift_features}</div>
            </div>
            <div className="summary-item">
              <div className="summary-label">Last Calculated</div>
              <div className="summary-value timestamp">
                {new Date(driftSummary.calculated_at).toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* PSI Chart */}
      {chartData.length > 0 && (
        <div className="card">
          <h3>Feature PSI Scores</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  color: '#f3f4f6',
                }}
              />
              <Legend wrapperStyle={{ color: '#9ca3af' }} />
              <Bar dataKey="PSI" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Drift Table */}
      <DriftTable features={driftMetrics?.features || []} />

      {/* Recent Predictions */}
      <RecentPredictions predictions={predictions} />
    </div>
  )
}

export default Overview
