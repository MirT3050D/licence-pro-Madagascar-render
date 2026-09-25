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

        <!-- Commission & Points Balance Card -->
        <div class="card balance-card">
          <div class="balance-header">
            <span class="text-sm text-muted">SOLDE DE POINTS & COMMISSIONS</span>
            <Award :size="24" class="text-amber" />
          </div>

          <div class="points-hero">
            <span class="points-number">{{ profileData?.statistiques?.points || 0 }}</span>
            <span class="points-unit">Points</span>
          </div>

          <p class="balance-desc">
            Vos points sont indexés sur votre statut de vendeur ({{ profileData?.user?.role?.nom }}). Chaque vente contribue à votre solde de commissions.
          </p>

          <div class="stats-pills">
            <div class="stat-pill">
              <span class="pill-label">Mes Ventes</span>
              <span class="pill-val">{{ profileData?.statistiques?.total_ventes || 0 }}</span>
            </div>
            <div class="stat-pill">
              <span class="pill-label">Chiffre d'Affaires</span>
              <span class="pill-val text-emerald">{{ formatPrice(profileData?.statistiques?.chiffre_affaires) }}</span>
            </div>
          </div>
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
  RefreshCw
} from '@lucide/vue'
import { useAuth } from '../composables/useAuth'

const { fetchProfile } = useAuth()
const loading = ref(false)
const profileData = ref(null)

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

onMounted(() => {
  loadProfileData()
})
</script>

<style scoped>
.profile-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1.3fr;
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
  padding: 2rem;
  gap: 1rem;
}

.avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--gradient-brand);
  color: white;
  font-size: 1.8rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
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
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: #818cf8;
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
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-subtle);
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.balance-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 2rem;
}

.balance-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 700;
}

.points-hero {
  display: flex;
  align-items: baseline;
  gap: 0.65rem;
  margin: 1.25rem 0;
}

.points-number {
  font-size: 3.5rem;
  font-weight: 900;
  letter-spacing: -0.04em;
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.points-unit {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f59e0b;
}

.balance-desc {
  font-size: 0.825rem;
  color: var(--text-secondary);
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
  padding: 0.85rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.pill-label {
  font-size: 0.725rem;
  color: var(--text-muted);
}

.pill-val {
  font-size: 1.1rem;
  font-weight: 800;
}

.card-header-bar {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header-bar h3 {
  font-size: 1.05rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  gap: 1rem;
}
</style>
