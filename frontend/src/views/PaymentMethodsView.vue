<template>
  <div class="payments-view">
    <!-- Header with Stats & Actions -->
    <div class="view-header">
      <div class="header-info">
        <div class="title-with-badge">
          <h2>Modes de Règlement</h2>
          <span class="badge badge-primary">{{ methods.length }} canaux</span>
        </div>
        <p class="text-sm text-muted">
          Configurez les comptes et canaux de réception des paiements (MVola, Orange Money, Espèces, Virement bancaire...).
        </p>
      </div>

      <div class="header-actions">
        <button @click="openCreateModal" class="btn btn-primary">
          <Plus :size="18" />
          <span>Nouveau Mode de Règlement</span>
        </button>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="card kpi-card">
        <div class="kpi-icon-box cyan">
          <CreditCard :size="22" />
        </div>
        <div class="kpi-body">
          <span class="kpi-label">TOTAL CANAUX</span>
          <span class="kpi-value">{{ methods.length }}</span>
        </div>
      </div>

      <div class="card kpi-card">
        <div class="kpi-icon-box emerald">
          <CheckCircle2 :size="22" />
        </div>
        <div class="kpi-body">
          <span class="kpi-label">CANAUX ACTIFS</span>
          <span class="kpi-value text-emerald">{{ activeCount }}</span>
        </div>
      </div>

      <div class="card kpi-card">
        <div class="kpi-icon-box amber">
          <Wallet :size="22" />
        </div>
        <div class="kpi-body">
          <span class="kpi-label">VENTES ASSOCIÉES</span>
          <span class="kpi-value text-amber">{{ totalSalesCount }}</span>
        </div>
      </div>
    </div>

    <!-- Filters & Search Toolbar -->
    <div class="toolbar card">
      <div class="search-box">
        <Search :size="18" class="search-icon" />
        <input
          v-model="searchQuery"
          type="text"
          class="form-input search-input"
          placeholder="Rechercher par nom (ex: MVola, BNI) ou coordonnées..."
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
          Tous ({{ methods.length }})
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
      <span>Chargement des méthodes de paiement...</span>
    </div>

    <!-- Payment Methods Grid -->
    <div v-else-if="filteredMethods.length" class="methods-grid">
      <div
        v-for="item in filteredMethods"
        :key="item.id"
        class="card method-card"
        :class="{ 'card-inactive': !item.is_active, [getMethodTheme(item.label)]: true }"
      >
        <!-- Card Header: Brand Icon, Name, and Status Toggle -->
        <div class="card-header-row">
          <div class="method-brand">
            <div class="brand-avatar" :class="getMethodTheme(item.label)">
              <component :is="getMethodIcon(item.label)" :size="20" />
            </div>
            <div class="brand-text">
              <h3 class="method-label">{{ item.label }}</h3>
              <span class="brand-type-badge">{{ getMethodTypeName(item.label) }}</span>
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

        <!-- Details / Account Instructions Box -->
        <div class="method-details-box">
          <div class="details-header">
            <span class="text-xs text-muted uppercase font-bold">Instructions client & Coordonnées</span>
            <button
              v-if="item.details"
              @click="copyDetails(item)"
              class="btn-copy-sm"
              title="Copier les coordonnées pour le client"
            >
              <Check v-if="copiedId === item.id" :size="13" class="text-emerald" />
              <Copy v-else :size="13" />
              <span>{{ copiedId === item.id ? 'Copié !' : 'Copier' }}</span>
            </button>
          </div>
          <div class="details-content">
            <p v-if="item.details" class="details-text">{{ item.details }}</p>
            <p v-else class="text-muted text-xs italic">Aucune consigne ou numéro renseigné.</p>
          </div>
        </div>

        <!-- Card Footer: Stats & Actions -->
        <div class="card-footer-row">
          <div class="sales-counter" :title="`${item.ventes_count || 0} vente(s) enregistrée(s) avec ce mode`">
            <ShoppingCart :size="14" class="text-secondary" />
            <span class="text-xs">
              <strong>{{ item.ventes_count || 0 }}</strong> {{ item.ventes_count === 1 ? 'vente' : 'ventes' }}
            </span>
          </div>

          <div class="card-actions">
            <button @click="openEditModal(item)" class="btn btn-secondary btn-sm" title="Modifier ce mode">
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
      <CreditCard :size="48" class="text-muted" />
      <h3>Aucun mode de règlement trouvé</h3>
      <p class="text-muted text-sm" v-if="searchQuery || statusFilter !== 'all'">
        Aucun résultat pour cette recherche. Essayez de réinitialiser vos filtres.
      </p>
      <p class="text-muted text-sm" v-else>
        Ajoutez votre premier compte de réception (MVola, Orange Money, Espèces...) pour enregistrer des ventes.
      </p>
      <button @click="openCreateModal" class="btn btn-primary mt-3">
        <Plus :size="16" />
        <span>Créer un Mode de Règlement</span>
      </button>
    </div>

    <!-- MODAL: Créer / Modifier Mode de Paiement -->
    <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
      <div class="modal-card card animate-fade">
        <div class="modal-header">
          <div class="modal-title-wrap">
            <div class="modal-icon-badge" :class="isEditing ? 'amber' : 'cyan'">
              <CreditCard :size="20" />
            </div>
            <div>
              <h3>{{ isEditing ? 'Modifier le Mode de Règlement' : 'Nouveau Mode de Règlement' }}</h3>
              <span class="text-xs text-muted">
                {{ isEditing ? 'Mise à jour des coordonnées et statut' : 'Ajoutez un nouveau canal de réception' }}
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
                :key="preset.label"
                @click="applyPreset(preset)"
                class="preset-chip"
                :class="preset.theme"
              >
                <span>{{ preset.emoji }}</span>
                <span>{{ preset.shortName }}</span>
              </button>
            </div>
          </div>

          <!-- Label -->
          <div class="form-group">
            <label class="form-label">Nom du mode de paiement *</label>
            <input
              v-model="form.label"
              required
              type="text"
              class="form-input"
              placeholder="Ex: MVola Telma, Orange Money, Espèces..."
            />
          </div>

          <!-- Details / Instructions -->
          <div class="form-group">
            <label class="form-label">Coordonnées & Instructions client</label>
            <textarea
              v-model="form.details"
              rows="3"
              class="form-textarea font-mono text-sm"
              placeholder="Ex: Numéro : 034 XX XXX XX (Titulaire : NOM Prénom)&#10;Tapez *111# pour valider le transfert."
            ></textarea>
            <span class="form-hint">
              Ces informations pourront être copiées en 1 clic par vos media buyers pour les transmettre aux clients.
            </span>
          </div>

          <!-- Active Switch -->
          <div class="form-group active-toggle-group">
            <label class="checkbox-container">
              <input type="checkbox" v-model="form.is_active" />
              <span class="checkmark"></span>
              <span class="checkbox-label">
                <strong>Mode actif</strong>
                <span class="text-xs text-muted block">Proposé automatiquement dans le menu déroulant des ventes.</span>
              </span>
            </label>
          </div>

          <!-- Actions -->
          <div class="modal-actions">
            <button type="button" @click="showModal = false" class="btn btn-secondary">
              Annuler
            </button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              <span v-if="submitting">Enregistrement...</span>
              <span v-else>{{ isEditing ? 'Sauvegarder les modifications' : 'Créer le mode' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  CreditCard,
  Plus,
  Search,
  X,
  Edit3,
  Trash2,
  Copy,
  Check,
  CheckCircle2,
  RefreshCw,
  Wallet,
  Smartphone,
  Banknote,
  Building2,
  ShoppingCart
} from '@lucide/vue'
import apiClient from '../api/client'

const methods = ref([])
const loading = ref(false)
const submitting = ref(false)
const togglingId = ref(null)
const copiedId = ref(null)

const searchQuery = ref('')
const statusFilter = ref('all') // 'all', 'active', 'inactive'

// Modal State
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

const form = ref({
  label: '',
  details: '',
  is_active: true,
})

// Quick Templates for Madagascar
const presets = [
  {
    label: 'MVola (Telma)',
    shortName: 'MVola',
    emoji: '📱',
    theme: 'theme-mvola',
    details: 'Numéro MVola : 034 XX XXX XX\nTitulaire : [Nom complet]\nValider via #111#'
  },
  {
    label: 'Orange Money',
    shortName: 'Orange Money',
    emoji: '🍊',
    theme: 'theme-orange',
    details: 'Numéro Orange Money : 032 XX XXX XX\nTitulaire : [Nom complet]\nValider via #144#'
  },
  {
    label: 'Airtel Money',
    shortName: 'Airtel Money',
    emoji: '🔴',
    theme: 'theme-airtel',
    details: 'Numéro Airtel Money : 033 XX XXX XX\nTitulaire : [Nom complet]\nValider via *436#'
  },
  {
    label: 'Espèces (En main propre)',
    shortName: 'Espèces',
    emoji: '💵',
    theme: 'theme-cash',
    details: 'Paiement en espèces lors de la remise de la licence / en main propre.'
  },
  {
    label: 'Virement Bancaire (BNI / BOA)',
    shortName: 'Banque',
    emoji: '🏦',
    theme: 'theme-bank',
    details: 'Banque : BNI Madagascar\nIBAN / RIB : 00004 00000 00000000000 00\nTitulaire : LICENCE PRO'
  }
]

// Computed counts
const activeCount = computed(() => methods.value.filter(m => m.is_active).length)
const inactiveCount = computed(() => methods.value.filter(m => !m.is_active).length)
const totalSalesCount = computed(() => {
  return methods.value.reduce((acc, m) => acc + (m.ventes_count || 0), 0)
})

// Filtered Methods list
const filteredMethods = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  return methods.value.filter(m => {
    // Status filter
    if (statusFilter.value === 'active' && !m.is_active) return false
    if (statusFilter.value === 'inactive' && m.is_active) return false

    // Search query
    if (!query) return true
    const labelMatch = (m.label || '').toLowerCase().includes(query)
    const detailsMatch = (m.details || '').toLowerCase().includes(query)
    return labelMatch || detailsMatch
  })
})

async function fetchMethods() {
  loading.value = true
  try {
    const res = await apiClient.get('/ventes/methodes-paiement/')
    methods.value = res.data
  } catch (err) {
    console.error('Erreur chargement méthodes:', err)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  isEditing.value = false
  editingId.value = null
  form.value = {
    label: '',
    details: '',
    is_active: true,
  }
  showModal.value = true
}

function openEditModal(item) {
  isEditing.value = true
  editingId.value = item.id
  form.value = {
    label: item.label,
    details: item.details || '',
    is_active: item.is_active,
  }
  showModal.value = true
}

function applyPreset(preset) {
  form.value.label = preset.label
  form.value.details = preset.details
  form.value.is_active = true
}

async function submitForm() {
  if (!form.value.label.trim()) return
  submitting.value = true
  try {
    if (isEditing.value && editingId.value) {
      await apiClient.put(`/ventes/methodes-paiement/${editingId.value}/`, form.value)
    } else {
      await apiClient.post('/ventes/methodes-paiement/', form.value)
    }
    showModal.value = false
    await fetchMethods()
  } catch (err) {
    alert(err.response?.data?.error || err.response?.data?.detail || "Erreur lors de l'enregistrement.")
  } finally {
    submitting.value = false
  }
}

async function toggleActive(item) {
  togglingId.value = item.id
  try {
    const res = await apiClient.post(`/ventes/methodes-paiement/${item.id}/toggle-active/`)
    item.is_active = res.data.is_active
  } catch (err) {
    // Fallback to standard patch if toggle-active route not available
    try {
      const res = await apiClient.patch(`/ventes/methodes-paiement/${item.id}/`, {
        is_active: !item.is_active
      })
      item.is_active = res.data.is_active
    } catch (fallbackErr) {
      alert("Erreur lors de la mise à jour du statut.")
    }
  } finally {
    togglingId.value = null
  }
}

async function confirmDelete(item) {
  if (item.ventes_count > 0) {
    const shouldDeactivate = confirm(
      `Ce mode de paiement est lié à ${item.ventes_count} vente(s) existante(s) et ne peut être supprimé pour préserver l'historique comptable.\n\nSouhaitez-vous le DÉSACTIVER pour qu'il ne soit plus proposé aux clients ?`
    )
    if (shouldDeactivate && item.is_active) {
      await toggleActive(item)
    }
    return
  }

  if (!confirm(`Confirmez-vous la suppression définitive du mode "${item.label}" ?`)) return

  try {
    await apiClient.delete(`/ventes/methodes-paiement/${item.id}/`)
    await fetchMethods()
  } catch (err) {
    const errMsg = err.response?.data?.error || "Erreur lors de la suppression."
    alert(errMsg)
  }
}

function copyDetails(item) {
  if (!item.details) return
  navigator.clipboard.writeText(item.details)
  copiedId.value = item.id
  setTimeout(() => {
    if (copiedId.value === item.id) copiedId.value = null
  }, 2200)
}

// Brand Visual Helpers
function getMethodTheme(label) {
  const l = (label || '').toLowerCase()
  if (l.includes('mvola')) return 'theme-mvola'
  if (l.includes('orange')) return 'theme-orange'
  if (l.includes('airtel')) return 'theme-airtel'
  if (l.includes('espèce') || l.includes('espece') || l.includes('cash')) return 'theme-cash'
  if (l.includes('virement') || l.includes('banque') || l.includes('bni') || l.includes('boa')) return 'theme-bank'
  return 'theme-default'
}

function getMethodIcon(label) {
  const l = (label || '').toLowerCase()
  if (l.includes('mvola') || l.includes('orange') || l.includes('airtel')) return Smartphone
  if (l.includes('espèce') || l.includes('espece') || l.includes('cash')) return Banknote
  if (l.includes('virement') || l.includes('banque') || l.includes('bni') || l.includes('boa')) return Building2
  return CreditCard
}

function getMethodTypeName(label) {
  const l = (label || '').toLowerCase()
  if (l.includes('mvola') || l.includes('orange') || l.includes('airtel')) return 'Mobile Money'
  if (l.includes('espèce') || l.includes('espece') || l.includes('cash')) return 'Paiement Espèces'
  if (l.includes('virement') || l.includes('banque')) return 'Virement Bancaire'
  return 'Canal de Paiement'
}

onMounted(() => {
  fetchMethods()
})
</script>

<style scoped>
.payments-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Header */
.view-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.title-with-badge h2 {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text-main);
  margin: 0;
}

/* KPI Summary Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.25rem;
}

.kpi-icon-box {
  width: 50px;
  height: 50px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-icon-box.cyan {
  background: rgba(0, 210, 255, 0.12);
  color: #00d2ff;
  border: 1px solid rgba(0, 210, 255, 0.3);
}

.kpi-icon-box.emerald {
  background: rgba(52, 211, 153, 0.12);
  color: #34d399;
  border: 1px solid rgba(52, 211, 153, 0.3);
}

.kpi-icon-box.amber {
  background: rgba(251, 191, 36, 0.12);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.3);
}

.kpi-body {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.kpi-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
}

.kpi-value {
  font-size: 1.75rem;
  font-weight: 800;
  line-height: 1;
}

/* Toolbar */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 1.25rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 260px;
  max-width: 480px;
}

.search-icon {
  position: absolute;
  left: 0.85rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding-left: 2.5rem;
  padding-right: 2rem;
}

.btn-clear-search {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
}

.filter-pills {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pill-btn {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  padding: 0.4rem 0.85rem;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pill-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-main);
}

.pill-btn.active {
  background: rgba(0, 210, 255, 0.15);
  border-color: var(--primary-color);
  color: var(--primary-color);
  box-shadow: 0 0 10px rgba(0, 210, 255, 0.2);
}

/* Grid of Methods */
.methods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.25rem;
}

.method-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1.25rem;
  gap: 1.15rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  position: relative;
  overflow: hidden;
}

.method-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.method-card.card-inactive {
  opacity: 0.65;
  filter: grayscale(0.2);
}

/* Card Header */
.card-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.method-brand {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.brand-avatar {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.05);
}

/* Brand Theme Styles */
.brand-avatar.theme-mvola {
  background: rgba(234, 179, 8, 0.15);
  color: #eab308;
  border-color: rgba(234, 179, 8, 0.35);
}

.brand-avatar.theme-orange {
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
  border-color: rgba(249, 115, 22, 0.35);
}

.brand-avatar.theme-airtel {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.35);
}

.brand-avatar.theme-cash {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
  border-color: rgba(52, 211, 153, 0.35);
}

.brand-avatar.theme-bank {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
  border-color: rgba(59, 130, 246, 0.35);
}

.brand-avatar.theme-default {
  background: rgba(0, 210, 255, 0.15);
  color: #00d2ff;
  border-color: rgba(0, 210, 255, 0.35);
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.method-label {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-main);
  margin: 0;
}

.brand-type-badge {
  font-size: 0.7rem;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* Status Toggle Button */
.status-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.65rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.status-toggle-btn.toggle-on {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
  border-color: rgba(52, 211, 153, 0.35);
}

.status-toggle-btn.toggle-on:hover {
  background: rgba(52, 211, 153, 0.25);
  box-shadow: 0 0 10px rgba(52, 211, 153, 0.3);
}

.status-toggle-btn.toggle-off {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
  border-color: rgba(255, 255, 255, 0.1);
}

.status-toggle-btn.toggle-off:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-main);
}

.toggle-indicator {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
}

/* Details Box */
.method-details-box {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: var(--radius-sm);
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.details-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.btn-copy-sm {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  padding: 0.15rem 0.45rem;
  font-size: 0.7rem;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-copy-sm:hover {
  background: rgba(0, 210, 255, 0.15);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.details-text {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: var(--text-secondary);
  white-space: pre-wrap;
  line-height: 1.45;
  margin: 0;
}

/* Card Footer */
.card-footer-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 0.85rem;
}

.sales-counter {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--text-muted);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Modal Styling */
.modal-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.modal-icon-badge {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-icon-badge.cyan {
  background: rgba(0, 210, 255, 0.15);
  color: #00d2ff;
  border: 1px solid rgba(0, 210, 255, 0.35);
}

.modal-icon-badge.amber {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.35);
}

/* Presets Group in Modal */
.presets-group {
  background: rgba(0, 210, 255, 0.04);
  border: 1px solid rgba(0, 210, 255, 0.15);
  border-radius: var(--radius-sm);
  padding: 0.85rem;
}

.presets-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.35rem;
}

.preset-chip {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  padding: 0.3rem 0.65rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.preset-chip:hover {
  background: rgba(0, 210, 255, 0.15);
  border-color: var(--primary-color);
  color: var(--text-main);
  transform: translateY(-1px);
}

.form-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
  line-height: 1.4;
  margin-top: 0.25rem;
  display: block;
}

/* Active Toggle in Modal */
.active-toggle-group {
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
}

.checkbox-container {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  position: relative;
  user-select: none;
}

.checkbox-container input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  height: 20px;
  width: 20px;
  background-color: rgba(255, 255, 255, 0.05);
  border: 1.5px solid var(--border-subtle);
  border-radius: 4px;
  display: inline-block;
  flex-shrink: 0;
  transition: all 0.2s ease;
  position: relative;
}

.checkbox-container input:checked ~ .checkmark {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.checkbox-container input:checked ~ .checkmark:after {
  content: "";
  position: absolute;
  display: block;
  left: 6px;
  top: 2px;
  width: 5px;
  height: 10px;
  border: solid #000;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-label {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
</style>
