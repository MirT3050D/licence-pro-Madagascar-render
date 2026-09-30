<template>
  <div class="suppliers-view">
    <!-- Header with Stats & Actions -->
    <div class="view-header">
      <div class="header-info">
        <div class="title-with-badge">
          <h2>Fournisseurs & Partenaires</h2>
          <span class="badge badge-primary">{{ suppliers.length }} fournisseurs</span>
        </div>
        <p class="text-sm text-muted">
          Gérez vos plateformes d'achat et grossistes (Kinguin, G2A, Eneba, Grossistes...) pour une traçabilité totale de vos clés de licences.
        </p>
      </div>

      <div class="header-actions">
        <button @click="openCreateModal" class="btn btn-primary">
          <Plus :size="18" />
          <span>Nouveau Fournisseur</span>
        </button>
      </div>
    </div>

    <!-- Alert notification -->
    <div v-if="actionMessage" class="action-alert animate-fade">
      <CheckCircle2 :size="18" class="text-emerald flex-shrink-0" />
      <span>{{ actionMessage }}</span>
      <button @click="actionMessage = ''" class="btn-clear-alert"><X :size="14" /></button>
    </div>

    <!-- Error notification -->
    <div v-if="errorMessage" class="action-alert error-alert animate-fade">
      <AlertCircle :size="18" class="text-rose flex-shrink-0" />
      <span>{{ errorMessage }}</span>
      <button @click="errorMessage = ''" class="btn-clear-alert"><X :size="14" /></button>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="card kpi-card">
        <div class="kpi-icon-box cyan">
          <Truck :size="22" />
        </div>
        <div class="kpi-body">
          <span class="kpi-label">TOTAL FOURNISSEURS</span>
          <span class="kpi-value">{{ suppliers.length }}</span>
        </div>
      </div>

      <div class="card kpi-card">
        <div class="kpi-icon-box emerald">
          <CheckCircle2 :size="22" />
        </div>
        <div class="kpi-body">
          <span class="kpi-label">FOURNISSEURS ACTIFS</span>
          <span class="kpi-value text-emerald">{{ activeCount }}</span>
        </div>
      </div>

      <div class="card kpi-card">
        <div class="kpi-icon-box amber">
          <ShoppingCart :size="22" />
        </div>
        <div class="kpi-body">
          <span class="kpi-label">COMMANDES RATTACHÉES</span>
          <span class="kpi-value text-amber">{{ totalSalesCount }}</span>
        </div>
      </div>

      <div class="card kpi-card">
        <div class="kpi-icon-box purple">
          <Award :size="22" />
        </div>
        <div class="kpi-body">
          <span class="kpi-label">FOURNISSEUR TOP</span>
          <span class="kpi-value text-purple font-truncate" :title="topSupplierName">
            {{ topSupplierName }}
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
          placeholder="Rechercher par nom (ex: Kinguin, G2A), contact ou notes..."
        />
        <button v-if="searchQuery" @click="searchQuery = ''" class="btn-clear-search">
          <X :size="14" />
        </button>
      </div>

      <div class="filter-pills">
        <button
          @click="statusFilter = 'all'"
          class="pill-btn"
          :class="{ active: statusFilter === 'all' }"
        >
          Tous ({{ suppliers.length }})
        </button>
        <button
          @click="statusFilter = 'active'"
          class="pill-btn"
          :class="{ active: statusFilter === 'active' }"
        >
          Actifs ({{ activeCount }})
        </button>
        <button
          @click="statusFilter = 'inactive'"
          class="pill-btn"
          :class="{ active: statusFilter === 'inactive' }"
        >
          Inactifs ({{ inactiveCount }})
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <RefreshCw :size="32" class="spin-icon text-primary" />
      <span>Chargement des fournisseurs...</span>
    </div>

    <!-- Suppliers Grid -->
    <div v-else-if="filteredSuppliers.length" class="suppliers-grid">
      <div
        v-for="item in filteredSuppliers"
        :key="item.id"
        class="card supplier-card"
        :class="{ 'card-inactive': !item.is_active }"
      >
        <!-- Header: Avatar, Name & Status Switch -->
        <div class="card-header-row">
          <div class="supplier-brand">
            <div class="brand-avatar" :class="getAvatarClass(item.nom)">
              <span>{{ getInitials(item.nom) }}</span>
            </div>
            <div class="brand-text">
              <h3 class="supplier-name">{{ item.nom }}</h3>
              <span class="supplier-date">Ajouté le {{ formatDate(item.created_at) }}</span>
            </div>
          </div>

          <!-- Quick Toggle Active Status -->
          <button
            @click="toggleActive(item)"
            class="status-toggle-btn"
            :class="item.is_active ? 'toggle-on' : 'toggle-off'"
            :title="item.is_active ? 'Cliquer pour désactiver' : 'Cliquer pour activer'"
            :disabled="togglingId === item.id"
          >
            <span class="toggle-indicator"></span>
            <span class="toggle-text">{{ item.is_active ? 'Actif' : 'Désactivé' }}</span>
          </button>
        </div>

        <!-- Details Box -->
        <div class="supplier-body-box">
          <!-- Web Link -->
          <div v-if="item.site_web" class="info-row">
            <span class="info-lbl">
              <Globe :size="13" />
              <span>Portail / Site web :</span>
            </span>
            <div class="link-actions">
              <a :href="normalizeUrl(item.site_web)" target="_blank" rel="noopener noreferrer" class="link-anchor" :title="item.site_web">
                <span>{{ cleanUrlDisplay(item.site_web) }}</span>
                <ExternalLink :size="12" />
              </a>
              <button @click="copyText(item.site_web, 'Lien copié !')" class="btn-copy-mini" title="Copier le lien">
                <Copy :size="11" />
              </button>
            </div>
          </div>

          <!-- Contact / Téléphone / WhatsApp -->
          <div v-if="item.contact" class="info-row">
            <span class="info-lbl">
              <MessageSquare :size="13" />
              <span>Contact :</span>
            </span>
            <div class="link-actions">
              <span class="contact-val">{{ item.contact }}</span>
              <button @click="copyText(item.contact, 'Contact copié !')" class="btn-copy-mini" title="Copier le contact">
                <Copy :size="11" />
              </button>
            </div>
          </div>

          <!-- Notes / Infos -->
          <div v-if="item.notes" class="notes-box">
            <span class="notes-lbl">Notes & Conditions :</span>
            <p class="notes-text">{{ item.notes }}</p>
          </div>

          <div v-if="!item.site_web && !item.contact && !item.notes" class="empty-info-msg">
            <span>Aucune coordonnée ou lien enregistré.</span>
          </div>
        </div>

        <!-- Footer: Stats & Actions -->
        <div class="card-footer-row">
          <div class="sales-counter" :title="`${item.ventes_count || 0} vente(s) achetée(s) chez ce fournisseur`">
            <ShoppingCart :size="14" class="text-secondary" />
            <span class="text-xs">
              <strong>{{ item.ventes_count || 0 }}</strong> {{ item.ventes_count === 1 ? 'commande' : 'commandes' }}
            </span>
          </div>

          <div class="card-actions">
            <button @click="openEditModal(item)" class="btn btn-secondary btn-sm" title="Modifier ce fournisseur">
              <Edit3 :size="14" />
              <span>Modifier</span>
            </button>

            <button
              @click="confirmDelete(item)"
              class="btn-icon btn-danger-icon"
              title="Supprimer définitivement"
            >
              <Trash2 :size="15" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state card">
      <Truck :size="48" class="text-muted" />
      <h3>Aucun fournisseur trouvé</h3>
      <p class="text-muted text-sm" v-if="searchQuery || statusFilter !== 'all'">
        Aucun résultat pour cette recherche. Essayez de réinitialiser vos filtres.
      </p>
      <p class="text-muted text-sm" v-else>
        Enregistrez vos fournisseurs (Kinguin, G2A, etc.) pour tracer chaque commande de licence en binôme avec le numéro de transaction.
      </p>
      <button @click="openCreateModal" class="btn btn-primary mt-3">
        <Plus :size="16" />
        <span>Créer un Fournisseur</span>
      </button>
    </div>

    <!-- MODAL: Créer / Modifier Fournisseur -->
    <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
      <div class="modal-card card animate-fade">
        <div class="modal-header">
          <div class="modal-title-wrap">
            <div class="modal-icon-badge" :class="isEditing ? 'amber' : 'cyan'">
              <Truck :size="20" />
            </div>
            <div>
              <h3>{{ isEditing ? 'Modifier le Fournisseur' : 'Nouveau Fournisseur' }}</h3>
              <span class="text-xs text-muted">
                {{ isEditing ? 'Mise à jour des coordonnées et informations' : 'Ajoutez une source d\'approvisionnement pour vos licences' }}
              </span>
            </div>
          </div>
          <button @click="showModal = false" class="btn-close"><X :size="20" /></button>
        </div>

        <form @submit.prevent="submitForm" class="modal-body">
          <!-- Quick Presets buttons (Creation only) -->
          <div v-if="!isEditing" class="form-group presets-group">
            <label class="form-label text-xs">Modèles rapides en 1 clic :</label>
            <div class="presets-row">
              <button
                type="button"
                v-for="preset in presets"
                :key="preset.nom"
                @click="applyPreset(preset)"
                class="preset-chip"
                :disabled="suppliers.some(s => s.nom.toLowerCase() === preset.nom.toLowerCase())"
              >
                <span>{{ preset.emoji }}</span>
                <span>{{ preset.nom }}</span>
              </button>
            </div>
          </div>

          <!-- Nom -->
          <div class="form-group">
            <label class="form-label">Nom du fournisseur *</label>
            <input
              v-model="form.nom"
              required
              type="text"
              class="form-input"
              placeholder="Ex: Kinguin, G2A, Eneba, Grossiste Dubaï..."
            />
          </div>

          <!-- Contact -->
          <div class="form-group">
            <label class="form-label">Contact / Référence</label>
            <input
              v-model="form.contact"
              type="text"
              class="form-input"
              placeholder="Ex: WhatsApp +33..., Telegram @fournisseur, support@..."
            />
            <span class="form-hint">Numéro, Telegram ou email du commercial ou support vendeur.</span>
          </div>

          <!-- Site Web / Portail d'achat -->
          <div class="form-group">
            <label class="form-label">Site web / Portail d'achat direct</label>
            <input
              v-model="form.site_web"
              type="text"
              class="form-input"
              placeholder="Ex: https://www.kinguin.net ou https://www.g2a.com"
            />
            <span class="form-hint">Lien direct vers la boutique pour acheter les clés en 1 clic.</span>
          </div>

          <!-- Notes / Infos -->
          <div class="form-group">
            <label class="form-label">Notes & Conditions de garantie</label>
            <textarea
              v-model="form.notes"
              rows="3"
              class="form-textarea text-sm"
              placeholder="Ex: Clé livrée instantanément par email. Garantie réclamation 7 jours. Paiement via PayPal ou CB."
            ></textarea>
          </div>

          <!-- Active Switch -->
          <div class="form-group active-toggle-group">
            <label class="checkbox-container">
              <input type="checkbox" v-model="form.is_active" />
              <span class="checkmark"></span>
              <span class="checkbox-label">
                <strong>Fournisseur actif</strong>
                <span class="text-xs text-muted block">Proposé immédiatement dans le menu déroulant lors des enregistrements de vente.</span>
              </span>
            </label>
          </div>

          <!-- Modal Actions -->
          <div class="modal-actions">
            <button type="button" @click="showModal = false" class="btn btn-secondary">
              Annuler
            </button>
            <button type="submit" class="btn btn-primary" :disabled="submitting || !form.nom.trim()">
              <span v-if="submitting">Enregistrement...</span>
              <span v-else>{{ isEditing ? 'Mettre à jour' : 'Créer le fournisseur' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL: Confirmation Suppression -->
    <div v-if="deleteModalItem" class="modal-backdrop" @click.self="deleteModalItem = null">
      <div class="modal-card card delete-confirm-card animate-fade">
        <div class="delete-icon-box">
          <AlertTriangle :size="32" class="text-rose" />
        </div>
        <h3>Confirmer la suppression</h3>
        <p class="text-sm text-muted">
          Êtes-vous certain de vouloir supprimer définitivement le fournisseur
          <strong>« {{ deleteModalItem.nom }} »</strong> ?
        </p>

        <div v-if="deleteModalItem.ventes_count > 0" class="delete-warning-box">
          <AlertCircle :size="16" class="text-amber flex-shrink-0" />
          <span>
            Attention : Ce fournisseur est rattaché à <strong>{{ deleteModalItem.ventes_count }} vente(s)</strong>.
            La suppression sera refusée pour préserver l'historique comptable. Privilégiez plutôt sa désactivation.
          </span>
        </div>

        <div class="modal-actions mt-4">
          <button type="button" @click="deleteModalItem = null" class="btn btn-secondary">
            Annuler
          </button>
          <button
            type="button"
            @click="executeDelete"
            class="btn btn-danger"
            :disabled="deleting"
          >
            <span v-if="deleting">Suppression...</span>
            <span v-else>Supprimer définitivement</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Truck,
  Plus,
  Search,
  X,
  Edit3,
  Trash2,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  RefreshCw,
  ShoppingCart,
  Award,
  Globe,
  MessageSquare,
  ExternalLink,
  Copy,
} from 'lucide-vue-next'
import apiClient from '../api/client'

// État local
const suppliers = ref([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('all') // 'all', 'active', 'inactive'

const actionMessage = ref('')
const errorMessage = ref('')
let alertTimeout = null

// Modal création / édition
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const togglingId = ref(null)

const form = ref({
  nom: '',
  contact: '',
  site_web: '',
  notes: '',
  is_active: true,
})

// Modal suppression
const deleteModalItem = ref(null)
const deleting = ref(false)

// Modèles rapides
const presets = [
  { nom: 'Kinguin', emoji: '👑', site_web: 'https://www.kinguin.net', contact: 'Support Kinguin', notes: 'Achat de clés numériques en instantané.' },
  { nom: 'G2A', emoji: '🎮', site_web: 'https://www.g2a.com', contact: 'Marketplace G2A', notes: 'Garantie de clé valide, livraison immédiate.' },
  { nom: 'Eneba', emoji: '⚡', site_web: 'https://www.eneba.com', contact: 'Support Eneba', notes: 'Clés globales / Europe.' },
  { nom: 'Gamivo', emoji: '🛡️', site_web: 'https://www.gamivo.com', contact: 'Support Gamivo', notes: 'Bon prix sur packs Office & Windows.' },
  { nom: 'Grossiste Local', emoji: '🏢', site_web: '', contact: 'WhatsApp / Tél', notes: 'Fournisseur partenaire direct en local.' },
]

// Calculs & KPI
const activeCount = computed(() => suppliers.value.filter((s) => s.is_active).length)
const inactiveCount = computed(() => suppliers.value.filter((s) => !s.is_active).length)

const totalSalesCount = computed(() => {
  return suppliers.value.reduce((acc, curr) => acc + (curr.ventes_count || 0), 0)
})

const topSupplierName = computed(() => {
  if (!suppliers.value.length) return 'Aucun'
  const sorted = [...suppliers.value].sort((a, b) => (b.ventes_count || 0) - (a.ventes_count || 0))
  if ((sorted[0].ventes_count || 0) === 0) return sorted[0].nom
  return `${sorted[0].nom} (${sorted[0].ventes_count})`
})

const filteredSuppliers = computed(() => {
  let list = suppliers.value

  if (statusFilter.value === 'active') {
    list = list.filter((s) => s.is_active)
  } else if (statusFilter.value === 'inactive') {
    list = list.filter((s) => !s.is_active)
  }

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim()
    list = list.filter((s) => {
      return (
        s.nom.toLowerCase().includes(q) ||
        (s.contact && s.contact.toLowerCase().includes(q)) ||
        (s.site_web && s.site_web.toLowerCase().includes(q)) ||
        (s.notes && s.notes.toLowerCase().includes(q))
      )
    })
  }

  return list
})

// Fonctions API
async function fetchSuppliers() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await apiClient.get('/ventes/fournisseurs/')
    suppliers.value = res.data.results || res.data || []
  } catch (err) {
    console.error('Erreur chargement fournisseurs:', err)
    errorMessage.value = 'Impossible de charger la liste des fournisseurs.'
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  isEditing.value = false
  editingId.value = null
  form.value = {
    nom: '',
    contact: '',
    site_web: '',
    notes: '',
    is_active: true,
  }
  showModal.value = true
}

function openEditModal(item) {
  isEditing.value = true
  editingId.value = item.id
  form.value = {
    nom: item.nom || '',
    contact: item.contact || '',
    site_web: item.site_web || '',
    notes: item.notes || '',
    is_active: item.is_active !== false,
  }
  showModal.value = true
}

function applyPreset(preset) {
  form.value.nom = preset.nom
  form.value.site_web = preset.site_web || ''
  form.value.contact = preset.contact || ''
  form.value.notes = preset.notes || ''
}

async function submitForm() {
  if (!form.value.nom.trim()) return

  submitting.value = true
  try {
    if (isEditing.value) {
      await apiClient.put(`/ventes/fournisseurs/${editingId.value}/`, form.value)
      flashMessage(`Fournisseur « ${form.value.nom} » mis à jour avec succès !`)
    } else {
      await apiClient.post('/ventes/fournisseurs/', form.value)
      flashMessage(`Fournisseur « ${form.value.nom} » créé avec succès !`)
    }
    showModal.value = false
    await fetchSuppliers()
  } catch (err) {
    console.error('Erreur sauvegarde fournisseur:', err)
    const backendMsg = err.response?.data?.nom?.[0] || err.response?.data?.error || 'Erreur lors de l\'enregistrement.'
    flashError(backendMsg)
  } finally {
    submitting.value = false
  }
}

async function toggleActive(item) {
  togglingId.value = item.id
  try {
    const res = await apiClient.post(`/ventes/fournisseurs/${item.id}/toggle-active/`)
    item.is_active = res.data.is_active
    flashMessage(
      `Fournisseur « ${item.nom} » ${item.is_active ? 'activé' : 'désactivé'} !`
    )
  } catch (err) {
    console.error('Erreur bascule statut:', err)
    flashError('Erreur lors du changement de statut.')
  } finally {
    togglingId.value = null
  }
}

function confirmDelete(item) {
  deleteModalItem.value = item
}

async function executeDelete() {
  if (!deleteModalItem.value) return
  const item = deleteModalItem.value
  deleting.value = true

  try {
    await apiClient.delete(`/ventes/fournisseurs/${item.id}/`)
    flashMessage(`Fournisseur « ${item.nom} » supprimé avec succès.`)
    deleteModalItem.value = null
    await fetchSuppliers()
  } catch (err) {
    console.error('Erreur suppression:', err)
    const backendErr = err.response?.data?.error || 'Impossible de supprimer ce fournisseur.'
    flashError(backendErr)
  } finally {
    deleting.value = false
  }
}

// Helpers
function flashMessage(msg) {
  actionMessage.value = msg
  if (alertTimeout) clearTimeout(alertTimeout)
  alertTimeout = setTimeout(() => {
    actionMessage.value = ''
  }, 4000)
}

function flashError(msg) {
  errorMessage.value = msg
  if (alertTimeout) clearTimeout(alertTimeout)
  alertTimeout = setTimeout(() => {
    errorMessage.value = ''
  }, 5000)
}

function copyText(val, successMsg) {
  if (!val) return
  navigator.clipboard.writeText(val)
  flashMessage(successMsg || 'Copié dans le presse-papier !')
}

function normalizeUrl(url) {
  if (!url) return '#'
  if (!/^https?:\/\//i.test(url)) {
    return 'https://' + url
  }
  return url
}

function cleanUrlDisplay(url) {
  if (!url) return ''
  return url.replace(/^https?:\/\/(www\.)?/i, '').replace(/\/$/, '')
}

function getInitials(name) {
  if (!name) return 'FR'
  return name.slice(0, 2).toUpperCase()
}

function getAvatarClass(name) {
  const code = (name || '').charCodeAt(0) || 0
  const variants = ['avatar-cyan', 'avatar-emerald', 'avatar-amber', 'avatar-purple', 'avatar-blue']
  return variants[code % variants.length]
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

onMounted(() => {
  fetchSuppliers()
})
</script>

<style scoped>
.suppliers-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 1300px;
  margin: 0 auto;
}

/* Header */
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.title-with-badge h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: -0.02em;
}

/* Notifications */
.action-alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.25);
  color: #10B981;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 500;
}

.error-alert {
  background: rgba(244, 63, 94, 0.1);
  border-color: rgba(244, 63, 94, 0.25);
  color: #F43F5E;
}

.btn-clear-alert {
  margin-left: auto;
  background: transparent;
  border: none;
  color: inherit;
  cursor: pointer;
  opacity: 0.8;
  display: flex;
  align-items: center;
}

.btn-clear-alert:hover {
  opacity: 1;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.15rem 1.25rem;
}

.kpi-icon-box {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-icon-box.cyan {
  background: rgba(6, 182, 212, 0.12);
  color: #06B6D4;
}

.kpi-icon-box.emerald {
  background: rgba(16, 185, 129, 0.12);
  color: #10B981;
}

.kpi-icon-box.amber {
  background: rgba(245, 158, 11, 0.12);
  color: #F59E0B;
}

.kpi-icon-box.purple {
  background: rgba(168, 85, 247, 0.12);
  color: #A855F7;
}

.kpi-body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.kpi-label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

.kpi-value {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1.2;
}

.font-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 0.85rem 1.25rem;
}

.search-box {
  display: flex;
  align-items: center;
  position: relative;
  flex: 1;
  min-width: 260px;
}

.search-icon {
  position: absolute;
  left: 0.85rem;
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  padding-left: 2.4rem;
  padding-right: 2rem;
  width: 100%;
}

.btn-clear-search {
  position: absolute;
  right: 0.75rem;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
}

.filter-pills {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pill-btn {
  background: var(--bg-hover);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 0.4rem 0.85rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pill-btn:hover {
  color: var(--text-main);
  border-color: rgba(255, 255, 255, 0.2);
}

.pill-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

/* Suppliers Grid */
.suppliers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1.25rem;
}

.supplier-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1.25rem;
  border-radius: 14px;
  border: 1px solid var(--border-color);
  background: var(--bg-surface);
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.supplier-card:hover {
  transform: translateY(-2px);
  border-color: rgba(6, 182, 212, 0.4);
  box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.3);
}

.card-inactive {
  opacity: 0.65;
  filter: grayscale(0.2);
}

/* Card Header */
.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.supplier-brand {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.brand-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.05rem;
  flex-shrink: 0;
}

.avatar-cyan { background: rgba(6, 182, 212, 0.15); color: #06B6D4; border: 1px solid rgba(6, 182, 212, 0.3); }
.avatar-emerald { background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); }
.avatar-amber { background: rgba(245, 158, 11, 0.15); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.3); }
.avatar-purple { background: rgba(168, 85, 247, 0.15); color: #A855F7; border: 1px solid rgba(168, 85, 247, 0.3); }
.avatar-blue { background: rgba(59, 130, 246, 0.15); color: #3B82F6; border: 1px solid rgba(59, 130, 246, 0.3); }

.brand-text {
  display: flex;
  flex-direction: column;
}

.supplier-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-main);
  margin: 0;
}

.supplier-date {
  font-size: 0.72rem;
  color: var(--text-muted);
}

/* Status Toggle */
.status-toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.65rem;
  border-radius: 20px;
  border: 1px solid transparent;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-on {
  background: rgba(16, 185, 129, 0.12);
  color: #10B981;
  border-color: rgba(16, 185, 129, 0.3);
}

.toggle-off {
  background: rgba(100, 116, 139, 0.15);
  color: #94A3B8;
  border-color: rgba(100, 116, 139, 0.3);
}

.toggle-indicator {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
}

/* Card Body */
.supplier-body-box {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 0.85rem;
  margin-bottom: 1rem;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.82rem;
}

.info-lbl {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

.link-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  overflow: hidden;
}

.link-anchor {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: #06B6D4;
  text-decoration: none;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.link-anchor:hover {
  text-decoration: underline;
}

.contact-val {
  color: var(--text-main);
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-copy-mini {
  background: rgba(255, 255, 255, 0.06);
  border: none;
  color: var(--text-muted);
  width: 22px;
  height: 22px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.btn-copy-mini:hover {
  background: rgba(6, 182, 212, 0.2);
  color: #06B6D4;
}

.notes-box {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  border-top: 1px dashed rgba(255, 255, 255, 0.07);
  padding-top: 0.5rem;
  margin-top: 0.25rem;
}

.notes-lbl {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
}

.notes-text {
  font-size: 0.78rem;
  color: var(--text-secondary);
  line-height: 1.4;
  margin: 0;
  white-space: pre-wrap;
}

.empty-info-msg {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-style: italic;
  text-align: center;
  padding: 0.4rem 0;
}

/* Card Footer */
.card-footer-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.sales-counter {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--text-muted);
}

.sales-counter strong {
  color: var(--text-main);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  background: transparent;
}

.btn-danger-icon {
  color: #F43F5E;
}

.btn-danger-icon:hover {
  background: rgba(244, 63, 94, 0.12);
  border-color: rgba(244, 63, 94, 0.3);
}

/* Loading & Empty */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  text-align: center;
  gap: 0.75rem;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Modal Backdrops & Cards */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-card {
  width: 100%;
  max-width: 520px;
  background: #111827;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.6);
  padding: 1.5rem;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.25rem;
}

.modal-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.modal-icon-badge {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-icon-badge.cyan { background: rgba(6, 182, 212, 0.15); color: #06B6D4; }
.modal-icon-badge.amber { background: rgba(245, 158, 11, 0.15); color: #F59E0B; }

.modal-title-wrap h3 {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-main);
  margin: 0;
}

.btn-close {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
}

.btn-close:hover {
  color: var(--text-main);
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Presets */
.presets-group {
  margin-bottom: 0.25rem;
}

.presets-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.35rem;
}

.preset-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-main);
  padding: 0.3rem 0.65rem;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.preset-chip:hover:not(:disabled) {
  background: rgba(6, 182, 212, 0.15);
  border-color: rgba(6, 182, 212, 0.3);
  color: #06B6D4;
}

.preset-chip:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-hint {
  font-size: 0.72rem;
  color: var(--text-muted);
}

/* Checkbox toggle */
.active-toggle-group {
  padding-top: 0.35rem;
}

.checkbox-container {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
}

.checkbox-container input {
  margin-top: 0.2rem;
  cursor: pointer;
}

.checkbox-label strong {
  display: block;
  font-size: 0.85rem;
  color: var(--text-main);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

/* Delete confirmation card */
.delete-confirm-card {
  max-width: 440px;
  text-align: center;
}

.delete-icon-box {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(244, 63, 94, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem auto;
}

.delete-warning-box {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.25);
  color: #F59E0B;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 0.78rem;
  text-align: left;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .suppliers-grid {
    grid-template-columns: 1fr;
  }
}
</style>
