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
            <span class="admin-sub">Validation des comptes & gestion des accès</span>
          </div>
          <button @click="loadUsers" class="btn-refresh-sm" :class="{ 'spinning': usersLoading }">
            <ion-icon :icon="refreshOutline" />
          </button>
        </div>

        <!-- Pending Registrations Alert Banner -->
        <div v-if="pendingCount > 0" class="pending-alert-banner">
          <div class="banner-left">
            <ion-icon :icon="alertCircleOutline" class="banner-icon" />
            <div class="banner-texts">
              <span class="banner-title">{{ pendingCount }} inscription{{ pendingCount > 1 ? 's' : '' }} en attente</span>
              <span class="banner-sub">Validation requise pour autoriser l'accès vendeur</span>
            </div>
          </div>
          <button
            v-if="activeFilter !== 'pending'"
            class="banner-quick-btn"
            @click="selectFilter('pending')"
          >
            Afficher
          </button>
        </div>

        <!-- Filter Segment -->
        <div class="admin-filter-bar">
          <button
            :class="['filter-btn', activeFilter === 'pending' ? 'active pending' : '']"
            @click="selectFilter('pending')"
          >
            En attente
            <span v-if="pendingCount > 0" class="filter-badge pending">{{ pendingCount }}</span>
          </button>
          <button
            :class="['filter-btn', activeFilter === 'active' ? 'active' : '']"
            @click="selectFilter('active')"
          >
            Actifs
            <span class="filter-badge">{{ activeCount }}</span>
          </button>
          <button
            :class="['filter-btn', activeFilter === 'all' ? 'active' : '']"
            @click="selectFilter('all')"
          >
            Tous
            <span class="filter-badge">{{ usersList.length }}</span>
          </button>
        </div>

        <!-- Search Bar -->
        <div class="admin-search-wrap">
          <ion-icon :icon="searchOutline" class="search-icon-sm" />
          <input
            v-model="userSearchQuery"
            type="text"
            placeholder="Rechercher par nom, email..."
            class="admin-search-input"
          />
          <button
            v-if="userSearchQuery"
            @click="userSearchQuery = ''"
            class="btn-clear-search"
          >
            ✕
          </button>
        </div>

        <!-- Empty State -->
        <div v-if="filteredUsers.length === 0" class="empty-users">
          <ion-icon :icon="personOutline" class="empty-icon" />
          <span v-if="activeFilter === 'pending'">Aucune inscription en attente de validation.</span>
          <span v-else-if="userSearchQuery">Aucun utilisateur trouvé pour "{{ userSearchQuery }}".</span>
          <span v-else>Aucun utilisateur enregistré.</span>
        </div>

        <!-- Users List -->
        <div v-else class="users-mobile-list">
          <div v-for="u in filteredUsers" :key="u.id" class="user-item-card">
            <div class="u-top">
              <div class="u-identity">
                <span class="u-name">{{ u.prenom }} {{ u.nom }}</span>
                <span class="u-role-pill">{{ u.role?.label || 'Sans rôle' }}</span>
              </div>
              <span :class="['u-status-badge', u.is_active ? 'active' : 'pending']">
                {{ u.is_active ? 'Actif' : 'En attente' }}
              </span>
            </div>

            <div class="u-details">
              <span class="u-meta-line">✉️ {{ u.email }}</span>
              <span class="u-meta-line" v-if="u.numero">📞 {{ u.numero }}</span>
              <span class="u-meta-line u-date" v-if="u.created_at">
                📅 Inscrit le {{ formatDate(u.created_at) }}
              </span>
            </div>

            <!-- Action buttons for admin -->
            <div class="u-actions" v-if="!u.is_superuser && u.id !== user?.id">
              <!-- When account is not active (pending registration or disabled) -->
              <template v-if="!u.is_active">
                <button
                  @click="approveUser(u)"
                  :disabled="loadingUserId === u.id"
                  class="btn-u-action approve"
                >
                  <ion-icon
                    :icon="loadingUserId === u.id ? refreshOutline : checkmarkCircleOutline"
                    :class="{ 'spinning': loadingUserId === u.id }"
                  />
                  <span>{{ loadingUserId === u.id ? 'Validation...' : 'Valider le compte' }}</span>
                </button>
                <button
                  @click="rejectUser(u)"
                  :disabled="loadingUserId === u.id"
                  class="btn-u-action reject"
                >
                  <ion-icon :icon="trashOutline" />
                  <span>Refuser</span>
                </button>
              </template>

              <!-- When account is active -->
              <button
                v-else
                @click="toggleUserActive(u)"
                :disabled="loadingUserId === u.id"
                class="btn-u-action deactivate"
              >
                <ion-icon
                  :icon="loadingUserId === u.id ? refreshOutline : closeCircleOutline"
                  :class="{ 'spinning': loadingUserId === u.id }"
                />
                <span>{{ loadingUserId === u.id ? 'Patientez...' : "Désactiver l'accès" }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Fournisseurs & Approvisionnement (Mobile) -->
      <div class="admin-console-card suppliers-card-wrap">
        <div class="admin-header">
          <div>
            <h3 class="admin-title">🏢 Fournisseurs & Licences</h3>
            <span class="admin-sub">{{ suppliersList.length }} fournisseur(s) · Traçabilité des achats</span>
          </div>
          <button @click="openSuppliersModal" class="btn-supplier-manage-header">
            Gérer
          </button>
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

    <!-- Modal Gestion Fournisseurs Mobile -->
    <ion-modal :is-open="isSuppliersModalOpen" @didDismiss="isSuppliersModalOpen = false" :initial-breakpoint="0.9" :breakpoints="[0, 0.9, 1]">
      <ion-header>
        <ion-toolbar class="main-toolbar">
          <ion-title>Fournisseurs de Licences</ion-title>
          <ion-buttons slot="end">
            <ion-button @click="isSuppliersModalOpen = false" class="btn-modal-close">Fermer</ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>
      <ion-content class="ion-padding supplier-modal-content">
        <!-- Top Action Button -->
        <div class="supplier-modal-top-bar">
          <button
            type="button"
            @click="showSupplierCreateForm = !showSupplierCreateForm"
            class="btn-add-supplier-top"
          >
            <ion-icon :icon="addCircleOutline" />
            <span>{{ showSupplierCreateForm ? 'Masquer formulaire' : '+ Nouveau Fournisseur' }}</span>
          </button>
        </div>

        <!-- Create / Edit Form Card -->
        <div v-if="showSupplierCreateForm" class="mobile-supplier-form-card animate-fade">
          <h4 class="form-title-mobile">{{ editingSupplierId ? 'Modifier Fournisseur' : 'Nouveau Fournisseur' }}</h4>
          <input
            v-model="supplierForm.nom"
            type="text"
            placeholder="Nom du fournisseur (ex: Kinguin, G2A) *"
            class="mobile-input"
          />
          <input
            v-model="supplierForm.site_web"
            type="url"
            placeholder="Portail d'achat (ex: https://...)"
            class="mobile-input"
          />
          <input
            v-model="supplierForm.contact"
            type="text"
            placeholder="Contact (ex: WhatsApp, Telegram...)"
            class="mobile-input"
          />
          <textarea
            v-model="supplierForm.notes"
            rows="2"
            placeholder="Conditions de garantie ou notes d'achat..."
            class="mobile-input"
          ></textarea>
          <div class="supplier-form-actions">
            <button type="button" @click="cancelSupplierForm" class="btn-cancel-sm">
              Annuler
            </button>
            <button
              type="button"
              @click="saveSupplier"
              class="btn-save-sm"
              :disabled="!supplierForm.nom.trim() || savingSupplier"
            >
              {{ savingSupplier ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </div>

        <!-- Suppliers List -->
        <div class="mobile-suppliers-list">
          <div v-for="s in suppliersList" :key="s.id" class="mobile-supplier-item">
            <div class="s-left">
              <span class="s-name">{{ s.nom }}</span>
              <a v-if="s.site_web" :href="s.site_web" target="_blank" class="s-link">
                {{ s.site_web.replace(/^https?:\/\//i, '').slice(0, 30) }}
              </a>
              <span v-if="s.contact" class="s-contact">📞 {{ s.contact }}</span>
              <span class="s-sales-count">{{ s.ventes_count || 0 }} commande(s) associée(s)</span>
            </div>
            <div class="s-right">
              <button
                type="button"
                @click="toggleSupplierActive(s)"
                class="btn-status-pill"
                :class="{ active: s.is_active }"
              >
                {{ s.is_active ? 'Actif' : 'Inactif' }}
              </button>
              <button type="button" @click="editSupplier(s)" class="btn-edit-icon" title="Modifier">
                <ion-icon :icon="createOutline" />
              </button>
            </div>
          </div>
          <div v-if="suppliersList.length === 0" class="empty-suppliers-mobile">
            <p>Aucun fournisseur enregistré pour le moment.</p>
          </div>
        </div>
      </ion-content>
    </ion-modal>
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
  IonModal,
  alertController,
  toastController,
} from '@ionic/vue'
import {
  logOutOutline,
  refreshOutline,
  checkmarkCircleOutline,
  closeCircleOutline,
  alertCircleOutline,
  searchOutline,
  trashOutline,
  personOutline,
  addCircleOutline,
  createOutline,
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
const usersLoading = ref(false)
const loadingUserId = ref(null)
const activeFilter = ref('all')
const hasUserManuallySelectedFilter = ref(false)
const userSearchQuery = ref('')

// Fournisseurs Mobile
const suppliersList = ref([])
const isSuppliersModalOpen = ref(false)
const showSupplierCreateForm = ref(false)
const editingSupplierId = ref(null)
const savingSupplier = ref(false)
const supplierForm = ref({
  nom: '',
  site_web: '',
  contact: '',
  notes: '',
  is_active: true,
})

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

const pendingCount = computed(() => usersList.value.filter((u) => !u.is_active).length)
const activeCount = computed(() => usersList.value.filter((u) => u.is_active).length)

const filteredUsers = computed(() => {
  return usersList.value.filter((u) => {
    if (activeFilter.value === 'pending' && u.is_active) return false
    if (activeFilter.value === 'active' && !u.is_active) return false

    if (userSearchQuery.value.trim()) {
      const q = userSearchQuery.value.trim().toLowerCase()
      const nom = (u.nom || '').toLowerCase()
      const prenom = (u.prenom || '').toLowerCase()
      const email = (u.email || '').toLowerCase()
      const numero = (u.numero || '').toLowerCase()
      if (!nom.includes(q) && !prenom.includes(q) && !email.includes(q) && !numero.includes(q)) {
        return false
      }
    }
    return true
  })
})

function formatPrice(val) {
  if (!val && val !== 0) return '0 Ar'
  return Math.round(val).toLocaleString('fr-FR') + ' Ar'
}

function formatDate(isoStr) {
  if (!isoStr) return ''
  try {
    const d = new Date(isoStr)
    return d.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  } catch {
    return ''
  }
}

function selectFilter(filter) {
  hasUserManuallySelectedFilter.value = true
  activeFilter.value = filter
}

async function loadData() {
  await fetchProfile()
  try {
    const res = await apiClient.get('/auth/profile/')
    if (res.data?.statistiques) {
      profileStats.value = res.data.statistiques
    }
  } catch (e) {
    console.error('Erreur chargement statistiques profil:', e)
  }

  if (isSuperAdmin.value) {
    await loadUsers()
  }
  await loadSuppliers()
}

async function loadSuppliers() {
  try {
    const res = await apiClient.get('/ventes/fournisseurs/')
    suppliersList.value = res.data.results || res.data || []
  } catch (e) {
    console.error('Erreur chargement fournisseurs mobile:', e)
  }
}

function openSuppliersModal() {
  showSupplierCreateForm.value = false
  editingSupplierId.value = null
  isSuppliersModalOpen.value = true
  loadSuppliers()
}

function cancelSupplierForm() {
  showSupplierCreateForm.value = false
  editingSupplierId.value = null
  supplierForm.value = { nom: '', site_web: '', contact: '', notes: '', is_active: true }
}

function editSupplier(s) {
  editingSupplierId.value = s.id
  supplierForm.value = {
    nom: s.nom,
    site_web: s.site_web || '',
    contact: s.contact || '',
    notes: s.notes || '',
    is_active: s.is_active !== false,
  }
  showSupplierCreateForm.value = true
}

async function saveSupplier() {
  if (!supplierForm.value.nom.trim()) return
  savingSupplier.value = true

  try {
    if (editingSupplierId.value) {
      await apiClient.put(`/ventes/fournisseurs/${editingSupplierId.value}/`, supplierForm.value)
      const toast = await toastController.create({
        message: `Fournisseur « ${supplierForm.value.nom} » mis à jour !`,
        duration: 2000,
        color: 'success',
        position: 'top',
      })
      await toast.present()
    } else {
      await apiClient.post('/ventes/fournisseurs/', supplierForm.value)
      const toast = await toastController.create({
        message: `Fournisseur « ${supplierForm.value.nom} » créé avec succès !`,
        duration: 2000,
        color: 'success',
        position: 'top',
      })
      await toast.present()
    }
    cancelSupplierForm()
    await loadSuppliers()
  } catch (e) {
    console.error('Erreur sauvegarde fournisseur:', e)
    const toast = await toastController.create({
      message: e.response?.data?.nom?.[0] || 'Erreur lors de la sauvegarde du fournisseur.',
      duration: 3000,
      color: 'danger',
      position: 'top',
    })
    await toast.present()
  } finally {
    savingSupplier.value = false
  }
}

async function toggleSupplierActive(s) {
  try {
    const res = await apiClient.post(`/ventes/fournisseurs/${s.id}/toggle-active/`)
    s.is_active = res.data.is_active
    const toast = await toastController.create({
      message: `Fournisseur « ${s.nom} » ${s.is_active ? 'activé' : 'désactivé'} !`,
      duration: 2000,
      color: 'success',
      position: 'top',
    })
    await toast.present()
  } catch (e) {
    console.error('Erreur bascule statut:', e)
  }
}

async function loadUsers() {
  usersLoading.value = true
  try {
    const res = await apiClient.get('/auth/users/')
    usersList.value = res.data.results || res.data || []
    if (pendingCount.value > 0 && !hasUserManuallySelectedFilter.value) {
      activeFilter.value = 'pending'
    }
  } catch (e) {
    console.error('Erreur users:', e)
  } finally {
    usersLoading.value = false
  }
}

async function approveUser(u) {
  if (loadingUserId.value) return
  loadingUserId.value = u.id

  try {
    const res = await apiClient.post(`/auth/users/${u.id}/approve/`)
    const toast = await toastController.create({
      message: res.data?.message || `Compte de ${u.prenom} validé avec succès !`,
      duration: 2500,
      color: 'success',
      position: 'top',
    })
    await toast.present()
    await loadUsers()
  } catch (e) {
    console.error('Erreur approbation inscription:', e)
    const errorMsg =
      e.response?.data?.error ||
      e.response?.data?.detail ||
      "Erreur lors de la validation du compte. Vérifiez votre connexion."
    const toast = await toastController.create({
      message: errorMsg,
      duration: 3500,
      color: 'danger',
      position: 'top',
    })
    await toast.present()
  } finally {
    loadingUserId.value = null
  }
}

async function rejectUser(u) {
  if (loadingUserId.value) return
  const alert = await alertController.create({
    header: "Refuser l'inscription",
    message: `Êtes-vous sûr de vouloir refuser et supprimer la demande de ${u.prenom} ${u.nom} (${u.email}) ?`,
    buttons: [
      { text: 'Annuler', role: 'cancel' },
      {
        text: 'Refuser et supprimer',
        role: 'destructive',
        handler: async () => {
          loadingUserId.value = u.id
          try {
            await apiClient.delete(`/auth/users/${u.id}/`)
            const toast = await toastController.create({
              message: `Demande de ${u.prenom} ${u.nom} refusée et supprimée.`,
              duration: 2500,
              color: 'warning',
              position: 'top',
            })
            await toast.present()
            await loadUsers()
          } catch (e) {
            console.error('Erreur refus:', e)
            const errorMsg =
              e.response?.data?.error ||
              e.response?.data?.detail ||
              "Erreur lors du refus de l'inscription."
            const toast = await toastController.create({
              message: errorMsg,
              duration: 3500,
              color: 'danger',
              position: 'top',
            })
            await toast.present()
          } finally {
            loadingUserId.value = null
          }
        },
      },
    ],
  })
  await alert.present()
}

async function toggleUserActive(u) {
  if (loadingUserId.value) return
  const willDeactivate = u.is_active
  const alert = await alertController.create({
    header: willDeactivate ? "Désactiver l'accès" : "Réactiver l'accès",
    message: willDeactivate
      ? `Êtes-vous sûr de vouloir désactiver le compte de ${u.prenom} ${u.nom} ? Il ne pourra plus se connecter.`
      : `Voulez-vous réactiver le compte de ${u.prenom} ${u.nom} ?`,
    buttons: [
      { text: 'Annuler', role: 'cancel' },
      {
        text: willDeactivate ? 'Désactiver' : 'Réactiver',
        role: willDeactivate ? 'destructive' : undefined,
        handler: async () => {
          loadingUserId.value = u.id
          try {
            const res = await apiClient.post(`/auth/users/${u.id}/toggle_active/`)
            const toast = await toastController.create({
              message: res.data?.message || 'Statut mis à jour avec succès.',
              duration: 2500,
              color: 'success',
              position: 'top',
            })
            await toast.present()
            await loadUsers()
          } catch (e) {
            console.error('Erreur toggle active:', e)
            const errorMsg =
              e.response?.data?.error ||
              e.response?.data?.detail ||
              'Erreur lors du changement de statut.'
            const toast = await toastController.create({
              message: errorMsg,
              duration: 3500,
              color: 'danger',
              position: 'top',
            })
            await toast.present()
          } finally {
            loadingUserId.value = null
          }
        },
      },
    ],
  })
  await alert.present()
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
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.spinning {
  animation: spin 0.8s linear infinite;
}

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
  transition: all 0.2s ease;
}

.btn-refresh-sm:active {
  transform: scale(0.95);
}

/* Pending Alert Banner */
.pending-alert-banner {
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.35);
  border-radius: 12px;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 8px;
}

.banner-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.banner-icon {
  font-size: 1.4rem;
  color: #F59E0B;
  flex-shrink: 0;
}

.banner-texts {
  display: flex;
  flex-direction: column;
}

.banner-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: #FDE68A;
}

.banner-sub {
  font-size: 0.68rem;
  color: #D97706;
}

.banner-quick-btn {
  background: #F59E0B;
  color: #0F172A;
  border: none;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 6px;
  white-space: nowrap;
}

/* Filter Bar */
.admin-filter-bar {
  display: flex;
  background: #0B1120;
  border-radius: 10px;
  padding: 3px;
  gap: 4px;
  margin-bottom: 10px;
}

.filter-btn {
  flex: 1;
  background: transparent;
  border: none;
  color: #94A3B8;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 7px 4px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.filter-btn.active {
  background: #1E293B;
  color: #FFFFFF;
}

.filter-btn.active.pending {
  background: rgba(245, 158, 11, 0.25);
  color: #FBBF24;
}

.filter-badge {
  background: rgba(255, 255, 255, 0.1);
  font-size: 0.65rem;
  padding: 1px 5px;
  border-radius: 9999px;
  color: inherit;
}

.filter-badge.pending {
  background: #F59E0B;
  color: #0F172A;
  font-weight: 800;
}

/* Search bar */
.admin-search-wrap {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.search-icon-sm {
  position: absolute;
  left: 10px;
  font-size: 1rem;
  color: #64748B;
  pointer-events: none;
}

.admin-search-input {
  width: 100%;
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 8px 30px 8px 32px;
  color: #FFFFFF;
  font-size: 0.8rem;
  outline: none;
}

.admin-search-input:focus {
  border-color: #0D9488;
}

.btn-clear-search {
  position: absolute;
  right: 8px;
  background: transparent;
  border: none;
  color: #64748B;
  font-size: 0.8rem;
  padding: 4px;
}

.empty-users {
  padding: 24px 16px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #64748B;
  font-size: 0.8rem;
}

.empty-icon {
  font-size: 2rem;
  color: #334155;
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
  padding: 12px;
}

.u-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.u-identity {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.u-name {
  font-size: 0.88rem;
  font-weight: 700;
  color: #FFFFFF;
}

.u-role-pill {
  font-size: 0.65rem;
  background: rgba(255, 255, 255, 0.07);
  color: #94A3B8;
  padding: 1px 6px;
  border-radius: 9999px;
}

.u-status-badge {
  font-size: 0.68rem;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.u-status-badge.active {
  background: rgba(16, 185, 129, 0.2);
  color: #34D399;
}

.u-status-badge.pending {
  background: rgba(245, 158, 11, 0.2);
  color: #FBBF24;
}

.u-details {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin-bottom: 10px;
}

.u-meta-line {
  font-size: 0.72rem;
  color: #94A3B8;
}

.u-date {
  color: #64748B;
  font-size: 0.68rem;
}

.u-actions {
  display: flex;
  gap: 8px;
}

.btn-u-action {
  flex: 1;
  border: none;
  padding: 8px;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn-u-action:active {
  transform: scale(0.98);
}

.btn-u-action.approve {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: #FFFFFF;
}

.btn-u-action.reject {
  flex: 0 0 90px;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #F87171;
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

/* Fournisseurs Mobile Styles */
.suppliers-card-wrap {
  margin: 0 16px 16px 16px;
}

.btn-supplier-manage-header {
  background: rgba(13, 148, 136, 0.2);
  border: 1px solid rgba(13, 148, 136, 0.4);
  color: #2DD4BF;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
}

.supplier-modal-content {
  --background: #0B1120;
}

.supplier-modal-top-bar {
  margin-bottom: 1rem;
}

.btn-add-supplier-top {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: linear-gradient(135deg, #0D9488 0%, #0284C7 100%);
  color: white;
  border: none;
  padding: 12px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
}

.mobile-supplier-form-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-title-mobile {
  font-size: 0.95rem;
  font-weight: 700;
  color: white;
  margin: 0 0 4px 0;
}

.supplier-form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 4px;
}

.btn-cancel-sm {
  background: rgba(255, 255, 255, 0.08);
  border: none;
  color: #94A3B8;
  padding: 7px 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
}

.btn-save-sm {
  background: #0D9488;
  border: none;
  color: white;
  padding: 7px 14px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
}

.mobile-suppliers-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mobile-supplier-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
  gap: 10px;
}

.s-left {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.s-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: white;
}

.s-link {
  font-size: 0.72rem;
  color: #38BDF8;
  text-decoration: underline;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.s-contact {
  font-size: 0.72rem;
  color: #94A3B8;
}

.s-sales-count {
  font-size: 0.7rem;
  color: #CBD5E1;
  opacity: 0.8;
}

.s-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.btn-status-pill {
  padding: 4px 10px;
  border-radius: 20px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(148, 163, 184, 0.1);
  color: #94A3B8;
  font-size: 0.7rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-status-pill.active {
  border-color: rgba(16, 185, 129, 0.4);
  background: rgba(16, 185, 129, 0.15);
  color: #34D399;
}

.btn-edit-icon {
  background: rgba(255, 255, 255, 0.06);
  border: none;
  color: #E2E8F0;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  cursor: pointer;
}

.empty-suppliers-mobile {
  text-align: center;
  color: #94A3B8;
  padding: 2rem 1rem;
  font-size: 0.85rem;
}
</style>
