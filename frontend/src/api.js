import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({ baseURL: BASE_URL })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// Auth
export const register = (email, password) =>
  api.post('/auth/register', { email, password })

export const login = (email, password) =>
  api.post('/auth/login', { email, password })

export const getMe = () => api.get('/auth/me')

// Items / Feed
export const getFeed = (params) => api.get('/items', { params })

// Tags & Settings
export const getTags = () => api.get('/user/tags')

export const updateTags = (tags) => api.put('/user/tags', { tags })

export const updateSettings = (settings) => api.put('/user/settings', settings)

// Digest
export const getDigest = () => api.get('/digest')

export const generateDigest = () => api.post('/digest/generate')

// LLM Configuration
export const getLLMConfig = () => api.get('/llm/config')

export const updateLLMConfig = (config) => api.put('/llm/config', config)

export const testLLMConnection = () => api.post('/llm/test-connection')

export const analyzeItem = (itemId) => api.post(`/llm/analyze-item/${itemId}`)

export const analyzeAllItems = () => api.post('/llm/analyze-all')

// Clustering & Topology
export const getCategories = () => api.get('/cluster/categories')

export const getClusters = (params) => api.get('/cluster/list', { params })

export const getTopology = (params) => api.get('/cluster/topology', { params })

export default api
