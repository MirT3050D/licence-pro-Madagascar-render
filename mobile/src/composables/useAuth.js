import { ref, computed } from 'vue'
import apiClient from '../api/client'

const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
const token = ref(localStorage.getItem('access_token') || null)

export function useAuth() {
  const isAuthenticated = computed(() => !!token.value)
  const isSuperAdmin = computed(() => {
    if (!user.value) return false
    return (
      user.value.is_superuser ||
      user.value.is_staff ||
      (user.value.role && user.value.role.point >= 50) ||
      user.value.role?.nom === 'admin'
    )
  })
  const isMediaBuyer = computed(() => {
    if (!user.value) return false
    return (user.value.role && user.value.role.point === 10) || user.value.role?.nom === 'media_buyer'
  })
  const userPermissionPoints = computed(() => user.value?.role?.point || 0)

  async function login(email, password) {
    const res = await apiClient.post('/auth/login/', { email, password })
    token.value = res.data.access
    user.value = res.data.user

    localStorage.setItem('access_token', res.data.access)
    localStorage.setItem('refresh_token', res.data.refresh)
    localStorage.setItem('user', JSON.stringify(res.data.user))

    return res.data
  }

  async function register(registrationData) {
    const res = await apiClient.post('/auth/register/', registrationData)
    if (res.data.access) {
      token.value = res.data.access
      user.value = res.data.user

      localStorage.setItem('access_token', res.data.access)
      localStorage.setItem('refresh_token', res.data.refresh)
      localStorage.setItem('user', JSON.stringify(res.data.user))
    }

    return res.data
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  async function fetchProfile() {
    try {
      const res = await apiClient.get('/auth/profile/')
      user.value = res.data.user
      localStorage.setItem('user', JSON.stringify(res.data.user))
      return res.data
    } catch (err) {
      console.error('Erreur chargement profil:', err)
      return null
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    isSuperAdmin,
    isMediaBuyer,
    userPermissionPoints,
    login,
    register,
    logout,
    fetchProfile,
  }
}
