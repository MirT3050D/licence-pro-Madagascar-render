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

        <!-- Mode Tabs: Connexion vs Inscription -->
        <div class="auth-tabs">
          <button
            type="button"
            class="tab-btn"
            :class="{ active: !isRegisterMode }"
            @click="switchMode(false)"
          >
            Se connecter
          </button>
          <button
            type="button"
            class="tab-btn"
            :class="{ active: isRegisterMode }"
            @click="switchMode(true)"
          >
            Créer un compte
          </button>
        </div>

        <!-- Error banner -->
        <div v-if="errorMessage" class="error-banner animate-fade">
          <AlertCircle :size="18" class="flex-shrink-0" />
          <span>{{ errorMessage }}</span>
        </div>

        <!-- Success banner -->
        <div v-if="successMessage" class="success-banner animate-fade">
          <CheckCircle2 :size="18" class="flex-shrink-0" />
          <span>{{ successMessage }}</span>
        </div>

        <!-- 1. LOGIN FORM -->
        <form v-if="!isRegisterMode" @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label class="form-label">Adresse Email</label>
            <div class="input-with-icon">
              <Mail :size="18" class="input-icon" />
              <input
                v-model="loginEmail"
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
                v-model="loginPassword"
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

          <div class="switch-helper">
            <span>Pas encore de compte ?</span>
            <button type="button" @click="switchMode(true)" class="link-switch">Créer un compte</button>
          </div>
        </form>

        <!-- 2. REGISTRATION FORM -->
        <form v-else @submit.prevent="handleRegister" class="login-form">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Prénom</label>
              <div class="input-with-icon">
                <User :size="18" class="input-icon" />
                <input
                  v-model="regPrenom"
                  type="text"
                  required
                  class="form-input"
                  placeholder="Jean"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Nom</label>
              <div class="input-with-icon">
                <UserCheck :size="18" class="input-icon" />
                <input
                  v-model="regNom"
                  type="text"
                  required
                  class="form-input"
                  placeholder="Rakoto"
                />
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Numéro de téléphone</label>
            <div class="input-with-icon">
              <Phone :size="18" class="input-icon" />
              <input
                v-model="regNumero"
                type="tel"
                class="form-input"
                placeholder="034 00 000 00"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Adresse Email</label>
            <div class="input-with-icon">
              <Mail :size="18" class="input-icon" />
              <input
                v-model="regEmail"
                type="email"
                required
                autocomplete="email"
                class="form-input"
                placeholder="nom@entreprise.mg"
              />
            </div>
          </div>

          <!-- Role Selector -->
          <div class="form-group">
            <label class="form-label">Type de compte</label>
            <div class="role-selector">
              <label
                class="role-option"
                :class="{ selected: regRole === 'admin' }"
              >
                <input
                  type="radio"
                  value="admin"
                  v-model="regRole"
                  class="sr-only"
                />
                <div class="role-content">
                  <div class="role-badge-title">👑 Administrateur</div>
                  <div class="role-badge-desc">Accès total aux ventes, produits & utilisateurs</div>
                </div>
              </label>

              <label
                class="role-option"
                :class="{ selected: regRole === 'vendeur' }"
              >
                <input
                  type="radio"
                  value="vendeur"
                  v-model="regRole"
                  class="sr-only"
                />
                <div class="role-content">
                  <div class="role-badge-title">💼 Vendeur / Commercial</div>
                  <div class="role-badge-desc">Affilié, enregistrement des ventes & commission</div>
                </div>
              </label>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Mot de passe (min. 6 caractères)</label>
            <div class="input-with-icon">
              <Lock :size="18" class="input-icon" />
              <input
                v-model="regPassword"
                :type="showPassword ? 'text' : 'password'"
                required
                minlength="6"
                autocomplete="new-password"
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

          <div class="form-group">
            <label class="form-label">Confirmer le mot de passe</label>
            <div class="input-with-icon">
              <Lock :size="18" class="input-icon" />
              <input
                v-model="regPasswordConfirm"
                :type="showPassword ? 'text' : 'password'"
                required
                minlength="6"
                autocomplete="new-password"
                class="form-input"
                placeholder="••••••••••••"
              />
            </div>
          </div>

          <button type="submit" class="btn btn-primary btn-submit" :disabled="loading">
            <span v-if="loading">Création du compte...</span>
            <span v-else>Créer mon compte & Accéder</span>
            <ArrowRight :size="18" v-if="!loading" />
          </button>

          <div class="switch-helper">
            <span>Vous avez déjà un compte ?</span>
            <button type="button" @click="switchMode(false)" class="link-switch">Se connecter</button>
          </div>
        </form>

        <!-- Secure Connection Footer -->
        <div class="login-footer-notice">
          <div class="security-badge">
            <ShieldCheck :size="14" class="text-primary" />
            <span>Sécurisation SSL & Authentification JWT</span>
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
  User,
  UserCheck,
  Phone,
  ArrowRight,
  AlertCircle,
  CheckCircle2,
  Eye,
  EyeOff,
  ShieldCheck
} from '@lucide/vue'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { login, register } = useAuth()

const isRegisterMode = ref(false)
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Login fields
const loginEmail = ref('')
const loginPassword = ref('')

// Registration fields
const regNom = ref('')
const regPrenom = ref('')
const regNumero = ref('')
const regEmail = ref('')
const regRole = ref('admin')
const regPassword = ref('')
const regPasswordConfirm = ref('')

function switchMode(registerMode) {
  isRegisterMode.value = registerMode
  errorMessage.value = ''
  successMessage.value = ''
}

async function handleLogin() {
  if (!loginEmail.value || !loginPassword.value) {
    errorMessage.value = 'Veuillez saisir votre email et votre mot de passe.'
    return
  }

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const trimmedEmail = loginEmail.value.trim().toLowerCase()
    await login(trimmedEmail, loginPassword.value)
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

async function handleRegister() {
  if (regPassword.value !== regPasswordConfirm.value) {
    errorMessage.value = 'Les deux mots de passe ne correspondent pas.'
    return
  }
  if (regPassword.value.length < 6) {
    errorMessage.value = 'Le mot de passe doit comporter au moins 6 caractères.'
    return
  }

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const payload = {
      nom: regNom.value.trim(),
      prenom: regPrenom.value.trim(),
      numero: regNumero.value.trim(),
      email: regEmail.value.trim().toLowerCase(),
      role_type: regRole.value,
      password: regPassword.value,
      password_confirm: regPasswordConfirm.value
    }

    await register(payload)
    successMessage.value = 'Votre compte a été créé avec succès ! Connexion en cours...'
    setTimeout(() => {
      router.push('/')
    }, 800)
  } catch (err) {
    const errData = err.response?.data
    if (errData) {
      if (errData.email) {
        errorMessage.value = Array.isArray(errData.email) ? errData.email[0] : errData.email
      } else if (errData.password_confirm) {
        errorMessage.value = Array.isArray(errData.password_confirm) ? errData.password_confirm[0] : errData.password_confirm
      } else if (errData.detail) {
        errorMessage.value = Array.isArray(errData.detail) ? errData.detail[0] : errData.detail
      } else {
        errorMessage.value = 'Impossible de créer le compte. Vérifiez les informations saisies.'
      }
    } else {
      errorMessage.value = 'Erreur réseau ou serveur inaccessible. Veuillez réessayer.'
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
  max-width: 480px;
  z-index: 10;
}

.login-card {
  padding: 2.5rem 2.25rem;
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-card);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7), 0 0 25px rgba(0, 210, 255, 0.12);
}

.brand-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.logo-box {
  width: 82px;
  height: 82px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 210, 255, 0.18) 0%, rgba(6, 13, 25, 0.85) 100%);
  border: 2px solid rgba(0, 210, 255, 0.45);
  box-shadow: 0 0 25px rgba(0, 210, 255, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.15rem;
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
  margin-top: 0.25rem;
  letter-spacing: 0.02em;
}

/* Tabs switcher */
.auth-tabs {
  display: flex;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 0.25rem;
  margin-bottom: 1.75rem;
  gap: 0.25rem;
}

.tab-btn {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 0.6rem 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab-btn.active {
  background: var(--primary);
  color: #060d19;
  font-weight: 700;
  box-shadow: 0 2px 10px rgba(0, 210, 255, 0.35);
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

.success-banner {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: var(--emerald-bg);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #6ee7b7;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  margin-bottom: 1.5rem;
  font-size: 0.85rem;
}

.flex-shrink-0 {
  flex-shrink: 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem;
}

.form-group {
  margin-bottom: 1.15rem;
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

/* Role Selector */
.role-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-top: 0.35rem;
}

.role-option {
  border: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-md);
  padding: 0.75rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  flex-direction: column;
}

.role-option:hover {
  background: rgba(0, 210, 255, 0.05);
  border-color: rgba(0, 210, 255, 0.3);
}

.role-option.selected {
  border-color: var(--primary);
  background: rgba(0, 210, 255, 0.12);
  box-shadow: 0 0 12px rgba(0, 210, 255, 0.2);
}

.role-badge-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 0.2rem;
}

.role-badge-desc {
  font-size: 0.68rem;
  color: var(--text-secondary);
  line-height: 1.3;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
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

.switch-helper {
  margin-top: 1.25rem;
  text-align: center;
  font-size: 0.825rem;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}

.link-switch {
  background: none;
  border: none;
  color: var(--primary);
  font-weight: 700;
  cursor: pointer;
  text-decoration: underline;
  padding: 0;
  font-size: 0.825rem;
}

.link-switch:hover {
  color: #38bdf8;
}

.login-footer-notice {
  margin-top: 2rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
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
