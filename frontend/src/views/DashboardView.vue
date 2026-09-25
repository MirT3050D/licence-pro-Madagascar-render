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

        <!-- 4. CLIENT -->
        <div class="filter-group-dash">
          <label class="filter-label-dash">
            <User :size="14" class="text-primary" />
            <span>Client</span>
          </label>
          <select v-model="filters.client" @change="loadDashboard" class="form-select select-dash">
            <option value="">Tous les clients</option>
            <option v-for="c in clientsList" :key="c.id" :value="c.id">{{ c.nom }}</option>
          </select>
        </div>

        <!-- 5. PROVENANCE -->
        <div class="filter-group-dash">
          <label class="filter-label-dash">
            <Globe :size="14" class="text-primary" />
            <span>Provenance</span>
          </label>
          <select v-model="filters.provenance" @change="loadDashboard" class="form-select select-dash">
            <option value="">Toutes provenances</option>
            <option v-for="p in provenancesList" :key="p.id" :value="p.id">{{ p.label }}</option>
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
        <span v-if="activeClientName" class="filter-pill">
          Client : <strong>{{ activeClientName }}</strong>
        </span>
        <span v-if="activeProvenanceName" class="filter-pill">
          Provenance : <strong>{{ activeProvenanceName }}</strong>
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

      <!-- Commission Media Buyer -->
      <div class="card kpi-card kpi-card-mb">
        <div class="kpi-header">
          <span class="kpi-title">Commission Media Buyer</span>
          <div class="kpi-icon-box icon-purple">
            <Target :size="22" />
          </div>
        </div>
        <div class="kpi-value text-purple">{{ formatCurrency(data?.commission_media_buyer?.commission_due || 0) }}</div>
        <div class="kpi-subtext">
          <span v-if="data?.commission_media_buyer?.statut?.seuil_atteint" class="badge badge-success">
            ✓ Compteur actif (100% amorti)
          </span>
          <span v-else class="badge badge-warning">
            ⏳ Coût pub : {{ data?.commission_media_buyer?.statut?.progression_recouvrement || 0 }}% amorti
          </span>
        </div>
      </div>
    </div>

    <!-- SECTION DÉTAILLÉE COMMISSION MEDIA BUYER -->
    <div class="card media-buyer-section" v-if="data?.commission_media_buyer">
      <div class="mb-section-header">
        <div class="mb-header-title-wrap">
          <div class="mb-icon-badge">
            <Megaphone :size="22" />
          </div>
          <div>
            <div class="mb-title-row">
              <h3 class="mb-title">Suivi Commission Media Buyer</h3>
              <div class="provenance-tags">
                <span class="prov-tag-label">Provenances éligibles :</span>
                <span
                  v-for="prov in (data?.commission_media_buyer?.config?.provenances || [])"
                  :key="prov.id"
                  class="badge badge-prov"
                >
                  🌐 {{ prov.label }}
                </span>
                <span v-if="!data?.commission_media_buyer?.config?.provenances?.length" class="text-xs text-muted">
                  Aucune configurée
                </span>
              </div>
            </div>
            <p class="text-xs text-muted mb-rules-summary">
              Règles : 
              <strong class="text-primary">{{ data?.commission_media_buyer?.config?.regle_ca || 10 }}% sur le CA</strong> pour les ventes à marge &gt; {{ data?.commission_media_buyer?.config?.seuil_marge || 40 }}% (strict sup) • 
              <strong class="text-emerald">{{ data?.commission_media_buyer?.config?.regle_benefice || 30 }}% sur le bénéfice</strong> pour les ventes à marge &le; {{ data?.commission_media_buyer?.config?.seuil_marge || 40 }}%
            </p>
          </div>
        </div>
        <button
          v-if="isSuperAdmin"
          @click="openCommissionConfigModal"
          class="btn btn-secondary btn-sm btn-config-mb"
          title="Modifier les taux, le coût publicitaire et les provenances"
        >
          <Sliders :size="15" />
          <span>Configurer règles</span>
        </button>
      </div>

      <!-- MB Content Grid: Jauge à gauche, Décomposition à droite -->
      <div class="mb-content-grid">
        <!-- Colonne 1: Amortissement du Coût Publicitaire -->
        <div class="mb-box mb-spend-box">
          <div class="mb-box-header">
            <span class="mb-box-title">Amortissement du Coût Publicitaire</span>
            <span
              :class="data?.commission_media_buyer?.statut?.seuil_atteint ? 'badge badge-success' : 'badge badge-warning'"
            >
              {{ data?.commission_media_buyer?.statut?.seuil_atteint ? '✓ Rentabilisé' : '⏳ Amortissement en cours' }}
            </span>
          </div>

          <div class="mb-progress-block">
            <div class="mb-progress-info">
              <span class="text-sm">
                Généré ({{ data?.commission_media_buyer?.statut?.base_recouvrement_label }}) :
                <strong class="text-cyan">{{ formatCurrency(data?.commission_media_buyer?.statut?.recouvrement_actuel || 0) }}</strong>
              </span>
              <span class="text-sm">
                Coût publicité :
                <strong>{{ formatCurrency(data?.commission_media_buyer?.statut?.cout_pub || 0) }}</strong>
              </span>
            </div>
            <div class="progress-bar-track">
              <div
                class="progress-bar-fill"
                :style="{ width: `${data?.commission_media_buyer?.statut?.progression_recouvrement || 0}%` }"
                :class="{ 'fill-complete': data?.commission_media_buyer?.statut?.seuil_atteint }"
              ></div>
            </div>
            <div class="mb-progress-footer">
              <span>Progression : <strong>{{ data?.commission_media_buyer?.statut?.progression_recouvrement || 0 }}%</strong></span>
              <span v-if="!data?.commission_media_buyer?.statut?.seuil_atteint" class="text-amber">
                Reste à amortir : <strong>{{ formatCurrency(data?.commission_media_buyer?.statut?.reste_a_recouvrir || 0) }}</strong>
              </span>
              <span v-else class="text-emerald">
                ✓ Seuil dépassé de {{ formatCurrency((data?.commission_media_buyer?.statut?.recouvrement_actuel || 0) - (data?.commission_media_buyer?.statut?.cout_pub || 0)) }}
              </span>
            </div>
          </div>

          <div class="mb-notice" :class="data?.commission_media_buyer?.statut?.seuil_atteint ? 'notice-success' : 'notice-warning'">
            <div v-if="data?.commission_media_buyer?.statut?.seuil_atteint">
              🎉 <strong>Compteur actif :</strong> Le coût de publicité a été intégralement récupéré. La commission de <strong>{{ formatCurrency(data?.commission_media_buyer?.commission_due || 0) }}</strong> est débloquée et comptabilisée.
            </div>
            <div v-else>
              ⚠️ <strong>Compteur bloqué à 0 Ar :</strong> La commission commencera uniquement une fois le coût publicitaire de 
              <strong>{{ formatCurrency(data?.commission_media_buyer?.statut?.cout_pub || 0) }}</strong> amorti.
              <div class="mt-1 text-xs">
                Commission potentielle accumulée en attente : 
                <strong class="text-purple">{{ formatCurrency(data?.commission_media_buyer?.commission_potentielle || 0) }}</strong>
              </div>
            </div>
          </div>
        </div>

        <!-- Colonne 2: Décomposition par règle -->
        <div class="mb-box mb-rules-box">
          <div class="mb-box-header">
            <span class="mb-box-title">Décomposition par règle commerciale</span>
            <span class="text-xs text-muted">
              {{ data?.commission_media_buyer?.nb_articles_eligible || 0 }} article(s) éligible(s)
            </span>
          </div>

          <div class="rules-cards-stack">
            <!-- Règle 1: Marge > seuil -->
            <div class="rule-detail-card card-marge-haute">
              <div class="rule-card-top">
                <span class="rule-tag tag-cyan">Produits marge &gt; {{ data?.commission_media_buyer?.config?.seuil_marge || 40 }}%</span>
                <span class="rule-pct">{{ data?.commission_media_buyer?.config?.regle_ca || 10 }}% sur CA</span>
              </div>
              <div class="rule-card-body">
                <div class="rule-stat">
                  <span class="lbl">CA des produits éligibles :</span>
                  <span class="val">{{ formatCurrency(data?.commission_media_buyer?.details?.marge_haute?.base_ca || 0) }}</span>
                </div>
                <div class="rule-stat">
                  <span class="lbl">Commission calculée :</span>
                  <span class="val text-cyan font-bold">+{{ formatCurrency(data?.commission_media_buyer?.details?.marge_haute?.commission || 0) }}</span>
                </div>
              </div>
            </div>

            <!-- Règle 2: Marge <= seuil -->
            <div class="rule-detail-card card-marge-basse">
              <div class="rule-card-top">
                <span class="rule-tag tag-emerald">Produits marge &le; {{ data?.commission_media_buyer?.config?.seuil_marge || 40 }}%</span>
                <span class="rule-pct">{{ data?.commission_media_buyer?.config?.regle_benefice || 30 }}% sur Bénéfice</span>
              </div>
              <div class="rule-card-body">
                <div class="rule-stat">
                  <span class="lbl">Bénéfice brut éligible :</span>
                  <span class="val">{{ formatCurrency(data?.commission_media_buyer?.details?.marge_basse?.base_benefice || 0) }}</span>
                </div>
                <div class="rule-stat">
                  <span class="lbl">Commission calculée :</span>
                  <span class="val text-emerald font-bold">+{{ formatCurrency(data?.commission_media_buyer?.details?.marge_basse?.commission || 0) }}</span>
                </div>
              </div>
            </div>

            <!-- Total Bar -->
            <div class="rule-total-bar">
              <span class="total-lbl">Commission Media Buyer Débloquée :</span>
              <span class="total-val" :class="data?.commission_media_buyer?.statut?.seuil_atteint ? 'text-purple' : 'text-muted-strikethrough'">
                {{ formatCurrency(data?.commission_media_buyer?.commission_due || 0) }}
              </span>
            </div>
          </div>
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

    <!-- MODAL DE CONFIGURATION COMMISSION MEDIA BUYER -->
    <div v-if="showConfigModal" class="modal-backdrop" @click.self="showConfigModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <div class="flex items-center gap-2">
            <Sliders :size="18" class="text-primary" />
            <h3 class="font-bold text-base">Configuration Commission Media Buyer</h3>
          </div>
          <button @click="showConfigModal = false" class="btn-close" type="button">
            <X :size="18" />
          </button>
        </div>

        <form @submit.prevent="saveCommissionConfig" class="modal-body">
          <div class="form-group mb-3">
            <label class="form-label">Coût publicité / Budget publicitaire (Ar)</label>
            <input
              v-model.number="configForm.cout_pub"
              type="number"
              step="any"
              min="0"
              class="form-input"
              placeholder="Ex: 500000"
              required
            />
            <span class="form-help text-xs text-muted">
              Le compteur de commission démarre uniquement une fois ce montant rentabilisé.
            </span>
          </div>

          <div class="form-row-2 mb-3">
            <div class="form-group">
              <label class="form-label">Taux com sur CA si marge &gt; seuil (%)</label>
              <input
                v-model.number="configForm.regle_ca"
                type="number"
                step="0.1"
                min="0"
                max="100"
                class="form-input"
                required
              />
              <span class="text-xs text-muted">Actuellement : 10%</span>
            </div>
            <div class="form-group">
              <label class="form-label">Taux com sur Bénéfice si marge &le; seuil (%)</label>
              <input
                v-model.number="configForm.regle_benefice"
                type="number"
                step="0.1"
                min="0"
                max="100"
                class="form-input"
                required
              />
              <span class="text-xs text-muted">Actuellement : 30%</span>
            </div>
          </div>

          <div class="form-row-2 mb-3">
            <div class="form-group">
              <label class="form-label">Seuil de marge bénéficiaire (%)</label>
              <input
                v-model.number="configForm.seuil_marge"
                type="number"
                step="0.1"
                min="0"
                max="100"
                class="form-input"
                required
              />
              <span class="text-xs text-muted">Strictement supérieur (Actuellement : 40%)</span>
            </div>
            <div class="form-group">
              <label class="form-label">Base de rentabilisation du coût pub</label>
              <select v-model="configForm.base_recouvrement" class="form-select">
                <option value="benefice">Bénéfice brut (Recommandé)</option>
                <option value="ca">Chiffre d'affaires</option>
              </select>
              <span class="text-xs text-muted">Montant généré servant à amortir le coût pub</span>
            </div>
          </div>

          <div class="form-group mb-3">
            <label class="form-label">Provenances éligibles aux commissions</label>
            <div class="provenances-checkbox-grid">
              <label
                v-for="prov in provenancesList"
                :key="prov.id"
                class="prov-checkbox-label"
              >
                <input
                  type="checkbox"
                  :value="prov.id"
                  v-model="configForm.provenances"
                />
                <span>{{ prov.label }}</span>
              </label>
            </div>
            <span class="text-xs text-muted">Seules les ventes issues de ces provenances génèrent des commissions (ex: Facebook, WhatsApp).</span>
          </div>

          <div v-if="configError" class="alert alert-danger mb-3">
            {{ configError }}
          </div>

          <div class="modal-footer">
            <button @click="showConfigModal = false" type="button" class="btn btn-secondary">
              Annuler
            </button>
            <button type="submit" class="btn btn-primary" :disabled="savingConfig">
              <span v-if="savingConfig">Enregistrement...</span>
              <span v-else>Enregistrer les paramètres</span>
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
  RotateCcw,
  User,
  Globe,
  Target,
  Megaphone,
  Sliders,
  X
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

const { user, isSuperAdmin } = useAuth()

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
const clientsList = ref([])
const provenancesList = ref([])

const filters = ref({
  vendeur: '',
  periode: 'all',
  date_debut: '',
  date_fin: '',
  methode_paiement: '',
  client: '',
  provenance: '',
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
    filters.value.methode_paiement ||
    filters.value.client ||
    filters.value.provenance
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
    client: '',
    provenance: '',
  }
  loadDashboard()
}

async function fetchDependencies() {
  try {
    const [uRes, mRes, cRes, pRes] = await Promise.all([
      apiClient.get('/auth/users/').catch(() => ({ data: [] })),
      apiClient.get('/ventes/methodes-paiement/').catch(() => ({ data: [] })),
      apiClient.get('/clients/').catch(() => ({ data: [] })),
      apiClient.get('/clients/provenances/').catch(() => ({ data: [] }))
    ])
    vendorsList.value = uRes.data.results || uRes.data || []
    paymentMethods.value = mRes.data.results || mRes.data || []
    clientsList.value = cRes.data.results || cRes.data || []
    provenancesList.value = pRes.data.results || pRes.data || []
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
    if (filters.value.client) params.client = filters.value.client
    if (filters.value.provenance) params.provenance = filters.value.provenance

    const res = await apiClient.get('/ventes/dashboard/', { params })
    data.value = res.data
  } catch (err) {
    console.error('Erreur chargement dashboard:', err)
  } finally {
    loading.value = false
  }
}

function formatCurrency(val) {
  const num = Number(val)
  if (isNaN(num)) return '0 Ar'
  return new Intl.NumberFormat('fr-MG').format(Math.round(num)) + ' Ar'
}

// Media Buyer Commission Modal & Settings
const showConfigModal = ref(false)
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

function openCommissionConfigModal() {
  const current = data.value?.commission_media_buyer?.config
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
      provenances: provenancesList.value
        .filter(p => /facebook|whatsapp/i.test(p.label))
        .map(p => p.id)
    }
  }
  configError.value = ''
  showConfigModal.value = true
}

async function saveCommissionConfig() {
  savingConfig.value = true
  configError.value = ''
  try {
    await apiClient.put('/ventes/commission-media-buyer/', configForm.value)
    showConfigModal.value = false
    await loadDashboard()
  } catch (err) {
    console.error('Erreur sauvegarde config commission:', err)
    configError.value = err.response?.data?.error || err.message || 'Erreur lors de la sauvegarde.'
  } finally {
    savingConfig.value = false
  }
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

/* MEDIA BUYER KPI & SECTION STYLING */
.icon-purple {
  background: rgba(168, 85, 247, 0.16);
  color: #c084fc;
}

.text-purple {
  color: #c084fc;
}

.text-cyan {
  color: #38bdf8;
}

.media-buyer-section {
  padding: 1.5rem;
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 27, 75, 0.35) 100%);
  border: 1px solid rgba(168, 85, 247, 0.25);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 0 20px -5px rgba(168, 85, 247, 0.15);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.mb-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.mb-header-title-wrap {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.mb-icon-badge {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.3), rgba(99, 102, 241, 0.3));
  border: 1px solid rgba(168, 85, 247, 0.4);
  color: #e879f9;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mb-title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.mb-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #f8fafc;
}

.provenance-tags {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.prov-tag-label {
  font-size: 0.72rem;
  color: var(--text-secondary);
  font-weight: 600;
}

.badge-prov {
  background: rgba(56, 189, 248, 0.12);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.3);
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-weight: 600;
}

.btn-config-mb {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(168, 85, 247, 0.15);
  border-color: rgba(168, 85, 247, 0.35);
  color: #e9d5ff;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-config-mb:hover {
  background: rgba(168, 85, 247, 0.3);
  border-color: rgba(168, 85, 247, 0.6);
  color: #fff;
}

.mb-content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 1.25rem;
}

.mb-box {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.mb-box-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.mb-box-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #cbd5e1;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.mb-progress-block {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mb-progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.progress-bar-track {
  width: 100%;
  height: 10px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 9999px;
  overflow: hidden;
  position: relative;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b 0%, #3b82f6 50%, #10b981 100%);
  border-radius: 9999px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-bar-fill.fill-complete {
  background: linear-gradient(90deg, #10b981, #059669);
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
}

.mb-progress-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.78rem;
  color: var(--text-secondary);
}

.mb-notice {
  font-size: 0.82rem;
  line-height: 1.45;
  padding: 0.85rem 1rem;
  border-radius: var(--radius-sm);
}

.notice-success {
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #6ee7b7;
}

.notice-warning {
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: #fcd34d;
}

.rules-cards-stack {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.rule-detail-card {
  padding: 0.85rem 1rem;
  border-radius: var(--radius-sm);
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.rule-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.rule-tag {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.tag-cyan {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.3);
}

.tag-emerald {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
  border: 1px solid rgba(52, 211, 153, 0.3);
}

.rule-pct {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-secondary);
}

.rule-card-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.rule-stat {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.rule-stat .lbl {
  color: var(--text-muted);
  font-size: 0.78rem;
}

.rule-total-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1rem;
  border-radius: var(--radius-sm);
  background: rgba(168, 85, 247, 0.12);
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.total-lbl {
  font-size: 0.85rem;
  font-weight: 700;
  color: #e9d5ff;
}

.total-val {
  font-size: 1.15rem;
  font-weight: 800;
}

.text-muted-strikethrough {
  color: var(--text-muted);
  text-decoration: line-through;
}

/* MODAL STYLES */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-card {
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 540px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  animation: modalIn 0.2s ease-out;
}

@keyframes modalIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.btn-close {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
}

.btn-close:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.provenances-checkbox-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.25);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.prov-checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #e2e8f0;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}
</style>
