<template>
  <div class="dashboard-view">
    <!-- Header with Title & Refresh -->
    <div class="dashboard-header">
      <div>
        <h1 class="text-xl font-bold">Tableau de bord</h1>
        <p class="text-muted text-sm">Performance des ventes et trésorerie en temps réel</p>
      </div>
      <div class="header-actions">
        <button @click="loadDashboard" class="btn btn-secondary btn-sm" :disabled="loading">
          <RefreshCw :size="16" :class="{ 'spin-icon': loading }" />
          <span>Actualiser</span>
        </button>
      </div>
    </div>

    <!-- BARRE DE FILTRES DU TABLEAU DE BORD -->
    <div class="dashboard-filter-bar card">
      <div class="dash-filters-row">
        <!-- 1. FILTRE VENDEUR / USER-AFFILIÉ (Mise en avant) -->
        <div class="filter-group-dash filter-vendor-dash">
          <label class="filter-label-dash">
            <Users :size="14" class="text-primary" />
            <span>Vendeur / Affilié</span>
          </label>
          <div class="vendor-input-group">
            <select v-model="filters.vendeur" @change="loadDashboard" class="form-select select-dash-vendor">
              <option value="">👥 Toute l'équipe (Global)</option>
              <option v-for="u in vendorsList" :key="u.id" :value="u.id">
                👤 {{ u.prenom }} {{ u.nom }} ({{ u.role?.label || 'Vendeur' }})
              </option>
            </select>
            <button
              v-if="user?.id"
              type="button"
              @click="toggleMyDashboard"
              class="btn btn-xs"
              :class="filters.vendeur === user.id ? 'btn-primary' : 'btn-secondary'"
              title="Filtrer sur mon compte uniquement"
            >
              <Zap :size="12" />
              <span>Moi</span>
            </button>
          </div>
        </div>

        <!-- 2. PÉRIODE RAPIDE -->
        <div class="filter-group-dash">
          <label class="filter-label-dash">
            <Calendar :size="14" class="text-primary" />
            <span>Période</span>
          </label>
          <div class="dash-period-presets">
            <button
              type="button"
              class="dash-preset-btn"
              :class="{ active: filters.periode === 'all' }"
              @click="setPeriodPreset('all')"
            >
              Tout
            </button>
            <button
              type="button"
              class="dash-preset-btn"
              :class="{ active: filters.periode === 'today' }"
              @click="setPeriodPreset('today')"
            >
              Aujourd'hui
            </button>
            <button
              type="button"
              class="dash-preset-btn"
              :class="{ active: filters.periode === '7d' }"
              @click="setPeriodPreset('7d')"
            >
              7 jours
            </button>
            <button
              type="button"
              class="dash-preset-btn"
              :class="{ active: filters.periode === 'month' }"
              @click="setPeriodPreset('month')"
            >
              Ce mois
            </button>
            <button
              type="button"
              class="dash-preset-btn"
              :class="{ active: filters.periode === 'custom' }"
              @click="filters.periode = 'custom'"
            >
              Dates...
            </button>
          </div>
        </div>

        <!-- Dates personnalisées -->
        <div v-if="filters.periode === 'custom'" class="filter-group-dash custom-dates-group">
          <label class="filter-label-dash">
            <span>Intervalle de dates</span>
          </label>
          <div class="dash-date-inputs">
            <input
              v-model="filters.date_debut"
              @change="loadDashboard"
              type="date"
              class="form-input date-input-dash"
            />
            <span class="sep">-</span>
            <input
              v-model="filters.date_fin"
              @change="loadDashboard"
              type="date"
              class="form-input date-input-dash"
            />
          </div>
        </div>

        <!-- 3. MODE DE PAIEMENT -->
        <div class="filter-group-dash">
          <label class="filter-label-dash">
            <CreditCard :size="14" class="text-primary" />
            <span>Paiement</span>
          </label>
          <select v-model="filters.methode_paiement" @change="loadDashboard" class="form-select select-dash">
            <option value="">Tous règlements</option>
            <option v-for="m in paymentMethods" :key="m.id" :value="m.id">{{ m.label }}</option>
          </select>
        </div>

        <!-- Reset Button -->
        <div class="filter-group-dash reset-group" v-if="hasActiveFilters">
          <button @click="resetFilters" type="button" class="btn btn-secondary btn-sm" title="Réinitialiser">
            <RotateCcw :size="14" />
            <span>Réinitialiser</span>
          </button>
        </div>
      </div>

      <!-- Bandeau récapitulatif des filtres appliqués -->
      <div v-if="hasActiveFilters" class="dash-active-filters-bar">
        <span class="text-xs text-muted">Données actuellement filtrées par :</span>
        <span v-if="activeVendorName" class="filter-pill">
          Vendeur : <strong>{{ activeVendorName }}</strong>
        </span>
        <span v-if="filters.periode !== 'all'" class="filter-pill">
          Période : <strong>{{ activePeriodLabel }}</strong>
        </span>
        <span v-if="activePaymentName" class="filter-pill">
          Règlement : <strong>{{ activePaymentName }}</strong>
        </span>
      </div>
    </div>

    <!-- KPI Cards Row -->
    <div class="kpi-grid">
      <!-- Chiffre d'affaires -->
      <div class="card kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Chiffre d'Affaires</span>
          <div class="kpi-icon-box icon-primary">
            <DollarSign :size="22" />
          </div>
        </div>
        <div class="kpi-value">{{ formatCurrency(data?.kpis?.chiffre_affaires || 0) }}</div>
        <div class="kpi-subtext">
          <span class="badge badge-primary">Volume encaissé</span>
        </div>
      </div>

      <!-- Marge Nette -->
      <div class="card kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Marge Nette Estimée</span>
          <div class="kpi-icon-box icon-emerald">
            <TrendingUp :size="22" />
          </div>
        </div>
        <div class="kpi-value text-emerald">{{ formatCurrency(data?.kpis?.marge_nette || 0) }}</div>
        <div class="kpi-subtext">
          <span class="badge badge-success">Bénéfice brut</span>
        </div>
      </div>

      <!-- Nombre de Ventes -->
      <div class="card kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Nombre de Ventes</span>
          <div class="kpi-icon-box icon-amber">
            <ShoppingCart :size="22" />
          </div>
        </div>
        <div class="kpi-value">{{ data?.kpis?.nombre_ventes || 0 }}</div>
        <div class="kpi-subtext">
          <span class="badge badge-warning">Transactions</span>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-grid">
      <!-- Sales Evolution Chart -->
      <div class="card chart-card">
        <div class="chart-header">
          <h3>Évolution des Ventes</h3>
          <span class="text-muted text-xs">Fréquence par date</span>
        </div>
        <div class="chart-container" v-if="salesChartData.labels.length">
          <Line :data="salesChartData" :options="lineChartOptions" />
        </div>
        <div v-else class="chart-empty">
          <p>Aucune donnée de vente pour ces critères.</p>
        </div>
      </div>

      <!-- Payment Methods Distribution Chart -->
      <div class="card chart-card">
        <div class="chart-header">
          <h3>Méthodes de Paiement</h3>
          <span class="text-muted text-xs">Répartition des règlements</span>
        </div>
        <div class="chart-container doughnut-container" v-if="paymentChartData.labels.length">
          <Doughnut :data="paymentChartData" :options="doughnutChartOptions" />
        </div>
        <div v-else class="chart-empty">
          <p>Aucune transaction enregistrée.</p>
        </div>
      </div>
    </div>

    <!-- Bottom Row: Top Products & Sellers Leaderboard -->
    <div class="bottom-grid">
      <!-- Top 5 Products -->
      <div class="card">
        <div class="section-title-box">
          <div class="title-with-icon">
            <Package :size="20" class="text-primary" />
            <h3>Top Produits</h3>
          </div>
        </div>
        <div v-if="data?.top_produits?.length" class="top-products-list">
          <div v-for="(prod, idx) in data.top_produits" :key="prod.produit__id" class="product-item">
            <div class="prod-rank">{{ idx + 1 }}</div>
            <div class="prod-info">
              <span class="prod-name">{{ prod.produit__nom }}</span>
              <span class="prod-ca">{{ formatCurrency(prod.total_ca) }}</span>
            </div>
            <div class="prod-sales-badge">
              <span>{{ prod.total_quantite }} vendus</span>
            </div>
          </div>
        </div>
        <div v-else class="text-muted text-sm py-4">
          Aucun produit vendu pour ces critères.
        </div>
      </div>

      <!-- Sellers Points Leaderboard -->
      <div class="card">
        <div class="section-title-box">
          <div class="title-with-icon">
            <Award :size="20" class="text-amber" />
            <h3>Classement des Vendeurs</h3>
          </div>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Rang</th>
                <th>Vendeur / Affilié</th>
                <th>Chiffre d'Affaires</th>
                <th>Ventes</th>
                <th>Habilitation</th>
                <th style="text-align: right;">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(vendeur, idx) in data?.classement_vendeurs || []" :key="vendeur.id">
                <td>
                  <span class="rank-pill" :class="'rank-' + (idx + 1)">#{{ idx + 1 }}</span>
                </td>
                <td>
                  <div class="font-bold">{{ vendeur.nom_complet }}</div>
                  <div class="text-xs text-muted">{{ vendeur.email }}</div>
                </td>
                <td>
                  <span class="font-bold text-emerald">{{ formatCurrency(vendeur.chiffre_affaires) }}</span>
                </td>
                <td>{{ vendeur.nombre_ventes }}</td>
                <td>
                  <span class="badge" :class="vendeur.points >= 50 ? 'badge-primary' : 'badge-neutral'">
                    {{ vendeur.role }} ({{ vendeur.points }} pts)
                  </span>
                </td>
                <td style="text-align: right;">
                  <router-link
                    :to="'/ventes?vendeur=' + vendeur.id"
                    class="btn btn-secondary btn-xs"
                    title="Voir les ventes de ce vendeur"
                  >
                    <span>Ventes ➔</span>
                  </router-link>
                </td>
              </tr>
              <tr v-if="!data?.classement_vendeurs?.length">
                <td colspan="6" class="text-center py-4 text-muted">
                  Aucun vendeur trouvé.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  DollarSign,
  TrendingUp,
  ShoppingCart,
  RefreshCw,
  Package,
  Award,
  Users,
  Zap,
  Calendar,
  CreditCard,
  RotateCcw
} from '@lucide/vue'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
} from 'chart.js'
import { Line, Doughnut } from 'vue-chartjs'
import apiClient from '../api/client'
import { useAuth } from '../composables/useAuth'

const { user } = useAuth()

// Register Chart.js elements
ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement
)

const loading = ref(false)
const vendorsList = ref([])
const paymentMethods = ref([])

const filters = ref({
  vendeur: '',
  periode: 'all',
  date_debut: '',
  date_fin: '',
  methode_paiement: '',
})

const data = ref({
  kpis: { chiffre_affaires: 0, marge_nette: 0, nombre_ventes: 0 },
  evolution_ventes: [],
  repartition_paiements: [],
  top_produits: [],
  classement_vendeurs: []
})

const hasActiveFilters = computed(() => {
  return !!(
    filters.value.vendeur ||
    filters.value.periode !== 'all' ||
    filters.value.methode_paiement
  )
})

const activeVendorName = computed(() => {
  if (!filters.value.vendeur) return ''
  const v = vendorsList.value.find(u => String(u.id) === String(filters.value.vendeur))
  return v ? `${v.prenom} ${v.nom}` : ''
})

const activePaymentName = computed(() => {
  if (!filters.value.methode_paiement) return ''
  const m = paymentMethods.value.find(item => String(item.id) === String(filters.value.methode_paiement))
  return m ? m.label : ''
})

const activePeriodLabel = computed(() => {
  switch (filters.value.periode) {
    case 'today': return "Aujourd'hui"
    case '7d': return "7 derniers jours"
    case 'month': return "Ce mois-ci"
    case 'custom':
      if (filters.value.date_debut && filters.value.date_fin) {
        return `Du ${filters.value.date_debut} au ${filters.value.date_fin}`
      }
      return "Dates personnalisées"
    default: return ""
  }
})

// Line chart data
const salesChartData = computed(() => {
  const evols = data.value.evolution_ventes || []
  return {
    labels: evols.map(e => e.jour),
    datasets: [
      {
        label: 'Nombre de ventes',
        data: evols.map(e => e.nb_ventes),
        borderColor: '#00d2ff',
        backgroundColor: 'rgba(0, 210, 255, 0.18)',
        tension: 0.35,
        fill: true,
        pointBackgroundColor: '#00e5ff',
        pointRadius: 4,
      }
    ]
  }
})

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }
  },
  scales: {
    x: {
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
      ticks: { color: '#94a3b8', font: { size: 11 } }
    },
    y: {
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
      ticks: { color: '#94a3b8', stepSize: 1, font: { size: 11 } }
    }
  }
}

// Doughnut chart data
const paymentChartData = computed(() => {
  const payments = data.value.repartition_paiements || []
  return {
    labels: payments.map(p => p.methode_paiement__label),
    datasets: [
      {
        data: payments.map(p => p.nb_ventes),
        backgroundColor: [
          '#00d2ff',
          '#10b981',
          '#f59e0b',
          '#0284c7',
          '#ec4899',
        ],
        borderWidth: 0,
      }
    ]
  }
})

const doughnutChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { color: '#e2e8f0', padding: 15, font: { size: 12 } }
    }
  }
}

function setPeriodPreset(preset) {
  filters.value.periode = preset
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
  loadDashboard()
}

function toggleMyDashboard() {
  if (!user.value?.id) return
  if (String(filters.value.vendeur) === String(user.value.id)) {
    filters.value.vendeur = ''
  } else {
    filters.value.vendeur = user.value.id
  }
  loadDashboard()
}

function resetFilters() {
  filters.value = {
    vendeur: '',
    periode: 'all',
    date_debut: '',
    date_fin: '',
    methode_paiement: '',
  }
  loadDashboard()
}

async function fetchDependencies() {
  try {
    const [uRes, mRes] = await Promise.all([
      apiClient.get('/auth/users/').catch(() => ({ data: [] })),
      apiClient.get('/ventes/methodes-paiement/').catch(() => ({ data: [] }))
    ])
    vendorsList.value = uRes.data.results || uRes.data || []
    paymentMethods.value = mRes.data || []
  } catch (err) {
    console.error('Erreur chargement dépendances dashboard:', err)
  }
}

async function loadDashboard() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.vendeur) params.vendeur = filters.value.vendeur
    if (filters.value.date_debut) params.date_debut = filters.value.date_debut
    if (filters.value.date_fin) params.date_fin = filters.value.date_fin
    if (filters.value.methode_paiement) params.methode_paiement = filters.value.methode_paiement

    const res = await apiClient.get('/ventes/dashboard/', { params })
    data.value = res.data
  } catch (err) {
    console.error('Erreur chargement dashboard:', err)
  } finally {
    loading.value = false
  }
}

function formatCurrency(val) {
  return new Intl.NumberFormat('fr-MG').format(val || 0) + ' Ar'
}

onMounted(async () => {
  await fetchDependencies()
  await loadDashboard()
})
</script>

<style scoped>
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* DASHBOARD FILTERS TOOLBAR */
.dashboard-filter-bar {
  padding: 1.15rem 1.35rem;
  background: var(--gradient-card);
  border: 1px solid var(--border-card);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.dash-filters-row {
  display: flex;
  align-items: flex-end;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.filter-group-dash {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.filter-vendor-dash {
  flex: 1;
  min-width: 280px;
}

.vendor-input-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.select-dash-vendor {
  flex: 1;
  font-weight: 600;
  border-color: rgba(0, 210, 255, 0.4);
  background: rgba(6, 13, 25, 0.85);
}

.filter-label-dash {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 0.35rem;
  letter-spacing: 0.04em;
}

.dash-period-presets {
  display: flex;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 0.2rem;
  gap: 0.2rem;
}

.dash-preset-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 0.4rem 0.65rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dash-preset-btn.active {
  background: var(--primary);
  color: #060d19;
  font-weight: 700;
}

.dash-date-inputs {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.date-input-dash {
  width: 130px;
  font-size: 0.78rem;
  padding: 0.4rem 0.5rem;
}

.sep {
  color: var(--text-muted);
}

.select-dash {
  width: 175px;
}

.reset-group {
  margin-left: auto;
}

.dash-active-filters-bar {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-subtle);
  font-size: 0.8rem;
  flex-wrap: wrap;
}

.filter-pill {
  background: rgba(0, 210, 255, 0.08);
  border: 1px solid rgba(0, 210, 255, 0.25);
  color: var(--text-secondary);
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.75rem;
}

.filter-pill strong {
  color: var(--primary);
}

/* KPI GRID */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
}

.kpi-card {
  display: flex;
  flex-direction: column;
}

.kpi-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.kpi-title {
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 600;
}

.kpi-icon-box {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-primary {
  background: var(--primary-light);
  color: var(--primary);
}

.icon-emerald {
  background: var(--emerald-bg);
  color: #34d399;
}

.icon-amber {
  background: var(--amber-bg);
  color: #fbbf24;
}

.kpi-value {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 0.5rem;
}

.kpi-subtext {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1.2fr;
  gap: 1.5rem;
}

@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  display: flex;
  flex-direction: column;
}

.chart-header {
  margin-bottom: 1.25rem;
}

.chart-header h3 {
  font-size: 1.1rem;
}

.chart-container {
  height: 280px;
  position: relative;
}

.doughnut-container {
  height: 240px;
}

.chart-empty {
  height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 1.5rem;
}

@media (max-width: 1024px) {
  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

.section-title-box {
  padding-bottom: 1.25rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid var(--border-subtle);
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.title-with-icon h3 {
  font-size: 1.05rem;
}

.top-products-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.product-item {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  background: rgba(255, 255, 255, 0.02);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}

.prod-rank {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--bg-surface);
  font-size: 0.75rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
}

.prod-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.prod-name {
  font-weight: 700;
  font-size: 0.875rem;
}

.prod-ca {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.prod-sales-badge {
  font-size: 0.75rem;
  font-weight: 700;
  color: #34d399;
}

.rank-pill {
  display: inline-flex;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 800;
}

.rank-1 { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
.rank-2 { background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.4); }
.rank-3 { background: rgba(217, 119, 6, 0.2); color: #f59e0b; border: 1px solid rgba(217, 119, 6, 0.4); }

.points-val {
  font-weight: 800;
  color: var(--amber);
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
