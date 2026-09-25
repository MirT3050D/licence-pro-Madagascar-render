<template>
  <div class="sales-view">
    <!-- Filters & Action Header -->
    <div class="view-header">
      <div class="filters-row">
        <!-- Date filters -->
        <input v-model="filters.date_debut" @change="fetchSales" type="date" class="form-input filter-input" title="Date de début" />
        <input v-model="filters.date_fin" @change="fetchSales" type="date" class="form-input filter-input" title="Date de fin" />

        <!-- Payment method filter -->
        <select v-model="filters.methode_paiement" @change="fetchSales" class="form-select filter-select">
          <option value="">Tous les règlements</option>
          <option v-for="m in paymentMethods" :key="m.id" :value="m.id">{{ m.label }}</option>
        </select>
      </div>

      <button @click="openCreateSaleModal" class="btn btn-primary">
        <Plus :size="18" />
        <span>Nouvelle Vente</span>
      </button>
    </div>

    <!-- Sales Table -->
    <div class="card p-0">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th># Réf</th>
              <th>Date & Heure</th>
              <th>Client</th>
              <th>Vendeur</th>
              <th>Règlement</th>
              <th>Articles</th>
              <th>Total</th>
              <th style="text-align: right;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="vente in sales" :key="vente.id">
              <td>
                <span class="font-mono font-bold text-primary">#{{ vente.id }}</span>
              </td>
              <td>
                <span class="text-sm">{{ formatDateTime(vente.date) }}</span>
              </td>
              <td>
                <div class="font-bold">{{ vente.client?.nom }}</div>
                <div class="text-xs text-muted">{{ vente.client?.numero || 'Sans numéro' }}</div>
              </td>
              <td>
                <span class="text-sm">{{ vente.user_affilie?.prenom }} {{ vente.user_affilie?.nom }}</span>
              </td>
              <td>
                <span class="badge badge-primary">{{ vente.methode_paiement?.label }}</span>
              </td>
              <td>
                <span class="badge badge-secondary">{{ vente.commandes?.length || 0 }} article(s)</span>
              </td>
              <td>
                <span class="font-bold text-emerald">{{ formatPrice(vente.total) }}</span>
              </td>
              <td style="text-align: right;">
                <div class="actions-group">
                  <button @click="openDetailModal(vente)" class="btn btn-secondary btn-xs" title="Voir les détails et copier les guides">
                    <FileText :size="14" />
                    <span>Détails & Guides</span>
                  </button>
                  <button @click="deleteSale(vente)" class="btn-icon btn-danger-icon" title="Supprimer la vente">
                    <Trash2 :size="14" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!sales.length && !loading">
              <td colspan="8" class="text-center py-6 text-muted">
                Aucune vente trouvée avec ces critères.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL: Créer une Vente Multi-Produits -->
    <div v-if="showCreateModal" class="modal-backdrop">
      <div class="modal-card modal-xl card animate-fade">
        <div class="modal-header">
          <div>
            <h3>Nouvelle Transaction</h3>
            <span class="text-xs text-muted">Sélectionnez le client, ajoutez les licences et validez</span>
          </div>
          <button @click="showCreateModal = false" class="btn-close"><X :size="20" /></button>
        </div>

        <form @submit.prevent="submitCreateSale" class="modal-body">
          <div class="sale-top-fields">
            <!-- Client selection -->
            <div class="form-group flex-1">
              <label class="form-label">Client *</label>
              <select v-model="form.client_id" required class="form-select">
                <option value="" disabled>-- Choisir le client --</option>
                <option v-for="c in clientsList" :key="c.id" :value="c.id">
                  {{ c.nom }} ({{ c.numero || 'Pas de numéro' }})
                </option>
              </select>
            </div>

            <!-- Payment method -->
            <div class="form-group flex-1">
              <label class="form-label">Mode de règlement *</label>
              <select v-model="form.methode_paiement_id" required class="form-select">
                <option value="" disabled>-- Méthode de paiement --</option>
                <option v-for="m in paymentMethods" :key="m.id" :value="m.id">
                  {{ m.label }} {{ m.details ? `(${m.details})` : '' }}
                </option>
              </select>
            </div>
          </div>

          <!-- Product lines section -->
          <div class="articles-section">
            <div class="articles-header">
              <h4>Articles commandés</h4>
              <button @click="addArticleLine" type="button" class="btn btn-secondary btn-xs">
                <Plus :size="14" />
                <span>Ajouter une ligne</span>
              </button>
            </div>

            <div class="articles-table">
              <div v-for="(line, idx) in form.articles" :key="idx" class="article-line">
                <!-- Product selector -->
                <div class="flex-2">
                  <label class="form-label text-xs">Produit *</label>
                  <select
                    v-model="line.produit_id"
                    @change="onProductSelect(line)"
                    required
                    class="form-select"
                  >
                    <option value="" disabled>Choisir un produit...</option>
                    <option v-for="p in productsList" :key="p.id" :value="p.id">
                      {{ p.nom }} (Actuel: {{ formatPrice(p.prix_actif) }})
                    </option>
                  </select>
                </div>

                <!-- Quantity -->
                <div class="flex-1">
                  <label class="form-label text-xs">Quantité</label>
                  <input
                    v-model.number="line.quantite"
                    type="number"
                    min="1"
                    required
                    class="form-input"
                  />
                </div>

                <!-- Unit price -->
                <div class="flex-1">
                  <label class="form-label text-xs">Prix Unitaire (Ar)</label>
                  <input
                    v-model.number="line.prix_unitaire"
                    type="number"
                    step="100"
                    required
                    class="form-input"
                  />
                </div>

                <!-- Line Subtotal -->
                <div class="line-subtotal">
                  <span class="text-xs text-muted">Sous-total</span>
                  <span class="font-bold text-emerald">
                    {{ formatPrice((line.quantite || 0) * (line.prix_unitaire || 0)) }}
                  </span>
                </div>

                <!-- Remove Line -->
                <button
                  v-if="form.articles.length > 1"
                  @click="removeArticleLine(idx)"
                  type="button"
                  class="btn-icon btn-danger-icon"
                  title="Supprimer la ligne"
                >
                  <Trash2 :size="14" />
                </button>
              </div>
            </div>
          </div>

          <!-- Total Summary & Submit -->
          <div class="sale-summary-bar">
            <div class="total-box">
              <span class="total-label">Montant Total à Payer :</span>
              <span class="total-amount">{{ formatPrice(computedTotal) }}</span>
            </div>

            <div class="modal-actions">
              <button @click="showCreateModal = false" type="button" class="btn btn-secondary">Annuler</button>
              <button type="submit" class="btn btn-success" :disabled="submitting || computedTotal <= 0">
                <Check :size="18" />
                <span v-if="submitting">Validation en cours...</span>
                <span v-else>Valider la vente</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL: Fiche Détail d'une Vente & Guides d'activation -->
    <div v-if="showDetailModal && selectedSale" class="modal-backdrop">
      <div class="modal-card modal-lg card animate-fade">
        <div class="modal-header">
          <div>
            <h3>Vente #{{ selectedSale.id }}</h3>
            <span class="text-xs text-muted">{{ formatDateTime(selectedSale.date) }}</span>
          </div>
          <button @click="showDetailModal = false" class="btn-close"><X :size="20" /></button>
        </div>

        <div class="modal-body detail-body">
          <!-- Client & Payment info banner -->
          <div class="sale-meta-card">
            <div>
              <span class="text-xs text-muted">CLIENT</span>
              <div class="font-bold">{{ selectedSale.client?.nom }}</div>
              <div class="text-xs text-secondary">{{ selectedSale.client?.numero || 'Pas de numéro' }}</div>
            </div>
            <div>
              <span class="text-xs text-muted">VENDEUR</span>
              <div class="font-bold">{{ selectedSale.user_affilie?.prenom }} {{ selectedSale.user_affilie?.nom }}</div>
              <div class="text-xs text-secondary">{{ selectedSale.user_affilie?.email }}</div>
            </div>
            <div>
              <span class="text-xs text-muted">RÈGLEMENT</span>
              <div><span class="badge badge-primary">{{ selectedSale.methode_paiement?.label }}</span></div>
            </div>
            <div>
              <span class="text-xs text-muted">TOTAL RÉGLÉ</span>
              <div class="font-extrabold text-lg text-emerald">{{ formatPrice(selectedSale.total) }}</div>
            </div>
          </div>

          <!-- Items Ordered Table -->
          <div class="section-title">Articles de la commande</div>
          <div class="table-container mb-4">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Produit</th>
                  <th>Qté</th>
                  <th>Prix Unitaire</th>
                  <th style="text-align: right;">Sous-total</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="cmd in selectedSale.commandes" :key="cmd.id">
                  <td class="font-bold">{{ cmd.produit_nom }}</td>
                  <td>{{ cmd.quantite }}</td>
                  <td>{{ formatPrice(cmd.prix_unitaire) }}</td>
                  <td style="text-align: right;" class="font-bold text-emerald">{{ formatPrice(cmd.sous_total) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Activation Guides to copy -->
          <div class="section-title">Guides d'activation pour le client</div>
          <div v-if="selectedSale.guides_activation?.length" class="guides-list">
            <div v-for="(g, i) in selectedSale.guides_activation" :key="i" class="guide-box">
              <div class="guide-header">
                <strong>{{ g.produit_nom }}</strong>
                <button @click="copyText(g.guide)" class="btn btn-secondary btn-xs">
                  <Copy :size="14" />
                  <span>Copier le texte</span>
                </button>
              </div>
              <pre class="guide-content">{{ g.guide }}</pre>
            </div>
          </div>
          <div v-else class="text-muted text-sm italic py-2">
            Aucun guide d'activation configuré pour ces licences.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  Plus,
  Search,
  FileText,
  Trash2,
  X,
  Check,
  Copy
} from '@lucide/vue'
import confetti from 'canvas-confetti'
import apiClient from '../api/client'

const route = useRoute()

const sales = ref([])
const clientsList = ref([])
const productsList = ref([])
const paymentMethods = ref([])
const loading = ref(false)
const submitting = ref(false)

const filters = ref({
  date_debut: '',
  date_fin: '',
  methode_paiement: '',
})

// Modals
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const selectedSale = ref(null)

const form = ref({
  client_id: '',
  methode_paiement_id: '',
  articles: [
    { produit_id: '', quantite: 1, prix_unitaire: 0 }
  ]
})

const computedTotal = computed(() => {
  return form.value.articles.reduce((acc, line) => {
    return acc + ((line.quantite || 0) * (line.prix_unitaire || 0))
  }, 0)
})

async function fetchSales() {
  loading.value = true
  try {
    const res = await apiClient.get('/ventes/', { params: filters.value })
    sales.value = res.data
  } catch (err) {
    console.error('Erreur chargement ventes:', err)
  } finally {
    loading.value = false
  }
}

async function fetchFormDependencies() {
  try {
    const [cRes, pRes, mRes] = await Promise.all([
      apiClient.get('/clients/'),
      apiClient.get('/produits/'),
      apiClient.get('/ventes/methodes-paiement/'),
    ])
    clientsList.value = cRes.data
    productsList.value = pRes.data
    paymentMethods.value = mRes.data
  } catch (err) {
    console.error('Erreur dépendances vente:', err)
  }
}

function openCreateSaleModal() {
  // Vérifier si des données de pré-remplissage IA sont présentes dans sessionStorage
  const prefill = sessionStorage.getItem('prefill_sale')
  if (prefill) {
    try {
      const data = JSON.parse(prefill)
      sessionStorage.removeItem('prefill_sale')
      form.value.client_id = data.client_id || ''
      form.value.methode_paiement_id = data.methode_paiement_id || (paymentMethods.value[0]?.id || '')

      if (data.articles?.length) {
        form.value.articles = data.articles.map(a => ({
          produit_id: a.produit_id,
          quantite: a.quantite || 1,
          prix_unitaire: a.prix_unitaire || 0
        }))
      } else {
        form.value.articles = [{ produit_id: '', quantite: 1, prix_unitaire: 0 }]
      }
    } catch (e) {
      resetForm()
    }
  } else {
    resetForm()
  }
  showCreateModal.value = true
}

function resetForm() {
  form.value = {
    client_id: clientsList.value[0]?.id || '',
    methode_paiement_id: paymentMethods.value[0]?.id || '',
    articles: [{ produit_id: '', quantite: 1, prix_unitaire: 0 }]
  }
}

function addArticleLine() {
  form.value.articles.push({ produit_id: '', quantite: 1, prix_unitaire: 0 })
}

function removeArticleLine(idx) {
  form.value.articles.splice(idx, 1)
}

function onProductSelect(line) {
  const prod = productsList.value.find(p => p.id === line.produit_id)
  if (prod && prod.prix_actif) {
    line.prix_unitaire = Number(prod.prix_actif)
  }
}

async function submitCreateSale() {
  submitting.value = true
  try {
    await apiClient.post('/ventes/', form.value)
    showCreateModal.value = false
    await fetchSales()

    // Confetti effect on sale validation!
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 }
    })
  } catch (err) {
    alert(err.response?.data?.detail || err.response?.data?.non_field_errors?.[0] || "Erreur lors de la validation de la vente")
  } finally {
    submitting.value = false
  }
}

function openDetailModal(vente) {
  selectedSale.value = vente
  showDetailModal.value = true
}

async function deleteSale(vente) {
  if (!confirm(`Supprimer la vente #${vente.id} ?`)) return
  try {
    await apiClient.delete(`/ventes/${vente.id}/`)
    await fetchSales()
  } catch (err) {
    alert("Impossible de supprimer la vente.")
  }
}

function copyText(txt) {
  navigator.clipboard.writeText(txt)
  alert("Guide d'activation copié dans le presse-papier !")
}

function formatPrice(val) {
  return new Intl.NumberFormat('fr-MG').format(val || 0) + ' Ar'
}

function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('fr-FR', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Watch route for action=nouvelle parameter
watch(() => route.query.action, (act) => {
  if (act === 'nouvelle') {
    openCreateSaleModal()
  }
})

onMounted(async () => {
  await fetchFormDependencies()
  await fetchSales()
  if (route.query.action === 'nouvelle') {
    openCreateSaleModal()
  }
})
</script>

<style scoped>
.sales-view {
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
}

.filter-input {
  width: 160px;
}

.filter-select {
  width: 200px;
}

.actions-group {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
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
  max-height: 90vh;
  overflow-y: auto;
}

.modal-xl {
  max-width: 850px;
}

.modal-lg {
  max-width: 700px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.sale-top-fields {
  display: flex;
  gap: 1.25rem;
}

.flex-1 { flex: 1; }
.flex-2 { flex: 2; }

.articles-section {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  margin: 1.25rem 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.articles-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.articles-table {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.article-line {
  display: flex;
  align-items: flex-end;
  gap: 0.85rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border-subtle);
}

.line-subtotal {
  display: flex;
  flex-direction: column;
  min-width: 120px;
  text-align: right;
  padding-bottom: 0.4rem;
}

.sale-summary-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-subtle);
}

.total-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.total-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.total-amount {
  font-size: 1.6rem;
  font-weight: 800;
  color: #34d399;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
}

.sale-meta-card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: 0.65rem;
}

.guides-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.guide-box {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 1rem;
}

.guide-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.65rem;
}

.guide-content {
  background: rgba(0, 0, 0, 0.35);
  padding: 0.85rem;
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: 0.8rem;
  white-space: pre-wrap;
  color: #cbd5e1;
  max-height: 180px;
  overflow-y: auto;
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
