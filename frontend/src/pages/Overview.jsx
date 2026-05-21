import { useState, useEffect } from 'react'
import { getHealth } from '../api/client'

function Overview() {
  const [backendStatus, setBackendStatus] = useState('loading')
  const [backendError, setBackendError] = useState(null)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const data = await getHealth()
        setBackendStatus(data.status)
        setBackendError(null)
      } catch (error) {
        setBackendStatus('error')
        setBackendError(error.message)
      }
    }

    checkHealth()
    // Check health every 10 seconds
    const interval = setInterval(checkHealth, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="overview-container">
      <div className="overview-header">
        <h1>ModelDrift</h1>
        <p>ML Monitoring {'\u0026'} Auto-Retraining Prototype</p>
      </div>

      <div className="status-card">
        <h2>System Status</h2>
        <div className="status-item">
          <div className={`status-indicator ${backendStatus === 'loading' ? 'loading' : backendStatus === 'ok' ? 'ok' : 'error'}`}></div>
          <div className="status-text">
            <span>Backend Service: </span>
            <span className="status-value">
              {backendStatus === 'loading' && 'Checking...'}
              {backendStatus === 'ok' && 'Healthy'}
              {backendStatus === 'error' && `Error: ${backendError}`}
            </span>
          </div>
        </div>
      </div>

      <div className="status-card">
        <h2>What's Next</h2>
        <p>This is a prototype scaffold. Core features coming soon:</p>
        <ul style={{ marginLeft: '20px', marginTop: '10px' }}>
          <li>Model performance monitoring</li>
          <li>Drift detection</li>
          <li>Auto-retraining triggers</li>
          <li>Training history and metrics</li>
          <li>Real-time dashboards</li>
        </ul>
      </div>
    </div>
  )
}

export default Overview
