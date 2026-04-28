import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface User {
  id: number
  email: string
  username: string
  tags: string[]
  email_reports: boolean
  created_at: string
}

export interface ContentItem {
  id: number
  title: string
  description: string
  url: string
  source: string
  tags: string[]
  score: number
  published_at: string | null
  created_at: string
  match_score: number | null
}

export interface FeedResponse {
  items: ContentItem[]
  total: number
  page: number
  size: number
  pages: number
}

export const authApi = {
  register: (data: { email: string; username: string; password: string }) =>
    api.post<User>('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post<{ access_token: string; token_type: string }>('/auth/login', data),
  me: () => api.get<User>('/auth/me'),
}

export const contentApi = {
  getFeed: (page = 1, size = 20, source?: string) =>
    api.get<FeedResponse>('/content/feed', { params: { page, size, source } }),
  search: (q: string, page = 1, size = 20) =>
    api.get<FeedResponse>('/content/search', { params: { q, page, size } }),
  refresh: () => api.post('/content/refresh'),
}

export const userApi = {
  getProfile: () => api.get<User>('/users/profile'),
  updateTags: (tags: string[]) => api.put<User>('/users/tags', { tags }),
  updateProfile: (data: { email_reports?: boolean }) => api.put<User>('/users/profile', data),
}

export const reportApi = {
  getWeekly: () => api.get<ContentItem[]>('/reports/weekly'),
  send: () => api.post('/reports/send'),
}

export default api
