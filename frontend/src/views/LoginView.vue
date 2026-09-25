<template>
  <div class="login-page">
    <div class="glow-bg glow-1"></div>
    <div class="glow-bg glow-2"></div>

    <div class="login-container">
      <div class="login-card card">
        <!-- Logo & Header -->
        <div class="brand-header">
          <div class="logo-box">
            <img src="/logo.png" alt="Licence Pro Madagascar" class="login-logo-img" />
          </div>
          <h1>Licence Pro</h1>
          <p class="brand-tag">Portail Officiel Madagascar</p>
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
                placeholder="votre.email@licencepro.mg"
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

        <!-- Secure Connection Footer -->
        <div class="login-footer-notice">
          <div class="security-badge">
            <ShieldCheck :size="14" class="text-primary" />
            <span>Connexion chiffrée SSL / JWT</span>
          </div>
          <p class="copyright">© Licence Pro Madagascar — Tous droits réservés</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  Mail,
  Lock,
  ArrowRight,
  AlertCircle,
  Eye,
  EyeOff,
  ShieldCheck
} from '@lucide/vue'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { login } = useAuth()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  if (!email.value || !password.value) {
    errorMessage.value = 'Veuillez saisir votre email et votre mot de passe.'
    return
  }

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
  width: 520px;
  height: 520px;
  border-radius: 50%;
  filter: blur(140px);
  opacity: 0.22;
  pointer-events: none;
}

.glow-1 {
  background: var(--primary);
  top: -120px;
  left: -120px;
}

.glow-2 {
  background: var(--emerald);
  bottom: -120px;
  right: -120px;
}

.login-container {
  width: 100%;
  max-width: 440px;
  z-index: 10;
}

.login-card {
  padding: 2.75rem 2.25rem;
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-card);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7), 0 0 25px rgba(0, 210, 255, 0.12);
}

.brand-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-box {
  width: 86px;
  height: 86px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 210, 255, 0.18) 0%, rgba(6, 13, 25, 0.85) 100%);
  border: 2px solid rgba(0, 210, 255, 0.45);
  box-shadow: 0 0 25px rgba(0, 210, 255, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.25rem;
  overflow: hidden;
  transition: transform var(--transition-normal);
}

.logo-box:hover {
  transform: scale(1.05);
  box-shadow: 0 0 35px rgba(0, 210, 255, 0.55);
}

.login-logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.brand-header h1 {
  font-size: 1.85rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, #ffffff 30%, var(--primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-tag {
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
  margin-top: 0.3rem;
  letter-spacing: 0.02em;
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
  padding: 0.9rem;
  font-size: 0.95rem;
  margin-top: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.login-footer-notice {
  margin-top: 2rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
}

.security-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.text-primary {
  color: var(--primary);
}

.copyright {
  font-size: 0.7rem;
  color: var(--text-muted);
  opacity: 0.7;
}
</style>
