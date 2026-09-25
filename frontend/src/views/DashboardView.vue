<template>
  <div class="dashboard-view">
    <!-- Header with Refresh Button -->
    <div class="dashboard-header">
      <div>
        <h1 class="text-xl font-bold">Vue d'ensemble</h1>
        <p class="text-muted text-sm">Performance des ventes et trésorerie en temps réel</p>
      </div>
      <button @click="loadDashboard" class="btn btn-secondary btn-sm" :disabled="loading">
        <RefreshCw :size="16" :class="{ 'spin-icon': loading }" />
        <span>Actualiser</span>
      </button>
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
          <span class="badge badge-primary">Volume global</span>
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
          <p>Aucune donnée de vente pour le moment.</p>
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
          Aucun produit vendu pour le moment.
        </div>
      </div>

      <!-- Sellers Points Leaderboard -->
      <div class="card">
        <div class="section-title-box">
          <div class="title-with-icon">
            <Award :size="20" class="text-amber" />
            <h3>Classement des Vendeurs (Points)</h3>
          </div>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Rang</th>
                <th>Vendeur</th>
                <th>Rôle</th>
                <th>Ventes</th>
                <th>Points</th>
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
                  <span class="badge badge-primary">{{ vendeur.role }}</span>
                </td>
                <td>{{ vendeur.nombre_ventes }}</td>
                <td>
                  <span class="points-val">{{ vendeur.points }} pts</span>
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
const data = ref({
  kpis: { chiffre_affaires: 0, marge_nette: 0, nombre_ventes: 0 },
  evolution_ventes: [],
  repartition_paiements: [],
  top_produits: [],
  classement_vendeurs: []
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

async function loadDashboard() {
  loading.value = true
  try {
    const res = await apiClient.get('/ventes/dashboard/')
    data.value = res.data
  } catch (err) {
    console.error('Erreur chargement dashboard:', err)
  } finally {
    loading.value = false
  }
}

function formatCurrency(val) {
  return new Intl.NumberFormat('fr-MG').format(val) + ' Ar'
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
}

.kpi-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1.5rem;
}

.kpi-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.kpi-title {
  color: var(--text-secondary);
  font-size: 0.85rem;
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
  font-size: 1.85rem;
  font-weight: 800;
  letter-spacing: -0.03em;
}

.text-emerald {
  color: #10b981;
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.25rem;
}

@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: 320px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  position: relative;
  flex: 1;
  height: 250px;
}

.chart-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 1.25rem;
}

@media (max-width: 1024px) {
  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

.section-title-box {
  margin-bottom: 1.25rem;
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.top-products-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.product-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
}

.prod-rank {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.07);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-secondary);
}

.prod-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.prod-name {
  font-weight: 600;
  font-size: 0.9rem;
}

.prod-ca {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.prod-sales-badge {
  background: var(--primary-light);
  color: #a5b4fc;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.rank-pill {
  font-weight: 800;
  font-size: 0.8rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.rank-1 {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
}

.rank-2 {
  background: rgba(148, 163, 184, 0.2);
  color: #cbd5e1;
}

.rank-3 {
  background: rgba(217, 119, 6, 0.2);
  color: #f59e0b;
}

.points-val {
  font-weight: 700;
  color: #fbbf24;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
