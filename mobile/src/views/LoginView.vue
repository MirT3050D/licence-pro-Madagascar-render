<template>
  <ion-page>
    <ion-content :fullscreen="true" class="login-content">
      <div class="login-wrapper">
        <!-- Logo & Branding -->
        <div class="brand-section">
          <div class="logo-box">
            <img src="/src/assets/logo.png" alt="Licence Pro Madagascar" class="login-logo" />
          </div>
          <h1 class="brand-title">Licence Pro</h1>
          <p class="brand-sub">Madagascar • Espace Mobile</p>
        </div>

        <!-- Auth Tabs: Connexion vs Inscription -->
        <div class="auth-card">
          <div class="auth-segment">
            <button
              :class="['seg-btn', !isRegister ? 'active' : '']"
              @click="isRegister = false"
            >
              Connexion
            </button>
            <button
              :class="['seg-btn', isRegister ? 'active' : '']"
              @click="isRegister = true"
            >
              Créer un compte
            </button>
          </div>

          <!-- Alert error -->
          <div v-if="errorMessage" class="error-box">
            {{ errorMessage }}
          </div>

          <!-- Alert success -->
          <div v-if="successMessage" class="success-box">
            {{ successMessage }}
          </div>

          <!-- LOGIN FORM -->
          <form v-if="!isRegister" @submit.prevent="submitLogin" class="form-body">
            <div class="form-group">
              <label class="form-lbl">Adresse Email</label>
              <input
                v-model="loginForm.email"
                type="email"
                required
                placeholder="votre.email@licencepro.mg"
                class="mobile-auth-input"
              />
            </div>

            <div class="form-group">
              <label class="form-lbl">Mot de passe</label>
              <div class="password-input-wrap">
                <input
                  v-model="loginForm.password"
                  :type="showLoginPassword ? 'text' : 'password'"
                  required
                  placeholder="••••••••••••"
                  class="mobile-auth-input"
                />
                <button
                  type="button"
                  class="btn-toggle-pwd"
                  @click="showLoginPassword = !showLoginPassword"
                  tabindex="-1"
                >
                  <ion-icon :icon="showLoginPassword ? eyeOffOutline : eyeOutline" />
                </button>
              </div>
            </div>

            <button type="submit" :disabled="loading" class="btn-auth-submit">
              <span v-if="loading">Connexion en cours...</span>
              <span v-else>Se connecter</span>
            </button>
          </form>

          <!-- REGISTER FORM -->
          <form v-else @submit.prevent="submitRegister" class="form-body">
            <div class="grid-2">
              <div class="form-group">
                <label class="form-lbl">Prénom *</label>
                <input
                  v-model="registerForm.prenom"
                  type="text"
                  required
                  placeholder="Jean"
                  class="mobile-auth-input"
                />
              </div>
              <div class="form-group">
                <label class="form-lbl">Nom *</label>
                <input
                  v-model="registerForm.nom"
                  type="text"
                  required
                  placeholder="Rakoto"
                  class="mobile-auth-input"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-lbl">Numéro WhatsApp / Téléphone *</label>
              <input
                v-model="registerForm.numero"
                type="tel"
                required
                placeholder="034 00 123 45"
                class="mobile-auth-input"
              />
            </div>

            <div class="form-group">
              <label class="form-lbl">Adresse Email *</label>
              <input
                v-model="registerForm.email"
                type="email"
                required
                placeholder="nom@exemple.mg"
                class="mobile-auth-input"
              />
            </div>

            <div class="form-group">
              <label class="form-lbl">Mot de passe *</label>
              <div class="password-input-wrap">
                <input
                  v-model="registerForm.password"
                  :type="showRegisterPassword ? 'text' : 'password'"
                  required
                  minlength="6"
                  placeholder="Minimum 6 caractères"
                  class="mobile-auth-input"
                />
                <button
                  type="button"
                  class="btn-toggle-pwd"
                  @click="showRegisterPassword = !showRegisterPassword"
                  tabindex="-1"
                >
                  <ion-icon :icon="showRegisterPassword ? eyeOffOutline : eyeOutline" />
                </button>
              </div>
            </div>

            <div class="form-group">
              <label class="form-lbl">Confirmer le mot de passe *</label>
              <div class="password-input-wrap">
                <input
                  v-model="registerForm.password_confirm"
                  :type="showRegisterPasswordConfirm ? 'text' : 'password'"
                  required
                  minlength="6"
                  placeholder="Répétez le mot de passe"
                  class="mobile-auth-input"
                />
                <button
                  type="button"
                  class="btn-toggle-pwd"
                  @click="showRegisterPasswordConfirm = !showRegisterPasswordConfirm"
                  tabindex="-1"
                >
                  <ion-icon :icon="showRegisterPasswordConfirm ? eyeOffOutline : eyeOutline" />
                </button>
              </div>
            </div>

            <button type="submit" :disabled="loading" class="btn-auth-submit register">
              <span v-if="loading">Création en cours...</span>
              <span v-else>Créer mon compte vendeur</span>
            </button>
          </form>
        </div>

        <p class="copyright-text">
          © 2026 Licence Pro Madagascar • Système Sécurisé
        </p>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { IonPage, IonContent, IonIcon } from '@ionic/vue'
import { eyeOutline, eyeOffOutline } from 'ionicons/icons'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { login, register } = useAuth()

const isRegister = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showLoginPassword = ref(false)
const showRegisterPassword = ref(false)
const showRegisterPasswordConfirm = ref(false)

const loginForm = ref({
  email: '',
  password: '',
})

const registerForm = ref({
  nom: '',
  prenom: '',
  numero: '',
  email: '',
  password: '',
  password_confirm: '',
})

async function submitLogin() {
  errorMessage.value = ''
  successMessage.value = ''
  loading.value = true

  try {
    await login(loginForm.value.email.trim(), loginForm.value.password)
    router.replace({ path: '/tabs/dashboard' })
  } catch (err) {
    errorMessage.value =
      err.response?.data?.detail ||
      err.response?.data?.error ||
      'Identifiants incorrects. Vérifiez votre adresse email et mot de passe.'
  } finally {
    loading.value = false
  }
}

async function submitRegister() {
  errorMessage.value = ''
  successMessage.value = ''

  if (
    !registerForm.value.prenom.trim() ||
    !registerForm.value.nom.trim() ||
    !registerForm.value.numero.trim() ||
    !registerForm.value.email.trim()
  ) {
    errorMessage.value = 'Veuillez renseigner tous les champs obligatoires.'
    return
  }

  if (registerForm.value.password.length < 6) {
    errorMessage.value = 'Le mot de passe doit comporter au moins 6 caractères.'
    return
  }

  if (registerForm.value.password !== registerForm.value.password_confirm) {
    errorMessage.value = 'Les mots de passe ne correspondent pas.'
    return
  }

  loading.value = true

  try {
    const res = await register({
      nom: registerForm.value.nom.trim(),
      prenom: registerForm.value.prenom.trim(),
      numero: registerForm.value.numero.trim(),
      email: registerForm.value.email.trim().toLowerCase(),
      password: registerForm.value.password,
      password_confirm: registerForm.value.password_confirm,
    })

    if (res.access) {
      router.replace({ path: '/tabs/dashboard' })
    } else {
      isRegister.value = false
      registerForm.value = {
        nom: '',
        prenom: '',
        numero: '',
        email: '',
        password: '',
        password_confirm: '',
      }
      successMessage.value =
        res.message ||
        'Votre compte vendeur a été créé avec succès ! Un administrateur doit valider votre accès.'
    }
  } catch (err) {
    const data = err.response?.data
    if (data && typeof data === 'object') {
      const fieldLabels = {
        nom: 'Nom',
        prenom: 'Prénom',
        numero: 'Numéro WhatsApp / Téléphone',
        email: 'Adresse email',
        password: 'Mot de passe',
        password_confirm: 'Confirmation du mot de passe',
      }
      const firstKey = Object.keys(data)[0]
      const rawMsg = Array.isArray(data[firstKey]) ? data[firstKey][0] : data[firstKey]
      if (firstKey && fieldLabels[firstKey]) {
        errorMessage.value = `${fieldLabels[firstKey]} : ${rawMsg}`
      } else if (typeof rawMsg === 'string') {
        errorMessage.value = rawMsg
      } else {
        errorMessage.value = JSON.stringify(rawMsg)
      }
    } else {
      errorMessage.value = "Impossible de créer le compte. Vérifiez les informations saisies."
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-content {
  --background: #0B1120;
  --color: #FFFFFF;
}

.login-wrapper {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 32px 20px;
}

.brand-section {
  text-align: center;
  margin-bottom: 24px;
}

.logo-box {
  display: inline-flex;
  padding: 12px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  margin-bottom: 12px;
}

.login-logo {
  height: 52px;
  width: auto;
  object-fit: contain;
}

.brand-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: #FFFFFF;
  margin: 0;
  letter-spacing: -0.02em;
}

.brand-sub {
  font-size: 0.8rem;
  color: #14B8A6;
  font-weight: 600;
  margin-top: 4px;
}

.auth-card {
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
}

.auth-segment {
  display: flex;
  background: #0B1120;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 20px;
}

.seg-btn {
  flex: 1;
  background: transparent;
  border: none;
  color: #94A3B8;
  padding: 10px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.seg-btn.active {
  background: #0D9488;
  color: #FFFFFF;
}

.error-box {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid #EF4444;
  color: #FCA5A5;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 0.82rem;
  margin-bottom: 16px;
}

.success-box {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid #10B981;
  color: #6EE7B7;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 0.82rem;
  margin-bottom: 16px;
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.form-lbl {
  font-size: 0.78rem;
  color: #94A3B8;
  margin-bottom: 6px;
  font-weight: 500;
}

.password-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.password-input-wrap .mobile-auth-input {
  padding-right: 46px;
}

.btn-toggle-pwd {
  position: absolute;
  right: 8px;
  background: transparent;
  border: none;
  color: #94A3B8;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  font-size: 1.25rem;
  cursor: pointer;
  z-index: 2;
}

.btn-toggle-pwd:focus {
  outline: none;
}

.mobile-auth-input {
  width: 100%;
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px 14px;
  color: #FFFFFF;
  font-size: 0.9rem;
  outline: none;
}

.mobile-auth-input:focus {
  border-color: #0D9488;
}

.btn-auth-submit {
  width: 100%;
  background: linear-gradient(135deg, #0D9488 0%, #0F766E 100%);
  color: #FFFFFF;
  border: none;
  padding: 14px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.95rem;
  margin-top: 8px;
}

.btn-auth-submit.register {
  background: linear-gradient(135deg, #0284C7 0%, #0D9488 100%);
}

.btn-auth-submit:disabled {
  opacity: 0.6;
}

.copyright-text {
  text-align: center;
  font-size: 0.72rem;
  color: #64748B;
  margin-top: 24px;
}
</style>
