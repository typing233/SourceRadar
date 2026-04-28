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

export default api
