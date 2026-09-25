<template>
  <div class="login-page">
    <div class="glow-bg glow-1"></div>
    <div class="glow-bg glow-2"></div>

    <div class="login-container">
      <div class="login-card card">
        <!-- Logo & Header -->
        <div class="brand-header">
          <div class="logo-box">
            <ShieldCheck :size="32" />
          </div>
          <h1>Licence Pro</h1>
          <p class="brand-tag">Portail de gestion Madagascar</p>
        </div>

        <!-- Error banner -->
        <div v-if="errorMessage" class="error-banner animate-fade">
          <AlertCircle :size="18" class="flex-shrink-0" />
          <span>{{ errorMessage }}</span>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label class="form-label">Adresse Email</label>
            <div class="input-with-icon">
              <Mail :size="18" class="input-icon" />
              <input
                v-model="email"
                type="email"
                required
                autocomplete="email"
                class="form-input"
                placeholder="admin@licencepro.mg"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Mot de passe</label>
            <div class="input-with-icon">
              <Lock :size="18" class="input-icon" />
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="current-password"
                class="form-input"
                placeholder="••••••••••••"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="btn-eye"
                title="Afficher/masquer le mot de passe"
              >
                <Eye :size="16" v-if="!showPassword" />
                <EyeOff :size="16" v-else />
              </button>
            </div>
          </div>

          <button type="submit" class="btn btn-primary btn-submit" :disabled="loading">
            <span v-if="loading">Connexion en cours...</span>
            <span v-else>Se connecter</span>
            <ArrowRight :size="18" v-if="!loading" />
          </button>
        </form>

        <!-- Quick 1-Click Connect Demo Buttons -->
        <div class="demo-helpers">
          <div class="demo-divider">
            <span>Connexion rapide en 1 clic</span>
          </div>
          <div class="demo-buttons">
            <button @click="quickLogin('admin')" type="button" class="btn-demo" :disabled="loading">
              <div class="demo-header">
                <strong>👑 Admin</strong>
                <span class="badge-quick">1 clic</span>
              </div>
              <span class="demo-email">admin@licencepro.mg</span>
            </button>

            <button @click="quickLogin('vendeur')" type="button" class="btn-demo" :disabled="loading">
              <div class="demo-header">
                <strong>💼 Vendeur</strong>
                <span class="badge-quick">1 clic</span>
              </div>
              <span class="demo-email">vendeur@licencepro.mg</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ShieldCheck,
  Mail,
  Lock,
  ArrowRight,
  AlertCircle,
  Eye,
  EyeOff
} from '@lucide/vue'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { login } = useAuth()

const email = ref('admin@licencepro.mg')
const password = ref('adminpassword123')
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')

async function quickLogin(role) {
  if (role === 'admin') {
    email.value = 'admin@licencepro.mg'
    password.value = 'adminpassword123'
  } else {
    email.value = 'vendeur@licencepro.mg'
    password.value = 'vendeurpassword123'
  }
  await handleLogin()
}

async function handleLogin() {
  loading.value = true
  errorMessage.value = ''
  try {
    const trimmedEmail = email.value.trim().toLowerCase()
    await login(trimmedEmail, password.value)
    router.push('/')
  } catch (err) {
    const detail = err.response?.data?.detail
    if (typeof detail === 'string') {
      errorMessage.value = detail
    } else if (Array.isArray(detail)) {
      errorMessage.value = detail[0]
    } else {
      errorMessage.value = err.response?.data?.error || 'Identifiants invalides ou serveur indisponible.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-app);
  position: relative;
  overflow: hidden;
  padding: 1.5rem;
}

.glow-bg {
  position: absolute;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.25;
  pointer-events: none;
}

.glow-1 {
  background: #6366f1;
  top: -100px;
  left: -100px;
}

.glow-2 {
  background: #d946ef;
  bottom: -100px;
  right: -100px;
}

.login-container {
  width: 100%;
  max-width: 440px;
  z-index: 10;
}

.login-card {
  padding: 2.5rem;
  border-radius: var(--radius-xl);
}

.brand-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-box {
  width: 60px;
  height: 60px;
  border-radius: var(--radius-lg);
  background: var(--gradient-brand);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  box-shadow: 0 10px 25px rgba(99, 102, 241, 0.4);
}

.brand-header h1 {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.03em;
}

.brand-tag {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: var(--rose-bg);
  border: 1px solid rgba(244, 63, 94, 0.3);
  color: #fda4af;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  margin-bottom: 1.5rem;
  font-size: 0.85rem;
}

.flex-shrink-0 {
  flex-shrink: 0;
}

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  color: var(--text-muted);
  pointer-events: none;
}

.input-with-icon .form-input {
  width: 100%;
  padding-left: 2.75rem;
  padding-right: 2.5rem;
}

.btn-eye {
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-eye:hover {
  color: var(--text-main);
}

.btn-submit {
  width: 100%;
  padding: 0.85rem;
  font-size: 0.95rem;
  margin-top: 0.5rem;
}

.demo-helpers {
  margin-top: 2rem;
}

.demo-divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.75rem;
  margin-bottom: 1rem;
}

.demo-divider::before,
.demo-divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid var(--border-subtle);
}

.demo-divider span {
  padding: 0 0.75rem;
}

.demo-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.btn-demo {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 0.75rem 0.65rem;
  text-align: left;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.demo-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.btn-demo strong {
  font-size: 0.825rem;
  color: var(--text-main);
}

.badge-quick {
  background: var(--primary-light);
  color: #a5b4fc;
  font-size: 0.65rem;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  font-weight: 700;
}

.demo-email {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.btn-demo:hover {
  background: rgba(99, 102, 241, 0.12);
  border-color: rgba(99, 102, 241, 0.4);
  transform: translateY(-1px);
}
</style>
