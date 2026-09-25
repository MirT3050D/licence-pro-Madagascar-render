<template>
  <ion-page>
    <ion-header :translucent="true">
      <ion-toolbar class="main-toolbar">
        <ion-title>Répertoire Clients</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="openCreateClient" class="btn-toolbar-action">
            <ion-icon :icon="personAddOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>

      <!-- Search & Filter -->
      <div class="filter-bar">
        <div class="search-input-wrap">
          <ion-icon :icon="searchOutline" class="search-icon" />
          <input
            v-model="searchQuery"
            @input="onSearch"
            type="text"
            placeholder="Rechercher par nom ou numéro..."
            class="search-field"
          />
          <button v-if="searchQuery" @click="clearSearch" class="clear-search-btn">
            <ion-icon :icon="closeCircle" />
          </button>
        </div>

        <!-- Provenance filter pills -->
        <div class="provenance-pills" v-if="provenances.length">
          <button
            :class="['prov-pill', selectedProvenance === null ? 'active' : '']"
            @click="setProvenance(null)"
          >
            Tous ({{ totalClientsCount }})
          </button>
          <button
            v-for="prov in provenances"
            :key="prov.id"
            :class="['prov-pill', selectedProvenance === prov.id ? 'active' : '']"
            @click="setProvenance(prov.id)"
          >
            {{ prov.label }} ({{ prov.clients_count || 0 }})
          </button>
        </div>
      </div>
    </ion-header>

    <ion-content :fullscreen="true" class="clients-content">
      <ion-refresher slot="fixed" @ionRefresh="handleRefresh($event)">
        <ion-refresher-content></ion-refresher-content>
      </ion-refresher>

      <div v-if="loading" class="empty-state">
        <span>Chargement des clients...</span>
      </div>

      <div v-else-if="filteredClients.length === 0" class="empty-state">
        <ion-icon :icon="peopleOutline" class="empty-icon" />
        <p>Aucun client trouvé.</p>
        <button class="btn-create-client-empty" @click="openCreateClient">
          Ajouter un client
        </button>
      </div>

      <div v-else class="clients-list">
        <div v-for="c in filteredClients" :key="c.id" class="client-card">
          <div class="client-top-row">
            <div class="client-avatar">
              {{ getInitials(c.nom) }}
            </div>
            <div class="client-main-meta">
              <div class="name-edit-wrap">
                <span class="client-name">{{ c.nom }}</span>
                <button class="btn-edit-client" @click="openEditClient(c)">
                  <ion-icon :icon="createOutline" />
                </button>
              </div>
              <span class="client-prov-badge" v-if="c.provenance">
                {{ c.provenance.label }}
              </span>
            </div>
          </div>

          <!-- Phone & Quick Actions -->
          <div class="client-phone-row" v-if="c.numero">
            <span class="phone-number">{{ c.numero }}</span>
            <div class="contact-actions">
              <a :href="`tel:${cleanPhone(c.numero)}`" class="btn-contact call" title="Appeler">
                <ion-icon :icon="callOutline" />
              </a>
              <a :href="`https://wa.me/${cleanPhone(c.numero)}`" target="_blank" class="btn-contact whatsapp" title="WhatsApp">
                <ion-icon :icon="logoWhatsapp" />
              </a>
            </div>
          </div>

          <!-- Bottom stats -->
          <div class="client-bottom-stats">
            <span class="stat-pill">
              <b>{{ c.ventes_count || 0 }}</b> vente(s)
            </span>
            <span class="stat-pill total">
              Total : <b>{{ formatPrice(c.total_achats || 0) }}</b>
            </span>
          </div>
        </div>
      </div>
    </ion-content>

    <ClientModal
      :is-open="isClientModalOpen"
      :client-data="selectedClientToEdit"
      :provenances="provenances"
      @close="isClientModalOpen = false"
      @saved="fetchClients"
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
} from '@ionic/vue'
import {
  personAddOutline,
  searchOutline,
  closeCircle,
  peopleOutline,
  createOutline,
  callOutline,
  logoWhatsapp,
} from 'ionicons/icons'
import apiClient from '../api/client'
import ClientModal from '../components/ClientModal.vue'

const loading = ref(false)
const clients = ref([])
const provenances = ref([])
const searchQuery = ref('')
const selectedProvenance = ref(null)

const isClientModalOpen = ref(false)
const selectedClientToEdit = ref(null)

const totalClientsCount = computed(() => clients.value.length)

const filteredClients = computed(() => {
  return clients.value.filter((c) => {
    // Provenance filter
    if (selectedProvenance.value !== null) {
      const pId = c.provenance?.id || c.provenance_id
      if (pId !== selectedProvenance.value) return false
    }
    // Search query
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase()
      const matchName = c.nom?.toLowerCase().includes(q)
      const matchNum = c.numero?.toLowerCase().includes(q)
      if (!matchName && !matchNum) return false
    }
    return true
  })
})

function formatPrice(val) {
  if (!val && val !== 0) return '0 Ar'
  return Math.round(val).toLocaleString('fr-FR') + ' Ar'
}

function getInitials(name) {
  if (!name) return 'C'
  const parts = name.trim().split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return parts[0].slice(0, 2).toUpperCase()
}

function cleanPhone(num) {
  if (!num) return ''
  return num.replace(/\s+/g, '').replace(/-/g, '')
}

async function fetchClients() {
  loading.value = true
  try {
    const [clientsRes, provRes] = await Promise.all([
      apiClient.get('/clients/'),
      apiClient.get('/clients/provenances/'),
    ])
    clients.value = clientsRes.data.results || clientsRes.data || []
    provenances.value = provRes.data.results || provRes.data || []
  } catch (err) {
    console.error('Erreur chargement clients:', err)
  } finally {
    loading.value = false
  }
}

function onSearch() {
  // filtered computed handles live filtering
}

function clearSearch() {
  searchQuery.value = ''
}

function setProvenance(pId) {
  selectedProvenance.value = pId
}

function openCreateClient() {
  selectedClientToEdit.value = null
  isClientModalOpen.value = true
}

function openEditClient(client) {
  selectedClientToEdit.value = client
  isClientModalOpen.value = true
}

async function handleRefresh(event) {
  await fetchClients()
  event.target.complete()
}

onMounted(() => {
  fetchClients()
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

.provenance-pills {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  overflow-x: auto;
}

.prov-pill {
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #94A3B8;
  padding: 5px 12px;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
}

.prov-pill.active {
  background: #0D9488;
  color: #FFFFFF;
  border-color: #0D9488;
}

.clients-content {
  --background: #0B1120;
  --color: #F8FAFC;
}

.clients-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
}

.client-card {
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 14px;
}

.client-top-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.client-avatar {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(135deg, #0D9488 0%, #0284C7 100%);
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.95rem;
}

.client-main-meta {
  flex: 1;
}

.name-edit-wrap {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.client-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: #FFFFFF;
}

.btn-edit-client {
  background: none;
  border: none;
  color: #64748B;
  font-size: 16px;
}

.client-prov-badge {
  display: inline-block;
  background: rgba(56, 189, 248, 0.15);
  color: #38BDF8;
  font-size: 0.68rem;
  padding: 2px 6px;
  border-radius: 4px;
  margin-top: 2px;
}

.client-phone-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #0B1120;
  border-radius: 10px;
  padding: 8px 12px;
  margin-top: 10px;
}

.phone-number {
  font-size: 0.85rem;
  color: #E2E8F0;
  font-weight: 500;
}

.contact-actions {
  display: flex;
  gap: 8px;
}

.btn-contact {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  text-decoration: none;
  font-size: 16px;
}

.btn-contact.call {
  background: #0284C7;
}

.btn-contact.whatsapp {
  background: #16A34A;
}

.client-bottom-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-pill {
  font-size: 0.72rem;
  color: #94A3B8;
}

.stat-pill b {
  color: #5EEAD4;
}

.stat-pill.total b {
  color: #34D399;
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

.btn-create-client-empty {
  background: #0D9488;
  color: #fff;
  border: none;
  padding: 10px 18px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
}
</style>
