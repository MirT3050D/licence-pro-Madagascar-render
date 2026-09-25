<template>
  <header class="top-navbar">
    <div class="navbar-left">
      <h2 class="page-title">{{ pageTitle }}</h2>
    </div>

    <div class="navbar-right">
      <!-- Seller Points Pill -->
      <div class="points-badge" title="Solde de points commission">
        <Award :size="16" class="points-icon" />
        <span class="points-count">{{ user?.role?.point || 0 }} pts</span>
      </div>

      <!-- Quick Action: New Sale -->
      <router-link to="/ventes?action=nouvelle" class="btn btn-primary btn-sm">
        <Plus :size="16" />
        <span>Nouvelle Vente</span>
      </router-link>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Plus, Award } from '@lucide/vue'
import { useAuth } from '../composables/useAuth'

const route = useRoute()
const { user } = useAuth()

const pageTitle = computed(() => {
  switch (route.name) {
    case 'dashboard': return 'Tableau de bord'
    case 'ventes': return 'Gestion des Ventes'
    case 'produits': return 'Catalogue des Produits'
    case 'clients': return 'Gestion des Clients'
    case 'profil': return 'Mon Profil'
    default: return 'Licence Pro'
  }
})
</script>

<style scoped>
.top-navbar {
  height: 70px;
  background: rgba(13, 19, 31, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  position: sticky;
  top: 0;
  z-index: 30;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.points-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--amber-bg);
  border: 1px solid rgba(245, 158, 11, 0.35);
  color: #fbbf24;
  padding: 0.4rem 0.85rem;
  border-radius: 9999px;
  font-size: 0.825rem;
  font-weight: 700;
  box-shadow: 0 0 15px rgba(245, 158, 11, 0.15);
}

.points-icon {
  color: #f59e0b;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.825rem;
}
</style>
