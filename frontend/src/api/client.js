import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Health check
export const getHealth = async () => {
  try {
    const response = await client.get('/health')
    return response.data
  } catch (error) {
    console.error('Health check failed:', error)
    return { status: 'offline' }
  }
}

// Predictions
export const getRecentPredictions = async (limit = 20) => {
  try {
    const response = await client.get(`/api/v1/predictions/recent?limit=${limit}`)
    return response.data
  } catch (error) {
    console.error('Failed to fetch recent predictions:', error)
    return []
  }
}

// Labels
export const getRecentLabels = async (limit = 20) => {
  try {
    const response = await client.get(`/api/v1/labels/recent?limit=${limit}`)
    return response.data
  } catch (error) {
    console.error('Failed to fetch recent labels:', error)
    return []
  }
}

// Drift
export const getDriftSummary = async (modelName = 'credit_risk', modelVersion = 'v1') => {
  try {
    const response = await client.get(
      `/api/v1/drift/summary?model_name=${modelName}&model_version=${modelVersion}`
    )
    return response.data
  } catch (error) {
    console.error('Failed to fetch drift summary:', error)
    return null
  }
}

export const getLatestDriftMetrics = async (modelName = 'credit_risk', modelVersion = 'v1') => {
  try {
    const response = await client.get(
      `/api/v1/drift/latest?model_name=${modelName}&model_version=${modelVersion}`
    )
    return response.data
  } catch (error) {
    console.error('Failed to fetch latest drift metrics:', error)
    return null
  }
}

export const runDriftCalculation = async (modelName = 'credit_risk', modelVersion = 'v1') => {
  try {
    const response = await client.post(
      `/api/v1/drift/run?model_name=${modelName}&model_version=${modelVersion}`
    )
    return response.data
  } catch (error) {
    console.error('Failed to run drift calculation:', error)
    return null
  }
}

// Retraining - Celery local
export const checkAndTriggerRetraining = async () => {
  try {
    const response = await client.post('/api/v1/retraining/check-and-trigger')
    return response.data
  } catch (error) {
    console.error('Failed to check and trigger retraining:', error)
    return { status: 'error', reason: error.message }
  }
}

export const manualTriggerRetraining = async () => {
  try {
    const response = await client.post('/api/v1/retraining/manual-trigger')
    return response.data
  } catch (error) {
    console.error('Failed to manually trigger retraining:', error)
    return { status: 'error', reason: error.message }
  }
}

export const getRetrainingRuns = async (limit = 20) => {
  try {
    const response = await client.get(`/api/v1/retraining/runs?limit=${limit}`)
    return response.data
  } catch (error) {
    console.error('Failed to fetch retraining runs:', error)
    return { runs: [], total_count: 0 }
  }
}

export const getLatestRetrainingRun = async () => {
  try {
    const response = await client.get('/api/v1/retraining/runs/latest')
    return response.data
  } catch (error) {
    console.error('Failed to fetch latest retraining run:', error)
    return { run: null }
  }
}

// GitHub Actions
export const getGitHubActionsConfigStatus = async () => {
  try {
    const response = await client.get('/api/v1/github-actions/config-status')
    return response.data
  } catch (error) {
    console.error('Failed to fetch GitHub Actions config status:', error)
    return { configured: false, missing: ['GITHUB_TOKEN', 'GITHUB_OWNER', 'GITHUB_REPO'] }
  }
}

export const triggerGitHubActionsRetraining = async (modelName = 'credit_risk', modelVersion = 'v1', triggerReason = 'manual') => {
  try {
    const response = await client.post('/api/v1/github-actions/trigger-retraining', {
      model_name: modelName,
      model_version: modelVersion,
      trigger_reason: triggerReason,
    })
    return response.data
  } catch (error) {
    console.error('Failed to trigger GitHub Actions retraining:', error)
    return { status: 'error', message: error.message }
  }
}

// Model Registry
export const registerModel = async (modelData) => {
  try {
    const response = await client.post('/api/v1/model-registry/register', modelData)
    return response.data
  } catch (error) {
    console.error('Failed to register model:', error)
    return { status: 'error', message: error.message }
  }
}

export const getModels = async () => {
  try {
    const response = await client.get('/api/v1/model-registry/models')
    return response.data
  } catch (error) {
    console.error('Failed to fetch models:', error)
    return { models: [], total_count: 0 }
  }
}

export const getChampion = async () => {
  try {
    const response = await client.get('/api/v1/model-registry/champion')
    return response.data
  } catch (error) {
    console.error('Failed to fetch champion model:', error)
    return null
  }
}

export const getChallenger = async () => {
  try {
    const response = await client.get('/api/v1/model-registry/challenger')
    return response.data
  } catch (error) {
    console.error('Failed to fetch challenger model:', error)
    return null
  }
}

export const getComparison = async () => {
  try {
    const response = await client.get('/api/v1/model-registry/comparison')
    return response.data
  } catch (error) {
    console.error('Failed to fetch model comparison:', error)
    return {
      champion: null,
      challenger: null,
      accuracy_delta: null,
      f1_delta: null,
      drift_delta: null,
      recommendation: 'keep_champion',
      reason: 'Unable to fetch comparison data'
    }
  }
}

export const promoteChallenger = async () => {
  try {
    const response = await client.post('/api/v1/model-registry/promote')
    return response.data
  } catch (error) {
    console.error('Failed to promote challenger:', error)
    return { status: 'error', message: error.message }
  }
}

export const seedDemoRegistry = async () => {
  try {
    const response = await client.post('/api/v1/model-registry/seed-demo')
    return response.data
  } catch (error) {
    console.error('Failed to seed demo registry:', error)
    return { status: 'error', message: error.message }
  }
}

export default client

