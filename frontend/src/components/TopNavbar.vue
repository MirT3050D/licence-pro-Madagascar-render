<template>
  <header class="top-navbar">
    <div class="navbar-left">
      <h2 class="page-title">{{ pageTitle }}</h2>
    </div>

    <div class="navbar-right">
      <!-- Role & Permissions Points Badge -->
      <div
        class="points-badge"
        :class="{ 'badge-admin': isSuperAdmin, 'badge-media-buyer': !isSuperAdmin }"
        :title="isSuperAdmin ? 'Permission : Niveau 50 (Admin - Saisie & Gestion totale)' : 'Permission : Niveau 10 (Media Buyer - Consultation & Ventes associées)'"
      >
        <ShieldCheck v-if="isSuperAdmin" :size="16" class="points-icon" />
        <Award v-else :size="16" class="points-icon" />
        <span class="points-count">{{ user?.role?.point || 0 }} pts</span>
        <span class="points-label">{{ isSuperAdmin ? 'Admin' : 'Media Buyer' }}</span>
      </div>

      <!-- Quick Action: New Sale (Reserved for Admin) -->
      <router-link v-if="isSuperAdmin" to="/ventes?action=nouvelle" class="btn btn-primary btn-sm">
        <Plus :size="16" />
        <span>Nouvelle Vente</span>
      </router-link>
      <div v-else class="sales-restricted-badge" title="Seul l'administrateur peut enregistrer de nouvelles ventes">
        <Lock :size="13" class="text-primary" />
        <span>Saisie ventes réservée à l'Admin</span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Plus, Award, ShieldCheck, Lock } from '@lucide/vue'
import { useAuth } from '../composables/useAuth'

const route = useRoute()
const { user, isSuperAdmin } = useAuth()

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
  padding: 0.35rem 0.85rem;
  border-radius: 9999px;
  font-size: 0.825rem;
  font-weight: 700;
  transition: all 0.2s ease;
}

.badge-admin {
  background: rgba(0, 210, 255, 0.12);
  border: 1px solid rgba(0, 210, 255, 0.4);
  color: #00d2ff;
  box-shadow: 0 0 15px rgba(0, 210, 255, 0.18);
}

.badge-admin .points-icon {
  color: #00d2ff;
}

.badge-media-buyer {
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.35);
  color: #10b981;
  box-shadow: 0 0 15px rgba(16, 185, 129, 0.15);
}

.badge-media-buyer .points-icon {
  color: #10b981;
}

.points-label {
  font-size: 0.725rem;
  opacity: 0.85;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding-left: 0.25rem;
  border-left: 1px solid currentColor;
}

.sales-restricted-badge {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.4rem 0.85rem;
  border-radius: var(--radius-md);
  background: rgba(13, 22, 41, 0.6);
  border: 1px dashed rgba(255, 255, 255, 0.15);
  font-size: 0.775rem;
  color: var(--text-muted);
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.825rem;
}
</style>
