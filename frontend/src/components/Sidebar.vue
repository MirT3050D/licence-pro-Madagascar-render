<template>
  <aside class="sidebar">
    <!-- Brand Header -->
    <div class="sidebar-header">
      <div class="brand-logo">
        <div class="logo-img-box">
          <img src="/logo.png" alt="Licence Pro Madagascar" class="sidebar-logo-img" />
        </div>
        <div class="logo-text">
          <span class="brand-title">Licence Pro</span>
          <span class="brand-subtitle">Madagascar</span>
        </div>
      </div>
    </div>

    <!-- Navigation Menu -->
    <nav class="sidebar-nav">
      <div class="nav-section-title">MENU PRINCIPAL</div>
      
      <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
        <LayoutDashboard :size="20" />
        <span>Tableau de bord</span>
      </router-link>

      <router-link to="/ventes" class="nav-item" :class="{ active: $route.path.startsWith('/ventes') }">
        <ShoppingCart :size="20" />
        <span>Ventes</span>
      </router-link>

      <router-link to="/produits" class="nav-item" :class="{ active: $route.path.startsWith('/produits') }">
        <Package :size="20" />
        <span>Produits & Licences</span>
      </router-link>

      <router-link to="/clients" class="nav-item" :class="{ active: $route.path.startsWith('/clients') }">
        <Users :size="20" />
        <span>Clients</span>
      </router-link>

      <router-link to="/paiements" class="nav-item" :class="{ active: $route.path.startsWith('/paiements') }">
        <CreditCard :size="20" />
        <span>Modes de règlement</span>
      </router-link>

      <div class="nav-section-title">COMPTE & PERFORMANCE</div>

      <router-link to="/profil" class="nav-item" :class="{ active: $route.path.startsWith('/profil') }">
        <User :size="20" />
        <span>Mon Profil & Permissions</span>
      </router-link>
    </nav>

    <!-- User Profile & Logout in Bottom Footer -->
    <div class="sidebar-footer">
      <div class="user-brief">
        <div class="user-avatar">
          {{ userInitials }}
        </div>
        <div class="user-details">
          <div class="user-name">{{ user?.prenom }} {{ user?.nom }}</div>
          <div class="user-role">{{ user?.role?.label || 'Utilisateur' }} ({{ user?.role?.point || 0 }} pts)</div>
        </div>
      </div>

      <button @click="handleLogout" class="btn-logout" title="Déconnexion">
        <LogOut :size="18" />
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  Users,
  CreditCard,
  User,
  LogOut,
} from '@lucide/vue'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { user, logout } = useAuth()

const userInitials = computed(() => {
  if (!user.value) return 'LP'
  const p = user.value.prenom ? user.value.prenom[0].toUpperCase() : ''
  const n = user.value.nom ? user.value.nom[0].toUpperCase() : ''
  return p + n || 'LP'
})

function handleLogout() {
  logout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  width: 260px;
  background-color: var(--bg-sidebar);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: sticky;
  top: 0;
  z-index: 40;
  user-select: none;
}

.sidebar-header {
  padding: 1.5rem 1.25rem;
  border-bottom: 1px solid var(--border-subtle);
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-img-box {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 210, 255, 0.2) 0%, rgba(6, 13, 25, 0.9) 100%);
  border: 1.5px solid rgba(0, 210, 255, 0.45);
  box-shadow: 0 0 16px rgba(0, 210, 255, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
}

.brand-logo:hover .logo-img-box {
  transform: scale(1.08) rotate(4deg);
  box-shadow: 0 0 24px rgba(0, 210, 255, 0.6);
}

.sidebar-logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.brand-title {
  font-weight: 800;
  font-size: 1.05rem;
  display: block;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #fff 0%, #cbd5e1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-subtitle {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--primary);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.sidebar-nav {
  flex: 1;
  padding: 1.25rem 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  overflow-y: auto;
}

.nav-section-title {
  font-size: 0.675rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.08em;
  padding: 0.75rem 0.75rem 0.35rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.7rem 0.9rem;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: all var(--transition-fast);
}

.nav-item:hover {
  color: var(--text-main);
  background: rgba(255, 255, 255, 0.04);
}

.nav-item.active {
  color: #ffffff;
  background: var(--primary-light);
  font-weight: 600;
  border: 1px solid rgba(99, 102, 241, 0.3);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.sidebar-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(10, 15, 26, 0.6);
}

.user-brief {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  overflow: hidden;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  font-weight: 700;
  font-size: 0.825rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-details {
  overflow: hidden;
}

.user-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 0.725rem;
  color: var(--text-muted);
}

.btn-logout {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.4rem;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.btn-logout:hover {
  color: var(--rose);
  background: var(--rose-bg);
}
</style>
