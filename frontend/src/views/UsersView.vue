<template>
  <div class="users-view">
    <!-- Header with Stats & Actions -->
    <div class="view-header">
      <div class="header-info">
        <div class="title-with-badge">
          <h2>Équipe & Utilisateurs</h2>
          <span class="badge badge-primary">{{ users.length }} membres</span>
        </div>
        <p class="text-sm text-muted">
          Gérez les membres de votre équipe commerciale, attribuez les rôles et configurez les accès à la plateforme.
        </p>
      </div>

      <div class="header-actions">
        <button @click="openCreateModal" class="btn btn-primary">
          <UserPlus :size="18" />
          <span>Nouveau Membre</span>
        </button>
      </div>
    </div>

    <!-- Alert notification -->
    <div v-if="actionMessage" class="action-alert animate-fade">
      <CheckCircle2 :size="18" class="text-emerald flex-shrink-0" />
      <span>{{ actionMessage }}</span>
      <button @click="actionMessage = ''" class="btn-clear-alert"><X :size="14" /></button>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="card kpi-card">
        <div class="kpi-icon-box cyan">
          <Users :size="22" />
        </div>
        <div class="kpi-body">
          <span class="kpi-label">TOTAL ÉQUIPE</span>
          <span class="kpi-value">{{ users.length }}</span>
        </div>
      </div>

      <div class="card kpi-card">
        <div class="kpi-icon-box amber">
          <ShieldCheck :size="22" />
        </div>
        <div class="kpi-body">
          <span class="kpi-label">ADMINISTRATEURS</span>
          <span class="kpi-value text-amber">{{ adminCount }}</span>
        </div>
      </div>

      <div class="card kpi-card">
        <div class="kpi-icon-box emerald">
          <UserCheck :size="22" />
        </div>
        <div class="kpi-body">
          <span class="kpi-label">VENDEURS / COMMERCIAUX</span>
          <span class="kpi-value text-emerald">{{ sellersCount }}</span>
        </div>
      </div>

      <div class="card kpi-card">
        <div class="kpi-icon-box rose">
          <Clock :size="22" />
        </div>
        <div class="kpi-body">
          <span class="kpi-label">EN ATTENTE D'ACCÈS</span>
          <span class="kpi-value" :class="pendingCount > 0 ? 'text-rose' : 'text-muted'">
            {{ pendingCount }}
          </span>
        </div>
      </div>
    </div>

    <!-- Toolbar: Search & Role / Status Filters -->
    <div class="toolbar card">
      <div class="search-box">
        <Search :size="18" class="search-icon" />
        <input
          v-model="searchQuery"
          type="text"
          class="form-input search-input"
          placeholder="Rechercher par nom, email ou numéro..."
        />
        <button v-if="searchQuery" @click="searchQuery = ''" class="btn-clear-search">
          <X :size="14" />
        </button>
      </div>

      <div class="filter-groups">
        <div class="filter-pills">
          <button
            @click="statusFilter = 'all'"
            class="pill-btn"
            :class="{ active: statusFilter === 'all' }"
          >
            Tous ({{ users.length }})
          </button>
          <button
            @click="statusFilter = 'active'"
            class="pill-btn"
            :class="{ active: statusFilter === 'active' }"
          >
            Actifs ({{ activeCount }})
          </button>
          <button
            @click="statusFilter = 'pending'"
            class="pill-btn"
            :class="{ active: statusFilter === 'pending' }"
          >
            En attente ({{ pendingCount }})
          </button>
        </div>

        <select v-model="selectedRoleFilter" class="form-select role-select">
          <option value="">Tous les rôles</option>
          <option v-for="r in roles" :key="r.id" :value="r.id">
            {{ r.label }} ({{ r.point }} pts)
          </option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <RefreshCw :size="32" class="spin-icon text-primary" />
      <span>Chargement des membres de l'équipe...</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredUsers.length === 0" class="empty-state card">
      <Users :size="48" class="text-muted" />
      <h3>Aucun utilisateur trouvé</h3>
      <p class="text-muted text-sm">
        {{ searchQuery ? "Aucun membre ne correspond à vos filtres de recherche." : "Commencez par ajouter un membre à votre équipe." }}
      </p>
    </div>

    <!-- Users Table -->
    <div v-else class="card p-0">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Membre</th>
              <th>Coordonnées</th>
              <th>Rôle & Habilitation</th>
              <th>Ventes Réalisées</th>
              <th>Statut d'accès</th>
              <th>Inscrit le</th>
              <th style="text-align: right;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in filteredUsers" :key="u.id">
              <td>
                <div class="user-cell">
                  <div class="user-avatar" :class="{ 'admin-avatar': u.role?.nom === 'admin' }">
                    {{ getUserInitials(u) }}
                  </div>
                  <div class="user-names">
                    <div class="user-fullname">
                      {{ u.prenom }} {{ u.nom }}
                      <span v-if="u.id === currentUser?.id" class="badge-self">Vous</span>
                    </div>
                    <span class="user-email">{{ u.email }}</span>
                  </div>
                </div>
              </td>

              <td>
                <span v-if="u.numero" class="font-mono text-sm">{{ u.numero }}</span>
                <span v-else class="text-muted text-xs">Non renseigné</span>
              </td>

              <td>
                <div class="role-badge" :class="u.role?.nom === 'admin' ? 'role-admin' : 'role-seller'">
                  <ShieldCheck v-if="u.role?.nom === 'admin'" :size="14" />
                  <UserCheck v-else :size="14" />
                  <span>{{ u.role?.label || 'Sans rôle' }}</span>
                  <span class="pts-tag">{{ u.role?.point || 0 }} pts</span>
                </div>
              </td>

              <td>
                <span class="font-bold font-mono">{{ u.ventes_count || 0 }}</span>
              </td>

              <td>
                <button
                  @click="toggleUserActive(u)"
                  class="status-btn"
                  :class="u.is_active ? 'status-active' : 'status-pending'"
                  :disabled="u.id === currentUser?.id"
                  :title="u.id === currentUser?.id ? 'Vous ne pouvez pas désactiver votre propre compte' : (u.is_active ? 'Cliquer pour désactiver' : 'Cliquer pour activer')"
                >
                  <span class="status-dot"></span>
                  <span>{{ u.is_active ? 'Actif' : 'En attente' }}</span>
                </button>
              </td>

              <td>
                <span class="text-muted text-xs">{{ formatDate(u.created_at) }}</span>
              </td>

              <td style="text-align: right;">
                <div class="actions-group">
                  <button @click="openEditModal(u)" class="btn btn-secondary btn-xs" title="Modifier le membre">
                    <Edit2 :size="13" />
                    <span>Modifier</span>
                  </button>

                  <button @click="openPasswordModal(u)" class="btn btn-secondary btn-xs" title="Réinitialiser le mot de passe">
                    <KeyRound :size="13" />
                  </button>

                  <button
                    v-if="u.id !== currentUser?.id"
                    @click="openDeleteModal(u)"
                    class="btn-icon btn-danger-icon"
                    title="Supprimer ce membre"
                  >
                    <Trash2 :size="14" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL: Créer un Membre -->
    <div v-if="showCreateModal" class="modal-backdrop">
      <div class="modal-card card animate-scale">
        <div class="modal-header">
          <div class="modal-title-wrap">
            <UserPlus :size="22" class="text-primary" />
            <h3>Nouveau Membre de l'Équipe</h3>
          </div>
          <button @click="showCreateModal = false" class="btn-close"><X :size="20" /></button>
        </div>

        <form @submit.prevent="submitCreateUser" class="modal-body">
          <div v-if="createError" class="error-banner">
            <AlertCircle :size="16" />
            <span>{{ createError }}</span>
          </div>

          <div class="form-row">
            <div class="form-group flex-1">
              <label class="form-label">Prénom *</label>
              <input v-model="createForm.prenom" required type="text" class="form-input" placeholder="Ex: Jean" />
            </div>
            <div class="form-group flex-1">
              <label class="form-label">Nom *</label>
              <input v-model="createForm.nom" required type="text" class="form-input" placeholder="Ex: Dupont" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Adresse Email *</label>
            <input v-model="createForm.email" required type="email" class="form-input" placeholder="vendeur@licencepro.mg" />
          </div>

          <div class="form-row">
            <div class="form-group flex-1">
              <label class="form-label">Numéro de téléphone</label>
              <input v-model="createForm.numero" type="text" class="form-input" placeholder="Ex: 034 12 345 67" />
            </div>
            <div class="form-group flex-1">
              <label class="form-label">Rôle attribué *</label>
              <select v-model="createForm.role_id" required class="form-select">
                <option v-for="r in roles" :key="r.id" :value="r.id">
                  {{ r.label }} ({{ r.point }} pts)
                </option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <div class="flex-between">
              <label class="form-label">Mot de passe temporaire *</label>
              <button type="button" @click="generateRandomPassword" class="text-xs text-primary btn-link">
                🎲 Générer un mot de passe
              </button>
            </div>
            <input
              v-model="createForm.password"
              required
              type="text"
              class="form-input font-mono"
              placeholder="Minimum 6 caractères"
            />
          </div>

          <div class="form-check-group">
            <label class="check-label">
              <input v-model="createForm.is_active" type="checkbox" class="check-box" />
              <span>Activer et valider ce compte immédiatement</span>
            </label>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showCreateModal = false" class="btn btn-secondary">Annuler</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              <RefreshCw v-if="submitting" :size="16" class="spin-icon" />
              <span>Créer l'utilisateur</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL: Modifier un Membre -->
    <div v-if="showEditModal" class="modal-backdrop">
      <div class="modal-card card animate-scale">
        <div class="modal-header">
          <div class="modal-title-wrap">
            <Edit2 :size="20" class="text-primary" />
            <h3>Modifier le membre</h3>
          </div>
          <button @click="showEditModal = false" class="btn-close"><X :size="20" /></button>
        </div>

        <form @submit.prevent="submitEditUser" class="modal-body">
          <div v-if="editError" class="error-banner">
            <AlertCircle :size="16" />
            <span>{{ editError }}</span>
          </div>

          <div class="form-row">
            <div class="form-group flex-1">
              <label class="form-label">Prénom *</label>
              <input v-model="editForm.prenom" required type="text" class="form-input" />
            </div>
            <div class="form-group flex-1">
              <label class="form-label">Nom *</label>
              <input v-model="editForm.nom" required type="text" class="form-input" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Numéro de téléphone</label>
            <input v-model="editForm.numero" type="text" class="form-input" placeholder="Ex: 034 12 345 67" />
          </div>

          <div class="form-group">
            <label class="form-label">Rôle</label>
            <select v-model="editForm.role_id" class="form-select">
              <option v-for="r in roles" :key="r.id" :value="r.id">
                {{ r.label }} ({{ r.point }} pts)
              </option>
            </select>
          </div>

          <div class="form-check-group" v-if="editForm.id !== currentUser?.id">
            <label class="check-label">
              <input v-model="editForm.is_active" type="checkbox" class="check-box" />
              <span>Compte actif et autorisé à se connecter</span>
            </label>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showEditModal = false" class="btn btn-secondary">Annuler</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              <RefreshCw v-if="submitting" :size="16" class="spin-icon" />
              <span>Enregistrer</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL: Réinitialiser le mot de passe -->
    <div v-if="showPasswordModal" class="modal-backdrop">
      <div class="modal-card card animate-scale">
        <div class="modal-header">
          <div class="modal-title-wrap">
            <KeyRound :size="20" class="text-amber" />
            <h3>Nouveau mot de passe pour {{ selectedUser?.prenom }}</h3>
          </div>
          <button @click="showPasswordModal = false" class="btn-close"><X :size="20" /></button>
        </div>

        <form @submit.prevent="submitPasswordReset" class="modal-body">
          <div v-if="passwordError" class="error-banner">
            <AlertCircle :size="16" />
            <span>{{ passwordError }}</span>
          </div>

          <p class="text-sm text-muted">
            Définissez un nouveau mot de passe pour <strong>{{ selectedUser?.email }}</strong>. L'utilisateur pourra ensuite se connecter immédiatement avec ces identifiants.
          </p>

          <div class="form-group">
            <div class="flex-between">
              <label class="form-label">Nouveau mot de passe *</label>
              <button type="button" @click="generateRandomPasswordForReset" class="text-xs text-primary btn-link">
                🎲 Générer aléatoirement
              </button>
            </div>
            <input
              v-model="newPassword"
              required
              type="text"
              class="form-input font-mono"
              placeholder="Minimum 6 caractères"
            />
          </div>

          <div class="modal-actions">
            <button type="button" @click="showPasswordModal = false" class="btn btn-secondary">Annuler</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting || newPassword.length < 6">
              <RefreshCw v-if="submitting" :size="16" class="spin-icon" />
              <span>Mettre à jour le mot de passe</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL: Supprimer un Membre -->
    <div v-if="showDeleteModal" class="modal-backdrop">
      <div class="modal-card card animate-scale danger-modal">
        <div class="modal-header danger-header">
          <div class="modal-title-wrap">
            <AlertTriangle :size="24" class="text-rose" />
            <h3>Supprimer le membre ?</h3>
          </div>
          <button @click="showDeleteModal = false" class="btn-close"><X :size="20" /></button>
        </div>

        <div class="modal-body">
          <p>
            Êtes-vous sûr de vouloir supprimer définitivement le compte de
            <strong>{{ userToDelete?.prenom }} {{ userToDelete?.nom }}</strong> ({{ userToDelete?.email }}) ?
          </p>

          <div v-if="userToDelete?.ventes_count > 0" class="warning-box mt-3">
            <AlertCircle :size="18" class="text-amber flex-shrink-0" />
            <div>
              <strong>Attention :</strong> Cet utilisateur a {{ userToDelete.ventes_count }} vente(s) enregistrée(s).
              La suppression est bloquée pour préserver la traçabilité comptable. Vous devez plutôt désactiver son compte.
            </div>
          </div>

          <div v-if="deleteError" class="error-banner mt-3">
            <AlertCircle :size="16" />
            <span>{{ deleteError }}</span>
          </div>

          <div class="modal-actions mt-4">
            <button type="button" @click="showDeleteModal = false" class="btn btn-secondary">
              Annuler
            </button>
            <button
              type="button"
              @click="confirmDeleteUser"
              class="btn btn-danger"
              :disabled="deleting || userToDelete?.ventes_count > 0"
            >
              <RefreshCw v-if="deleting" :size="16" class="spin-icon" />
              <span>Supprimer définitivement</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Users,
  UserPlus,
  UserCheck,
  ShieldCheck,
  Clock,
  Search,
  Edit2,
  Trash2,
  KeyRound,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  RefreshCw,
  X,
} from 'lucide-vue-next'
import apiClient from '../api/client'
import { useAuth } from '../composables/useAuth'

const { user: currentUser } = useAuth()

const users = ref([])
const roles = ref([])
const loading = ref(true)
const submitting = ref(false)
const deleting = ref(false)

const searchQuery = ref('')
const statusFilter = ref('all')
const selectedRoleFilter = ref('')
const actionMessage = ref('')

// Create Modal
const showCreateModal = ref(false)
const createError = ref('')
const createForm = ref({
  prenom: '',
  nom: '',
  email: '',
  numero: '',
  role_id: null,
  password: '',
  is_active: true,
})

// Edit Modal
const showEditModal = ref(false)
const editError = ref('')
const editForm = ref({
  id: null,
  prenom: '',
  nom: '',
  numero: '',
  role_id: null,
  is_active: true,
})

// Password Reset Modal
const showPasswordModal = ref(false)
const selectedUser = ref(null)
const newPassword = ref('')
const passwordError = ref('')

// Delete Modal
const showDeleteModal = ref(false)
const userToDelete = ref(null)
const deleteError = ref('')

const adminCount = computed(() => {
  return users.value.filter(u => u.role?.nom === 'admin' || (u.role?.point || 0) >= 50).length
})

const sellersCount = computed(() => {
  return users.value.filter(u => u.role?.nom !== 'admin' && (u.role?.point || 0) < 50).length
})

const activeCount = computed(() => {
  return users.value.filter(u => u.is_active).length
})

const pendingCount = computed(() => {
  return users.value.filter(u => !u.is_active).length
})

const filteredUsers = computed(() => {
  return users.value.filter(u => {
    // Search
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase().trim()
      const matchName = `${u.prenom} ${u.nom}`.toLowerCase().includes(q)
      const matchEmail = (u.email || '').toLowerCase().includes(q)
      const matchNumero = (u.numero || '').toLowerCase().includes(q)
      if (!matchName && !matchEmail && !matchNumero) return false
    }

    // Status
    if (statusFilter.value === 'active' && !u.is_active) return false
    if (statusFilter.value === 'pending' && u.is_active) return false

    // Role
    if (selectedRoleFilter.value && u.role?.id !== Number(selectedRoleFilter.value)) return false

    return true
  })
})

function getUserInitials(u) {
  const p = u.prenom ? u.prenom[0].toUpperCase() : ''
  const n = u.nom ? u.nom[0].toUpperCase() : ''
  return p + n || 'U'
}

function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function generateRandomPassword() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!@#$%^&*'
  let pass = ''
  for (let i = 0; i < 10; i++) {
    pass += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  createForm.value.password = pass
}

function generateRandomPasswordForReset() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!@#$%^&*'
  let pass = ''
  for (let i = 0; i < 10; i++) {
    pass += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  newPassword.value = pass
}

async function fetchUsers() {
  loading.value = true
  try {
    const [usersRes, rolesRes] = await Promise.all([
      apiClient.get('/accounts/users/'),
      apiClient.get('/accounts/roles/'),
    ])
    users.value = usersRes.data
    roles.value = rolesRes.data
    if (!createForm.value.role_id && roles.value.length > 0) {
      const defaultRole = roles.value.find(r => r.nom === 'media_buyer') || roles.value[0]
      createForm.value.role_id = defaultRole.id
    }
  } catch (err) {
    console.error('Erreur chargement utilisateurs:', err)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  createError.value = ''
  createForm.value = {
    prenom: '',
    nom: '',
    email: '',
    numero: '',
    role_id: roles.value.find(r => r.nom === 'media_buyer')?.id || roles.value[0]?.id || null,
    password: '',
    is_active: true,
  }
  generateRandomPassword()
  showCreateModal.value = true
}

async function submitCreateUser() {
  submitting.value = true
  createError.value = ''

  try {
    const payload = {
      prenom: createForm.value.prenom.trim(),
      nom: createForm.value.nom.trim(),
      email: createForm.value.email.trim().toLowerCase(),
      numero: createForm.value.numero.trim() || null,
      role_id: createForm.value.role_id,
      password: createForm.value.password,
      is_active: createForm.value.is_active,
    }
    await apiClient.post('/accounts/users/', payload)
    actionMessage.value = `Le membre ${payload.prenom} ${payload.nom} a été créé avec succès.`
    showCreateModal.value = false
    await fetchUsers()
    setTimeout(() => { actionMessage.value = '' }, 4000)
  } catch (err) {
    createError.value = err.response?.data?.error || err.response?.data?.email?.[0] || 'Erreur lors de la création.'
  } finally {
    submitting.value = false
  }
}

function openEditModal(u) {
  editError.value = ''
  editForm.value = {
    id: u.id,
    prenom: u.prenom,
    nom: u.nom,
    numero: u.numero || '',
    role_id: u.role?.id || null,
    is_active: u.is_active,
  }
  showEditModal.value = true
}

async function submitEditUser() {
  submitting.value = true
  editError.value = ''

  try {
    const payload = {
      prenom: editForm.value.prenom.trim(),
      nom: editForm.value.nom.trim(),
      numero: editForm.value.numero.trim() || null,
      role_id: editForm.value.role_id,
      is_active: editForm.value.is_active,
    }
    await apiClient.patch(`/accounts/users/${editForm.value.id}/`, payload)
    actionMessage.value = `Informations de ${payload.prenom} ${payload.nom} mises à jour.`
    showEditModal.value = false
    await fetchUsers()
    setTimeout(() => { actionMessage.value = '' }, 4000)
  } catch (err) {
    editError.value = err.response?.data?.error || 'Erreur lors de la mise à jour.'
  } finally {
    submitting.value = false
  }
}

function openPasswordModal(u) {
  selectedUser.value = u
  newPassword.value = ''
  passwordError.value = ''
  generateRandomPasswordForReset()
  showPasswordModal.value = true
}

async function submitPasswordReset() {
  if (!selectedUser.value || newPassword.value.length < 6) return
  submitting.value = true
  passwordError.value = ''

  try {
    await apiClient.post(`/accounts/users/${selectedUser.value.id}/reset-password/`, {
      password: newPassword.value,
    })
    actionMessage.value = `Mot de passe de ${selectedUser.value.prenom} ${selectedUser.value.nom} mis à jour avec succès.`
    showPasswordModal.value = false
    setTimeout(() => { actionMessage.value = '' }, 4000)
  } catch (err) {
    passwordError.value = err.response?.data?.error || 'Erreur lors de la réinitialisation.'
  } finally {
    submitting.value = false
  }
}

async function toggleUserActive(u) {
  if (u.id === currentUser.value?.id) return
  try {
    const res = await apiClient.post(`/accounts/users/${u.id}/toggle_active/`)
    u.is_active = res.data.is_active
    actionMessage.value = res.data.message
    setTimeout(() => { actionMessage.value = '' }, 4000)
  } catch (err) {
    console.error('Erreur toggle actif:', err)
  }
}

function openDeleteModal(u) {
  userToDelete.value = u
  deleteError.value = ''
  showDeleteModal.value = true
}

async function confirmDeleteUser() {
  if (!userToDelete.value) return
  deleting.value = true
  deleteError.value = ''

  try {
    await apiClient.delete(`/accounts/users/${userToDelete.value.id}/`)
    actionMessage.value = `Utilisateur ${userToDelete.value.prenom} ${userToDelete.value.nom} supprimé.`
    showDeleteModal.value = false
    await fetchUsers()
    setTimeout(() => { actionMessage.value = '' }, 4000)
  } catch (err) {
    deleteError.value = err.response?.data?.error || 'Erreur lors de la suppression.'
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.users-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.view-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.title-with-badge h2 {
  font-size: 1.6rem;
  margin: 0;
}

.badge-primary {
  background: rgba(0, 210, 255, 0.15);
  color: var(--primary);
  border: 1px solid rgba(0, 210, 255, 0.3);
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
}

.badge-self {
  font-size: 0.65rem;
  background: rgba(0, 210, 255, 0.2);
  color: var(--primary);
  border-radius: 4px;
  padding: 0.1rem 0.35rem;
  margin-left: 0.35rem;
  font-weight: 700;
}

.action-alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #34d399;
  padding: 0.85rem 1.25rem;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
}

.btn-clear-alert {
  margin-left: auto;
  background: none;
  border: none;
  color: currentColor;
  cursor: pointer;
  opacity: 0.7;
}
.btn-clear-alert:hover { opacity: 1; }

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.25rem 1.5rem;
}

.kpi-icon-box {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-icon-box.cyan {
  background: rgba(0, 210, 255, 0.14);
  color: var(--primary);
}

.kpi-icon-box.emerald {
  background: rgba(16, 185, 129, 0.14);
  color: var(--emerald);
}

.kpi-icon-box.amber {
  background: rgba(245, 158, 11, 0.14);
  color: var(--amber);
}

.kpi-icon-box.rose {
  background: rgba(244, 63, 94, 0.14);
  color: var(--rose);
}

.kpi-body {
  display: flex;
  flex-direction: column;
}

.kpi-label {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

.kpi-value {
  font-size: 1.5rem;
  font-weight: 800;
  margin-top: 0.15rem;
}

/* Toolbar */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1.25rem;
}

.search-box {
  position: relative;
  max-width: 380px;
  width: 100%;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.search-input {
  width: 100%;
  padding-left: 2.5rem;
  padding-right: 2.2rem;
  background: rgba(10, 20, 36, 0.6);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-main);
  height: 42px;
}

.search-input:focus {
  border-color: var(--primary);
  outline: none;
}

.btn-clear-search {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
}

.filter-groups {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.filter-pills {
  display: flex;
  background: rgba(10, 20, 36, 0.6);
  padding: 3px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}

.pill-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  padding: 0.4rem 0.85rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.pill-btn.active {
  background: var(--primary);
  color: #060d19;
  font-weight: 700;
}

.role-select {
  padding: 0.45rem 1rem;
  background: rgba(10, 20, 36, 0.6);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-main);
  font-size: 0.85rem;
  height: 40px;
}

/* User table styles */
.user-cell {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(0, 210, 255, 0.15);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.user-avatar.admin-avatar {
  background: rgba(245, 158, 11, 0.2);
  color: var(--amber);
}

.user-names {
  display: flex;
  flex-direction: column;
}

.user-fullname {
  font-weight: 700;
  color: var(--text-main);
  font-size: 0.95rem;
}

.user-email {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.role-admin {
  background: rgba(245, 158, 11, 0.15);
  color: var(--amber);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.role-seller {
  background: rgba(0, 210, 255, 0.12);
  color: var(--primary);
  border: 1px solid rgba(0, 210, 255, 0.25);
}

.pts-tag {
  opacity: 0.75;
  font-size: 0.7rem;
}

/* Status Button */
.status-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.status-active {
  background: rgba(16, 185, 129, 0.14);
  color: #34d399;
  border-color: rgba(16, 185, 129, 0.3);
}

.status-pending {
  background: rgba(244, 63, 94, 0.14);
  color: #fda4af;
  border-color: rgba(244, 63, 94, 0.3);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.actions-group {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.btn-xs {
  padding: 0.35rem 0.65rem;
  font-size: 0.75rem;
}

.btn-icon {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.4rem;
  border-radius: var(--radius-sm);
  transition: all 0.2s;
}

.btn-danger-icon:hover {
  background: rgba(244, 63, 94, 0.15);
  color: var(--rose);
}

.btn-danger {
  background: #e11d48;
  color: white;
}
.btn-danger:hover {
  background: #be123c;
}

/* Form Styles */
.form-row {
  display: flex;
  gap: 1rem;
}

.flex-1 { flex: 1; }

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-input, .form-select {
  width: 100%;
  padding: 0.65rem 0.85rem;
  background: rgba(10, 20, 36, 0.8);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-main);
  font-size: 0.9rem;
}

.form-input:focus, .form-select:focus {
  border-color: var(--primary);
  outline: none;
}

.btn-link {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
}

.form-check-group {
  display: flex;
  align-items: center;
  margin-top: 0.35rem;
}

.check-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.check-box {
  width: 16px;
  height: 16px;
  accent-color: var(--primary);
  cursor: pointer;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-card {
  max-width: 520px;
  width: 100%;
  padding: 1.75rem;
  background: #0d1b2e;
  border: 1px solid var(--border-active);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
}

.danger-modal {
  border-color: rgba(244, 63, 94, 0.4);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.modal-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.modal-title-wrap h3 {
  font-size: 1.25rem;
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
}
.btn-close:hover { color: var(--text-main); }

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(244, 63, 94, 0.15);
  border: 1px solid rgba(244, 63, 94, 0.3);
  color: #fda4af;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
}

.warning-box {
  display: flex;
  gap: 0.65rem;
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: #fde68a;
  padding: 0.85rem;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  line-height: 1.4;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 4rem 1rem;
  color: var(--text-secondary);
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-fade {
  animation: fadeIn 0.25s ease-out;
}

.animate-scale {
  animation: scaleIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>
