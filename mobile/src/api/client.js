import axios from 'axios'

// Determine the base URL. If running in Capacitor native (file:// or capacitor://), relative '/api' won't work.
const isNative = typeof window !== 'undefined' && (window.location.protocol === 'capacitor:' || window.location.protocol === 'file:')
const defaultProductionUrl = 'https://licence-pro-madagascar-render.onrender.com/api'

const baseURL = import.meta.env.VITE_API_URL 
  ? (isNative && import.meta.env.VITE_API_URL.startsWith('/') ? defaultProductionUrl : import.meta.env.VITE_API_URL)
  : (isNative ? defaultProductionUrl : '/api')

const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to attach JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          const res = await axios.post(`${baseURL}/auth/refresh/`, {
            refresh: refreshToken,
          })
          const newAccess = res.data.access
          localStorage.setItem('access_token', newAccess)
          originalRequest.headers.Authorization = `Bearer ${newAccess}`
          return apiClient(originalRequest)
        } catch (refreshErr) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
        }
      } else {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
