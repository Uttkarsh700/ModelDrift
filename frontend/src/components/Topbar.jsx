import React, { useState, useEffect } from 'react'
import { getHealth } from '../api/client'
import StatusBadge from './StatusBadge'

const Topbar = () => {
  const [health, setHealth] = useState({ status: 'offline' })

  useEffect(() => {
    const checkHealth = async () => {
      const data = await getHealth()
      setHealth(data)
    }

    checkHealth()
    const interval = setInterval(checkHealth, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="topbar">
      <div className="topbar-left">
        <h1 className="app-title">ModelDrift</h1>
      </div>

      <div className="topbar-right">
        <StatusBadge status="default" label="Prototype" />
        <div className="health-status">
          <span className="health-label">Backend:</span>
          <StatusBadge status={health.status} label={health.status?.toUpperCase()} />
        </div>
      </div>
    </div>
  )
}

export default Topbar
