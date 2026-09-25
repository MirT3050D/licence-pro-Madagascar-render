<template>
  <div class="clients-view">
    <!-- Filters & Actions Header -->
    <div class="view-header">
      <div class="filters-row">
        <div class="search-box">
          <Search :size="18" class="search-icon" />
          <input
            v-model="searchQuery"
            @input="fetchClients"
            type="text"
            class="form-input search-input"
            placeholder="Rechercher par nom ou numéro..."
          />
        </div>

        <select v-model="selectedProvenance" @change="fetchClients" class="form-select prov-select">
          <option value="">Toutes les provenances</option>
          <option v-for="prov in provenances" :key="prov.id" :value="prov.id">
            {{ prov.label }}
          </option>
        </select>
      </div>

      <button @click="openCreateModal" class="btn btn-primary">
        <Plus :size="18" />
        <span>Nouveau Client</span>
      </button>
    </div>

    <!-- Clients Table -->
    <div class="card p-0">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Client</th>
              <th>Numéro Téléphone</th>
              <th>Provenance</th>
              <th>Ventes Réalisées</th>
              <th>Total Cumulé</th>
              <th>Inscrit le</th>
              <th style="text-align: right;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="client in clients" :key="client.id">
              <td>
                <div class="client-name">{{ client.nom }}</div>
              </td>
              <td>
                <span v-if="client.numero" class="font-mono text-sm">{{ client.numero }}</span>
                <span v-else class="text-muted text-xs">Non renseigné</span>
              </td>
              <td>
                <span class="badge badge-primary">
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
            <tr v-if="!clients.length && !loading">
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
            <label class="form-label">Provenance (Canal d'acquisition)</label>
            <select v-model="form.provenance_id" class="form-select">
              <option :value="null">-- Choisir un canal --</option>
              <option v-for="prov in provenances" :key="prov.id" :value="prov.id">
                {{ prov.label }}
              </option>
            </select>
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
import { ref, onMounted } from 'vue'
import { Search, Plus, History, Trash2, X } from '@lucide/vue'
import apiClient from '../api/client'

const clients = ref([])
const provenances = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedProvenance = ref('')

const showCreateModal = ref(false)
const showHistoryModal = ref(false)
const selectedClientHistory = ref(null)
const submitting = ref(false)

const form = ref({
  nom: '',
  numero: '',
  provenance_id: null,
})

async function fetchClients() {
  loading.value = true
  try {
    const res = await apiClient.get('/clients/', {
      params: {
        search: searchQuery.value,
        provenance: selectedProvenance.value,
      }
    })
    clients.value = res.data
  } catch (err) {
    console.error('Erreur chargement clients:', err)
  } finally {
    loading.value = false
  }
}

async function fetchProvenances() {
  try {
    const res = await apiClient.get('/clients/provenances/')
    provenances.value = res.data
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

.view-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.filters-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.search-box {
  position: relative;
  max-width: 350px;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.search-input {
  width: 100%;
  padding-left: 2.75rem;
}

.prov-select {
  width: 200px;
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
</style>
