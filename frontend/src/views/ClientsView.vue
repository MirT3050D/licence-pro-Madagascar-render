<template>
  <div class="clients-view">
    <!-- Filters & Actions Header -->
    <div class="view-header-card card">
      <div class="filters-row">
        <!-- Recherche textuelle -->
        <div class="search-box">
          <Search :size="16" class="search-icon" />
          <input
            v-model="searchQuery"
            @input="onSearchInput"
            type="text"
            class="form-input search-input"
            placeholder="Rechercher client par nom ou numéro..."
          />
          <button v-if="searchQuery" @click="searchQuery = ''; fetchClients()" class="btn-clear-search">
            <X :size="13" />
          </button>
        </div>

        <!-- Multi-Sélection Provenances -->
        <MultiSelectDropdown
          v-model="selectedProvenances"
          :options="provenanceOptions"
          label="Provenances"
          placeholder="🌐 Toutes provenances"
          :icon="Globe"
          @change="fetchClients"
        />

        <!-- Sélecteur de Tri -->
        <div class="sort-selector-wrapper">
          <SlidersHorizontal :size="13" class="text-primary" />
          <span class="sort-label text-xs font-semibold text-muted">Trier :</span>
          <select v-model="sortSelectValue" @change="onSortSelectChange" class="form-select sort-select-compact">
            <option value="nom-asc">👤 Nom (A → Z)</option>
            <option value="nom-desc">👤 Nom (Z → A)</option>
            <option value="total-desc">💰 Total achats (Plus élevé)</option>
            <option value="total-asc">💰 Total achats (Plus bas)</option>
            <option value="ventes-desc">📦 Ventes (Plus de commandes)</option>
            <option value="ventes-asc">📦 Ventes (Moins de commandes)</option>
            <option value="provenance-asc">🌐 Provenance (A → Z)</option>
            <option value="created_at-desc">🕒 Date (Plus récents)</option>
            <option value="created_at-asc">🕒 Date (Plus anciens)</option>
          </select>
        </div>

        <!-- Reset Button -->
        <button
          v-if="hasActiveFilters"
          type="button"
          @click="resetFilters"
          class="btn btn-secondary btn-sm"
          title="Réinitialiser tous les filtres"
        >
          <RotateCcw :size="13" />
          <span>Réinitialiser</span>
        </button>

        <div class="header-actions-right">
          <router-link to="/provenances" class="btn btn-secondary btn-sm">
            <Share2 :size="15" />
            <span>Canaux</span>
          </router-link>
          <button @click="openCreateModal" class="btn btn-primary btn-sm">
            <Plus :size="16" />
            <span>Nouveau Client</span>
          </button>
        </div>
      </div>

      <!-- Quick Provenance Chips Bar -->
      <div v-if="provenances.length > 0" class="provenance-quick-bar">
        <div class="quick-bar-label">
          <Globe :size="13" class="text-primary" />
          <span>Canaux :</span>
        </div>
        <div class="quick-chips-scroll custom-scroll">
          <button
            type="button"
            class="prov-chip-btn"
            :class="{ 'active-all': selectedProvenances.length === 0 }"
            @click="clearProvenancesFilter"
            title="Afficher tous les canaux"
          >
            🌐 Tous ({{ clients.length }})
          </button>
          <button
            v-for="prov in provenances"
            :key="prov.id"
            type="button"
            class="prov-chip-btn"
            :class="{ active: selectedProvenances.includes(prov.id) }"
            :style="getProvenanceChipStyle(prov)"
            @click="toggleProvenanceFilter(prov.id)"
          >
            <span class="chip-dot" :style="{ backgroundColor: getProvenanceStyle(prov.label).dot }"></span>
            <span>{{ prov.label }}</span>
            <span v-if="prov.annotated_clients_count || prov.clients_count || getClientsCountForProv(prov.id)" class="chip-count">
              {{ prov.annotated_clients_count ?? prov.clients_count ?? getClientsCountForProv(prov.id) }}
            </span>
            <Check v-if="selectedProvenances.includes(prov.id)" :size="12" class="chip-check" />
          </button>
        </div>
      </div>

      <!-- Active Filters Pills Banner -->
      <div v-if="hasActiveFilters" class="active-filters-banner">
        <span class="text-xs text-muted">Filtres actifs :</span>
        <div class="active-pills-wrap">
          <span
            v-for="pId in selectedProvenances"
            :key="'pill-c-' + pId"
            class="active-filter-pill pill-provenance"
            :style="{
              borderColor: getProvenanceStyle(getProvenanceLabel(pId)).border,
              color: getProvenanceStyle(getProvenanceLabel(pId)).text
            }"
          >
            <span class="pill-dot" :style="{ backgroundColor: getProvenanceStyle(getProvenanceLabel(pId)).dot }"></span>
            <span>Canal : <strong>{{ getProvenanceLabel(pId) }}</strong></span>
            <button type="button" @click="removeProvenanceFilter(pId)" class="pill-remove-btn"><X :size="11" /></button>
          </span>

          <span v-if="searchQuery" class="active-filter-pill">
            <span>Recherche : <strong>"{{ searchQuery }}"</strong></span>
            <button type="button" @click="searchQuery = ''; fetchClients()" class="pill-remove-btn"><X :size="11" /></button>
          </span>
        </div>
      </div>
    </div>

    <!-- Clients Table -->
    <div class="card p-0">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th class="sortable-th" @click="toggleSort('nom')" title="Cliquer pour trier par Nom">
                <div class="th-content">
                  <span>Client</span>
                  <span class="th-sort-icon">
                    <ArrowUp v-if="currentSort.field === 'nom' && currentSort.direction === 'asc'" :size="13" class="sort-active" />
                    <ArrowDown v-else-if="currentSort.field === 'nom' && currentSort.direction === 'desc'" :size="13" class="sort-active" />
                    <ArrowUpDown v-else :size="12" class="sort-idle" />
                  </span>
                </div>
              </th>
              <th>Numéro Téléphone</th>
              <th class="sortable-th" @click="toggleSort('provenance')" title="Cliquer pour trier par Provenance">
                <div class="th-content">
                  <span>Provenance</span>
                  <span class="th-sort-icon">
                    <ArrowUp v-if="currentSort.field === 'provenance' && currentSort.direction === 'asc'" :size="13" class="sort-active" />
                    <ArrowDown v-else-if="currentSort.field === 'provenance' && currentSort.direction === 'desc'" :size="13" class="sort-active" />
                    <ArrowUpDown v-else :size="12" class="sort-idle" />
                  </span>
                </div>
              </th>
              <th class="sortable-th" @click="toggleSort('ventes')" title="Cliquer pour trier par Ventes Réalisées">
                <div class="th-content">
                  <span>Ventes Réalisées</span>
                  <span class="th-sort-icon">
                    <ArrowUp v-if="currentSort.field === 'ventes' && currentSort.direction === 'asc'" :size="13" class="sort-active" />
                    <ArrowDown v-else-if="currentSort.field === 'ventes' && currentSort.direction === 'desc'" :size="13" class="sort-active" />
                    <ArrowUpDown v-else :size="12" class="sort-idle" />
                  </span>
                </div>
              </th>
              <th class="sortable-th" @click="toggleSort('total')" title="Cliquer pour trier par Total Cumulé">
                <div class="th-content">
                  <span>Total Cumulé</span>
                  <span class="th-sort-icon">
                    <ArrowUp v-if="currentSort.field === 'total' && currentSort.direction === 'asc'" :size="13" class="sort-active" />
                    <ArrowDown v-else-if="currentSort.field === 'total' && currentSort.direction === 'desc'" :size="13" class="sort-active" />
                    <ArrowUpDown v-else :size="12" class="sort-idle" />
                  </span>
                </div>
              </th>
              <th class="sortable-th" @click="toggleSort('created_at')" title="Cliquer pour trier par Date d'Inscription">
                <div class="th-content">
                  <span>Inscrit le</span>
                  <span class="th-sort-icon">
                    <ArrowUp v-if="currentSort.field === 'created_at' && currentSort.direction === 'asc'" :size="13" class="sort-active" />
                    <ArrowDown v-else-if="currentSort.field === 'created_at' && currentSort.direction === 'desc'" :size="13" class="sort-active" />
                    <ArrowUpDown v-else :size="12" class="sort-idle" />
                  </span>
                </div>
              </th>
              <th style="text-align: right;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="client in sortedClients" :key="client.id">
              <td>
                <div class="client-name">{{ client.nom }}</div>
              </td>
              <td>
                <span v-if="client.numero" class="font-mono text-sm">{{ client.numero }}</span>
                <span v-else class="text-muted text-xs">Non renseigné</span>
              </td>
              <td>
                <span
                  class="badge badge-xs prov-badge-table"
                  :style="{
                    backgroundColor: getProvenanceStyle(client.provenance?.label || 'Direct').bg,
                    color: getProvenanceStyle(client.provenance?.label || 'Direct').text,
                    borderColor: getProvenanceStyle(client.provenance?.label || 'Direct').border
                  }"
                >
                  {{ client.provenance?.label || 'Direct' }}
                </span>
              </td>
              <td>
                <span class="font-bold">{{ client.ventes_count || 0 }}</span>
              </td>
              <td>
                <span class="font-bold text-emerald">{{ formatPrice(client.total_achats || 0) }}</span>
              </td>
              <td>
                <span class="text-muted text-xs">{{ formatDate(client.created_at) }}</span>
              </td>
              <td style="text-align: right;">
                <div class="actions-group">
                  <button @click="viewHistory(client)" class="btn btn-secondary btn-xs" title="Historique d'achats">
                    <History :size="14" />
                    <span>Historique</span>
                  </button>
                  <button @click="deleteClient(client)" class="btn-icon btn-danger-icon" title="Supprimer">
                    <Trash2 :size="14" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!sortedClients.length && !loading">
              <td colspan="7" class="text-center py-6 text-muted">
                Aucun client trouvé.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL: Créer un Client -->
    <div v-if="showCreateModal" class="modal-backdrop">
      <div class="modal-card card animate-fade" style="max-width: 480px;">
        <div class="modal-header">
          <h3>Nouveau Client</h3>
          <button @click="showCreateModal = false" class="btn-close"><X :size="20" /></button>
        </div>

        <form @submit.prevent="submitCreateClient" class="modal-body">
          <div class="form-group">
            <label class="form-label">Nom complet / Entreprise *</label>
            <input v-model="form.nom" required type="text" class="form-input" placeholder="Ex: Jean Dupont" />
          </div>

          <div class="form-group">
            <label class="form-label">Numéro de téléphone</label>
            <input v-model="form.numero" type="text" class="form-input" placeholder="Ex: 034 12 345 67" />
          </div>

          <div class="form-group">
            <div class="flex-between">
              <label class="form-label">Provenance (Canal d'acquisition)</label>
              <button
                v-if="!showInlineProv"
                type="button"
                @click="showInlineProv = true"
                class="text-xs text-primary btn-link"
              >
                + Nouveau canal
              </button>
            </div>

            <div v-if="showInlineProv" class="inline-prov-row animate-fade">
              <input
                v-model="newProvInput"
                type="text"
                class="form-input form-input-sm"
                placeholder="Ex: TikTok, Instagram..."
                @keyup.enter.prevent="quickCreateProvenance"
                autofocus
              />
              <button
                type="button"
                @click="quickCreateProvenance"
                class="btn btn-primary btn-xs"
                :disabled="!newProvInput.trim() || creatingProv"
              >
                <span>Ajouter</span>
              </button>
              <button
                type="button"
                @click="showInlineProv = false"
                class="btn btn-secondary btn-xs"
              >
                ✕
              </button>
            </div>

            <SearchableSelect
              v-else
              v-model="form.provenance_id"
              :options="provenances"
              label-key="label"
              value-key="id"
              placeholder="-- Choisir un canal / provenance --"
              search-placeholder="Rechercher un canal..."
              allow-clear
            />
          </div>

          <div class="modal-actions">
            <button @click="showCreateModal = false" type="button" class="btn btn-secondary">Annuler</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              <span v-if="submitting">Création...</span>
              <span v-else>Enregistrer</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL: Historique d'achats du Client -->
    <div v-if="showHistoryModal && selectedClientHistory" class="modal-backdrop">
      <div class="modal-card modal-lg card animate-fade">
        <div class="modal-header">
          <div>
            <h3>Historique de {{ selectedClientHistory.client_nom }}</h3>
            <span class="text-xs text-muted">Détail des transactions passées</span>
          </div>
          <button @click="showHistoryModal = false" class="btn-close"><X :size="20" /></button>
        </div>

        <div class="modal-body">
          <div v-if="selectedClientHistory.historique_achats?.length" class="history-list">
            <div
              v-for="vente in selectedClientHistory.historique_achats"
              :key="vente.id"
              class="history-card"
            >
              <div class="history-card-header">
                <div>
                  <span class="font-bold">Vente #{{ vente.id }}</span>
                  <span class="text-xs text-muted ml-2">{{ formatDate(vente.date) }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="badge badge-primary">{{ vente.methode_paiement }}</span>
                  <span class="font-bold text-emerald">{{ formatPrice(vente.total) }}</span>
                </div>
              </div>

              <!-- Commande items -->
              <div class="order-items-table">
                <div
                  v-for="(cmd, i) in vente.commandes"
                  :key="i"
                  class="order-item-row"
                >
                  <span class="item-name">{{ cmd.quantite }}x {{ cmd.produit_nom }}</span>
                  <span class="item-price">{{ formatPrice(cmd.sous_total) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-muted text-center py-6">
            Ce client n'a pas encore passé de commande.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Search,
  Plus,
  History,
  Trash2,
  X,
  Share2,
  Globe,
  SlidersHorizontal,
  RotateCcw,
  Check,
  ArrowUpDown,
  ArrowUp,
  ArrowDown
} from '@lucide/vue'
import apiClient from '../api/client'
import MultiSelectDropdown from '../components/MultiSelectDropdown.vue'
import SearchableSelect from '../components/SearchableSelect.vue'
import { getProvenanceStyle } from '../utils/provenanceHelper'

const clients = ref([])
const provenances = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedProvenances = ref([])

// Système de tri multicritère
const currentSort = ref({
  field: 'nom',
  direction: 'asc'
})
const sortSelectValue = ref('nom-asc')

let searchTimeout = null

const showCreateModal = ref(false)
const showHistoryModal = ref(false)
const selectedClientHistory = ref(null)
const submitting = ref(false)

const showInlineProv = ref(false)
const newProvInput = ref('')
const creatingProv = ref(false)

const form = ref({
  nom: '',
  numero: '',
  provenance_id: null,
})

const hasActiveFilters = computed(() => {
  return !!(selectedProvenances.value.length > 0 || searchQuery.value.trim())
})

const provenanceOptions = computed(() => {
  return provenances.value.map(p => {
    const st = getProvenanceStyle(p.label)
    return {
      id: p.id,
      label: p.label,
      count: p.annotated_clients_count ?? p.clients_count,
      color: {
        dot: st.dot,
        text: st.text,
        bg: st.bg
      }
    }
  })
})

function onSearchInput() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchClients()
  }, 350)
}

function toggleSort(field) {
  if (currentSort.value.field === field) {
    currentSort.value.direction = currentSort.value.direction === 'asc' ? 'desc' : 'asc'
  } else {
    currentSort.value.field = field
    currentSort.value.direction = (field === 'total' || field === 'ventes' || field === 'created_at') ? 'desc' : 'asc'
  }
  sortSelectValue.value = `${currentSort.value.field}-${currentSort.value.direction}`
  fetchClients()
}

function onSortSelectChange() {
  const [field, direction] = sortSelectValue.value.split('-')
  currentSort.value = { field, direction }
  fetchClients()
}

// Tri dynamique côté client
const sortedClients = computed(() => {
  if (!Array.isArray(clients.value)) return []
  const list = [...clients.value]
  const { field, direction } = currentSort.value
  const factor = direction === 'asc' ? 1 : -1

  return list.sort((a, b) => {
    switch (field) {
      case 'nom':
        return (a.nom || '').localeCompare(b.nom || '') * factor

      case 'provenance': {
        const provA = a.provenance?.label || 'Direct'
        const provB = b.provenance?.label || 'Direct'
        return provA.localeCompare(provB) * factor
      }

      case 'ventes':
        return ((Number(a.ventes_count) || 0) - (Number(b.ventes_count) || 0)) * factor

      case 'total':
        return ((Number(a.total_achats) || 0) - (Number(b.total_achats) || 0)) * factor

      case 'created_at':
        return ((new Date(a.created_at).getTime() || 0) - (new Date(b.created_at).getTime() || 0)) * factor

      default:
        return 0
    }
  })
})

// Fonctions rapides de gestion des provenances
function toggleProvenanceFilter(id) {
  const idx = selectedProvenances.value.indexOf(id)
  if (idx >= 0) {
    selectedProvenances.value.splice(idx, 1)
  } else {
    selectedProvenances.value.push(id)
  }
  fetchClients()
}

function clearProvenancesFilter() {
  selectedProvenances.value = []
  fetchClients()
}

function removeProvenanceFilter(id) {
  const idx = selectedProvenances.value.indexOf(id)
  if (idx >= 0) {
    selectedProvenances.value.splice(idx, 1)
    fetchClients()
  }
}

function getProvenanceLabel(id) {
  const p = provenances.value.find(item => String(item.id) === String(id))
  return p ? p.label : ''
}

function getClientsCountForProv(id) {
  if (!clients.value) return 0
  return clients.value.filter(c => String(c.provenance?.id) === String(id)).length
}

function getProvenanceChipStyle(prov) {
  const isSelected = selectedProvenances.value.includes(prov.id)
  const st = getProvenanceStyle(prov.label)
  if (isSelected) {
    return {
      backgroundColor: st.bg,
      borderColor: st.border,
      color: st.text,
      boxShadow: `0 0 10px ${st.border}`
    }
  }
  return {}
}

function resetFilters() {
  selectedProvenances.value = []
  searchQuery.value = ''
  currentSort.value = { field: 'nom', direction: 'asc' }
  sortSelectValue.value = 'nom-asc'
  fetchClients()
}

async function quickCreateProvenance() {
  const label = newProvInput.value.trim()
  if (!label) return
  creatingProv.value = true
  try {
    const res = await apiClient.post('/clients/provenances/', { label })
    await fetchProvenances()
    form.value.provenance_id = res.data.id
    newProvInput.value = ''
    showInlineProv.value = false
  } catch (err) {
    alert(err.response?.data?.label?.[0] || err.response?.data?.error || "Erreur lors de la création de la provenance")
  } finally {
    creatingProv.value = false
  }
}

async function fetchClients() {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (selectedProvenances.value.length) {
      params.provenances = selectedProvenances.value.join(',')
    }

    if (currentSort.value.field) {
      const backendMap = {
        nom: 'nom',
        created_at: 'created_at',
        provenance: 'provenance__label'
      }
      const fieldName = backendMap[currentSort.value.field]
      if (fieldName) {
        params.ordering = currentSort.value.direction === 'desc' ? `-${fieldName}` : fieldName
      }
    }

    const res = await apiClient.get('/clients/', { params })
    clients.value = res.data.results || res.data || []
  } catch (err) {
    console.error('Erreur chargement clients:', err)
  } finally {
    loading.value = false
  }
}

async function fetchProvenances() {
  try {
    const res = await apiClient.get('/clients/provenances/')
    provenances.value = res.data.results || res.data || []
  } catch (err) {
    console.error('Erreur provenances:', err)
  }
}

function openCreateModal() {
  form.value = { nom: '', numero: '', provenance_id: null }
  showCreateModal.value = true
}

async function submitCreateClient() {
  submitting.value = true
  try {
    await apiClient.post('/clients/', form.value)
    showCreateModal.value = false
    await fetchClients()
  } catch (err) {
    alert(err.response?.data?.detail || "Erreur lors de la création du client")
  } finally {
    submitting.value = false
  }
}

async function viewHistory(client) {
  try {
    const res = await apiClient.get(`/clients/${client.id}/historique/`)
    selectedClientHistory.value = res.data
    showHistoryModal.value = true
  } catch (err) {
    alert("Impossible de charger l'historique du client.")
  }
}

async function deleteClient(client) {
  if (!confirm(`Supprimer le client "${client.nom}" ?`)) return
  try {
    await apiClient.delete(`/clients/${client.id}/`)
    await fetchClients()
  } catch (err) {
    alert("Impossible de supprimer ce client car il est rattaché à des ventes existantes.")
  }
}

function formatPrice(val) {
  return new Intl.NumberFormat('fr-MG').format(val || 0) + ' Ar'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}

onMounted(() => {
  fetchClients()
  fetchProvenances()
})
</script>

<style scoped>
.clients-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.view-header-card {
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: var(--gradient-card);
  border: 1px solid var(--border-card);
}

.filters-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  min-width: 240px;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 0.85rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.search-input {
  width: 100%;
  padding-left: 2.4rem;
  padding-right: 2rem;
}

.btn-clear-search {
  position: absolute;
  right: 0.65rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
}

.header-actions-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: auto;
}

/* Sort Selector */
.sort-selector-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(255, 255, 255, 0.04);
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

.sort-select-compact {
  padding: 0.25rem 0.5rem;
  font-size: 0.76rem;
  background: transparent;
  border: none;
  color: var(--text-main);
  font-weight: 600;
  cursor: pointer;
}

.sort-select-compact option {
  background: #091322;
  color: #fff;
}

/* Provenances Quick Bar */
.provenance-quick-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.55rem 0.75rem;
  background: rgba(0, 0, 0, 0.25);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow-x: auto;
}

.quick-bar-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-secondary);
  white-space: nowrap;
}

.quick-chips-scroll {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  overflow-x: auto;
  padding-bottom: 2px;
}

.prov-chip-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.65rem;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.prov-chip-btn:hover {
  background: rgba(255, 255, 255, 0.09);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.2);
}

.prov-chip-btn.active-all {
  background: var(--primary-light, rgba(0, 210, 255, 0.15));
  border-color: var(--primary, #00d2ff);
  color: var(--primary, #00d2ff);
}

.prov-chip-btn.active {
  font-weight: 700;
}

.chip-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.chip-count {
  font-size: 0.65rem;
  background: rgba(0, 0, 0, 0.3);
  padding: 0.1rem 0.35rem;
  border-radius: 9999px;
  line-height: 1;
}

.chip-check {
  margin-left: -0.1rem;
}

/* Active Filters Banner */
.active-filters-banner {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-subtle);
  flex-wrap: wrap;
}

.active-pills-wrap {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.active-filter-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.active-filter-pill strong {
  color: var(--text-main);
}

.pill-provenance {
  background: rgba(0, 0, 0, 0.3);
}

.pill-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.pill-remove-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 1px;
  border-radius: 50%;
  transition: all 0.15s;
}

.pill-remove-btn:hover {
  color: #f43f5e;
  background: rgba(244, 63, 94, 0.2);
}

/* Sortable Table Headers */
.sortable-th {
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;
}

.sortable-th:hover {
  background: rgba(0, 210, 255, 0.08) !important;
  color: #fff !important;
}

.th-content {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.th-sort-icon {
  display: inline-flex;
  align-items: center;
}

.sort-active {
  color: var(--primary);
}

.sort-idle {
  color: rgba(255, 255, 255, 0.2);
}

.sortable-th:hover .sort-idle {
  color: rgba(255, 255, 255, 0.6);
}

.prov-badge-table {
  border-width: 1px;
  border-style: solid;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.client-name {
  font-weight: 600;
  font-size: 0.9rem;
}

.actions-group {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 400px;
  overflow-y: auto;
}

.history-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.history-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 0.5rem;
}

.order-items-table {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.order-item-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
}

.item-name {
  color: var(--text-secondary);
}

.item-price {
  font-weight: 600;
  color: #34d399;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(6px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.modal-card {
  width: 100%;
  border-radius: var(--radius-xl);
  padding: 1.75rem;
}

.modal-lg {
  max-width: 650px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-xs {
  padding: 0.35rem 0.65rem;
  font-size: 0.75rem;
}

.btn-danger-icon {
  background: rgba(244, 63, 94, 0.1);
  border: 1px solid rgba(244, 63, 94, 0.2);
  color: var(--rose);
  padding: 0.4rem;
}

.btn-danger-icon:hover {
  background: var(--rose);
  color: white;
}

.btn-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
}

.flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.btn-link {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
}

.inline-prov-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.form-input-sm {
  padding: 0.4rem 0.65rem;
  font-size: 0.85rem;
}
</style>
