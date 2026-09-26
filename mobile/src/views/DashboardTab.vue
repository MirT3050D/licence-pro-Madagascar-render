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

      <!-- Filtres Dashboard Mobile Multi-Critères -->
      <div class="dash-filters-card">
        <div class="filters-card-header">
          <div class="filter-header-left">
            <ion-icon :icon="funnelOutline" class="filter-main-icon" />
            <span class="filter-main-title">Filtre Multi-Critères</span>
            <span v-if="hasActiveFilters" class="active-badge">
              {{ activeFilterCount }} actif{{ activeFilterCount > 1 ? 's' : '' }}
            </span>
          </div>
          <button v-if="hasActiveFilters" @click="resetFilters" class="btn-reset-filters">
            <ion-icon :icon="closeCircleOutline" />
            <span>Effacer tout</span>
          </button>
        </div>

        <!-- 1. Périodes rapides -->
        <div class="dash-period-pills">
          <button
            v-for="p in periodOptions"
            :key="p.id"
            :class="['period-pill', activePeriod === p.id ? 'active' : '']"
            @click="setPeriod(p.id)"
          >
            {{ p.label }}
          </button>
        </div>

        <!-- Dates personnalisées si mode custom -->
        <div v-if="activePeriod === 'custom'" class="custom-dates-box">
          <div class="custom-date-item">
            <span class="custom-date-lbl">Du :</span>
            <input type="date" v-model="customDateDebut" @change="loadDashboardData" class="date-picker-input" />
          </div>
          <div class="custom-date-item">
            <span class="custom-date-lbl">Au :</span>
            <input type="date" v-model="customDateFin" @change="loadDashboardData" class="date-picker-input" />
          </div>
        </div>

        <!-- 2. Multi-Sélection Provenances (ex: Facebook ET WhatsApp simultanément) -->
        <div class="filter-section-group">
          <div class="section-title-row">
            <span class="section-label">Provenances</span>
            <span class="section-hint">
              {{ selectedProvenances.length === 0 ? 'Toutes' : `${selectedProvenances.length} sélectionnée(s)` }}
            </span>
          </div>
          <div class="chips-scroll-row">
            <button
              type="button"
              :class="['chip-btn', selectedProvenances.length === 0 ? 'active-all' : '']"
              @click="clearProvenances"
            >
              🌐 Toutes
            </button>
            <button
              v-for="prov in provenances"
              :key="prov.id"
              type="button"
              :class="[
                'chip-btn',
                selectedProvenances.includes(prov.id) ? 'active' : '',
                getProvenanceStyleClass(prov.label)
              ]"
              @click="toggleProvenance(prov.id)"
            >
              <ion-icon
                v-if="selectedProvenances.includes(prov.id)"
                :icon="checkmarkCircle"
                class="chip-check-icon"
              />
              <span class="chip-dot" v-else></span>
              <span>{{ prov.label }}</span>
            </button>
          </div>
        </div>

        <!-- 3. Multi-Sélection Modes de Règlement -->
        <div class="filter-section-group">
          <div class="section-title-row">
            <span class="section-label">Modes de paiement</span>
            <span class="section-hint">
              {{ selectedPaymentMethods.length === 0 ? 'Tous' : `${selectedPaymentMethods.length} sélectionné(s)` }}
            </span>
          </div>
          <div class="chips-scroll-row">
            <button
              type="button"
              :class="['chip-btn', selectedPaymentMethods.length === 0 ? 'active-all' : '']"
              @click="clearPaymentMethods"
            >
              💳 Tous
            </button>
            <button
              v-for="pm in paymentMethods"
              :key="pm.id"
              type="button"
              :class="['chip-btn', selectedPaymentMethods.includes(pm.id) ? 'active' : '']"
              @click="togglePaymentMethod(pm.id)"
            >
              <ion-icon
                v-if="selectedPaymentMethods.includes(pm.id)"
                :icon="checkmarkCircle"
                class="chip-check-icon"
              />
              <span class="chip-dot" v-else></span>
              <span>{{ pm.label }}</span>
            </button>
          </div>
        </div>

        <!-- 4. Bouton pour déplier Autres critères -->
        <div class="advanced-toggle-row">
          <button
            type="button"
            class="btn-toggle-advanced"
            @click="isMoreFiltersOpen = !isMoreFiltersOpen"
          >
            <div class="toggle-adv-left">
              <ion-icon :icon="optionsOutline" />
              <span>Plus de critères (Logiciels, Vendeurs, Montant...)</span>
            </div>
            <div class="toggle-adv-right">
              <span v-if="advancedCriteriaCount > 0" class="adv-badge">{{ advancedCriteriaCount }}</span>
              <ion-icon :icon="isMoreFiltersOpen ? chevronUpOutline : chevronDownOutline" />
            </div>
          </button>
        </div>

        <!-- Critères avancés (Logiciels, Vendeurs, Clients, Tranche de montant) -->
        <div v-show="isMoreFiltersOpen" class="advanced-filters-body">
          <!-- Logiciels / Produits Multi-Sélection -->
          <div class="adv-filter-block">
            <div class="section-title-row">
              <span class="section-label">Logiciels / Produits</span>
              <span class="section-hint">
                {{ selectedProducts.length === 0 ? 'Tous' : `${selectedProducts.length} sélectionné(s)` }}
              </span>
            </div>
            <div class="chips-scroll-row">
              <button
                type="button"
                :class="['chip-btn', selectedProducts.length === 0 ? 'active-all' : '']"
                @click="selectedProducts = []; loadDashboardData()"
              >
                📦 Tous logiciels
              </button>
              <button
                v-for="prod in productsList"
                :key="prod.id"
                type="button"
                :class="['chip-btn', selectedProducts.includes(prod.id) ? 'active' : '']"
                @click="toggleProduct(prod.id)"
              >
                <ion-icon
                  v-if="selectedProducts.includes(prod.id)"
                  :icon="checkmarkCircle"
                  class="chip-check-icon"
                />
                <span>{{ prod.nom }}</span>
              </button>
            </div>
          </div>

          <!-- Vendeurs Multi-Sélection (SuperAdmin) -->
          <div v-if="isSuperAdmin" class="adv-filter-block">
            <div class="section-title-row">
              <span class="section-label">Vendeurs & Collaborateurs</span>
              <button
                v-if="user?.id"
                type="button"
                @click="toggleMySales"
                :class="['btn-my-sales-mini', selectedVendors.includes(Number(user.id)) && selectedVendors.length === 1 ? 'active' : '']"
              >
                <ion-icon :icon="flashOutline" />
                <span>Mes ventes</span>
              </button>
            </div>
            <div class="chips-scroll-row">
              <button
                type="button"
                :class="['chip-btn', selectedVendors.length === 0 ? 'active-all' : '']"
                @click="selectedVendors = []; loadDashboardData()"
              >
                👥 Tous vendeurs
              </button>
              <button
                v-for="v in vendorsList"
                :key="v.id"
                type="button"
                :class="['chip-btn', selectedVendors.includes(v.id) ? 'active' : '']"
                @click="toggleVendor(v.id)"
              >
                <ion-icon
                  v-if="selectedVendors.includes(v.id)"
                  :icon="checkmarkCircle"
                  class="chip-check-icon"
                />
                <span>{{ v.prenom }} {{ v.nom }}</span>
              </button>
            </div>
          </div>

          <!-- Client & Tranche de montant -->
          <div class="adv-filter-grid-2">
            <div class="adv-input-col">
              <label class="adv-lbl">Client spécifique</label>
              <select v-model="selectedClient" @change="loadDashboardData" class="dash-filter-select">
                <option value="">👤 Tous les clients</option>
                <option v-for="c in clients" :key="c.id" :value="c.id">{{ c.nom }}</option>
              </select>
            </div>

            <div class="adv-input-col">
              <label class="adv-lbl">Montant min (Ar)</label>
              <input
                type="number"
                v-model="montantMin"
                @change="loadDashboardData"
                placeholder="Ex: 50000"
                class="dash-filter-input"
              />
            </div>
          </div>
        </div>

        <!-- Tags récapitulatifs des filtres actifs -->
        <div v-if="activeFilterTags.length > 0" class="active-tags-container">
          <div class="active-tags-header">Filtres actifs :</div>
          <div class="active-tags-list">
            <span
              v-for="tag in activeFilterTags"
              :key="tag.id"
              class="active-tag-chip"
              @click="tag.remove()"
            >
              <span>{{ tag.label }}</span>
              <ion-icon :icon="closeOutline" class="tag-close-icon" />
            </span>
          </div>
        </div>
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

        <!-- Commission Media Buyer KPI -->
        <div class="kpi-card kpi-card-mb-mobile">
          <div class="kpi-header">
            <span class="kpi-label">Com. Media Buyer</span>
            <ion-icon :icon="megaphoneOutline" class="kpi-icon orange" />
          </div>
          <div class="kpi-value orange">{{ formatPrice(kpiData.commission_media_buyer?.commission_due || 0) }}</div>
          <span class="kpi-footer">
            {{ kpiData.commission_media_buyer?.statut?.seuil_atteint ? '✓ Débloqué (100% amorti)' : `⏳ Amorti : ${kpiData.commission_media_buyer?.statut?.progression_recouvrement || 0}%` }}
          </span>
        </div>
      </div>

      <!-- Section Commission Media Buyer Mobile -->
      <div class="section-card mb-mobile-card" v-if="kpiData.commission_media_buyer">
        <div class="section-header">
          <div class="mb-header-left">
            <ion-icon :icon="megaphoneOutline" class="text-orange" />
            <h3 class="section-heading">Commission Media Buyer</h3>
          </div>
          <button v-if="isSuperAdmin" @click="openConfigModal" class="btn-config-icon" title="Paramétrer les règles">
            <ion-icon :icon="settingsOutline" />
          </button>
        </div>

        <!-- Coût pub status banner -->
        <div class="mb-spend-mobile" :class="kpiData.commission_media_buyer.statut?.seuil_atteint ? 'rentabilise' : 'en-cours'">
          <div class="spend-header">
            <span class="spend-lbl">Coût Pub : <strong>{{ formatPrice(kpiData.commission_media_buyer.statut?.cout_pub || 0) }}</strong></span>
            <span class="spend-badge" :class="kpiData.commission_media_buyer.statut?.seuil_atteint ? 'badge-rentabilise' : 'badge-en-cours'">
              {{ kpiData.commission_media_buyer.statut?.seuil_atteint ? '✓ Amorti à 100%' : `${kpiData.commission_media_buyer.statut?.progression_recouvrement || 0}% amorti` }}
            </span>
          </div>
          <div class="spend-bar-track">
            <div class="spend-bar-fill" :style="{ width: `${kpiData.commission_media_buyer.statut?.progression_recouvrement || 0}%` }"></div>
          </div>
          <div class="spend-details">
            <span>Généré : <strong>{{ formatPrice(kpiData.commission_media_buyer.statut?.recouvrement_actuel || 0) }}</strong></span>
            <span v-if="!kpiData.commission_media_buyer.statut?.seuil_atteint" class="text-amber">
              Reste : <strong>{{ formatPrice(kpiData.commission_media_buyer.statut?.reste_a_recouvrir || 0) }}</strong>
            </span>
            <span v-else class="text-green">✓ Seuil atteint</span>
          </div>
        </div>

        <!-- Info message if not reached -->
        <div v-if="!kpiData.commission_media_buyer.statut?.seuil_atteint" class="mb-notice-mobile">
          <ion-icon :icon="timeOutline" />
          <span>Compteur bloqué à 0 Ar. La commission démarrera dès remboursement total du coût publicitaire de <strong>{{ formatPrice(kpiData.commission_media_buyer.statut?.cout_pub || 0) }}</strong>.</span>
        </div>

        <!-- 2 Rules Breakdown -->
        <div class="mb-rules-grid-mobile">
          <div class="rule-box-mobile rule-box-blue">
            <div class="rule-box-top">
              <span class="rule-pill-mobile blue">Marge &gt; {{ kpiData.commission_media_buyer.config?.seuil_marge }}%</span>
              <span class="rule-rate">{{ kpiData.commission_media_buyer.config?.regle_ca }}% CA</span>
            </div>
            <div class="rule-box-val">+{{ formatPrice(kpiData.commission_media_buyer.details?.marge_haute?.commission || 0) }}</div>
            <div class="rule-box-sub">sur CA excédentaire : {{ formatPrice(kpiData.commission_media_buyer.details?.marge_haute?.base_ca || 0) }}</div>
          </div>

          <div class="rule-box-mobile rule-box-green">
            <div class="rule-box-top">
              <span class="rule-pill-mobile green">Marge &le; {{ kpiData.commission_media_buyer.config?.seuil_marge }}%</span>
              <span class="rule-rate">{{ kpiData.commission_media_buyer.config?.regle_benefice }}% Marge</span>
            </div>
            <div class="rule-box-val text-green">+{{ formatPrice(kpiData.commission_media_buyer.details?.marge_basse?.commission || 0) }}</div>
            <div class="rule-box-sub">sur Bénéf. excédentaire : {{ formatPrice(kpiData.commission_media_buyer.details?.marge_basse?.base_benefice || 0) }}</div>
          </div>
        </div>

        <div class="mb-prov-list-mobile">
          <span class="prov-label-mini">Provenances éligibles :</span>
          <span v-for="p in kpiData.commission_media_buyer.config?.provenances" :key="p.id" class="prov-badge-mini">
            {{ p.label }}
          </span>
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
          <span>Aucune vente ne correspond aux critères.</span>
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

    <!-- Modal Paramètres Commission Media Buyer (Admin uniquement) -->
    <ion-modal :is-open="isConfigModalOpen && isSuperAdmin" @didDismiss="isConfigModalOpen = false" :initial-breakpoint="0.9" :breakpoints="[0, 0.9, 1]">
      <ion-header>
        <ion-toolbar class="modal-toolbar">
          <ion-title>Règles Commission MB</ion-title>
          <ion-buttons slot="end">
            <ion-button @click="isConfigModalOpen = false">
              <ion-icon :icon="closeOutline" />
            </ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>
      <ion-content class="ion-padding modal-config-content">
        <form @submit.prevent="saveCommissionConfig">
          <div class="m-form-group">
            <label class="m-form-label">Coût publicité (Ar)</label>
            <input
              v-model.number="configForm.cout_pub"
              type="number"
              step="any"
              min="0"
              class="m-form-input"
              placeholder="Ex: 500000"
              required
            />
            <span class="m-form-help">Le compteur démarre uniquement quand ce montant est amorti.</span>
          </div>

          <div class="m-form-row">
            <div class="m-form-group">
              <label class="m-form-label">Com. CA (%) [&gt; seuil]</label>
              <input
                v-model.number="configForm.regle_ca"
                type="number"
                step="0.1"
                min="0"
                max="100"
                class="m-form-input"
                required
              />
            </div>
            <div class="m-form-group">
              <label class="m-form-label">Com. Marge (%) [&le; seuil]</label>
              <input
                v-model.number="configForm.regle_benefice"
                type="number"
                step="0.1"
                min="0"
                max="100"
                class="m-form-input"
                required
              />
            </div>
          </div>

          <div class="m-form-row">
            <div class="m-form-group">
              <label class="m-form-label">Seuil marge (%)</label>
              <input
                v-model.number="configForm.seuil_marge"
                type="number"
                step="0.1"
                min="0"
                max="100"
                class="m-form-input"
                required
              />
            </div>
            <div class="m-form-group">
              <label class="m-form-label">Base amortissement</label>
              <select v-model="configForm.base_recouvrement" class="m-form-select">
                <option value="benefice">Bénéfice brut</option>
                <option value="ca">Chiffre d'affaires</option>
              </select>
            </div>
          </div>

          <div class="m-form-group">
            <label class="m-form-label">Provenances éligibles</label>
            <div class="m-prov-checkboxes">
              <label v-for="prov in provenances" :key="prov.id" class="m-prov-checkbox-label">
                <input type="checkbox" :value="prov.id" v-model="configForm.provenances" />
                <span>{{ prov.label }}</span>
              </label>
            </div>
          </div>

          <div v-if="configError" class="m-alert-error">
            {{ configError }}
          </div>

          <button type="submit" class="btn-save-config" :disabled="savingConfig">
            <span v-if="savingConfig">Enregistrement...</span>
            <span v-else>Enregistrer les règles</span>
          </button>
        </form>
      </ion-content>
    </ion-modal>
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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
  IonModal,
  IonTitle,
  onIonViewWillEnter,
} from '@ionic/vue'
import {
  refreshOutline,
  cartOutline,
  personAddOutline,
  cashOutline,
  trendingUpOutline,
  receiptOutline,
  cubeOutline,
  funnelOutline,
  flashOutline,
  closeCircleOutline,
  megaphoneOutline,
  settingsOutline,
  timeOutline,
  closeOutline,
  checkmarkCircle,
  optionsOutline,
  chevronDownOutline,
  chevronUpOutline,
} from 'ionicons/icons'
import apiClient from '../api/client'
import { useAuth } from '../composables/useAuth'
import SaleModal from '../components/SaleModal.vue'
import ClientModal from '../components/ClientModal.vue'

const { user, isSuperAdmin } = useAuth()

const loading = ref(false)
const kpiData = ref({
  chiffre_affaires: 0,
  marge_nette: 0,
  nombre_ventes: 0,
  quantite_totale: 0,
  top_produits: [],
})
const recentSales = ref([])
const clients = ref([])
const provenances = ref([])
const paymentMethods = ref([])
const vendorsList = ref([])
const productsList = ref([])

// Multi-criteria filter states:
const selectedProvenances = ref([])
const selectedPaymentMethods = ref([])
const selectedVendors = ref([])
const selectedProducts = ref([])
const selectedClient = ref('')
const montantMin = ref('')
const montantMax = ref('')
const activePeriod = ref('all')
const customDateDebut = ref('')
const customDateFin = ref('')

const isMoreFiltersOpen = ref(false)

const periodOptions = [
  { id: 'all', label: 'Tout' },
  { id: 'today', label: "Aujourd'hui" },
  { id: '7d', label: '7 jours' },
  { id: 'month', label: 'Ce mois' },
  { id: 'custom', label: 'Dates...' },
]

const isSaleModalOpen = ref(false)
const isClientModalOpen = ref(false)

function getProvenanceStyleClass(label) {
  if (!label) return ''
  const l = label.toLowerCase()
  if (l.includes('facebook')) return 'chip-facebook'
  if (l.includes('whatsapp')) return 'chip-whatsapp'
  if (l.includes('tiktok')) return 'chip-tiktok'
  return ''
}

function toggleProvenance(id) {
  const numId = Number(id)
  const idx = selectedProvenances.value.indexOf(numId)
  if (idx > -1) {
    selectedProvenances.value.splice(idx, 1)
  } else {
    selectedProvenances.value.push(numId)
  }
  loadDashboardData()
}

function clearProvenances() {
  selectedProvenances.value = []
  loadDashboardData()
}

function togglePaymentMethod(id) {
  const numId = Number(id)
  const idx = selectedPaymentMethods.value.indexOf(numId)
  if (idx > -1) {
    selectedPaymentMethods.value.splice(idx, 1)
  } else {
    selectedPaymentMethods.value.push(numId)
  }
  loadDashboardData()
}

function clearPaymentMethods() {
  selectedPaymentMethods.value = []
  loadDashboardData()
}

function toggleVendor(id) {
  const numId = Number(id)
  const idx = selectedVendors.value.indexOf(numId)
  if (idx > -1) {
    selectedVendors.value.splice(idx, 1)
  } else {
    selectedVendors.value.push(numId)
  }
  loadDashboardData()
}

function toggleMySales() {
  if (!user.value?.id) return
  const myId = Number(user.value.id)
  if (selectedVendors.value.includes(myId) && selectedVendors.value.length === 1) {
    selectedVendors.value = []
  } else {
    selectedVendors.value = [myId]
  }
  loadDashboardData()
}

function toggleProduct(id) {
  const numId = Number(id)
  const idx = selectedProducts.value.indexOf(numId)
  if (idx > -1) {
    selectedProducts.value.splice(idx, 1)
  } else {
    selectedProducts.value.push(numId)
  }
  loadDashboardData()
}

function setPeriod(pId) {
  activePeriod.value = pId
  loadDashboardData()
}

const advancedCriteriaCount = computed(() => {
  let count = 0
  if (selectedProducts.value.length > 0) count += selectedProducts.value.length
  if (selectedVendors.value.length > 0) count += selectedVendors.value.length
  if (selectedClient.value) count += 1
  if (montantMin.value || montantMax.value) count += 1
  return count
})

const activeFilterCount = computed(() => {
  let count = 0
  if (selectedProvenances.value.length > 0) count += selectedProvenances.value.length
  if (selectedPaymentMethods.value.length > 0) count += selectedPaymentMethods.value.length
  if (selectedVendors.value.length > 0) count += selectedVendors.value.length
  if (selectedProducts.value.length > 0) count += selectedProducts.value.length
  if (selectedClient.value) count += 1
  if (montantMin.value || montantMax.value) count += 1
  if (activePeriod.value !== 'all' || customDateDebut.value || customDateFin.value) count += 1
  return count
})

const hasActiveFilters = computed(() => activeFilterCount.value > 0)

const activeFilterTags = computed(() => {
  const tags = []
  for (const provId of selectedProvenances.value) {
    const prov = provenances.value.find((p) => p.id === provId)
    if (prov) {
      tags.push({
        id: `prov-${provId}`,
        label: prov.label,
        remove: () => toggleProvenance(provId),
      })
    }
  }
  for (const pmId of selectedPaymentMethods.value) {
    const pm = paymentMethods.value.find((m) => m.id === pmId)
    if (pm) {
      tags.push({
        id: `pm-${pmId}`,
        label: pm.label,
        remove: () => togglePaymentMethod(pmId),
      })
    }
  }
  for (const vId of selectedVendors.value) {
    const v = vendorsList.value.find((u) => u.id === vId)
    if (v) {
      tags.push({
        id: `v-${vId}`,
        label: `${v.prenom} ${v.nom}`,
        remove: () => toggleVendor(vId),
      })
    }
  }
  for (const pId of selectedProducts.value) {
    const p = productsList.value.find((prod) => prod.id === pId)
    if (p) {
      tags.push({
        id: `prod-${pId}`,
        label: p.nom,
        remove: () => toggleProduct(pId),
      })
    }
  }
  if (selectedClient.value) {
    const c = clients.value.find((cli) => cli.id === Number(selectedClient.value))
    tags.push({
      id: 'client',
      label: `Client: ${c ? c.nom : selectedClient.value}`,
      remove: () => {
        selectedClient.value = ''
        loadDashboardData()
      },
    })
  }
  if (montantMin.value || montantMax.value) {
    let lbl = 'Montant: '
    if (montantMin.value && montantMax.value) lbl += `${montantMin.value} - ${montantMax.value} Ar`
    else if (montantMin.value) lbl += `≥ ${montantMin.value} Ar`
    else lbl += `≤ ${montantMax.value} Ar`
    tags.push({
      id: 'montant',
      label: lbl,
      remove: () => {
        montantMin.value = ''
        montantMax.value = ''
        loadDashboardData()
      },
    })
  }
  return tags
})

function resetFilters() {
  selectedProvenances.value = []
  selectedPaymentMethods.value = []
  selectedVendors.value = []
  selectedProducts.value = []
  selectedClient.value = ''
  montantMin.value = ''
  montantMax.value = ''
  activePeriod.value = 'all'
  customDateDebut.value = ''
  customDateFin.value = ''
  loadDashboardData()
}

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

async function loadFilterDependencies() {
  try {
    const [cRes, pRes, mRes, uRes, prodRes] = await Promise.all([
      apiClient.get('/clients/').catch(() => ({ data: [] })),
      apiClient.get('/clients/provenances/').catch(() => ({ data: [] })),
      apiClient.get('/ventes/methodes-paiement/').catch(() => ({ data: [] })),
      apiClient.get('/auth/users/').catch(() => ({ data: [] })),
      apiClient.get('/produits/').catch(() => ({ data: [] })),
    ])
    clients.value = cRes.data.results || cRes.data || []
    provenances.value = pRes.data.results || pRes.data || []
    paymentMethods.value = (mRes.data.results || mRes.data || []).filter((m) => m.is_active !== false)
    vendorsList.value = uRes.data.results || uRes.data || []
    productsList.value = prodRes.data.results || prodRes.data || []
  } catch (err) {
    console.error('Erreur dépendances dashboard mobile:', err)
  }
}

async function loadDashboardData() {
  loading.value = true
  try {
    const params = {}
    if (selectedProvenances.value.length > 0) {
      params.provenances = selectedProvenances.value.join(',')
    }
    if (selectedPaymentMethods.value.length > 0) {
      params.methodes_paiement = selectedPaymentMethods.value.join(',')
    }
    if (selectedVendors.value.length > 0) {
      params.vendeurs = selectedVendors.value.join(',')
    }
    if (selectedProducts.value.length > 0) {
      params.produits = selectedProducts.value.join(',')
    }
    if (selectedClient.value) {
      params.client = selectedClient.value
    }
    if (montantMin.value) {
      params.montant_min = montantMin.value
    }
    if (montantMax.value) {
      params.montant_max = montantMax.value
    }

    const today = new Date()
    const pad = (n) => String(n).padStart(2, '0')
    const formatYMD = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`

    if (activePeriod.value === 'today') {
      const ymd = formatYMD(today)
      params.date_debut = ymd
      params.date_fin = ymd
    } else if (activePeriod.value === '7d') {
      const past = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
      params.date_debut = formatYMD(past)
      params.date_fin = formatYMD(today)
    } else if (activePeriod.value === 'month') {
      const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
      params.date_debut = formatYMD(firstDay)
      params.date_fin = formatYMD(today)
    } else if (activePeriod.value === 'custom') {
      if (customDateDebut.value) params.date_debut = customDateDebut.value
      if (customDateFin.value) params.date_fin = customDateFin.value
    }

    const salesParams = { ...params }

    const [dashRes, salesRes] = await Promise.all([
      apiClient.get('/ventes/dashboard/', { params }),
      apiClient.get('/ventes/', { params: salesParams }).catch(() => ({ data: [] })),
    ])

    const resData = dashRes.data || {}
    const kpis = resData.kpis || resData
    kpiData.value = {
      chiffre_affaires: kpis.chiffre_affaires ?? resData.chiffre_affaires ?? 0,
      marge_nette: kpis.marge_nette ?? resData.marge_nette ?? 0,
      nombre_ventes: kpis.nombre_ventes ?? resData.nombre_ventes ?? 0,
      quantite_totale: kpis.quantite_totale ?? resData.quantite_totale ?? 0,
      commission_media_buyer: resData.commission_media_buyer || null,
      top_produits: resData.top_produits || [],
    }
    recentSales.value = (salesRes.data.results || salesRes.data || []).slice(0, 5)
  } catch (err) {
    console.error('Erreur chargement dashboard:', err)
  } finally {
    loading.value = false
  }
}

// Media Buyer Configuration Settings (Mobile)
const isConfigModalOpen = ref(false)
const savingConfig = ref(false)
const configError = ref('')
const configForm = ref({
  cout_pub: 0,
  regle_ca: 10,
  regle_benefice: 30,
  seuil_marge: 40,
  base_recouvrement: 'benefice',
  provenances: []
})

function openConfigModal() {
  if (!isSuperAdmin.value) return
  const current = kpiData.value?.commission_media_buyer?.config
  if (current) {
    configForm.value = {
      cout_pub: current.cout_pub ?? 0,
      regle_ca: current.regle_ca ?? 10,
      regle_benefice: current.regle_benefice ?? 30,
      seuil_marge: current.seuil_marge ?? 40,
      base_recouvrement: current.base_recouvrement ?? 'benefice',
      provenances: (current.provenances || []).map(p => p.id)
    }
  } else {
    configForm.value = {
      cout_pub: 0,
      regle_ca: 10,
      regle_benefice: 30,
      seuil_marge: 40,
      base_recouvrement: 'benefice',
      provenances: provenances.value
        .filter(p => /facebook|whatsapp/i.test(p.label))
        .map(p => p.id)
    }
  }
  configError.value = ''
  isConfigModalOpen.value = true
}

async function saveCommissionConfig() {
  if (!isSuperAdmin.value) return
  savingConfig.value = true
  configError.value = ''
  try {
    await apiClient.put('/ventes/commission-media-buyer/', configForm.value)
    isConfigModalOpen.value = false
    await loadDashboardData()
  } catch (err) {
    console.error('Erreur sauvegarde config commission:', err)
    configError.value = err.response?.data?.error || err.message || 'Erreur lors de la sauvegarde.'
  } finally {
    savingConfig.value = false
  }
}

async function handleRefresh(event) {
  await Promise.all([loadFilterDependencies(), loadDashboardData()])
  event.target.complete()
}

function onSaleCreated() {
  loadDashboardData()
}

onMounted(() => {
  loadFilterDependencies()
  loadDashboardData()
})

onIonViewWillEnter(() => {
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
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #14B8A6;
  text-transform: uppercase;
}

.dashboard-content {
  --background: #0B1120;
  --color: #F8FAFC;
}

.welcome-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  margin: 12px 16px;
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
}

.greeting-subtitle {
  font-size: 0.75rem;
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
  margin: 0 16px 14px 16px;
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

/* FILTRES DU DASHBOARD */
.dash-filters-card {
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 14px;
  margin: 0 16px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.filters-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2px;
}

.filter-header-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.filter-main-icon {
  color: #38BDF8;
  font-size: 16px;
}

.filter-main-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: #E2E8F0;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.active-badge {
  background: rgba(16, 185, 129, 0.2);
  color: #34D399;
  font-size: 0.65rem;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 700;
}

.btn-reset-filters {
  background: transparent;
  color: #F87171;
  border: none;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
  cursor: pointer;
}

.dash-period-pills {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding-bottom: 2px;
}

.period-pill {
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #94A3B8;
  padding: 6px 14px;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
}

.period-pill.active {
  background: #0D9488;
  color: #FFFFFF;
  border-color: #0D9488;
}

.custom-dates-box {
  display: flex;
  gap: 8px;
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 8px 10px;
}

.custom-date-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
}

.custom-date-lbl {
  font-size: 0.75rem;
  color: #94A3B8;
  font-weight: 600;
}

.date-picker-input {
  width: 100%;
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 6px 8px;
  color: #FFFFFF;
  font-size: 0.78rem;
  outline: none;
  color-scheme: dark;
}

/* Groupes Multi-Sélection (Provenances, Règlement) */
.filter-section-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-label {
  font-size: 0.73rem;
  font-weight: 700;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.section-hint {
  font-size: 0.68rem;
  color: #14B8A6;
  font-weight: 600;
}

.chips-scroll-row {
  display: flex;
  gap: 7px;
  overflow-x: auto;
  padding: 2px 0 4px 0;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.chips-scroll-row::-webkit-scrollbar {
  display: none;
}

.chip-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #CBD5E1;
  padding: 6px 12px;
  border-radius: 9999px;
  font-size: 0.74rem;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
}

.chip-btn:active {
  transform: scale(0.96);
}

.chip-btn.active {
  background: #0D9488;
  color: #FFFFFF;
  border-color: #14B8A6;
  box-shadow: 0 2px 8px rgba(13, 148, 136, 0.35);
}

.chip-btn.active-all {
  background: rgba(255, 255, 255, 0.12);
  color: #FFFFFF;
  border-color: rgba(255, 255, 255, 0.25);
}

.chip-facebook.active {
  background: #1877F2;
  border-color: #3B82F6;
  box-shadow: 0 2px 8px rgba(24, 119, 242, 0.4);
}

.chip-whatsapp.active {
  background: #16A34A;
  border-color: #22C55E;
  box-shadow: 0 2px 8px rgba(22, 163, 74, 0.4);
}

.chip-tiktok.active {
  background: #BE185D;
  border-color: #EC4899;
  box-shadow: 0 2px 8px rgba(190, 24, 93, 0.4);
}

.chip-check-icon {
  font-size: 13px;
  color: #FFFFFF;
}

.chip-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
}

/* Bouton pour afficher/masquer les filtres avancés */
.advanced-toggle-row {
  margin-top: 4px;
}

.btn-toggle-advanced {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px dashed rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  padding: 8px 12px;
  color: #94A3B8;
  font-size: 0.74rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-toggle-advanced:hover, .btn-toggle-advanced:active {
  background: rgba(255, 255, 255, 0.06);
  color: #E2E8F0;
}

.toggle-adv-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.toggle-adv-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.adv-badge {
  background: #0284C7;
  color: #FFFFFF;
  font-size: 0.62rem;
  font-weight: 800;
  padding: 1px 6px;
  border-radius: 10px;
}

.advanced-filters-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
  background: rgba(11, 17, 32, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
}

.adv-filter-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.btn-my-sales-mini {
  background: rgba(56, 189, 248, 0.12);
  color: #38BDF8;
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 8px;
  padding: 2px 8px;
  font-size: 0.68rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

.btn-my-sales-mini.active {
  background: #0284C7;
  color: #FFFFFF;
}

.adv-filter-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.adv-input-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.adv-lbl {
  font-size: 0.68rem;
  color: #94A3B8;
  font-weight: 600;
}

.dash-filter-select {
  width: 100%;
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 7px 10px;
  color: #FFFFFF;
  font-size: 0.78rem;
  outline: none;
}

.dash-filter-input {
  width: 100%;
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 7px 10px;
  color: #FFFFFF;
  font-size: 0.78rem;
  outline: none;
}

/* Tags actifs récapitulatifs */
.active-tags-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 4px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.active-tags-header {
  font-size: 0.68rem;
  color: #64748B;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.active-tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.active-tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(13, 148, 136, 0.15);
  border: 1px solid rgba(13, 148, 136, 0.35);
  color: #5EEAD4;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 600;
  cursor: pointer;
}

.tag-close-icon {
  font-size: 12px;
  color: #F87171;
}

/* KPIS */
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
  padding: 14px;
  display: flex;
  flex-direction: column;
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.kpi-label {
  font-size: 0.75rem;
  color: #94A3B8;
  font-weight: 600;
}

.kpi-icon {
  font-size: 18px;
}

.kpi-icon.teal { color: #14B8A6; }
.kpi-icon.green { color: #10B981; }
.kpi-icon.blue { color: #38BDF8; }
.kpi-icon.purple { color: #A855F7; }

.kpi-value {
  font-size: 1.15rem;
  font-weight: 800;
  color: #FFFFFF;
}

.kpi-value.green {
  color: #34D399;
}

.kpi-footer {
  font-size: 0.65rem;
  color: #64748B;
  margin-top: 4px;
}

.section-card {
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 16px;
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
  color: #FFFFFF;
  margin: 0;
}

.link-more {
  color: #38BDF8;
  font-size: 0.75rem;
  font-weight: 600;
  text-decoration: none;
}

.top-products-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.top-prod-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 10px;
  background: #0B1120;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.prod-rank {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.08);
  color: #5EEAD4;
  font-size: 0.72rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

.prod-info {
  flex: 1;
  min-width: 0;
}

.prod-title {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: #FFFFFF;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.prod-meta {
  font-size: 0.7rem;
  color: #94A3B8;
}

.prod-rev {
  font-size: 0.82rem;
  font-weight: 700;
  color: #34D399;
  white-space: nowrap;
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
  padding: 10px;
  background: #0B1120;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.sale-client-col {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.sale-client-nom {
  font-size: 0.85rem;
  font-weight: 600;
  color: #FFFFFF;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  gap: 2px;
}

.sale-price {
  font-size: 0.88rem;
  font-weight: 700;
  color: #34D399;
}

.sale-badge {
  font-size: 0.65rem;
  background: rgba(255, 255, 255, 0.06);
  color: #94A3B8;
  padding: 1px 6px;
  border-radius: 4px;
}

.empty-state {
  text-align: center;
  padding: 24px 10px;
  color: #64748B;
  font-size: 0.82rem;
}

/* MEDIA BUYER MOBILE STYLES */
.kpi-icon.orange {
  background: rgba(245, 158, 11, 0.15);
  color: #F59E0B;
}

.kpi-value.orange {
  color: #F59E0B;
}

.text-orange {
  color: #F59E0B;
}

.mb-mobile-card {
  border-left: 3px solid #F59E0B;
}

.btn-config-icon {
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: #F59E0B;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}

.mb-spend-mobile {
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.spend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: #E2E8F0;
}

.spend-badge {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 9999px;
}

.badge-rentabilise {
  background: rgba(16, 185, 129, 0.18);
  color: #34D399;
  border: 1px solid rgba(16, 185, 129, 0.35);
}

.badge-en-cours {
  background: rgba(245, 158, 11, 0.18);
  color: #FBBF24;
  border: 1px solid rgba(245, 158, 11, 0.35);
}

.spend-bar-track {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 9999px;
  overflow: hidden;
}

.spend-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #F59E0B, #10B981);
  border-radius: 9999px;
  transition: width 0.4s ease;
}

.spend-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.74rem;
  color: #94A3B8;
}

.mb-notice-mobile {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 0.74rem;
  color: #FCD34D;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: 8px;
  padding: 8px 10px;
  margin-bottom: 12px;
  line-height: 1.35;
}

.mb-rules-grid-mobile {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 12px;
}

.rule-box-mobile {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rule-box-blue {
  border-top: 2px solid #38BDF8;
}

.rule-box-green {
  border-top: 2px solid #34D399;
}

.rule-box-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.68rem;
}

.rule-pill-mobile {
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 4px;
}

.rule-pill-mobile.blue {
  background: rgba(56, 189, 248, 0.15);
  color: #38BDF8;
}

.rule-pill-mobile.green {
  background: rgba(52, 211, 153, 0.15);
  color: #34D399;
}

.rule-rate {
  font-weight: 700;
  color: #94A3B8;
}

.rule-box-val {
  font-size: 0.95rem;
  font-weight: 800;
  color: #38BDF8;
  margin-top: 2px;
}

.rule-box-val.text-green {
  color: #34D399;
}

.rule-box-sub {
  font-size: 0.68rem;
  color: #64748B;
}

.mb-prov-list-mobile {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.prov-label-mini {
  font-size: 0.7rem;
  color: #94A3B8;
}

.prov-badge-mini {
  font-size: 0.68rem;
  font-weight: 600;
  background: rgba(56, 189, 248, 0.12);
  color: #38BDF8;
  padding: 2px 6px;
  border-radius: 9999px;
  border: 1px solid rgba(56, 189, 248, 0.25);
}

/* MODAL CONFIG MOBILE */
.modal-config-content {
  --background: #0F172A;
  color: #F8FAFC;
}

.m-form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}

.m-form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.m-form-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.m-form-input,
.m-form-select {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  padding: 10px 12px;
  color: #F8FAFC;
  font-size: 0.9rem;
}

.m-form-input:focus,
.m-form-select:focus {
  outline: none;
  border-color: #00D2FF;
}

.m-form-help {
  font-size: 0.7rem;
  color: #64748B;
  margin-top: 2px;
}

.m-prov-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
}

.m-prov-checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: #CBD5E1;
  background: rgba(255, 255, 255, 0.05);
  padding: 4px 8px;
  border-radius: 6px;
}

.m-alert-error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #FCA5A5;
  font-size: 0.8rem;
  padding: 8px 10px;
  border-radius: 6px;
  margin-bottom: 12px;
}

.btn-save-config {
  width: 100%;
  background: linear-gradient(135deg, #00D2FF, #0084FF);
  color: #060D19;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  margin-top: 10px;
}

.btn-save-config:disabled {
  opacity: 0.6;
}
</style>
