import React, { useState, useEffect } from 'react'
import {
  getAlerts,
  getActiveAlerts,
  getAlertsSummary,
  getGitHubActionsConfigStatus,
  getHealth,
  resolveAlert,
  seedDemoAlerts,
} from '../api/client'
import AlertCard from '../components/AlertCard'

const Alerts = () => {
  const [summary, setSummary] = useState(null)
  const [activeAlerts, setActiveAlerts] = useState([])
  const [allAlerts, setAllAlerts] = useState([])
  const [healthStatus, setHealthStatus] = useState({})
  const [githubConfigured, setGithubConfigured] = useState(false)
  const [actionMessage, setActionMessage] = useState(null)
  const [actionLoading, setActionLoading] = useState(null)
  const [resolvingAlerts, setResolvingAlerts] = useState(new Set())
  const [loading, setLoading] = useState(true)

  // Fetch data on mount and every 10 seconds
  useEffect(() => {
    const fetchData = async () => {
      try {
        const summaryData = await getAlertsSummary()
        setSummary(summaryData)

        const activeAlertsData = await getActiveAlerts()
        setActiveAlerts(activeAlertsData.alerts || [])

        const allAlertsData = await getAlerts(50)
        setAllAlerts(allAlertsData.alerts || [])

        const healthData = await getHealth()
        setHealthStatus(healthData)

        const githubStatus = await getGitHubActionsConfigStatus()
        setGithubConfigured(githubStatus.configured)
      } catch (error) {
        console.error('Failed to fetch data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])

  const handleResolveAlert = async (alertId) => {
    setResolvingAlerts((prev) => new Set(prev).add(alertId))

    try {
      const result = await resolveAlert(alertId)

      if (result.status === 'resolved') {
        setActionMessage({
          type: 'success',
          text: '✅ Alert resolved!',
        })

        // Refresh data after 1 second
        setTimeout(async () => {
          const summaryData = await getAlertsSummary()
          setSummary(summaryData)

          const activeAlertsData = await getActiveAlerts()
          setActiveAlerts(activeAlertsData.alerts || [])

          const allAlertsData = await getAlerts(50)
          setAllAlerts(allAlertsData.alerts || [])
        }, 1000)
      } else {
        setActionMessage({
          type: 'error',
          text: `❌ Failed to resolve alert: ${result.message}`,
        })
      }
    } catch (error) {
      console.error('Error resolving alert:', error)
      setActionMessage({
        type: 'error',
        text: `❌ Error resolving alert: ${error.message}`,
      })
    } finally {
      setResolvingAlerts((prev) => {
        const newSet = new Set(prev)
        newSet.delete(alertId)
        return newSet
      })
    }
  }

  const handleSeedDemo = async () => {
    setActionLoading('seed')
    setActionMessage(null)

    try {
      const result = await seedDemoAlerts()

      if (result.status === 'seeded') {
        setActionMessage({
          type: 'success',
          text: `✅ Demo alerts seeded with ${result.created} alerts.`,
        })

        // Refresh after 1 second
        setTimeout(async () => {
          const summaryData = await getAlertsSummary()
          setSummary(summaryData)

          const activeAlertsData = await getActiveAlerts()
          setActiveAlerts(activeAlertsData.alerts || [])

          const allAlertsData = await getAlerts(50)
          setAllAlerts(allAlertsData.alerts || [])
        }, 1000)
      } else if (result.status === 'skipped') {
        setActionMessage({
          type: 'info',
          text: `ℹ️ Alerts already seeded. ${result.reason}`,
        })
      } else {
        setActionMessage({
          type: 'error',
          text: `❌ Seeding failed: ${result.message || 'Unknown error'}`,
        })
      }
    } catch (error) {
      console.error('Seed error:', error)
      setActionMessage({
        type: 'error',
        text: `❌ Seed error: ${error.message}`,
      })
    } finally {
      setActionLoading(null)
    }
  }

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>Loading...</div>
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Alerts & System Health</h1>
        <p>Monitor drift alerts, retraining failures, and automation issues.</p>
      </div>

      {/* KPI Cards */}
      {summary && (
        <div className="metrics-grid" style={{ marginBottom: '24px' }}>
          <div className="kpi-card">
            <div className="kpi-label">Total Alerts</div>
            <div className="kpi-value">{summary.total_alerts}</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Active Alerts</div>
            <div className="kpi-value" style={{ color: summary.active_alerts > 0 ? '#ef4444' : '#10b981' }}>
              {summary.active_alerts}
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Critical</div>
            <div className="kpi-value" style={{ color: '#ef4444' }}>
              {summary.critical_alerts}
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Resolved</div>
            <div className="kpi-value" style={{ color: '#10b981' }}>
              {summary.resolved_alerts}
            </div>
          </div>
        </div>
      )}

      {/* Action Message */}
      {actionMessage && actionLoading === null && (
        <div
          className={`action-message action-message-${actionMessage.type}`}
          style={{ marginBottom: '24px' }}
        >
          {actionMessage.text}
        </div>
      )}

      {/* Active Alerts Section */}
      {activeAlerts.length > 0 && (
        <div className="card" style={{ marginBottom: '24px' }}>
          <h2>Active Alerts ({activeAlerts.length})</h2>
          <p style={{ color: '#cbd5e1', marginBottom: '16px' }}>
            Unresolved alerts requiring attention.
          </p>
          {activeAlerts.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              onResolve={handleResolveAlert}
              isResolving={resolvingAlerts.has(alert.id)}
            />
          ))}
        </div>
      )}

      {activeAlerts.length === 0 && (
        <div className="card" style={{ marginBottom: '24px', textAlign: 'center', padding: '40px' }}>
          <div style={{ fontSize: '24px', marginBottom: '12px' }}>✅</div>
          <div style={{ fontSize: '16px', fontWeight: '600', marginBottom: '4px' }}>
            No Active Alerts
          </div>
          <div style={{ color: '#94a3b8' }}>All systems operating normally.</div>
        </div>
      )}

      {/* System Health Card */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <h2>System Health</h2>
        <p style={{ color: '#cbd5e1', marginBottom: '16px' }}>
          Status of core system components.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
          {/* Backend API */}
          <div
            style={{
              padding: '12px',
              backgroundColor: '#0f172a',
              borderRadius: '6px',
              border: `2px solid ${healthStatus.status === 'healthy' ? '#10b981' : '#ef4444'}`,
            }}
          >
            <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Backend API</div>
            <div
              style={{
                fontSize: '14px',
                fontWeight: '600',
                color: healthStatus.status === 'healthy' ? '#10b981' : '#ef4444',
              }}
            >
              {healthStatus.status === 'healthy' ? '✅ Healthy' : '❌ Offline'}
            </div>
          </div>

          {/* GitHub Actions */}
          <div
            style={{
              padding: '12px',
              backgroundColor: '#0f172a',
              borderRadius: '6px',
              border: `2px solid ${githubConfigured ? '#10b981' : '#f59e0b'}`,
            }}
          >
            <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>GitHub Actions</div>
            <div
              style={{
                fontSize: '14px',
                fontWeight: '600',
                color: githubConfigured ? '#10b981' : '#f59e0b',
              }}
            >
              {githubConfigured ? '✅ Configured' : '⚠️ Not configured'}
            </div>
          </div>

          {/* PostgreSQL */}
          <div
            style={{
              padding: '12px',
              backgroundColor: '#0f172a',
              borderRadius: '6px',
              border: '2px solid #3b82f6',
            }}
          >
            <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>PostgreSQL</div>
            <div style={{ fontSize: '14px', fontWeight: '600', color: '#3b82f6' }}>ℹ️ Manual check</div>
          </div>

          {/* Redis */}
          <div
            style={{
              padding: '12px',
              backgroundColor: '#0f172a',
              borderRadius: '6px',
              border: '2px solid #3b82f6',
            }}
          >
            <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Redis/Celery</div>
            <div style={{ fontSize: '14px', fontWeight: '600', color: '#3b82f6' }}>ℹ️ Manual check</div>
          </div>
        </div>
      </div>

      {/* Demo Seed Card */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <h2>Demo Setup</h2>
        <p style={{ color: '#cbd5e1', marginBottom: '16px' }}>
          Create demo alerts (only if empty):
        </p>

        <button
          className="action-button"
          onClick={handleSeedDemo}
          disabled={actionLoading !== null}
          style={{
            backgroundColor: '#8b5cf6',
            width: '100%',
            maxWidth: '300px',
            padding: '12px',
            fontSize: '14px',
            fontWeight: '600',
          }}
        >
          {actionLoading === 'seed' ? 'Seeding...' : '🌱 Seed Demo Alerts'}
        </button>
      </div>

      {/* All Alerts Table */}
      <div className="card">
        <h2>All Alerts</h2>
        <p style={{ color: '#cbd5e1', marginBottom: '16px' }}>
          Complete alert history (last 50 alerts).
        </p>

        {allAlerts.length > 0 ? (
          <table className="retraining-table" style={{ width: '100%' }}>
            <thead>
              <tr>
                <th>Severity</th>
                <th>Title</th>
                <th>Source</th>
                <th>Status</th>
                <th>Created</th>
                <th>Resolved</th>
              </tr>
            </thead>
            <tbody>
              {allAlerts.map((alert) => (
                <tr key={alert.id}>
                  <td>
                    <span
                      className={`status-badge status-${alert.severity}`}
                      style={{
                        backgroundColor:
                          alert.severity === 'critical'
                            ? '#ef4444'
                            : alert.severity === 'warning'
                              ? '#f59e0b'
                              : alert.severity === 'info'
                                ? '#3b82f6'
                                : '#6b7280',
                        color: 'white',
                      }}
                    >
                      {alert.severity}
                    </span>
                  </td>
                  <td>{alert.title}</td>
                  <td>
                    {alert.source === 'drift'
                      ? '📊 Drift'
                      : alert.source === 'retraining'
                        ? '🔄 Retraining'
                        : alert.source === 'github_actions'
                          ? '🔷 GitHub'
                          : '⚙️ System'}
                  </td>
                  <td>
                    <span
                      style={{
                        backgroundColor:
                          alert.status === 'active'
                            ? 'rgba(239, 68, 68, 0.1)'
                            : 'rgba(16, 185, 129, 0.1)',
                        color: alert.status === 'active' ? '#ef4444' : '#10b981',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: '600',
                      }}
                    >
                      {alert.status}
                    </span>
                  </td>
                  <td style={{ fontSize: '12px', color: '#94a3b8' }}>
                    {new Date(alert.created_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: '2-digit',
                      year: '2-digit',
                    })}{' '}
                    {new Date(alert.created_at).toLocaleTimeString('en-US', {
                      hour: '2-digit',
                      minute: '2-digit',
                      hour12: true,
                    })}
                  </td>
                  <td style={{ fontSize: '12px', color: '#94a3b8' }}>
                    {alert.resolved_at
                      ? new Date(alert.resolved_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: '2-digit',
                          year: '2-digit',
                        })
                      : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>
            No alerts to display.
          </div>
        )}
      </div>
    </div>
  )
}

export default Alerts
