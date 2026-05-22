import React, { useState, useEffect } from 'react'
import {
  getComparison,
  getModels,
  promoteChallenger,
  seedDemoRegistry,
} from '../api/client'
import ModelRegistryTable from '../components/ModelRegistryTable'

const Experiments = () => {
  const [comparison, setComparison] = useState(null)
  const [models, setModels] = useState([])
  const [actionMessage, setActionMessage] = useState(null)
  const [actionLoading, setActionLoading] = useState(null)
  const [loading, setLoading] = useState(true)

  // Fetch comparison and models on mount and every 10 seconds
  useEffect(() => {
    const fetchData = async () => {
      try {
        const comparisonData = await getComparison()
        setComparison(comparisonData)

        const modelsData = await getModels()
        setModels(modelsData.models || [])
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

  const handlePromoteChallenger = async () => {
    setActionLoading('promote')
    setActionMessage(null)

    try {
      const result = await promoteChallenger()

      if (result.status === 'promoted') {
        setActionMessage({
          type: 'success',
          text: `✅ ${result.message}. Model ${result.promoted_model.model_version} is now in production.`,
        })

        // Refresh comparison and models after 1 second
        setTimeout(async () => {
          const comparisonData = await getComparison()
          setComparison(comparisonData)

          const modelsData = await getModels()
          setModels(modelsData.models || [])
        }, 1000)
      } else {
        setActionMessage({
          type: 'error',
          text: `❌ Promotion failed: ${result.message || 'Unknown error'}`,
        })
      }
    } catch (error) {
      console.error('Promotion error:', error)
      setActionMessage({
        type: 'error',
        text: `❌ Promotion error: ${error.message}`,
      })
    } finally {
      setActionLoading(null)
    }
  }

  const handleSeedDemo = async () => {
    setActionLoading('seed')
    setActionMessage(null)

    try {
      const result = await seedDemoRegistry()

      if (result.status === 'seeded') {
        setActionMessage({
          type: 'success',
          text: `✅ Demo registry seeded with ${result.created} models.`,
        })

        // Refresh after 1 second
        setTimeout(async () => {
          const comparisonData = await getComparison()
          setComparison(comparisonData)

          const modelsData = await getModels()
          setModels(modelsData.models || [])
        }, 1000)
      } else if (result.status === 'skipped') {
        setActionMessage({
          type: 'info',
          text: `ℹ️ Registry already has data. ${result.reason}`,
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
        <h1>Experiments & Model Registry</h1>
        <p>Compare and promote model versions. Manage champion and challenger models.</p>
      </div>

      {/* Champion vs Challenger Comparison Card */}
      {comparison && (
        <div className="card" style={{ marginBottom: '24px' }}>
          <h2>Champion vs Challenger Comparison</h2>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
            {/* Champion */}
            <div
              style={{
                padding: '16px',
                borderRadius: '8px',
                border: '2px solid #10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.05)',
              }}
            >
              <div style={{ color: '#10b981', fontSize: '12px', fontWeight: '600', marginBottom: '8px' }}>
                👑 CHAMPION (Production)
              </div>
              {comparison.champion ? (
                <div>
                  <div style={{ fontSize: '14px', marginBottom: '8px' }}>
                    <strong>{comparison.champion.model_name}</strong> {comparison.champion.model_version}
                  </div>
                  <div style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: '1.6' }}>
                    <div>Accuracy: {(comparison.champion.accuracy * 100).toFixed(1)}%</div>
                    <div>F1 Score: {(comparison.champion.f1_score * 100).toFixed(1)}%</div>
                    <div>
                      Drift:{' '}
                      {comparison.champion.drift_score !== null
                        ? (comparison.champion.drift_score * 100).toFixed(1) + '%'
                        : 'N/A'}
                    </div>
                  </div>
                </div>
              ) : (
                <div style={{ color: '#94a3b8' }}>No champion model</div>
              )}
            </div>

            {/* Challenger */}
            <div
              style={{
                padding: '16px',
                borderRadius: '8px',
                border: '2px solid #3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.05)',
              }}
            >
              <div style={{ color: '#3b82f6', fontSize: '12px', fontWeight: '600', marginBottom: '8px' }}>
                🚀 CHALLENGER (Staging)
              </div>
              {comparison.challenger ? (
                <div>
                  <div style={{ fontSize: '14px', marginBottom: '8px' }}>
                    <strong>{comparison.challenger.model_name}</strong> {comparison.challenger.model_version}
                  </div>
                  <div style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: '1.6' }}>
                    <div>Accuracy: {(comparison.challenger.accuracy * 100).toFixed(1)}%</div>
                    <div>F1 Score: {(comparison.challenger.f1_score * 100).toFixed(1)}%</div>
                    <div>
                      Drift:{' '}
                      {comparison.challenger.drift_score !== null
                        ? (comparison.challenger.drift_score * 100).toFixed(1) + '%'
                        : 'N/A'}
                    </div>
                  </div>
                </div>
              ) : (
                <div style={{ color: '#94a3b8' }}>No challenger model</div>
              )}
            </div>
          </div>

          {/* Deltas */}
          {comparison.accuracy_delta !== null && (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '12px',
                marginBottom: '24px',
                fontSize: '13px',
              }}
            >
              <div style={{ padding: '12px', backgroundColor: '#334155', borderRadius: '6px' }}>
                <div style={{ color: '#94a3b8', marginBottom: '4px' }}>Accuracy Delta</div>
                <div
                  style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    color: comparison.accuracy_delta > 0 ? '#10b981' : '#ef4444',
                  }}
                >
                  {comparison.accuracy_delta > 0 ? '+' : ''}
                  {(comparison.accuracy_delta * 100).toFixed(2)}%
                </div>
              </div>

              <div style={{ padding: '12px', backgroundColor: '#334155', borderRadius: '6px' }}>
                <div style={{ color: '#94a3b8', marginBottom: '4px' }}>F1 Delta</div>
                <div
                  style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    color: comparison.f1_delta >= 0 ? '#10b981' : '#ef4444',
                  }}
                >
                  {comparison.f1_delta >= 0 ? '+' : ''}
                  {(comparison.f1_delta * 100).toFixed(2)}%
                </div>
              </div>

              <div style={{ padding: '12px', backgroundColor: '#334155', borderRadius: '6px' }}>
                <div style={{ color: '#94a3b8', marginBottom: '4px' }}>Drift Delta</div>
                <div
                  style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    color:
                      comparison.drift_delta === null || comparison.drift_delta <= 0 ? '#10b981' : '#ef4444',
                  }}
                >
                  {comparison.drift_delta !== null ? (comparison.drift_delta <= 0 ? '-' : '+') : 'N/A'}
                  {comparison.drift_delta !== null ? (Math.abs(comparison.drift_delta) * 100).toFixed(2) + '%' : ''}
                </div>
              </div>
            </div>
          )}

          {/* Recommendation */}
          <div
            style={{
              padding: '16px',
              borderRadius: '8px',
              backgroundColor:
                comparison.recommendation === 'promote_challenger'
                  ? 'rgba(34, 197, 94, 0.1)'
                  : 'rgba(100, 116, 139, 0.1)',
              border: `2px solid ${
                comparison.recommendation === 'promote_challenger' ? '#22c55e' : '#64748b'
              }`,
            }}
          >
            <div
              style={{
                fontSize: '14px',
                fontWeight: '600',
                color: comparison.recommendation === 'promote_challenger' ? '#22c55e' : '#94a3b8',
                marginBottom: '8px',
              }}
            >
              {comparison.recommendation === 'promote_challenger'
                ? '✅ Ready to Promote'
                : '⏸️ Keep Current Champion'}
            </div>
            <div style={{ fontSize: '13px', color: '#cbd5e1' }}>{comparison.reason}</div>
          </div>
        </div>
      )}

      {/* Promotion Action Card */}
      {comparison && comparison.recommendation === 'promote_challenger' && comparison.challenger && (
        <div className="card" style={{ marginBottom: '24px' }}>
          <h2>Promotion Action</h2>
          <p style={{ color: '#cbd5e1', marginBottom: '16px' }}>
            Challenger model {comparison.challenger.model_version} is ready to be promoted to production.
          </p>

          <button
            className="action-button action-button-manual"
            onClick={handlePromoteChallenger}
            disabled={actionLoading !== null}
            style={{
              width: '100%',
              padding: '12px',
              fontSize: '14px',
              fontWeight: '600',
            }}
          >
            {actionLoading === 'promote' ? 'Promoting...' : '🚀 Promote Challenger to Production'}
          </button>

          {actionMessage && actionMessage.type === 'success' && (
            <div className="action-message action-message-success" style={{ marginTop: '12px' }}>
              {actionMessage.text}
            </div>
          )}
          {actionMessage && actionMessage.type === 'error' && (
            <div className="action-message action-message-error" style={{ marginTop: '12px' }}>
              {actionMessage.text}
            </div>
          )}
        </div>
      )}

      {/* Demo Seed Card */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <h2>Demo Setup</h2>
        <p style={{ color: '#cbd5e1', marginBottom: '16px' }}>
          Create demo model registry data (only if empty):
        </p>

        <button
          className="action-button"
          onClick={handleSeedDemo}
          disabled={actionLoading !== null}
          style={{
            backgroundColor: '#8b5cf6',
            width: '100%',
            padding: '12px',
            fontSize: '14px',
            fontWeight: '600',
          }}
        >
          {actionLoading === 'seed' ? 'Seeding...' : '🌱 Seed Demo Registry'}
        </button>

        {actionMessage && actionMessage.type === 'success' && actionLoading === null && (
          <div className="action-message action-message-success" style={{ marginTop: '12px' }}>
            {actionMessage.text}
          </div>
        )}
        {actionMessage && actionMessage.type === 'error' && actionLoading === null && (
          <div className="action-message action-message-error" style={{ marginTop: '12px' }}>
            {actionMessage.text}
          </div>
        )}
        {actionMessage && actionMessage.type === 'info' && actionLoading === null && (
          <div className="action-message action-message-info" style={{ marginTop: '12px' }}>
            {actionMessage.text}
          </div>
        )}
      </div>

      {/* Model Registry Table */}
      <div className="card">
        <h2>Model Registry</h2>
        <p style={{ color: '#cbd5e1', marginBottom: '16px' }}>
          All model versions with their metrics and deployment status.
        </p>
        <ModelRegistryTable models={models} />
      </div>
    </div>
  )
}

export default Experiments
