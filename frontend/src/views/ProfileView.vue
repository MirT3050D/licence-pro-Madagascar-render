<template>
  <div class="profile-view">
    <div v-if="loading" class="loading-state">
      <RefreshCw :size="28" class="spin-icon text-primary" />
      <span>Chargement de votre profil...</span>
    </div>

    <div v-else class="profile-content">
      <!-- Top Grid: User Info & Performance Cards -->
      <div class="profile-grid">
        <!-- Personal Info Card -->
        <div class="card info-card">
          <div class="avatar-large">
            {{ userInitials }}
          </div>
          <div class="user-main-info">
            <h2>{{ profileData?.user?.prenom }} {{ profileData?.user?.nom }}</h2>
            <div class="role-pill">
              <ShieldCheck :size="14" />
              <span>{{ profileData?.user?.role?.label || 'Utilisateur' }}</span>
            </div>
          </div>

          <div class="contact-details">
            <div class="contact-item">
              <Mail :size="16" class="text-muted" />
              <span>{{ profileData?.user?.email }}</span>
            </div>
            <div class="contact-item">
              <Phone :size="16" class="text-muted" />
              <span>{{ profileData?.user?.numero || 'Aucun numéro configuré' }}</span>
            </div>
          </div>
        </div>

        <!-- Points d'habilitation & Permissions Card -->
        <div class="card balance-card">
          <div class="balance-header">
            <span class="text-sm text-muted">HABILITATION & PERMISSIONS</span>
            <Award :size="24" class="text-amber" />
          </div>

          <div class="points-hero">
            <span class="points-number">{{ profileData?.user?.role?.point || 0 }}</span>
            <span class="points-unit">Points d'accès</span>
          </div>

          <p class="balance-desc">
            <span v-if="profileData?.user?.role?.point >= 50" class="text-primary font-bold">
              👑 Niveau 50 (Administrateur) : Gestion totale, validation des comptes et enregistrement exclusif des ventes.
            </span>
            <span v-else class="text-secondary">
              💼 Niveau 10 (Media Buyer) : Consultation de son tableau de bord et suivi de ses ventes associées.
            </span>
          </p>

          <div class="stats-pills">
            <div class="stat-pill">
              <span class="pill-label">Ventes Associées</span>
              <span class="pill-val">{{ profileData?.statistiques?.total_ventes || 0 }}</span>
            </div>
            <div class="stat-pill">
              <span class="pill-label">Chiffre d'Affaires</span>
              <span class="pill-val text-emerald">{{ formatPrice(profileData?.statistiques?.chiffre_affaires) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Admin Team Management & Seller Approvals (Visible only to Admin) -->
      <div v-if="isSuperAdmin" class="card p-0 mt-4 admin-users-card">
        <div class="card-header-bar flex-between">
          <div>
            <h3>👑 Gestion de l'Équipe & Validation des Vendeurs</h3>
            <span class="text-xs text-muted">Validez les nouveaux inscrits et gérez les accès de votre équipe</span>
          </div>
          <button @click="loadUsers" class="btn btn-secondary btn-sm" :disabled="loadingUsers">
            <RefreshCw :size="14" :class="{ 'spin-icon': loadingUsers }" />
            <span>Actualiser</span>
          </button>
        </div>

        <div v-if="adminActionMessage" class="action-alert animate-fade">
          <CheckCircle2 :size="16" class="text-emerald flex-shrink-0" />
          <span>{{ adminActionMessage }}</span>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Utilisateur / Vendeur</th>
                <th>Coordonnées</th>
                <th>Rôle</th>
                <th>Statut d'accès</th>
                <th style="text-align: right;">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in usersList" :key="u.id">
                <td>
                  <div class="font-bold">{{ u.prenom }} {{ u.nom }}</div>
                  <div class="text-xs text-muted">Inscrit le {{ formatDate(u.created_at) }}</div>
                </td>
                <td>
                  <div class="font-mono text-sm">{{ u.email }}</div>
                  <div class="text-xs text-muted">{{ u.numero || 'Non renseigné' }}</div>
                </td>
                <td>
                  <span class="badge" :class="u.role?.nom === 'admin' ? 'badge-primary' : 'badge-neutral'">
                    {{ u.role?.label || 'Vendeur' }} ({{ u.role?.point || 0 }} pts)
                  </span>
                </td>
                <td>
                  <span v-if="u.is_active" class="badge badge-success">
                    <CheckCircle2 :size="13" />
                    <span>Actif</span>
                  </span>
                  <span v-else class="badge badge-warning pulse-badge">
                    <Clock :size="13" />
                    <span>En attente de validation</span>
                  </span>
                </td>
                <td style="text-align: right;">
                  <button
                    v-if="u.id !== profileData?.user?.id"
                    @click="toggleUserActive(u)"
                    class="btn btn-sm"
                    :class="u.is_active ? 'btn-danger-outline' : 'btn-success'"
                    :disabled="togglingId === u.id"
                  >
                    <span v-if="togglingId === u.id">Mise à jour...</span>
                    <span v-else-if="!u.is_active">✓ Valider & Activer</span>
                    <span v-else>Suspendre</span>
                  </button>
                  <span v-else class="text-xs text-muted font-italic">Votre compte</span>
                </td>
              </tr>
              <tr v-if="!usersList.length && !loadingUsers">
                <td colspan="5" class="text-center py-6 text-muted">
                  Aucun autre utilisateur enregistré.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Personal Sales History Table -->
      <div class="card p-0 mt-4">
        <div class="card-header-bar">
          <h3>Mes Ventes Récentes</h3>
          <span class="text-xs text-muted">Transactions enregistrées par mon compte</span>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Réf</th>
                <th>Date</th>
                <th>Client</th>
                <th>Méthode</th>
                <th style="text-align: right;">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="vente in profileData?.ventes_recentes || []" :key="vente.id">
                <td><span class="font-mono font-bold text-primary">#{{ vente.id }}</span></td>
                <td>{{ formatDate(vente.date) }}</td>
                <td class="font-bold">{{ vente.client_nom }}</td>
                <td><span class="badge badge-primary">{{ vente.methode_paiement }}</span></td>
                <td style="text-align: right;" class="font-bold text-emerald">{{ formatPrice(vente.total) }}</td>
              </tr>
              <tr v-if="!profileData?.ventes_recentes?.length">
                <td colspan="5" class="text-center py-6 text-muted">
                  Vous n'avez pas encore enregistré de ventes personnelles.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  ShieldCheck,
  Mail,
  Phone,
  Award,
  RefreshCw,
  CheckCircle2,
  Clock
} from '@lucide/vue'
import { useAuth } from '../composables/useAuth'
import apiClient from '../api/client'

const { fetchProfile, isSuperAdmin } = useAuth()
const loading = ref(false)
const profileData = ref(null)

// Admin team management state
const usersList = ref([])
const loadingUsers = ref(false)
const togglingId = ref(null)
const adminActionMessage = ref('')

const userInitials = computed(() => {
  const u = profileData.value?.user
  if (!u) return 'LP'
  const p = u.prenom ? u.prenom[0].toUpperCase() : ''
  const n = u.nom ? u.nom[0].toUpperCase() : ''
  return p + n || 'LP'
})

async function loadProfileData() {
  loading.value = true
  try {
    profileData.value = await fetchProfile()
  } finally {
    loading.value = false
  }
}

async function loadUsers() {
  if (!isSuperAdmin.value) return
  loadingUsers.value = true
  try {
    const res = await apiClient.get('/auth/users/')
    usersList.value = res.data.results || res.data || []
  } catch (err) {
    console.error('Erreur chargement utilisateurs:', err)
  } finally {
    loadingUsers.value = false
  }
}

async function toggleUserActive(userItem) {
  togglingId.value = userItem.id
  adminActionMessage.value = ''
  try {
    const res = await apiClient.post(`/auth/users/${userItem.id}/toggle_active/`)
    userItem.is_active = res.data.is_active
    adminActionMessage.value = res.data.message
    setTimeout(() => {
      adminActionMessage.value = ''
    }, 4500)
  } catch (err) {
    console.error('Erreur activation utilisateur:', err)
  } finally {
    togglingId.value = null
  }
}

function formatPrice(val) {
  return new Intl.NumberFormat('fr-MG').format(val || 0) + ' Ar'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('fr-FR', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(async () => {
  await loadProfileData()
  if (isSuperAdmin.value) {
    loadUsers()
  }
})
</script>

<style scoped>
.profile-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  gap: 1rem;
  color: var(--text-muted);
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 900px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}

.info-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 2.25rem 1.5rem;
}

.avatar-large {
  width: 76px;
  height: 76px;
  border-radius: 50%;
  background: var(--gradient-brand);
  color: #060d19;
  font-size: 1.75rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
  box-shadow: 0 0 20px rgba(0, 210, 255, 0.4);
}

.user-main-info h2 {
  font-size: 1.35rem;
  margin-bottom: 0.35rem;
}

.role-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--primary-light);
  border: 1px solid rgba(0, 210, 255, 0.35);
  color: var(--primary);
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.contact-details {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  width: 100%;
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-subtle);
}

.contact-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.balance-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1.75rem;
}

.balance-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.points-hero {
  margin: 1.25rem 0;
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.points-number {
  font-size: 3.5rem;
  font-weight: 900;
  line-height: 1;
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.points-unit {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-secondary);
}

.balance-desc {
  font-size: 0.825rem;
  color: var(--text-muted);
  line-height: 1.5;
  margin-bottom: 1.5rem;
}

.stats-pills {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.stat-pill {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
}

.pill-label {
  font-size: 0.7rem;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}

.pill-val {
  font-size: 1.25rem;
  font-weight: 800;
}

.flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header-bar {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-subtle);
}

.card-header-bar h3 {
  font-size: 1.05rem;
}

.admin-users-card {
  border: 1px solid rgba(0, 210, 255, 0.25);
  box-shadow: 0 0 25px rgba(0, 210, 255, 0.08);
}

.action-alert {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: var(--emerald-bg);
  border-bottom: 1px solid rgba(16, 185, 129, 0.3);
  color: #6ee7b7;
  padding: 0.75rem 1.5rem;
  font-size: 0.85rem;
}

.pulse-badge {
  animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
  0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
  70% { box-shadow: 0 0 0 8px rgba(245, 158, 11, 0); }
  100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
}

.badge-neutral {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-secondary);
}

.btn-success {
  background: var(--gradient-emerald);
  color: white;
  border: none;
  font-weight: 700;
  box-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);
}

.btn-success:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.btn-danger-outline {
  background: transparent;
  border: 1px solid rgba(244, 63, 94, 0.4);
  color: #fda4af;
}

.btn-danger-outline:hover {
  background: rgba(244, 63, 94, 0.15);
  border-color: rgba(244, 63, 94, 0.7);
}

.font-italic {
  font-style: italic;
}
</style>
