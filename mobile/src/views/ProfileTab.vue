<template>
  <ion-page>
    <ion-header :translucent="true">
      <ion-toolbar class="main-toolbar">
        <ion-title>Mon Compte & Profil</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="handleLogout" class="btn-logout-icon">
            <ion-icon :icon="logOutOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" class="profile-content">
      <ion-refresher slot="fixed" @ionRefresh="handleRefresh($event)">
        <ion-refresher-content></ion-refresher-content>
      </ion-refresher>

      <!-- Profile Header Card -->
      <div class="user-profile-card">
        <div class="profile-avatar-wrap">
          <div class="profile-avatar">
            {{ userInitials }}
          </div>
          <span class="role-badge" :class="isSuperAdmin ? 'admin' : 'seller'">
            {{ user?.role?.label || 'Vendeur' }}
          </span>
        </div>

        <h2 class="user-fullname">{{ user?.prenom }} {{ user?.nom }}</h2>
        <span class="user-email">{{ user?.email }}</span>
        <span class="user-phone" v-if="user?.numero">📞 {{ user?.numero }}</span>

        <!-- Commission & Points Badge -->
        <div class="points-pill-card">
          <div class="points-col">
            <span class="p-num">{{ user?.role?.point || 0 }}</span>
            <span class="p-sub">Niveau Habilitation</span>
          </div>
          <div class="p-divider"></div>
          <div class="points-col">
            <span class="p-num text-green">{{ profileStats.total_ventes || 0 }}</span>
            <span class="p-sub">Ventes Associées</span>
          </div>
          <div class="p-divider"></div>
          <div class="points-col">
            <span class="p-num text-teal">{{ formatPrice(profileStats.chiffre_affaires) }}</span>
            <span class="p-sub">Chiffre d'Affaires</span>
          </div>
        </div>
      </div>

      <!-- Admin Console (Visible only to Admin level >= 50) -->
      <div v-if="isSuperAdmin" class="admin-console-card">
        <div class="admin-header">
          <div>
            <h3 class="admin-title">👑 Administration Équipe</h3>
            <span class="admin-sub">Validation des comptes vendeurs</span>
          </div>
          <button @click="loadUsers" class="btn-refresh-sm">
            <ion-icon :icon="refreshOutline" />
          </button>
        </div>

        <div v-if="usersList.length === 0" class="empty-users">
          <span>Aucun utilisateur enregistré.</span>
        </div>

        <div v-else class="users-mobile-list">
          <div v-for="u in usersList" :key="u.id" class="user-item-card">
            <div class="u-top">
              <span class="u-name">{{ u.prenom }} {{ u.nom }}</span>
              <span :class="['u-status-badge', u.is_active ? 'active' : 'pending']">
                {{ u.is_active ? 'Actif' : 'En attente' }}
              </span>
            </div>
            <span class="u-meta">{{ u.email }} • {{ u.role?.label || 'Sans rôle' }}</span>

            <!-- Action buttons for admin -->
            <div class="u-actions" v-if="!u.is_superuser && u.id !== user?.id">
              <button
                v-if="!u.is_active"
                @click="approveUser(u)"
                class="btn-u-action approve"
              >
                <ion-icon :icon="checkmarkCircleOutline" />
                <span>Valider le compte</span>
              </button>
              <button
                v-else
                @click="toggleUserActive(u)"
                class="btn-u-action deactivate"
              >
                <span>Désactiver l'accès</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Connection / Server Info -->
      <div class="info-card-box">
        <h4 class="info-title">Connexion Système</h4>
        <div class="info-line">
          <span>Environnement API :</span>
          <b>{{ apiServerLabel }}</b>
        </div>
        <div class="info-line">
          <span>Application Mobile :</span>
          <b>v1.0.0 (Capacitor + Ionic)</b>
        </div>
      </div>

      <!-- Logout Button -->
      <div class="logout-wrap">
        <button class="btn-logout" @click="handleLogout">
          <ion-icon :icon="logOutOutline" />
          <span>Se déconnecter</span>
        </button>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonButton,
  IonIcon,
  IonContent,
  IonRefresher,
  IonRefresherContent,
  alertController,
  toastController,
} from '@ionic/vue'
import {
  logOutOutline,
  refreshOutline,
  checkmarkCircleOutline,
} from 'ionicons/icons'
import apiClient from '../api/client'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { user, isSuperAdmin, logout, fetchProfile } = useAuth()

const profileStats = ref({
  total_ventes: 0,
  chiffre_affaires: 0,
})
const usersList = ref([])

const userInitials = computed(() => {
  const p = user.value?.prenom || ''
  const n = user.value?.nom || ''
  if (!p && !n) return 'U'
  return ((p[0] || '') + (n[0] || '')).toUpperCase()
})

const apiServerLabel = computed(() => {
  const url = import.meta.env.VITE_API_URL || '/api'
  return url.includes('render.com') ? 'Production Cloud (Render)' : 'Serveur Local (Dev)'
})

function formatPrice(val) {
  if (!val && val !== 0) return '0 Ar'
  return Math.round(val).toLocaleString('fr-FR') + ' Ar'
}

async function loadData() {
  await fetchProfile()
  try {
    const res = await apiClient.get('/auth/profile/')
    if (res.data?.statistiques) {
      profileStats.value = res.data.statistiques
    }
  } catch (e) {
    console.error(e)
  }

  if (isSuperAdmin.value) {
    loadUsers()
  }
}

async function loadUsers() {
  try {
    const res = await apiClient.get('/auth/users/')
    usersList.value = res.data.results || res.data || []
  } catch (e) {
    console.error('Erreur users:', e)
  }
}

async function approveUser(u) {
  try {
    await apiClient.post(`/auth/users/${u.id}/approve/`)
    const toast = await toastController.create({
      message: `Compte de ${u.prenom} validé avec succès.`,
      duration: 2000,
      color: 'success',
      position: 'top',
    })
    await toast.present()
    loadUsers()
  } catch (e) {
    alert("Erreur lors de l'approbation.")
  }
}

async function toggleUserActive(u) {
  try {
    await apiClient.post(`/auth/users/${u.id}/toggle-active/`)
    loadUsers()
  } catch (e) {
    // fallback
  }
}

async function handleRefresh(event) {
  await loadData()
  event.target.complete()
}

async function handleLogout() {
  const alert = await alertController.create({
    header: 'Déconnexion',
    message: 'Êtes-vous sûr de vouloir vous déconnecter de votre compte ?',
    buttons: [
      { text: 'Annuler', role: 'cancel' },
      {
        text: 'Déconnexion',
        role: 'destructive',
        handler: () => {
          logout()
          router.replace({ name: 'login' })
        },
      },
    ],
  })
  await alert.present()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.main-toolbar {
  --background: #0B1120;
  --color: #FFFFFF;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.btn-logout-icon {
  --color: #EF4444;
  font-size: 20px;
}

.profile-content {
  --background: #0B1120;
  --color: #F8FAFC;
}

.user-profile-card {
  margin: 16px;
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.profile-avatar-wrap {
  position: relative;
  margin-bottom: 12px;
}

.profile-avatar {
  width: 72px;
  height: 72px;
  border-radius: 24px;
  background: linear-gradient(135deg, #0D9488 0%, #0284C7 100%);
  color: #FFFFFF;
  font-size: 1.6rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 25px -5px rgba(13, 148, 136, 0.4);
}

.role-badge {
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 9999px;
  white-space: nowrap;
}

.role-badge.admin {
  background: #F59E0B;
  color: #0F172A;
}

.role-badge.seller {
  background: #0D9488;
  color: #FFFFFF;
}

.user-fullname {
  font-size: 1.25rem;
  font-weight: 800;
  color: #FFFFFF;
  margin: 6px 0 2px 0;
}

.user-email {
  font-size: 0.8rem;
  color: #94A3B8;
}

.user-phone {
  font-size: 0.8rem;
  color: #38BDF8;
  margin-top: 4px;
}

.points-pill-card {
  width: 100%;
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 12px;
  margin-top: 18px;
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.points-col {
  display: flex;
  flex-direction: column;
}

.p-num {
  font-size: 1.15rem;
  font-weight: 800;
  color: #FFFFFF;
}

.p-num.text-green { color: #10B981; }
.p-num.text-teal { color: #14B8A6; }

.p-sub {
  font-size: 0.65rem;
  color: #64748B;
  margin-top: 2px;
}

.p-divider {
  width: 1px;
  height: 30px;
  background: rgba(255, 255, 255, 0.08);
}

.admin-console-card {
  margin: 16px;
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 16px;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.admin-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #F8FAFC;
  margin: 0;
}

.admin-sub {
  font-size: 0.72rem;
  color: #94A3B8;
}

.btn-refresh-sm {
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #CBD5E1;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.users-mobile-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.user-item-card {
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 10px;
}

.u-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.u-name {
  font-size: 0.88rem;
  font-weight: 700;
  color: #FFFFFF;
}

.u-status-badge {
  font-size: 0.68rem;
  padding: 2px 6px;
  border-radius: 4px;
}

.u-status-badge.active {
  background: rgba(16, 185, 129, 0.2);
  color: #34D399;
}

.u-status-badge.pending {
  background: rgba(245, 158, 11, 0.2);
  color: #FBBF24;
}

.u-meta {
  font-size: 0.72rem;
  color: #94A3B8;
  display: block;
  margin: 3px 0 8px 0;
}

.u-actions {
  display: flex;
  gap: 8px;
}

.btn-u-action {
  flex: 1;
  border: none;
  padding: 6px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.btn-u-action.approve {
  background: #10B981;
  color: #FFFFFF;
}

.btn-u-action.deactivate {
  background: rgba(239, 68, 68, 0.15);
  color: #EF4444;
}

.info-card-box {
  margin: 16px;
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 14px;
}

.info-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #5EEAD4;
  margin: 0 0 10px 0;
}

.info-line {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
  color: #94A3B8;
  margin-bottom: 6px;
}

.info-line b {
  color: #E2E8F0;
}

.logout-wrap {
  margin: 16px 16px 32px 16px;
}

.btn-logout {
  width: 100%;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #F87171;
  padding: 14px;
  border-radius: 14px;
  font-weight: 700;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
</style>
