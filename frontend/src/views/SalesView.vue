<template>
  <div class="sales-view">
    <!-- FILTRES AVANCÉS & ACTION NOUVELLE VENTE -->
    <div class="sales-filter-card card">
      <!-- 1. FILTRE PRIMORDIAL : VENDEUR / USER-AFFILIÉ -->
      <div class="primary-vendor-filter">
        <div class="filter-header-label">
          <div class="label-with-icon">
            <Users :size="16" class="text-primary" />
            <span class="label-title">FILTRER PAR VENDEUR / AFFILIÉ</span>
          </div>
          <span class="badge badge-primary">Filtre Prioritaire</span>
        </div>

        <div class="vendor-controls">
          <div class="vendor-select-wrapper">
            <select v-model="filters.vendeur" @change="fetchSales" class="form-select vendor-select">
              <option value="">👥 Tous les vendeurs / affiliés</option>
              <option v-for="u in vendorsList" :key="u.id" :value="u.id">
                👤 {{ u.prenom }} {{ u.nom }} ({{ u.role?.label || 'Vendeur' }})
              </option>
            </select>
          </div>

          <button
            v-if="user?.id"
            type="button"
            @click="toggleMySales"
            class="btn btn-sm"
            :class="filters.vendeur === user.id ? 'btn-primary' : 'btn-secondary'"
            title="Afficher uniquement les ventes que j'ai enregistrées"
          >
            <Zap :size="14" />
            <span>Mes Ventes</span>
          </button>
        </div>
      </div>

      <!-- 2. FILTRES COMPLÉMENTAIRES : RECHERCHE, PÉRIODE, MODE DE PAIEMENT, NOUVELLE VENTE -->
      <div class="secondary-filters-row">
        <!-- Recherche textuelle -->
        <div class="search-box">
          <Search :size="16" class="search-icon" />
          <input
            v-model="filters.search"
            @input="onSearchInput"
            type="text"
            class="form-input search-input"
            placeholder="Rechercher client, réf #, téléphone..."
          />
          <button v-if="filters.search" @click="clearSearch" class="btn-clear-search">
            <X :size="14" />
          </button>
        </div>

        <!-- Périodes rapides -->
        <div class="period-presets">
          <button
            type="button"
            class="preset-btn"
            :class="{ active: activePeriodPreset === 'all' }"
            @click="setPeriodPreset('all')"
          >
            Tout
          </button>
          <button
            type="button"
            class="preset-btn"
            :class="{ active: activePeriodPreset === 'today' }"
            @click="setPeriodPreset('today')"
          >
            Aujourd'hui
          </button>
          <button
            type="button"
            class="preset-btn"
            :class="{ active: activePeriodPreset === '7d' }"
            @click="setPeriodPreset('7d')"
          >
            7 jours
          </button>
          <button
            type="button"
            class="preset-btn"
            :class="{ active: activePeriodPreset === 'month' }"
            @click="setPeriodPreset('month')"
          >
            Ce mois
          </button>
        </div>

        <!-- Dates personnalisées -->
        <div class="date-range-inputs">
          <input
            v-model="filters.date_debut"
            @change="onCustomDateChange"
            type="date"
            class="form-input date-input"
            title="Date de début"
          />
          <span class="date-sep">à</span>
          <input
            v-model="filters.date_fin"
            @change="onCustomDateChange"
            type="date"
            class="form-input date-input"
            title="Date de fin"
          />
        </div>

        <!-- Mode de paiement -->
        <select v-model="filters.methode_paiement" @change="fetchSales" class="form-select filter-select">
          <option value="">Tous les règlements</option>
          <option v-for="m in paymentMethods" :key="m.id" :value="m.id">{{ m.label }}</option>
        </select>

        <!-- Filtre Client -->
        <select v-model="filters.client" @change="fetchSales" class="form-select filter-select">
          <option value="">👤 Tous les clients</option>
          <option v-for="c in clientsList" :key="c.id" :value="c.id">{{ c.nom }}</option>
        </select>

        <!-- Filtre Provenance -->
        <select v-model="filters.provenance" @change="fetchSales" class="form-select filter-select">
          <option value="">🌐 Toutes provenances</option>
          <option v-for="prov in provenancesList" :key="prov.id" :value="prov.id">{{ prov.label }}</option>
        </select>

        <!-- Bouton Réinitialiser -->
        <button
          v-if="hasActiveFilters"
          type="button"
          @click="resetFilters"
          class="btn btn-secondary btn-sm"
          title="Réinitialiser tous les filtres"
        >
          <RotateCcw :size="14" />
          <span>Réinitialiser</span>
        </button>

        <!-- Nouvelle Vente (Réservé Administrateur) -->
        <button v-if="isSuperAdmin" @click="openCreateSaleModal" class="btn btn-primary btn-new-sale">
          <Plus :size="18" />
          <span>Nouvelle Vente</span>
        </button>
        <div v-else class="admin-only-badge">
          <Lock :size="13" class="text-primary" />
          <span>Saisie réservée à l'Admin</span>
        </div>
      </div>

      <!-- 3. BANDEAU RÉSUMÉ DES RÉSULTATS FILTRÉS -->
      <div class="filter-results-summary">
        <div class="summary-left">
          <span class="results-count">
            <strong>{{ sales.length }}</strong> vente(s) affichée(s)
          </span>
          <span v-if="activeFilterVendorName" class="active-filter-pill">
            Vendeur : <strong>{{ activeFilterVendorName }}</strong>
          </span>
          <span v-if="activeClientName" class="active-filter-pill">
            Client : <strong>{{ activeClientName }}</strong>
          </span>
          <span v-if="activeProvenanceName" class="active-filter-pill">
            Provenance : <strong>{{ activeProvenanceName }}</strong>
          </span>
          <span v-if="filters.search" class="active-filter-pill">
            Recherche : <strong>"{{ filters.search }}"</strong>
          </span>
          <span v-if="activePeriodPreset !== 'all'" class="active-filter-pill">
            Période : <strong>{{ activePeriodLabel }}</strong>
          </span>
        </div>
        <div class="summary-right">
          <span class="total-label">Total encaissé :</span>
          <span class="total-val text-emerald">{{ formatPrice(filteredSalesTotal) }}</span>
        </div>
      </div>
    </div>

    <!-- Tableau des Ventes -->
    <div class="card p-0">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th># Réf</th>
              <th>Date & Heure</th>
              <th>Client</th>
              <th>Vendeur / Affilié</th>
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
                <div class="text-xs text-muted flex items-center gap-1.5 mt-0.5">
                  <span>{{ vente.client?.numero || 'Sans numéro' }}</span>
                  <span v-if="vente.client?.provenance?.label" class="badge badge-secondary badge-xs">
                    {{ vente.client.provenance.label }}
                  </span>
                </div>
              </td>
              <td>
                <div class="vendor-cell">
                  <span class="vendor-name">{{ vente.user_affilie?.prenom }} {{ vente.user_affilie?.nom }}</span>
                  <span class="vendor-role-tag">{{ vente.user_affilie?.role?.label || 'Vendeur' }}</span>
                </div>
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
                  <button v-if="isSuperAdmin" @click="openEditSaleModal(vente)" class="btn-icon btn-secondary-icon" title="Modifier cette vente">
                    <Pencil :size="14" />
                  </button>
                  <button v-if="isSuperAdmin" @click="deleteSale(vente)" class="btn-icon btn-danger-icon" title="Supprimer la vente">
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
    <Teleport to="body">
      <div v-if="showCreateModal" class="modal-backdrop" @click.self="showCreateModal = false">
        <div class="sale-modal-card card animate-fade">
          <!-- Header -->
          <div class="modal-header-custom">
            <div class="modal-header-info">
              <div class="modal-header-icon">
                <Pencil v-if="isEditing" :size="22" />
                <ShoppingCart v-else :size="22" />
              </div>
              <div>
                <h3 class="modal-title">{{ isEditing ? `Modifier la Transaction #${editingSaleId}` : 'Nouvelle Transaction' }}</h3>
                <p class="modal-subtitle">{{ isEditing ? 'Modifiez le client, la date, le mode de règlement ou les articles de cette vente' : 'Sélectionnez le client, ajustez les produits et validez la vente' }}</p>
              </div>
            </div>
            <button @click="showCreateModal = false" class="btn-close" title="Fermer"><X :size="20" /></button>
          </div>

          <form @submit.prevent="submitCreateSale" class="sale-modal-body">
            <!-- 1. Champs Principaux : Grille 2x2 propre, 50/50 stricte -->
            <div class="sale-fields-grid">
              <!-- Client selection (Haut Gauche) -->
              <div class="form-group">
                <label class="form-label">Client *</label>
                <select v-model="form.client_id" required class="form-select">
                  <option value="" disabled>-- Choisir le client --</option>
                  <option v-for="c in clientsList" :key="c.id" :value="c.id">
                    {{ c.nom }} ({{ c.numero || 'Pas de numéro' }})
                  </option>
                </select>
              </div>

              <!-- Date de la vente (Haut Droite) -->
              <div class="form-group">
                <div class="field-label-row">
                  <label class="form-label">Date de la vente *</label>
                  <button
                    type="button"
                    @click="form.date = getLocalDateTimeString()"
                    class="btn-now-shortcut"
                    title="Rétablir à la date et heure actuelles"
                  >
                    <Clock :size="12" />
                    <span>Maintenant</span>
                  </button>
                </div>
                <input
                  v-model="form.date"
                  type="datetime-local"
                  required
                  class="form-input"
                />
              </div>

              <!-- Mode de paiement (Bas Gauche) -->
              <div class="form-group">
                <div class="field-label-row">
                  <label class="form-label">Méthode de Paiement *</label>
                  <router-link
                    to="/paiements"
                    target="_blank"
                    class="field-link"
                    title="Gérer ou ajouter des méthodes de paiement"
                  >
                    <ExternalLink :size="12" />
                    <span>Gérer</span>
                  </router-link>
                </div>
                <select v-model="form.methode_paiement_id" required class="form-select">
                  <option value="" disabled>-- Choisir le mode de paiement --</option>
                  <option v-for="m in paymentMethods" :key="m.id" :value="m.id">
                    {{ m.label }} <span v-if="m.details">({{ m.details }})</span>
                  </option>
                </select>
              </div>

              <!-- Vendeur / Affilié (Bas Droite) -->
              <div class="form-group">
                <label class="form-label">Vendeur / Affilié *</label>
                <select v-model="form.user_affilie_id" class="form-select">
                  <option :value="user?.id">👑 Moi-même ({{ user?.prenom }} {{ user?.nom }})</option>
                  <option v-for="u in vendorsList" :key="u.id" :value="u.id">
                    👤 {{ u.prenom }} {{ u.nom }} ({{ u.role?.label || 'Vendeur' }})
                  </option>
                </select>
              </div>
            </div>

            <!-- 2. Section Articles & Licences sous forme de tableau épuré -->
            <div class="sale-items-card">
              <div class="sale-items-header">
                <div class="sale-items-title">
                  <Package :size="16" class="text-primary" />
                  <span>Articles & Licences inclus</span>
                  <span class="badge badge-primary">{{ form.articles.length }} article(s)</span>
                </div>
                <button @click="addArticleLine" type="button" class="btn btn-secondary btn-xs">
                  <Plus :size="14" />
                  <span>Ajouter un produit</span>
                </button>
              </div>

              <!-- En-tête des colonnes du tableau -->
              <div class="sale-table-head">
                <span>Produit / Licence *</span>
                <span>Qté *</span>
                <span>Prix Unitaire (Ar) *</span>
                <span style="text-align: right;">Sous-total</span>
                <span></span>
              </div>

              <!-- Lignes d'articles -->
              <div class="sale-table-body">
                <div v-for="(line, idx) in form.articles" :key="idx" class="sale-table-row">
                  <!-- Produit -->
                  <div class="cell-product">
                    <select
                      v-model="line.produit_id"
                      @change="onProductSelect(line)"
                      required
                      class="form-select"
                    >
                      <option value="" disabled>-- Sélectionner le produit --</option>
                      <option v-for="p in productsList" :key="p.id" :value="p.id">
                        {{ p.nom }} (Prix actif: {{ formatPrice(p.prix_actif) }})
                      </option>
                    </select>
                  </div>

                  <!-- Quantité -->
                  <div class="cell-qty">
                    <input
                      v-model.number="line.quantite"
                      type="number"
                      min="1"
                      required
                      class="form-input"
                    />
                  </div>

                  <!-- Prix unitaire -->
                  <div class="cell-price">
                    <input
                      v-model.number="line.prix_unitaire"
                      type="number"
                      min="0"
                      step="100"
                      required
                      class="form-input"
                      placeholder="Prix unitaire"
                    />
                    <button
                      v-if="getActivePrice(line.produit_id) !== null && line.prix_unitaire !== Number(getActivePrice(line.produit_id))"
                      type="button"
                      @click="resetToActivePrice(line)"
                      class="price-reset-hint"
                      title="Rétablir au prix actif du catalogue"
                    >
                      ↺ Prix actif ({{ formatPrice(getActivePrice(line.produit_id)) }})
                    </button>
                  </div>

                  <!-- Sous-total -->
                  <div class="cell-subtotal">
                    {{ formatPrice((line.quantite || 0) * (line.prix_unitaire || 0)) }}
                  </div>

                  <!-- Suppression -->
                  <div class="cell-action">
                    <button
                      v-if="form.articles.length > 1"
                      @click="removeArticleLine(idx)"
                      type="button"
                      class="btn-icon btn-danger-icon"
                      title="Supprimer cette ligne"
                    >
                      <Trash2 :size="15" />
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 3. Pied de page & validation -->
            <div class="sale-modal-footer">
              <div class="total-display-group">
                <span class="total-display-label">Montant Total à Payer :</span>
                <span class="total-display-amount">{{ formatPrice(computedTotal) }}</span>
              </div>

              <div class="footer-btn-actions">
                <button @click="showCreateModal = false" type="button" class="btn btn-secondary">Annuler</button>
                <button type="submit" class="btn btn-success" :disabled="submitting || computedTotal <= 0">
                  <Check :size="18" />
                  <span v-if="submitting">{{ isEditing ? 'Enregistrement...' : 'Validation en cours...' }}</span>
                  <span v-else>{{ isEditing ? 'Enregistrer les modifications' : 'Valider la vente' }}</span>
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- MODAL: Fiche Détail d'une Vente & Guides d'activation -->
    <Teleport to="body">
      <div v-if="showDetailModal && selectedSale" class="modal-backdrop" @click.self="showDetailModal = false">
        <div class="modal-card modal-lg card animate-fade">
          <div class="modal-header">
            <div>
              <h3>Vente #{{ selectedSale.id }}</h3>
              <span class="text-xs text-muted">{{ formatDateTime(selectedSale.date) }}</span>
            </div>
            <div class="flex items-center gap-2">
              <button v-if="isSuperAdmin" @click="openEditSaleModal(selectedSale)" class="btn btn-secondary btn-xs" title="Modifier cette vente">
                <Pencil :size="13" />
                <span>Modifier</span>
              </button>
              <button @click="showDetailModal = false" class="btn-close"><X :size="20" /></button>
            </div>
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
          <div class="detail-items-table">
            <div v-for="cmd in selectedSale.commandes" :key="cmd.id" class="detail-item-row">
              <div class="item-prod-wrapper">
                <div v-if="cmd.produit_image" class="sale-item-thumb">
                  <img :src="resolveImageUrl(cmd.produit_image)" :alt="cmd.produit_nom" class="sale-item-thumb-img" />
                </div>
                <div v-else class="sale-item-thumb-fallback">
                  <Package :size="18" />
                </div>
                <div class="item-name-col">
                  <strong>{{ cmd.produit_nom || cmd.produit?.nom }}</strong>
                  <p class="text-xs text-muted" v-if="cmd.produit?.description">{{ cmd.produit?.description }}</p>
                </div>
              </div>
              <div class="item-calc-col">
                <span>{{ cmd.quantite }} x {{ formatPrice(cmd.prix_unitaire) }}</span>
                <strong class="text-emerald">{{ formatPrice(cmd.quantite * cmd.prix_unitaire) }}</strong>
              </div>

              <!-- Activation Guides & Copy Buttons -->
              <div v-if="cmd.produit?.activations?.length" class="activation-guides-box">
                <div v-for="act in cmd.produit.activations" :key="act.id" class="act-guide-item">
                  <div class="guide-header">
                    <span class="guide-badge">Guide d'activation</span>
                    <button @click="copyText(act.guide)" class="btn btn-xs btn-secondary" title="Copier le guide client">
                      <Copy :size="12" />
                      <span>Copier le guide</span>
                    </button>
                  </div>
                  <pre class="guide-pre">{{ act.guide }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  Plus,
  Search,
  FileText,
  Pencil,
  Trash2,
  X,
  Check,
  Copy,
  Users,
  Zap,
  RotateCcw,
  Lock,
  Package,
  ExternalLink,
  ShoppingCart,
  Clock
} from '@lucide/vue'
import confetti from 'canvas-confetti'
import apiClient from '../api/client'
import { useAuth } from '../composables/useAuth'
import { resolveImageUrl } from '../utils/imageHelper'

const route = useRoute()
const { user, isSuperAdmin } = useAuth()

const sales = ref([])
const clientsList = ref([])
const productsList = ref([])
const paymentMethods = ref([])
const vendorsList = ref([])
const provenancesList = ref([])
const loading = ref(false)
const submitting = ref(false)

const filters = ref({
  vendeur: '',
  search: '',
  date_debut: '',
  date_fin: '',
  methode_paiement: '',
  client: '',
  provenance: '',
})

const activePeriodPreset = ref('all')
let searchTimeout = null

function getLocalDateTimeString(date = new Date()) {
  const pad = (n) => String(n).padStart(2, '0')
  const year = date.getFullYear()
  const month = pad(date.getMonth() + 1)
  const day = pad(date.getDate())
  const hours = pad(date.getHours())
  const minutes = pad(date.getMinutes())
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

// Modals
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const selectedSale = ref(null)
const isEditing = ref(false)
const editingSaleId = ref(null)

const form = ref({
  client_id: '',
  date: getLocalDateTimeString(),
  user_affilie_id: '',
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

const hasActiveFilters = computed(() => {
  return !!(
    filters.value.vendeur ||
    filters.value.search ||
    filters.value.date_debut ||
    filters.value.date_fin ||
    filters.value.methode_paiement ||
    filters.value.client ||
    filters.value.provenance ||
    activePeriodPreset.value !== 'all'
  )
})

const activeFilterVendorName = computed(() => {
  if (!filters.value.vendeur) return ''
  const v = vendorsList.value.find(u => String(u.id) === String(filters.value.vendeur))
  return v ? `${v.prenom} ${v.nom}` : ''
})

const activeClientName = computed(() => {
  if (!filters.value.client) return ''
  const c = clientsList.value.find(item => String(item.id) === String(filters.value.client))
  return c ? c.nom : ''
})

const activeProvenanceName = computed(() => {
  if (!filters.value.provenance) return ''
  const p = provenancesList.value.find(item => String(item.id) === String(filters.value.provenance))
  return p ? p.label : ''
})

const activePeriodLabel = computed(() => {
  switch (activePeriodPreset.value) {
    case 'today': return "Aujourd'hui"
    case '7d': return "7 derniers jours"
    case 'month': return "Ce mois-ci"
    default: return ""
  }
})

const filteredSalesTotal = computed(() => {
  if (!Array.isArray(sales.value)) return 0
  return sales.value.reduce((acc, v) => acc + (Number(v.total) || 0), 0)
})

async function fetchSales() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.vendeur) params.vendeur = filters.value.vendeur
    if (filters.value.search) params.search = filters.value.search.trim()
    if (filters.value.date_debut) params.date_debut = filters.value.date_debut
    if (filters.value.date_fin) params.date_fin = filters.value.date_fin
    if (filters.value.methode_paiement) params.methode_paiement = filters.value.methode_paiement
    if (filters.value.client) params.client = filters.value.client
    if (filters.value.provenance) params.provenance = filters.value.provenance

    const res = await apiClient.get('/ventes/', { params })
    sales.value = res.data.results || res.data || []
  } catch (err) {
    console.error('Erreur chargement ventes:', err)
  } finally {
    loading.value = false
  }
}

async function fetchFormDependencies() {
  try {
    const [cRes, pRes, mRes, uRes, provRes] = await Promise.all([
      apiClient.get('/clients/'),
      apiClient.get('/produits/'),
      apiClient.get('/ventes/methodes-paiement/'),
      apiClient.get('/auth/users/').catch(() => ({ data: [] })),
      apiClient.get('/clients/provenances/').catch(() => ({ data: [] }))
    ])
    clientsList.value = cRes.data.results || cRes.data || []
    productsList.value = pRes.data.results || pRes.data || []
    paymentMethods.value = mRes.data.results || mRes.data || []
    vendorsList.value = uRes.data.results || uRes.data || []
    provenancesList.value = provRes.data.results || provRes.data || []
  } catch (err) {
    console.error('Erreur dépendances vente:', err)
  }
}

function toggleMySales() {
  if (!user.value?.id) return
  if (String(filters.value.vendeur) === String(user.value.id)) {
    filters.value.vendeur = ''
  } else {
    filters.value.vendeur = user.value.id
  }
  fetchSales()
}

function onSearchInput() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchSales()
  }, 350)
}

function clearSearch() {
  filters.value.search = ''
  fetchSales()
}

function setPeriodPreset(preset) {
  activePeriodPreset.value = preset
  const now = new Date()

  if (preset === 'today') {
    const ymd = now.toISOString().split('T')[0]
    filters.value.date_debut = ymd
    filters.value.date_fin = ymd
  } else if (preset === '7d') {
    const past = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    filters.value.date_debut = past.toISOString().split('T')[0]
    filters.value.date_fin = now.toISOString().split('T')[0]
  } else if (preset === 'month') {
    const firstDay = new Date(now.getFullYear(), now.getMonth(), 1)
    filters.value.date_debut = firstDay.toISOString().split('T')[0]
    filters.value.date_fin = now.toISOString().split('T')[0]
  } else {
    // all
    filters.value.date_debut = ''
    filters.value.date_fin = ''
  }
  fetchSales()
}

function onCustomDateChange() {
  activePeriodPreset.value = 'custom'
  fetchSales()
}

function resetFilters() {
  filters.value = {
    vendeur: '',
    search: '',
    date_debut: '',
    date_fin: '',
    methode_paiement: '',
    client: '',
    provenance: '',
  }
  activePeriodPreset.value = 'all'
  fetchSales()
}

function getActivePrice(productId) {
  if (!productId) return null
  const p = productsList.value.find(item => item.id === productId)
  return p?.prix_actif ?? null
}

function resetToActivePrice(line) {
  const price = getActivePrice(line.produit_id)
  if (price !== null && price !== undefined) {
    line.prix_unitaire = Number(price)
  }
}

// Watchers to auto-fill defaults once lists are fetched
watch(productsList, (newProds) => {
  if (newProds?.length) {
    if (!form.value.articles[0]?.produit_id) {
      form.value.articles[0].produit_id = newProds[0].id
      form.value.articles[0].prix_unitaire = Number(newProds[0].prix_actif || 0)
    }
  }
}, { immediate: true })

watch(clientsList, (newClients) => {
  if (newClients?.length && !form.value.client_id) {
    form.value.client_id = newClients[0].id
  }
}, { immediate: true })

watch(paymentMethods, (newMethods) => {
  if (newMethods?.length && !form.value.methode_paiement_id) {
    form.value.methode_paiement_id = newMethods[0].id
  }
}, { immediate: true })

async function openCreateSaleModal() {
  if (!isSuperAdmin.value) {
    alert("Permission refusée. Seul un administrateur (niveau 50) peut enregistrer de nouvelles ventes.")
    return
  }
  isEditing.value = false
  editingSaleId.value = null

  if (!productsList.value.length || !clientsList.value.length) {
    await fetchFormDependencies()
  }

  const prefill = sessionStorage.getItem('prefill_sale')
  if (prefill) {
    try {
      const data = JSON.parse(prefill)
      sessionStorage.removeItem('prefill_sale')
      form.value.client_id = data.client_id || (clientsList.value[0]?.id || '')
      form.value.date = data.date || getLocalDateTimeString()
      form.value.user_affilie_id = data.user_affilie_id || (user.value?.id || '')
      form.value.methode_paiement_id = data.methode_paiement_id || (paymentMethods.value[0]?.id || '')

      if (data.articles?.length) {
        form.value.articles = data.articles.map(a => {
          const prod = productsList.value.find(p => p.id === a.produit_id)
          const activePrice = prod?.prix_actif ? Number(prod.prix_actif) : 0
          return {
            produit_id: a.produit_id,
            quantite: a.quantite || 1,
            prix_unitaire: a.prix_unitaire !== undefined ? Number(a.prix_unitaire) : activePrice
          }
        })
      } else {
        const defaultProd = productsList.value[0]
        form.value.articles = [{
          produit_id: defaultProd?.id || '',
          quantite: 1,
          prix_unitaire: defaultProd?.prix_actif ? Number(defaultProd.prix_actif) : 0
        }]
      }
    } catch (e) {
      resetForm()
    }
  } else {
    resetForm()
  }
  showCreateModal.value = true
}

function openEditSaleModal(vente) {
  if (!isSuperAdmin.value) {
    alert("Permission refusée. Seul un administrateur (niveau 50) peut modifier des ventes.")
    return
  }
  isEditing.value = true
  editingSaleId.value = vente.id
  showDetailModal.value = false

  form.value = {
    client_id: vente.client?.id || '',
    date: vente.date ? getLocalDateTimeString(new Date(vente.date)) : getLocalDateTimeString(),
    user_affilie_id: vente.user_affilie?.id || (user.value?.id || ''),
    methode_paiement_id: vente.methode_paiement?.id || '',
    articles: vente.commandes?.length
      ? vente.commandes.map(cmd => ({
          produit_id: cmd.produit?.id || cmd.produit,
          quantite: cmd.quantite || 1,
          prix_unitaire: Number(cmd.prix_unitaire || 0)
        }))
      : [
          {
            produit_id: productsList.value[0]?.id || '',
            quantite: 1,
            prix_unitaire: Number(productsList.value[0]?.prix_actif || 0)
          }
        ]
  }
  showCreateModal.value = true
}

function resetForm() {
  const defaultProduct = productsList.value[0]
  const defaultClient = clientsList.value[0]
  const defaultMethod = paymentMethods.value[0]
  form.value = {
    client_id: defaultClient?.id || '',
    date: getLocalDateTimeString(),
    user_affilie_id: user.value?.id || '',
    methode_paiement_id: defaultMethod?.id || '',
    articles: [
      {
        produit_id: defaultProduct?.id || '',
        quantite: 1,
        prix_unitaire: defaultProduct?.prix_actif ? Number(defaultProduct.prix_actif) : 0
      }
    ]
  }
}

function addArticleLine() {
  const defaultProduct = productsList.value[0]
  form.value.articles.push({
    produit_id: defaultProduct?.id || '',
    quantite: 1,
    prix_unitaire: defaultProduct?.prix_actif ? Number(defaultProduct.prix_actif) : 0
  })
}

function removeArticleLine(idx) {
  form.value.articles.splice(idx, 1)
}

function onProductSelect(line) {
  const p = productsList.value.find(item => item.id === line.produit_id)
  if (p) {
    line.prix_unitaire = Number(p.prix_actif ?? 0)
  }
}

function extractErrorMessage(err) {
  if (!err) return "Une erreur est survenue lors de l'enregistrement de la vente."
  if (err.response?.data) {
    const data = err.response.data
    if (typeof data === 'string') return data
    if (data.error) return data.error
    if (data.detail) return data.detail
    if (Array.isArray(data.non_field_errors) && data.non_field_errors.length) {
      return data.non_field_errors.join(' ')
    }
    const errors = []
    for (const [key, value] of Object.entries(data)) {
      if (Array.isArray(value)) {
        errors.push(`${key}: ${value.join(', ')}`)
      } else if (typeof value === 'object' && value !== null) {
        errors.push(`${key}: ${JSON.stringify(value)}`)
      } else {
        errors.push(`${key}: ${value}`)
      }
    }
    if (errors.length) return errors.join('\n')
  }
  return err.message || "Erreur lors de la validation de la vente"
}

async function submitCreateSale() {
  submitting.value = true
  try {
    const payload = {
      client_id: form.value.client_id,
      user_affilie_id: form.value.user_affilie_id || undefined,
      methode_paiement_id: form.value.methode_paiement_id,
      date: form.value.date ? new Date(form.value.date).toISOString() : undefined,
      articles: form.value.articles.map(a => ({
        produit_id: a.produit_id,
        quantite: a.quantite,
        prix_unitaire: a.prix_unitaire
      }))
    }

    if (isEditing.value && editingSaleId.value) {
      await apiClient.put(`/ventes/${editingSaleId.value}/`, payload)
    } else {
      await apiClient.post('/ventes/', payload)
    }

    showCreateModal.value = false
    await fetchSales()

    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 }
    })
  } catch (err) {
    console.error('Erreur validation vente:', err)
    alert(extractErrorMessage(err))
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
  const num = Number(val)
  if (isNaN(num)) return '0 Ar'
  return new Intl.NumberFormat('fr-MG').format(Math.round(num)) + ' Ar'
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

watch(() => route.query.vendeur, (vId) => {
  if (vId) {
    filters.value.vendeur = vId
    fetchSales()
  }
})

onMounted(async () => {
  if (route.query.vendeur) {
    filters.value.vendeur = route.query.vendeur
  }
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

/* FILTERS CARD */
.sales-filter-card {
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
  background: var(--gradient-card);
  border: 1px solid var(--border-card);
}

/* 1. PRIMARY VENDOR FILTER HIGHLIGHT */
.primary-vendor-filter {
  background: rgba(0, 210, 255, 0.08);
  border: 1.5px solid rgba(0, 210, 255, 0.4);
  box-shadow: 0 0 20px rgba(0, 210, 255, 0.12);
  border-radius: var(--radius-md);
  padding: 0.85rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.filter-header-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.label-with-icon {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.label-title {
  font-size: 0.85rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  color: var(--primary);
  text-transform: uppercase;
}

.vendor-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  max-width: 500px;
}

.vendor-select-wrapper {
  flex: 1;
}

.vendor-select {
  width: 100%;
  font-weight: 600;
  border-color: rgba(0, 210, 255, 0.5);
  background-color: rgba(6, 13, 25, 0.85);
}

/* 2. SECONDARY FILTERS */
.secondary-filters-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 220px;
}

.search-icon {
  position: absolute;
  left: 0.85rem;
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
  right: 0.65rem;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
}

.btn-clear-search:hover {
  color: var(--text-main);
}

.period-presets {
  display: flex;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 0.2rem;
  gap: 0.2rem;
}

.preset-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 0.35rem 0.65rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.preset-btn.active {
  background: var(--primary);
  color: #060d19;
  font-weight: 700;
}

.date-range-inputs {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.date-input {
  width: 135px;
  font-size: 0.8rem;
  padding: 0.4rem 0.5rem;
}

.date-sep {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.filter-select {
  width: 180px;
}

.btn-new-sale {
  margin-left: auto;
}

.admin-only-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  padding: 0.5rem 0.85rem;
  border-radius: var(--radius-md);
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-left: auto;
}

/* 3. SUMMARY BANNER */
.filter-results-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-subtle);
  font-size: 0.85rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.summary-left {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.results-count strong {
  color: var(--primary);
}

.active-filter-pill {
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

.summary-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.total-label {
  color: var(--text-secondary);
  font-weight: 600;
}

.total-val {
  font-size: 1.1rem;
  font-weight: 800;
}

/* VENDOR CELL IN TABLE */
.vendor-cell {
  display: flex;
  flex-direction: column;
}

.vendor-name {
  font-weight: 600;
  font-size: 0.875rem;
}

.vendor-role-tag {
  font-size: 0.7rem;
  color: var(--primary);
}

.actions-group {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

/* MODAL STYLES */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1.5rem;
}

/* MODAL STYLES */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(3, 7, 18, 0.85);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1.5rem;
}

.sale-modal-card {
  width: 100%;
  max-width: 860px;
  max-height: 92vh;
  overflow-y: auto;
  background: #0b1526;
  border: 1px solid rgba(0, 210, 255, 0.3);
  border-radius: var(--radius-xl);
  box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.85), 0 0 35px rgba(0, 210, 255, 0.1);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.modal-header-custom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border-subtle);
}

.modal-header-info {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.modal-header-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  background: rgba(0, 210, 255, 0.12);
  border: 1px solid rgba(0, 210, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-main);
}

.modal-subtitle {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 0.15rem;
}

.btn-close {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.btn-close:hover {
  color: var(--text-main);
  background: rgba(255, 255, 255, 0.08);
}

/* 1. TOP FIELDS: STRICT 50/50 GRID */
.sale-fields-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.25rem 1.75rem;
  width: 100%;
}

.sale-fields-grid .form-group {
  margin-bottom: 0;
  width: 100%;
  min-width: 0;
}

.sale-fields-grid .form-input,
.sale-fields-grid .form-select {
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
  min-width: 0 !important;
}

.field-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.35rem;
  min-width: 0;
}

.field-label-row .form-label {
  margin-bottom: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.field-link {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

.field-link:hover {
  text-decoration: underline;
  filter: brightness(1.2);
}

.btn-now-shortcut {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: rgba(0, 210, 255, 0.1);
  border: 1px solid rgba(0, 210, 255, 0.25);
  color: var(--primary);
  padding: 0.2rem 0.55rem;
  border-radius: var(--radius-sm);
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  transition: all var(--transition-fast);
}

.btn-now-shortcut:hover {
  background: rgba(0, 210, 255, 0.2);
  border-color: var(--primary);
}

/* 2. ARTICLES TABLE CARD */
.sale-items-card {
  background: rgba(14, 25, 45, 0.6);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-top: 0.25rem;
}

.sale-items-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1.25rem;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid var(--border-subtle);
}

.sale-items-title {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--text-main);
}

.sale-table-head {
  display: grid;
  grid-template-columns: 1fr 90px 160px 120px 38px;
  gap: 0.85rem;
  padding: 0.65rem 1.25rem;
  background: rgba(6, 13, 25, 0.6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  text-transform: uppercase;
  align-items: center;
}

.sale-table-body {
  display: flex;
  flex-direction: column;
  padding: 0.4rem 0;
}

.sale-table-row {
  display: grid;
  grid-template-columns: 1fr 90px 160px 120px 38px;
  gap: 0.85rem;
  padding: 0.65rem 1.25rem;
  align-items: center;
  transition: background var(--transition-fast);
}

.sale-table-row:hover {
  background: rgba(255, 255, 255, 0.02);
}

.cell-product {
  min-width: 0;
}

.cell-product select {
  width: 100% !important;
  box-sizing: border-box !important;
}

.cell-qty {
  min-width: 0;
}

.cell-qty input {
  width: 100% !important;
  text-align: center;
  box-sizing: border-box !important;
}

.cell-price {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.cell-price input {
  width: 100% !important;
  box-sizing: border-box !important;
}

.cell-subtotal {
  text-align: right;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--emerald);
  white-space: nowrap;
}

.cell-action {
  display: flex;
  align-items: center;
  justify-content: center;
}

.price-reset-hint {
  font-size: 0.68rem;
  color: var(--primary);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  text-align: left;
  text-decoration: underline;
}

/* 3. SUMMARY BAR & ACTIONS */
.sale-modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-subtle);
  flex-wrap: wrap;
  gap: 1rem;
}

.total-display-group {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}

.total-display-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.total-display-amount {
  font-size: 1.85rem;
  font-weight: 800;
  color: var(--emerald);
  letter-spacing: -0.02em;
}

.footer-btn-actions {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.modal-card {
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-card);
  padding: 2rem;
}

.modal-lg { max-width: 680px; }
.modal-xl { max-width: 880px; }

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: 1.5rem;
}

.sale-meta-card {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  background: rgba(255, 255, 255, 0.03);
  padding: 1.25rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-secondary);
  margin-bottom: 0.85rem;
}

.detail-items-table {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 0.85rem 1rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.item-prod-wrapper {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex: 1;
  min-width: 200px;
}

.sale-item-thumb {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid rgba(0, 210, 255, 0.35);
  background: rgba(0, 0, 0, 0.4);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sale-item-thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sale-item-thumb-fallback {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  flex-shrink: 0;
}

.act-guide-item {
  margin-top: 0.75rem;
  background: rgba(0, 210, 255, 0.05);
  border: 1px solid rgba(0, 210, 255, 0.2);
  border-radius: var(--radius-sm);
  padding: 0.75rem;
}

.guide-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.guide-badge {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--primary);
}

.guide-pre {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  white-space: pre-wrap;
  color: var(--text-secondary);
  line-height: 1.4;
}
</style>
