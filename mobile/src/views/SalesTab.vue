<template>
  <ion-page>
    <ion-header :translucent="true">
      <ion-toolbar class="main-toolbar">
        <ion-title>Historique des Ventes</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="openNewSale" class="btn-toolbar-action">
            <ion-icon :icon="addCircleOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>

      <!-- Search & Filters -->
      <div class="filter-bar">
        <div class="search-input-wrap">
          <ion-icon :icon="searchOutline" class="search-icon" />
          <input
            v-model="searchQuery"
            @input="onSearch"
            type="text"
            placeholder="Rechercher client, tél, n°..."
            class="search-field"
          />
          <button v-if="searchQuery || selectedClient || selectedProvenance" @click="clearSearch" class="clear-search-btn">
            <ion-icon :icon="closeCircle" />
          </button>
        </div>

        <div class="filter-selects-row">
          <select v-model="selectedProvenance" @change="fetchSales" class="mobile-filter-select">
            <option value="">🌐 Toutes provenances</option>
            <option v-for="prov in provenances" :key="prov.id" :value="prov.id">{{ prov.label }}</option>
          </select>
          <select v-model="selectedClient" @change="fetchSales" class="mobile-filter-select">
            <option value="">👤 Tous clients</option>
            <option v-for="c in clients" :key="c.id" :value="c.id">{{ c.nom }}</option>
          </select>
        </div>

        <div class="period-pills">
          <button
            v-for="p in periodOptions"
            :key="p.id"
            :class="['period-pill', activePeriod === p.id ? 'active' : '']"
            @click="setPeriod(p.id)"
          >
            {{ p.label }}
          </button>
        </div>
      </div>
    </ion-header>

    <ion-content :fullscreen="true" class="sales-content">
      <ion-refresher slot="fixed" @ionRefresh="handleRefresh($event)">
        <ion-refresher-content></ion-refresher-content>
      </ion-refresher>

      <!-- Stats Bar -->
      <div class="sales-stats-row">
        <span class="count-label"><b>{{ sales.length }}</b> vente(s) affichée(s)</span>
        <span class="sum-label">Total : <b>{{ formatPrice(totalSalesAmount) }}</b></span>
      </div>

      <!-- Sales List -->
      <div v-if="loading" class="empty-state">
        <span>Chargement des ventes...</span>
      </div>

      <div v-else-if="sales.length === 0" class="empty-state">
        <ion-icon :icon="cartOutline" class="empty-icon" />
        <p>Aucune vente ne correspond aux critères.</p>
        <button class="btn-create-sale-empty" @click="openNewSale">
          Enregistrer une première vente
        </button>
      </div>

      <div v-else class="sales-cards-container">
        <div
          v-for="sale in sales"
          :key="sale.id"
          class="sale-card"
          @click="toggleExpand(sale.id)"
        >
          <div class="sale-header">
            <div class="sale-client-info">
              <div class="client-name-line">
                <span class="client-name">{{ sale.client?.nom || 'Client Inconnu' }}</span>
                <span v-if="sale.client?.provenance?.label" class="provenance-badge">
                  {{ sale.client.provenance.label }}
                </span>
              </div>
              <span class="sale-meta">{{ formatDate(sale.date) }} • {{ sale.methode_paiement?.label || 'Direct' }}</span>
            </div>
            <div class="sale-header-right">
              <div class="sale-total-block">
                <span class="sale-total">{{ formatPrice(sale.total) }}</span>
                <span class="badge-status">Conclue</span>
              </div>
              <button
                v-if="isSuperAdmin"
                type="button"
                class="btn-edit-badge"
                @click.stop="openEditSale(sale)"
                title="Modifier cette vente"
              >
                <ion-icon :icon="createOutline" />
              </button>
            </div>
          </div>

          <!-- Items preview -->
          <div class="sale-items-compact">
            <span
              v-for="(cmd, cIdx) in sale.commandes"
              :key="cIdx"
              class="item-tag"
            >
              {{ cmd.quantite }}x {{ cmd.produit_nom }}
            </span>
          </div>

          <!-- Expanded details & activation guide -->
          <div v-if="expandedSaleId === sale.id" class="expanded-details animate-fade">
            <div class="detail-divider"></div>

            <div class="detail-section">
              <div class="detail-row">
                <span class="lbl">Vendeur :</span>
                <span class="val">{{ sale.user_affilie?.prenom }} {{ sale.user_affilie?.nom || '' }}</span>
              </div>
              <div class="detail-row" v-if="sale.client?.numero">
                <span class="lbl">Téléphone client :</span>
                <a :href="`tel:${sale.client.numero}`" class="phone-link" @click.stop>
                  📞 {{ sale.client.numero }}
                </a>
              </div>
            </div>

            <!-- Action Modifier la vente -->
            <div v-if="isSuperAdmin" class="card-edit-action-box">
              <button
                type="button"
                @click.stop="openEditSale(sale)"
                class="btn-edit-sale-expanded"
              >
                <ion-icon :icon="createOutline" />
                <span>Modifier cette vente</span>
              </button>
            </div>

            <!-- Activation guides -->
            <div v-if="sale.guides_activation && sale.guides_activation.length" class="activation-guides-box">
              <div class="activation-header">
                <strong>Guide d'activation pour le client :</strong>
              </div>
              <div
                v-for="(g, gIdx) in sale.guides_activation"
                :key="gIdx"
                class="guide-snippet"
              >
                <div class="guide-title">{{ g.produit_nom }}</div>
                <div class="guide-text">{{ g.guide }}</div>
                <button
                  type="button"
                  @click.stop="copyActivationGuide(g)"
                  class="btn-copy-guide"
                >
                  <ion-icon :icon="copyOutline" />
                  <span>Copier le guide (pour WhatsApp)</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ion-content>

    <SaleModal
      :is-open="isSaleModalOpen"
      :sale-to-edit="saleToEdit"
      @close="onCloseSaleModal"
      @sale-created="onSaleCreated"
      @sale-updated="onSaleUpdated"
    />
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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
  toastController,
} from '@ionic/vue'
import {
  addCircleOutline,
  searchOutline,
  closeCircle,
  cartOutline,
  copyOutline,
  createOutline,
} from 'ionicons/icons'
import apiClient from '../api/client'
import { useAuth } from '../composables/useAuth'
import SaleModal from '../components/SaleModal.vue'

const { isSuperAdmin } = useAuth()

const loading = ref(false)
const sales = ref([])
const clients = ref([])
const provenances = ref([])
const selectedProvenance = ref('')
const selectedClient = ref('')
const searchQuery = ref('')
const activePeriod = ref('all')
const expandedSaleId = ref(null)

const isSaleModalOpen = ref(false)
const saleToEdit = ref(null)

const periodOptions = [
  { id: 'all', label: 'Tout' },
  { id: 'today', label: "Aujourd'hui" },
  { id: '7d', label: '7 jours' },
  { id: '30d', label: '30 jours' },
]

const totalSalesAmount = computed(() => {
  if (!Array.isArray(sales.value)) return 0
  return sales.value.reduce((acc, curr) => acc + (Number(curr.total) || 0), 0)
})

function formatPrice(val) {
  const num = Number(val)
  if (isNaN(num)) return '0 Ar'
  return Math.round(num).toLocaleString('fr-FR') + ' Ar'
}

function formatDate(isoStr) {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' }) + ' ' + d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

function toggleExpand(id) {
  expandedSaleId.value = expandedSaleId.value === id ? null : id
}

function openNewSale() {
  saleToEdit.value = null
  isSaleModalOpen.value = true
}

function openEditSale(sale) {
  if (!isSuperAdmin.value) {
    showToast("Seul un administrateur peut modifier une vente.", 'warning')
    return
  }
  saleToEdit.value = sale
  isSaleModalOpen.value = true
}

function onCloseSaleModal() {
  isSaleModalOpen.value = false
  saleToEdit.value = null
}

async function onSaleCreated() {
  await fetchSales()
  showToast('Vente enregistrée avec succès !', 'success')
}

async function onSaleUpdated() {
  await fetchSales()
  showToast('Vente mise à jour avec succès !', 'success')
}

async function showToast(message, color = 'success') {
  const toast = await toastController.create({
    message,
    duration: 2500,
    color,
    position: 'top',
  })
  await toast.present()
}

async function loadFilterOptions() {
  try {
    const [cRes, pRes] = await Promise.all([
      apiClient.get('/clients/'),
      apiClient.get('/clients/provenances/'),
    ])
    clients.value = cRes.data.results || cRes.data || []
    provenances.value = pRes.data.results || pRes.data || []
  } catch (err) {
    console.error('Erreur chargement filtres ventes:', err)
  }
}

async function fetchSales() {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    if (selectedClient.value) {
      params.client = selectedClient.value
    }
    if (selectedProvenance.value) {
      params.provenance = selectedProvenance.value
    }

    const today = new Date()
    if (activePeriod.value === 'today') {
      params.date_debut = today.toISOString().split('T')[0]
    } else if (activePeriod.value === '7d') {
      const past = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
      params.date_debut = past.toISOString().split('T')[0]
    } else if (activePeriod.value === '30d') {
      const past = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
      params.date_debut = past.toISOString().split('T')[0]
    }

    const res = await apiClient.get('/ventes/', { params })
    sales.value = res.data.results || res.data || []
  } catch (err) {
    console.error('Erreur chargement ventes:', err)
  } finally {
    loading.value = false
  }
}

let searchTimeout = null
function onSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchSales()
  }, 300)
}

function clearSearch() {
  searchQuery.value = ''
  selectedProvenance.value = ''
  selectedClient.value = ''
  fetchSales()
}

function setPeriod(pId) {
  activePeriod.value = pId
  fetchSales()
}

async function handleRefresh(event) {
  await fetchSales()
  event.target.complete()
}

async function copyActivationGuide(guideObj) {
  const text = `*Licence Pro Madagascar*\n\nGuide pour ${guideObj.produit_nom} :\n${guideObj.guide}\n\n_Merci pour votre achat ! En cas de question, nous restons disponibles._`
  
  if (navigator.clipboard) {
    await navigator.clipboard.writeText(text)
  }

  showToast('Guide copié ! Prêt à être collé au client sur WhatsApp.', 'success')
}

onMounted(() => {
  loadFilterOptions()
  fetchSales()
})
</script>

<style scoped>
.main-toolbar {
  --background: #0B1120;
  --color: #FFFFFF;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.btn-toolbar-action {
  --color: #14B8A6;
  font-size: 24px;
}

.filter-bar {
  background: #0B1120;
  padding: 8px 16px 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: #64748B;
  font-size: 16px;
}

.search-field {
  width: 100%;
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 10px 36px 10px 36px;
  color: #FFFFFF;
  font-size: 0.85rem;
  outline: none;
}

.clear-search-btn {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: #94A3B8;
  font-size: 18px;
}

.period-pills {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  overflow-x: auto;
}

.filter-selects-row {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.mobile-filter-select {
  flex: 1;
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 8px 10px;
  color: #FFFFFF;
  font-size: 0.78rem;
  outline: none;
}

.client-name-line {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.provenance-badge {
  background: rgba(56, 189, 248, 0.15);
  color: #38BDF8;
  font-size: 0.65rem;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.period-pill {
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #94A3B8;
  padding: 6px 14px;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.period-pill.active {
  background: #0D9488;
  color: #FFFFFF;
  border-color: #0D9488;
}

.sales-content {
  --background: #0B1120;
  --color: #F8FAFC;
}

.sales-stats-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px 4px 16px;
  font-size: 0.8rem;
  color: #94A3B8;
}

.sales-stats-row b {
  color: #5EEAD4;
}

.sales-cards-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px 16px 24px 16px;
}

.sale-card {
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sale-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.sale-client-info {
  flex: 1;
  min-width: 0;
  padding-right: 8px;
}

.client-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: #FFFFFF;
  display: block;
}

.sale-meta {
  font-size: 0.72rem;
  color: #94A3B8;
  margin-top: 2px;
  display: block;
}

.sale-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sale-total-block {
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.sale-total {
  font-size: 1rem;
  font-weight: 800;
  color: #34D399;
}

.badge-status {
  font-size: 0.65rem;
  background: rgba(16, 185, 129, 0.15);
  color: #10B981;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
  margin-top: 2px;
}

.btn-edit-badge {
  background: rgba(56, 189, 248, 0.12);
  color: #38BDF8;
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit-badge:active {
  transform: scale(0.92);
  background: rgba(56, 189, 248, 0.25);
}

.sale-items-compact {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.item-tag {
  background: #0B1120;
  color: #93C5FD;
  font-size: 0.72rem;
  padding: 3px 8px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.expanded-details {
  margin-top: 12px;
}

.detail-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
  margin-bottom: 12px;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
}

.detail-row .lbl {
  color: #64748B;
}

.detail-row .val {
  color: #E2E8F0;
  font-weight: 600;
}

.phone-link {
  color: #38BDF8;
  text-decoration: none;
  font-weight: 600;
}

.card-edit-action-box {
  margin-top: 12px;
}

.btn-edit-sale-expanded {
  width: 100%;
  background: rgba(59, 130, 246, 0.12);
  color: #60A5FA;
  border: 1px solid rgba(59, 130, 246, 0.25);
  padding: 9px 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit-sale-expanded:active {
  background: rgba(59, 130, 246, 0.25);
}

.activation-guides-box {
  margin-top: 10px;
  background: #0B1120;
  border-radius: 10px;
  padding: 10px;
  border: 1px solid rgba(13, 148, 136, 0.3);
}

.activation-header {
  font-size: 0.78rem;
  color: #5EEAD4;
  margin-bottom: 6px;
}

.guide-snippet {
  margin-top: 6px;
}

.guide-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: #FFFFFF;
}

.guide-text {
  font-size: 0.75rem;
  color: #CBD5E1;
  white-space: pre-wrap;
  margin: 4px 0 8px 0;
  max-height: 120px;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.03);
  padding: 6px 8px;
  border-radius: 6px;
}

.btn-copy-guide {
  width: 100%;
  background: #0D9488;
  color: #FFFFFF;
  border: none;
  padding: 8px;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #64748B;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.empty-icon {
  font-size: 48px;
  color: #334155;
}

.btn-create-sale-empty {
  background: #0D9488;
  color: #fff;
  border: none;
  padding: 10px 18px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
}
</style>
