<template>
  <ion-page>
    <ion-header :translucent="true">
      <ion-toolbar class="main-toolbar">
        <div class="toolbar-brand">
          <img src="/src/assets/logo.png" alt="Logo" class="brand-logo" />
          <div class="brand-text">
            <span class="brand-name">Licence Pro</span>
            <span class="brand-sub">Madagascar</span>
          </div>
        </div>
        <ion-buttons slot="end">
          <ion-button @click="loadDashboardData" :disabled="loading">
            <ion-icon :icon="refreshOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" class="dashboard-content">
      <ion-refresher slot="fixed" @ionRefresh="handleRefresh($event)">
        <ion-refresher-content></ion-refresher-content>
      </ion-refresher>

      <!-- Welcome Banner -->
      <div class="welcome-card">
        <div class="welcome-left">
          <p class="greeting-subtitle">Bienvenue sur l'espace mobile</p>
          <h2 class="greeting-name">{{ user?.prenom ? `${user.prenom} ${user.nom || ''}` : 'Équipe Commerciale' }}</h2>
          <div class="user-role-badge">
            <span>{{ user?.role?.label || 'Vendeur Agréé' }}</span>
          </div>
        </div>
        <div class="welcome-points">
          <span class="points-val">{{ user?.solde_points || user?.role?.point || 0 }}</span>
          <span class="points-lbl">Pts Commission</span>
        </div>
      </div>

      <!-- Quick Action Buttons -->
      <div class="quick-actions-grid">
        <button class="action-card primary" @click="isSaleModalOpen = true">
          <div class="action-icon-wrap">
            <ion-icon :icon="cartOutline" />
          </div>
          <span class="action-text">Nouvelle Vente</span>
        </button>

        <button class="action-card secondary" @click="isClientModalOpen = true">
          <div class="action-icon-wrap">
            <ion-icon :icon="personAddOutline" />
          </div>
          <span class="action-text">+ Nouveau Client</span>
        </button>
      </div>

      <!-- KPI Summary Cards -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Chiffre d'Affaires</span>
            <ion-icon :icon="cashOutline" class="kpi-icon teal" />
          </div>
          <div class="kpi-value">{{ formatPrice(kpiData.chiffre_affaires) }}</div>
          <span class="kpi-footer">Ventes encaissées</span>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Marge Nette</span>
            <ion-icon :icon="trendingUpOutline" class="kpi-icon green" />
          </div>
          <div class="kpi-value green">{{ formatPrice(kpiData.marge_nette) }}</div>
          <span class="kpi-footer">Bénéfice estimé</span>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Nombre de Ventes</span>
            <ion-icon :icon="receiptOutline" class="kpi-icon blue" />
          </div>
          <div class="kpi-value">{{ kpiData.nombre_ventes || 0 }}</div>
          <span class="kpi-footer">Transactions conclues</span>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Licences Écoulées</span>
            <ion-icon :icon="cubeOutline" class="kpi-icon purple" />
          </div>
          <div class="kpi-value">{{ kpiData.quantite_totale || 0 }}</div>
          <span class="kpi-footer">Clés d'activation</span>
        </div>
      </div>

      <!-- Top Produits Section -->
      <div class="section-card" v-if="kpiData.top_produits && kpiData.top_produits.length">
        <div class="section-header">
          <h3 class="section-heading">🔥 Top Logiciels Vendus</h3>
        </div>

        <div class="top-products-list">
          <div v-for="(prod, pIdx) in kpiData.top_produits" :key="pIdx" class="top-prod-item">
            <div class="prod-rank">{{ pIdx + 1 }}</div>
            <div class="prod-info">
              <span class="prod-title">{{ prod.produit__nom || prod.nom }}</span>
              <span class="prod-meta">{{ prod.total_quantite }} licence(s) vendue(s)</span>
            </div>
            <div class="prod-rev">{{ formatPrice(prod.total_ca) }}</div>
          </div>
        </div>
      </div>

      <!-- Dernières Ventes -->
      <div class="section-card">
        <div class="section-header">
          <h3 class="section-heading">🕒 Ventes Récentes</h3>
          <router-link to="/tabs/ventes" class="link-more">Voir tout</router-link>
        </div>

        <div v-if="loading" class="empty-state">
          <span>Chargement des données...</span>
        </div>

        <div v-else-if="recentSales.length === 0" class="empty-state">
          <span>Aucune vente enregistrée pour le moment.</span>
        </div>

        <div v-else class="recent-sales-list">
          <div v-for="sale in recentSales" :key="sale.id" class="recent-sale-row">
            <div class="sale-client-col">
              <span class="sale-client-nom">{{ sale.client?.nom || 'Client Anonyme' }}</span>
              <span class="sale-date">{{ formatDate(sale.date) }} • {{ sale.methode_paiement?.label || 'Direct' }}</span>
            </div>
            <div class="sale-amount-col">
              <span class="sale-price">{{ formatPrice(sale.total) }}</span>
              <span class="sale-badge">{{ sale.commandes?.length || 1 }} art.</span>
            </div>
          </div>
        </div>
      </div>
    </ion-content>

    <!-- Modals -->
    <SaleModal :is-open="isSaleModalOpen" @close="isSaleModalOpen = false" @sale-created="onSaleCreated" />
    <ClientModal :is-open="isClientModalOpen" @close="isClientModalOpen = false" @saved="loadDashboardData" />
  </ion-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonButtons,
  IonButton,
  IonIcon,
  IonContent,
  IonRefresher,
  IonRefresherContent,
} from '@ionic/vue'
import {
  refreshOutline,
  cartOutline,
  personAddOutline,
  cashOutline,
  trendingUpOutline,
  receiptOutline,
  cubeOutline,
} from 'ionicons/icons'
import apiClient from '../api/client'
import { useAuth } from '../composables/useAuth'
import SaleModal from '../components/SaleModal.vue'
import ClientModal from '../components/ClientModal.vue'

const { user } = useAuth()

const loading = ref(false)
const kpiData = ref({
  chiffre_affaires: 0,
  marge_nette: 0,
  nombre_ventes: 0,
  quantite_totale: 0,
  top_produits: [],
})
const recentSales = ref([])

const isSaleModalOpen = ref(false)
const isClientModalOpen = ref(false)

function formatPrice(val) {
  if (!val && val !== 0) return '0 Ar'
  return Math.round(val).toLocaleString('fr-FR') + ' Ar'
}

function formatDate(isoStr) {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' }) + ' ' + d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

async function loadDashboardData() {
  loading.value = true
  try {
    const [dashRes, salesRes] = await Promise.all([
      apiClient.get('/ventes/dashboard/'),
      apiClient.get('/ventes/?limit=5'),
    ])

    kpiData.value = dashRes.data || {}
    recentSales.value = (salesRes.data.results || salesRes.data || []).slice(0, 5)
  } catch (err) {
    console.error('Erreur chargement dashboard:', err)
  } finally {
    loading.value = false
  }
}

async function handleRefresh(event) {
  await loadDashboardData()
  event.target.complete()
}

function onSaleCreated() {
  loadDashboardData()
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.main-toolbar {
  --background: #0B1120;
  --color: #FFFFFF;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.toolbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-left: 12px;
}

.brand-logo {
  height: 32px;
  width: auto;
  object-fit: contain;
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-weight: 800;
  font-size: 0.95rem;
  letter-spacing: -0.02em;
  color: #FFFFFF;
}

.brand-sub {
  font-size: 0.65rem;
  color: #14B8A6;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.dashboard-content {
  --background: #0B1120;
  --color: #F8FAFC;
  padding: 16px;
}

.welcome-card {
  margin: 16px;
  background: linear-gradient(135deg, #151F32 0%, #1E293B 100%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.greeting-subtitle {
  font-size: 0.72rem;
  color: #94A3B8;
  margin: 0;
}

.greeting-name {
  font-size: 1.15rem;
  font-weight: 700;
  color: #FFFFFF;
  margin: 2px 0 6px 0;
}

.user-role-badge {
  display: inline-block;
  background: rgba(13, 148, 136, 0.2);
  color: #5EEAD4;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
}

.welcome-points {
  text-align: right;
  display: flex;
  flex-direction: column;
  background: rgba(2, 132, 199, 0.15);
  border: 1px solid rgba(56, 189, 248, 0.3);
  padding: 8px 12px;
  border-radius: 12px;
}

.points-val {
  font-size: 1.3rem;
  font-weight: 800;
  color: #38BDF8;
}

.points-lbl {
  font-size: 0.65rem;
  color: #94A3B8;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 0 16px 16px 16px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 14px;
  border: none;
  cursor: pointer;
}

.action-card.primary {
  background: linear-gradient(135deg, #0D9488 0%, #0F766E 100%);
  color: #FFFFFF;
}

.action-card.secondary {
  background: #1E293B;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #F8FAFC;
}

.action-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.action-text {
  font-size: 0.85rem;
  font-weight: 700;
}

.kpi-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin: 0 16px 16px 16px;
}

.kpi-card {
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 12px;
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.kpi-label {
  font-size: 0.72rem;
  color: #94A3B8;
  font-weight: 500;
}

.kpi-icon {
  font-size: 16px;
}

.kpi-icon.teal { color: #14B8A6; }
.kpi-icon.green { color: #10B981; }
.kpi-icon.blue { color: #38BDF8; }
.kpi-icon.purple { color: #A855F7; }

.kpi-value {
  font-size: 1.05rem;
  font-weight: 800;
  color: #FFFFFF;
  margin-bottom: 2px;
}

.kpi-value.green {
  color: #34D399;
}

.kpi-footer {
  font-size: 0.65rem;
  color: #64748B;
}

.section-card {
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 14px;
  margin: 0 16px 16px 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-heading {
  font-size: 0.9rem;
  font-weight: 700;
  color: #F8FAFC;
  margin: 0;
}

.link-more {
  color: #38BDF8;
  font-size: 0.75rem;
  text-decoration: none;
  font-weight: 600;
}

.top-products-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.top-prod-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  background: #0B1120;
  border-radius: 10px;
}

.prod-rank {
  font-size: 0.8rem;
  font-weight: 800;
  color: #5EEAD4;
  width: 20px;
}

.prod-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.prod-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: #FFFFFF;
}

.prod-meta {
  font-size: 0.7rem;
  color: #94A3B8;
}

.prod-rev {
  font-size: 0.82rem;
  font-weight: 700;
  color: #10B981;
}

.recent-sales-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recent-sale-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  background: #0B1120;
  border-radius: 10px;
}

.sale-client-nom {
  display: block;
  font-size: 0.84rem;
  font-weight: 600;
  color: #FFFFFF;
}

.sale-date {
  font-size: 0.7rem;
  color: #94A3B8;
}

.sale-amount-col {
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.sale-price {
  font-size: 0.88rem;
  font-weight: 700;
  color: #34D399;
}

.sale-badge {
  font-size: 0.65rem;
  background: #1E293B;
  color: #94A3B8;
  padding: 1px 6px;
  border-radius: 4px;
}

.empty-state {
  padding: 20px;
  text-align: center;
  font-size: 0.82rem;
  color: #64748B;
}
</style>
