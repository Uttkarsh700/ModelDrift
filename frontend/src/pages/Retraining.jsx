/**
 * Retraining Page
 * UI for triggering and monitoring retraining automation.
 */

import React, { useState, useEffect } from 'react'
import MetricCard from '../components/MetricCard'
import StatusBadge from '../components/StatusBadge'
import RetrainingRunsTable from '../components/RetrainingRunsTable'
import {
  getDriftSummary,
  checkAndTriggerRetraining,
  manualTriggerRetraining,
  getLatestRetrainingRun,
  getRetrainingRuns,
  getGitHubActionsConfigStatus,
  triggerGitHubActionsRetraining,
} from '../api/client'

const Retraining = () => {
  // State for drift data
  const [driftSummary, setDriftSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // State for retraining runs
  const [latestRun, setLatestRun] = useState(null)
  const [runs, setRuns] = useState([])

  // State for GitHub Actions
  const [gitHubConfigured, setGitHubConfigured] = useState(false)

  // State for action buttons
  const [actionLoading, setActionLoading] = useState(null) // 'check', 'manual', 'github'
  const [actionMessage, setActionMessage] = useState(null) // { type: 'success'|'error', message: string }

  // Fetch data on component mount and on interval
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)

      try {
        // Fetch drift summary
        const drift = await getDriftSummary()
        setDriftSummary(drift)

        // Fetch latest run
        const latestRunData = await getLatestRetrainingRun()
        setLatestRun(latestRunData.run)

        // Fetch run history
        const runsData = await getRetrainingRuns(20)
        setRuns(runsData.runs || [])

        // Fetch GitHub Actions config
        const gitHubStatus = await getGitHubActionsConfigStatus()
        setGitHubConfigured(gitHubStatus.configured)
      } catch (err) {
        setError('Failed to load retraining data')
        console.error('Error loading data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()

    // Refresh every 10 seconds
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])

  // Handle check and trigger retraining
  const handleCheckAndTrigger = async () => {
    setActionLoading('check')
    setActionMessage(null)

    try {
      const result = await checkAndTriggerRetraining()

      if (result.status === 'triggered') {
        setActionMessage({
          type: 'success',
          message: `✅ Retraining triggered! Run ID: ${result.run_id}`,
        })
      } else if (result.status === 'skipped') {
        setActionMessage({
          type: 'info',
          message: `ℹ️ ${result.reason}. Monitoring only.`,
        })
      } else {
        setActionMessage({
          type: 'error',
          message: `Error: ${result.reason}`,
        })
      }

      // Refresh runs after a short delay
      setTimeout(() => {
        const refreshRuns = async () => {
          const latestRunData = await getLatestRetrainingRun()
          setLatestRun(latestRunData.run)
          const runsData = await getRetrainingRuns(20)
          setRuns(runsData.runs || [])
        }
        refreshRuns()
      }, 1000)
    } catch (err) {
      setActionMessage({
        type: 'error',
        message: `Error: ${err.message}`,
      })
    } finally {
      setActionLoading(null)
    }
  }

  // Handle manual trigger
  const handleManualTrigger = async () => {
    setActionLoading('manual')
    setActionMessage(null)

    try {
      const result = await manualTriggerRetraining()

      if (result.status === 'triggered') {
        setActionMessage({
          type: 'success',
          message: `✅ Manual retraining started! Run ID: ${result.run_id}`,
        })
      } else {
        setActionMessage({
          type: 'error',
          message: `Error: ${result.reason}`,
        })
      }

      // Refresh runs
      setTimeout(() => {
        const refreshRuns = async () => {
          const latestRunData = await getLatestRetrainingRun()
          setLatestRun(latestRunData.run)
          const runsData = await getRetrainingRuns(20)
          setRuns(runsData.runs || [])
        }
        refreshRuns()
      }, 1000)
    } catch (err) {
      setActionMessage({
        type: 'error',
        message: `Error: ${err.message}`,
      })
    } finally {
      setActionLoading(null)
    }
  }

  // Handle GitHub Actions trigger
  const handleGitHubTrigger = async () => {
    if (!gitHubConfigured) {
      setActionMessage({
        type: 'error',
        message: 'GitHub Actions is not configured. Set GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO in .env',
      })
      return
    }

    setActionLoading('github')
    setActionMessage(null)

    try {
      const result = await triggerGitHubActionsRetraining('credit_risk', 'v1', 'triggered from UI')

      if (result.status === 'triggered') {
        setActionMessage({
          type: 'success',
          message: `✅ GitHub Actions workflow triggered on ${result.ref}. Check GitHub Actions tab to monitor.`,
        })
      } else {
        setActionMessage({
          type: 'error',
          message: `Error: ${result.message}`,
        })
      }
    } catch (err) {
      setActionMessage({
        type: 'error',
        message: `Error: ${err.message}`,
      })
    } finally {
      setActionLoading(null)
    }
  }

  // Determine if retraining is needed
  const isRetrainingNeeded = () => {
    if (!driftSummary) return false
    const driftHigh = driftSummary.overall_drift_level === 'high'
    const accuracyDropped = driftSummary.accuracy_drop >= 0.10
    return driftHigh || accuracyDropped
  }

  const driftToColor = (level) => {
    if (level === 'high') return '#ef4444'
    if (level === 'medium') return '#f59e0b'
    if (level === 'low') return '#10b981'
    return '#6b7280'
  }

  if (loading) {
    return (
      <div className="page-content">
        <div className="page-header">
          <h1>Retraining & Automation</h1>
        </div>
        <div className="loading-state">
          <p>Loading retraining data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-content">
        <div className="page-header">
          <h1>Retraining & Automation</h1>
        </div>
        <div className="error-state">
          <p>❌ {error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="page-content">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1>Retraining & Automation</h1>
          <p className="page-subtitle">
            Trigger retraining when drift is high or model accuracy drops.
          </p>
        </div>
      </div>

      {/* Action Message */}
      {actionMessage && (
        <div className={`action-message action-message-${actionMessage.type}`}>
          {actionMessage.message}
        </div>
      )}

      {/* KPI Cards */}
      <div className="metrics-grid">
        <MetricCard
          label="Overall Drift Level"
          value={driftSummary?.overall_drift_level || 'N/A'}
          unit=""
          borderColor={driftToColor(driftSummary?.overall_drift_level)}
        />
        <MetricCard
          label="Accuracy Drop"
          value={driftSummary?.accuracy_drop ? (driftSummary.accuracy_drop * 100).toFixed(1) : '0'}
          unit="%"
          borderColor={driftSummary?.accuracy_drop >= 0.10 ? '#ef4444' : '#10b981'}
        />
        <MetricCard
          label="Latest Retraining Status"
          value={latestRun?.status || 'none'}
          unit=""
          borderColor={
            latestRun?.status === 'completed'
              ? '#10b981'
              : latestRun?.status === 'running'
              ? '#3b82f6'
              : latestRun?.status === 'failed'
              ? '#ef4444'
              : '#6b7280'
          }
        />
        <MetricCard
          label="GitHub Actions Config"
          value={gitHubConfigured ? 'Configured' : 'Not Set'}
          unit=""
          borderColor={gitHubConfigured ? '#10b981' : '#f59e0b'}
        />
      </div>

      {/* Automation Decision Card */}
      <div className="automation-card">
        <h3>Automation Decision</h3>
        <div className="automation-content">
          <div className="automation-row">
            <span className="automation-label">Overall Drift Level:</span>
            <StatusBadge status={driftSummary?.overall_drift_level || 'low'} />
            <span className="automation-value">{driftSummary?.overall_drift_level || 'low'}</span>
          </div>
          <div className="automation-row">
            <span className="automation-label">Accuracy Drop:</span>
            <span className="automation-value">
              {driftSummary?.accuracy_drop ? (driftSummary.accuracy_drop * 100).toFixed(1) : '0'}%
            </span>
          </div>
          <div className="automation-row">
            <span className="automation-label">Retrain Rule:</span>
            <span className="automation-rule">
              if drift is HIGH or accuracy_drop ≥ 10%
            </span>
          </div>
          <div className="automation-row automation-result">
            <span className="automation-label">Result:</span>
            {isRetrainingNeeded() ? (
              <span className="automation-recommended">🔴 Retraining Recommended</span>
            ) : (
              <span className="automation-monitor">🟢 Monitoring Only</span>
            )}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="action-buttons-group">
        <button
          className="action-button action-button-check"
          onClick={handleCheckAndTrigger}
          disabled={actionLoading !== null}
        >
          {actionLoading === 'check' ? 'Checking...' : 'Check & Trigger Retraining'}
        </button>

        <button
          className="action-button action-button-manual"
          onClick={handleManualTrigger}
          disabled={actionLoading !== null}
        >
          {actionLoading === 'manual' ? 'Triggering...' : 'Manual Local Retraining'}
        </button>

        <button
          className={`action-button action-button-github ${gitHubConfigured ? '' : 'disabled'}`}
          onClick={handleGitHubTrigger}
          disabled={!gitHubConfigured || actionLoading !== null}
          title={gitHubConfigured ? 'Trigger GitHub Actions workflow' : 'GitHub Actions not configured'}
        >
          {actionLoading === 'github' ? 'Triggering...' : 'Trigger GitHub Actions'}
        </button>
      </div>

      {/* Latest Retraining Run */}
      {latestRun && (
        <div className="latest-run-card">
          <h3>Latest Retraining Run</h3>
          <div className="latest-run-content">
            <div className="run-row">
              <span className="run-label">Status:</span>
              <StatusBadge status={latestRun.status} />
              <span className="run-value">{latestRun.status}</span>
            </div>
            <div className="run-row">
              <span className="run-label">Model:</span>
              <span className="run-value">{latestRun.model_name}</span>
            </div>
            <div className="run-row">
              <span className="run-label">Version:</span>
              <span className="run-value">{latestRun.model_version}</span>
            </div>
            <div className="run-row">
              <span className="run-label">Reason:</span>
              <span className="run-value">{latestRun.trigger_reason}</span>
            </div>
            <div className="run-row">
              <span className="run-label">Started:</span>
              <span className="run-value">
                {new Date(latestRun.started_at).toLocaleString()}
              </span>
            </div>
            <div className="run-row">
              <span className="run-label">Finished:</span>
              <span className="run-value">
                {latestRun.finished_at ? new Date(latestRun.finished_at).toLocaleString() : '-'}
              </span>
            </div>
            {latestRun.logs && (
              <div className="run-logs">
                <span className="run-label">Logs:</span>
                <pre className="logs-content">{latestRun.logs.substring(0, 500)}...</pre>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Retraining Run History */}
      <div className="runs-history-card">
        <h3>Retraining Run History</h3>
        <RetrainingRunsTable runs={runs} />
      </div>
    </div>
  )
}

export default Retraining
