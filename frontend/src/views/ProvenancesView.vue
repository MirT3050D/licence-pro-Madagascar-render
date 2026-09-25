<template>
  <div class="provenances-view">
    <!-- Header with Stats & Actions -->
    <div class="view-header">
      <div class="header-info">
        <div class="title-with-badge">
          <h2>Canaux de Provenance</h2>
          <span class="badge badge-primary">{{ provenances.length }} canaux</span>
        </div>
        <p class="text-sm text-muted">
          Gérez les canaux d'acquisition et sources de vos clients (Facebook, WhatsApp, TikTok, Bouche à oreille, Site Web...).
        </p>
      </div>

      <div class="header-actions">
        <button @click="openCreateModal" class="btn btn-primary">
          <Plus :size="18" />
          <span>Nouveau Canal</span>
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
          <Share2 :size="22" />
        </div>
        <div class="kpi-body">
          <span class="kpi-label">TOTAL CANAUX</span>
          <span class="kpi-value">{{ provenances.length }}</span>
        </div>
      </div>

      <div class="card kpi-card">
        <div class="kpi-icon-box emerald">
          <Users :size="22" />
        </div>
        <div class="kpi-body">
          <span class="kpi-label">CLIENTS ATTRIBUÉS</span>
          <span class="kpi-value text-emerald">{{ totalClientsAssigned }}</span>
        </div>
      </div>

      <div class="card kpi-card">
        <div class="kpi-icon-box amber">
          <Award :size="22" />
        </div>
        <div class="kpi-body">
          <span class="kpi-label">MEILLEUR CANAL</span>
          <span class="kpi-value text-amber font-truncate" :title="topChannelName">
            {{ topChannelName }}
          </span>
        </div>
      </div>
    </div>

    <!-- Toolbar & Search -->
    <div class="toolbar card">
      <div class="search-box">
        <Search :size="18" class="search-icon" />
        <input
          v-model="searchQuery"
          type="text"
          class="form-input search-input"
          placeholder="Rechercher un canal (ex: Facebook, WhatsApp, TikTok)..."
        />
        <button v-if="searchQuery" @click="searchQuery = ''" class="btn-clear-search">
          <X :size="14" />
        </button>
      </div>

      <div class="quick-tags">
        <span class="text-xs text-muted">Suggestions rapides :</span>
        <div class="tag-chips">
          <button
            v-for="sugg in quickSuggestions"
            :key="sugg"
            @click="quickAddSuggestion(sugg)"
            class="chip-btn"
            :disabled="provenances.some(p => p.label.toLowerCase() === sugg.toLowerCase())"
            :title="provenances.some(p => p.label.toLowerCase() === sugg.toLowerCase()) ? 'Déjà ajouté' : 'Ajouter ' + sugg"
          >
            + {{ sugg }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <RefreshCw :size="32" class="spin-icon text-primary" />
      <span>Chargement des canaux de provenance...</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredProvenances.length === 0" class="empty-state card">
      <div class="empty-icon-wrap">
        <Compass :size="48" class="text-muted" />
      </div>
      <h3>Aucun canal de provenance trouvé</h3>
      <p class="text-muted text-sm">
        {{ searchQuery ? "Aucun canal ne correspond à votre recherche." : "Commencez par ajouter votre premier canal d'acquisition client." }}
      </p>
      <button @click="openCreateModal" class="btn btn-primary mt-3">
        <Plus :size="16" />
        <span>Créer un canal</span>
      </button>
    </div>

    <!-- Provenance Cards Grid -->
    <div v-else class="cards-grid">
      <div
        v-for="prov in filteredProvenances"
        :key="prov.id"
        class="card prov-card animate-fade"
      >
        <div class="prov-card-header">
          <div class="prov-badge-icon" :style="{ background: getChannelColor(prov.label).bg, color: getChannelColor(prov.label).text }">
            <component :is="getChannelIcon(prov.label)" :size="20" />
          </div>
          <div class="prov-meta">
            <h3 class="prov-title">{{ prov.label }}</h3>
            <span class="text-xs text-muted">ID canal: #{{ prov.id }}</span>
          </div>
        </div>

        <div class="prov-stats">
          <div class="stat-row">
            <span class="stat-title">Clients rattachés</span>
            <span class="stat-num font-mono">{{ prov.clients_count || 0 }}</span>
          </div>
          <div class="progress-track">
            <div
              class="progress-fill"
              :style="{
                width: `${getPercentage(prov.clients_count)}%`,
                backgroundColor: getChannelColor(prov.label).text
              }"
            ></div>
          </div>
          <div class="stat-footer-text">
            <span>{{ getPercentage(prov.clients_count) }}% du portefeuille client</span>
          </div>
        </div>

        <div class="prov-card-actions">
          <button @click="openEditModal(prov)" class="btn btn-secondary btn-sm" title="Modifier le libellé">
            <Edit2 :size="14" />
            <span>Modifier</span>
          </button>
          <button @click="openDeleteModal(prov)" class="btn-icon btn-danger-icon" title="Supprimer ce canal">
            <Trash2 :size="16" />
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL: Créer / Modifier une provenance -->
    <div v-if="showModal" class="modal-backdrop">
      <div class="modal-card card animate-scale">
        <div class="modal-header">
          <div class="modal-title-wrap">
            <component :is="isEditing ? Edit2 : PlusCircle" :size="22" class="text-primary" />
            <h3>{{ isEditing ? 'Modifier le canal' : 'Nouveau canal de provenance' }}</h3>
          </div>
          <button @click="closeModal" class="btn-close"><X :size="20" /></button>
        </div>

        <form @submit.prevent="saveProvenance" class="modal-body">
          <div v-if="formError" class="error-banner">
            <AlertCircle :size="16" />
            <span>{{ formError }}</span>
          </div>

          <div class="form-group">
            <label class="form-label">Nom du canal d'acquisition *</label>
            <input
              v-model="form.label"
              type="text"
              class="form-input"
              placeholder="Ex: Facebook, WhatsApp, TikTok, Site Web..."
              required
              autofocus
            />
            <span class="form-hint">Ce nom apparaîtra dans les fiches clients et les rapports de ventes.</span>
          </div>

          <!-- Quick pick suggestions -->
          <div class="form-group">
            <label class="form-label text-xs text-muted">Ou choisissez parmi les modèles courants :</label>
            <div class="chip-container">
              <button
                v-for="sugg in quickSuggestions"
                :key="sugg"
                type="button"
                @click="form.label = sugg"
                class="chip-select"
                :class="{ active: form.label === sugg }"
              >
                {{ sugg }}
              </button>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              Annuler
            </button>
            <button type="submit" class="btn btn-primary" :disabled="submitting || !form.label.trim()">
              <RefreshCw v-if="submitting" :size="16" class="spin-icon" />
              <span>{{ isEditing ? 'Enregistrer les modifications' : 'Créer le canal' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL: Confirmation de suppression -->
    <div v-if="showDeleteConfirm" class="modal-backdrop">
      <div class="modal-card card animate-scale danger-modal">
        <div class="modal-header danger-header">
          <div class="modal-title-wrap">
            <AlertTriangle :size="24" class="text-rose" />
            <h3>Supprimer le canal ?</h3>
          </div>
          <button @click="showDeleteConfirm = false" class="btn-close"><X :size="20" /></button>
        </div>

        <div class="modal-body">
          <p>
            Êtes-vous sûr de vouloir supprimer le canal <strong>« {{ itemToDelete?.label }} »</strong> ?
          </p>

          <div v-if="itemToDelete?.clients_count > 0" class="warning-box mt-3">
            <AlertCircle :size="18" class="text-amber flex-shrink-0" />
            <div>
              <strong>Attention :</strong> {{ itemToDelete.clients_count }} client(s) utilisent actuellement cette provenance.
              Leur provenance sera réinitialisée à <em>Non renseignée</em>.
            </div>
          </div>

          <div v-if="deleteError" class="error-banner mt-3">
            <AlertCircle :size="16" />
            <span>{{ deleteError }}</span>
          </div>

          <div class="modal-actions mt-4">
            <button type="button" @click="showDeleteConfirm = false" class="btn btn-secondary">
              Annuler
            </button>
            <button
              type="button"
              @click="confirmDelete(true)"
              class="btn btn-danger"
              :disabled="deleting"
            >
              <RefreshCw v-if="deleting" :size="16" class="spin-icon" />
              <span>Confirmer la suppression</span>
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
  Share2,
  Users,
  Award,
  Search,
  Plus,
  PlusCircle,
  Edit2,
  Trash2,
  X,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  Compass,
  Globe,
  MessageCircle,
  PhoneCall,
  UserCheck,
} from 'lucide-vue-next'
import apiClient from '../api/client'

const provenances = ref([])
const loading = ref(true)
const submitting = ref(false)
const deleting = ref(false)
const searchQuery = ref('')
const actionMessage = ref('')

const showModal = ref(false)
const isEditing = ref(false)
const form = ref({ id: null, label: '' })
const formError = ref('')

const showDeleteConfirm = ref(false)
const itemToDelete = ref(null)
const deleteError = ref('')

const quickSuggestions = [
  'Facebook',
  'WhatsApp',
  'TikTok',
  'Bouche à oreille',
  'Site Web',
  'Instagram',
  'LinkedIn',
  'Prospection directe',
  'Foire / Salon',
  'Recommandation client',
]

const totalClientsAssigned = computed(() => {
  return provenances.value.reduce((acc, p) => acc + (p.clients_count || 0), 0)
})

const topChannelName = computed(() => {
  if (!provenances.value.length) return 'Aucun canal'
  const sorted = [...provenances.value].sort((a, b) => (b.clients_count || 0) - (a.clients_count || 0))
  if (!sorted[0].clients_count) return sorted[0].label
  return `${sorted[0].label} (${sorted[0].clients_count})`
})

const filteredProvenances = computed(() => {
  if (!searchQuery.value.trim()) return provenances.value
  const q = searchQuery.value.toLowerCase().trim()
  return provenances.value.filter(p => p.label.toLowerCase().includes(q))
})

function getPercentage(count) {
  if (!totalClientsAssigned.value || !count) return 0
  return Math.round((count / totalClientsAssigned.value) * 100)
}

function getChannelColor(label) {
  const l = (label || '').toLowerCase()
  if (l.includes('facebook')) return { bg: 'rgba(24, 119, 242, 0.18)', text: '#1877f2' }
  if (l.includes('whatsapp')) return { bg: 'rgba(37, 211, 102, 0.18)', text: '#25d366' }
  if (l.includes('tiktok')) return { bg: 'rgba(254, 44, 85, 0.18)', text: '#fe2c55' }
  if (l.includes('insta')) return { bg: 'rgba(225, 48, 108, 0.18)', text: '#e1306c' }
  if (l.includes('linkedin')) return { bg: 'rgba(10, 102, 194, 0.18)', text: '#0a66c2' }
  if (l.includes('site') || l.includes('web')) return { bg: 'rgba(0, 210, 255, 0.18)', text: '#00d2ff' }
  if (l.includes('bouche') || l.includes('recommandation')) return { bg: 'rgba(245, 158, 11, 0.18)', text: '#f59e0b' }
  return { bg: 'rgba(139, 92, 246, 0.18)', text: '#8b5cf6' }
}

function getChannelIcon(label) {
  const l = (label || '').toLowerCase()
  if (l.includes('whatsapp') || l.includes('message')) return MessageCircle
  if (l.includes('site') || l.includes('web')) return Globe
  if (l.includes('phone') || l.includes('appel')) return PhoneCall
  if (l.includes('bouche') || l.includes('recommandation')) return UserCheck
  return Share2
}

async function fetchProvenances() {
  loading.value = true
  try {
    const res = await apiClient.get('/clients/provenances/')
    provenances.value = res.data
  } catch (err) {
    console.error('Erreur chargement provenances:', err)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  isEditing.value = false
  form.value = { id: null, label: '' }
  formError.value = ''
  showModal.value = true
}

function openEditModal(prov) {
  isEditing.value = true
  form.value = { id: prov.id, label: prov.label }
  formError.value = ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  formError.value = ''
}

async function saveProvenance() {
  const label = form.value.label.trim()
  if (!label) return

  submitting.value = true
  formError.value = ''

  try {
    if (isEditing.value) {
      await apiClient.put(`/clients/provenances/${form.value.id}/`, { label })
      actionMessage.value = `Canal « ${label} » mis à jour avec succès.`
    } else {
      await apiClient.post('/clients/provenances/', { label })
      actionMessage.value = `Nouveau canal « ${label} » ajouté avec succès.`
    }
    closeModal()
    await fetchProvenances()
    setTimeout(() => { actionMessage.value = '' }, 4000)
  } catch (err) {
    formError.value = err.response?.data?.label?.[0] || err.response?.data?.error || 'Erreur lors de l’enregistrement.'
  } finally {
    submitting.value = false
  }
}

async function quickAddSuggestion(sugg) {
  if (provenances.value.some(p => p.label.toLowerCase() === sugg.toLowerCase())) return
  try {
    await apiClient.post('/clients/provenances/', { label: sugg })
    actionMessage.value = `Canal « ${sugg} » ajouté avec succès.`
    await fetchProvenances()
    setTimeout(() => { actionMessage.value = '' }, 4000)
  } catch (err) {
    console.error('Erreur ajout suggestion:', err)
  }
}

function openDeleteModal(prov) {
  itemToDelete.value = prov
  deleteError.value = ''
  showDeleteConfirm.value = true
}

async function confirmDelete(force = false) {
  if (!itemToDelete.value) return
  deleting.value = true
  deleteError.value = ''

  try {
    const url = `/clients/provenances/${itemToDelete.value.id}/${force ? '?force=true' : ''}`
    await apiClient.delete(url)
    actionMessage.value = `Canal « ${itemToDelete.value.label} » supprimé.`
    showDeleteConfirm.value = false
    await fetchProvenances()
    setTimeout(() => { actionMessage.value = '' }, 4000)
  } catch (err) {
    deleteError.value = err.response?.data?.error || 'Erreur lors de la suppression.'
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  fetchProvenances()
})
</script>

<style scoped>
.provenances-view {
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
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
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

.kpi-body {
  display: flex;
  flex-direction: column;
  overflow: hidden;
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

.font-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Toolbar */
.toolbar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.25rem;
}

.search-box {
  position: relative;
  max-width: 480px;
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

.quick-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.chip-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  border-radius: 9999px;
  padding: 0.25rem 0.65rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.chip-btn:hover:not(:disabled) {
  background: rgba(0, 210, 255, 0.15);
  color: var(--primary);
  border-color: rgba(0, 210, 255, 0.3);
}

.chip-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Cards Grid */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
}

.prov-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1.25rem;
  padding: 1.35rem;
  border-radius: var(--radius-lg);
}

.prov-card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.prov-badge-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.prov-meta {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.prov-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.prov-stats {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  background: rgba(0, 0, 0, 0.2);
  padding: 0.85rem;
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.03);
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.stat-title {
  color: var(--text-secondary);
}

.stat-num {
  font-weight: 800;
  font-size: 1.05rem;
}

.progress-track {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  overflow: hidden;
  margin-top: 0.2rem;
}

.progress-fill {
  height: 100%;
  transition: width 0.4s ease;
  border-radius: 3px;
}

.stat-footer-text {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.prov-card-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 0.85rem;
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
  max-width: 500px;
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
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.form-input {
  width: 100%;
  padding: 0.7rem 0.9rem;
  background: rgba(10, 20, 36, 0.8);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-main);
  font-size: 0.95rem;
}

.form-input:focus {
  border-color: var(--primary);
  outline: none;
  box-shadow: 0 0 10px rgba(0, 210, 255, 0.2);
}

.chip-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.2rem;
}

.chip-select {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  border-radius: 9999px;
  padding: 0.3rem 0.7rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.chip-select:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.chip-select.active {
  background: rgba(0, 210, 255, 0.2);
  border-color: var(--primary);
  color: var(--primary);
  font-weight: 700;
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem 1.5rem;
  gap: 0.5rem;
}

.empty-icon-wrap {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.loading-state {
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
