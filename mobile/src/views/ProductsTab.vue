<template>
  <ion-page>
    <ion-header :translucent="true">
      <ion-toolbar class="main-toolbar">
        <ion-title>Catalogue Logiciels</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="openCreateProduct" class="btn-toolbar-action">
            <ion-icon :icon="addCircleOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>

      <div class="filter-bar">
        <div class="search-input-wrap">
          <ion-icon :icon="searchOutline" class="search-icon" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher Windows, Office, Canva..."
            class="search-field"
          />
          <button v-if="searchQuery" @click="searchQuery = ''" class="clear-search-btn">
            <ion-icon :icon="closeCircle" />
          </button>
        </div>
      </div>
    </ion-header>

    <ion-content :fullscreen="true" class="products-content">
      <ion-refresher slot="fixed" @ionRefresh="handleRefresh($event)">
        <ion-refresher-content></ion-refresher-content>
      </ion-refresher>

      <div class="products-meta-bar">
        <span><b>{{ filteredProducts.length }}</b> logiciel(s) au catalogue</span>
      </div>

      <div v-if="loading" class="empty-state">
        <span>Chargement du catalogue...</span>
      </div>

      <div v-else-if="filteredProducts.length === 0" class="empty-state">
        <ion-icon :icon="cubeOutline" class="empty-icon" />
        <p>Aucun produit ne correspond à la recherche.</p>
        <button class="btn-create-product-empty" @click="openCreateProduct">
          Ajouter un logiciel
        </button>
      </div>

      <div v-else class="products-grid">
        <div v-for="p in filteredProducts" :key="p.id" class="product-card">
          <div class="product-top">
            <div class="prod-thumb">
              <img v-if="p.image" :src="p.image" alt="Product" class="thumb-img" />
              <div v-else class="thumb-placeholder">
                <ion-icon :icon="cubeOutline" />
              </div>
            </div>

            <div class="prod-header-info">
              <span class="prod-title">{{ p.nom }}</span>
              <div class="price-tags-wrap">
                <span class="price-selling">{{ formatPrice(p.prix_actif || p.prix_achat) }}</span>
                <span class="price-cost" v-if="p.prix_achat > 0">Coût: {{ formatPrice(p.prix_achat) }}</span>
              </div>
            </div>

            <button class="btn-edit" @click="openEditProduct(p)" title="Modifier">
              <ion-icon :icon="createOutline" />
            </button>
          </div>

          <p class="prod-desc" v-if="p.description">{{ p.description }}</p>

          <!-- Quick price changer & activation guide button -->
          <div class="product-actions-bar">
            <button class="btn-action-pill" @click="promptChangePrice(p)">
              <ion-icon :icon="pricetagOutline" />
              <span>Changer le prix</span>
            </button>

            <button
              class="btn-action-pill guide"
              @click="toggleGuide(p.id)"
              v-if="p.activations && p.activations.length"
            >
              <ion-icon :icon="bookOutline" />
              <span>{{ activeGuideProductId === p.id ? 'Masquer guide' : 'Guide activation' }}</span>
            </button>
          </div>

          <!-- Guide viewer -->
          <div v-if="activeGuideProductId === p.id" class="guide-display-box animate-fade">
            <div class="guide-header">
              <span>Procédure d'activation client :</span>
              <button class="btn-copy-sm" @click="copyGuide(p)">Copier</button>
            </div>
            <div class="guide-content">
              {{ p.activations[0].description_activation }}
            </div>
          </div>
        </div>
      </div>
    </ion-content>

    <ProductModal
      :is-open="isProductModalOpen"
      :product-data="selectedProductToEdit"
      @close="isProductModalOpen = false"
      @saved="fetchProducts"
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
  alertController,
  toastController,
} from '@ionic/vue'
import {
  addCircleOutline,
  searchOutline,
  closeCircle,
  cubeOutline,
  createOutline,
  pricetagOutline,
  bookOutline,
} from 'ionicons/icons'
import apiClient from '../api/client'
import ProductModal from '../components/ProductModal.vue'

const loading = ref(false)
const products = ref([])
const searchQuery = ref('')
const activeGuideProductId = ref(null)

const isProductModalOpen = ref(false)
const selectedProductToEdit = ref(null)

const filteredProducts = computed(() => {
  if (!searchQuery.value.trim()) return products.value
  const q = searchQuery.value.toLowerCase()
  return products.value.filter(
    (p) =>
      p.nom?.toLowerCase().includes(q) ||
      p.description?.toLowerCase().includes(q)
  )
})

function formatPrice(val) {
  if (!val && val !== 0) return '0 Ar'
  return Math.round(val).toLocaleString('fr-FR') + ' Ar'
}

async function fetchProducts() {
  loading.value = true
  try {
    const res = await apiClient.get('/produits/')
    products.value = res.data.results || res.data || []
  } catch (err) {
    console.error('Erreur catalogue:', err)
  } finally {
    loading.value = false
  }
}

async function handleRefresh(event) {
  await fetchProducts()
  event.target.complete()
}

function openCreateProduct() {
  selectedProductToEdit.value = null
  isProductModalOpen.value = true
}

function openEditProduct(prod) {
  selectedProductToEdit.value = prod
  isProductModalOpen.value = true
}

function toggleGuide(prodId) {
  activeGuideProductId.value = activeGuideProductId.value === prodId ? null : prodId
}

async function promptChangePrice(prod) {
  const currentPrice = prod.prix_actif ? Number(prod.prix_actif) : Number(prod.prix_achat) || 0
  const alert = await alertController.create({
    header: 'Nouveau prix de vente',
    subHeader: prod.nom,
    inputs: [
      {
        name: 'prix',
        type: 'number',
        placeholder: 'Prix en Ariary',
        value: currentPrice,
      },
    ],
    buttons: [
      {
        text: 'Annuler',
        role: 'cancel',
      },
      {
        text: 'Valider',
        handler: async (data) => {
          if (!data.prix) return false
          try {
            await apiClient.post(`/produits/${prod.id}/changer-prix/`, {
              prix: Number(data.prix),
            })
            const toast = await toastController.create({
              message: 'Prix mis à jour avec succès.',
              duration: 2000,
              color: 'success',
              position: 'top',
            })
            await toast.present()
            fetchProducts()
          } catch (e) {
            alert('Erreur lors du changement de prix.')
          }
        },
      },
    ],
  })

  await alert.present()
}

async function copyGuide(prod) {
  const guide = prod.activations?.[0]?.description_activation
  if (!guide) return
  if (navigator.clipboard) {
    await navigator.clipboard.writeText(`*Activation ${prod.nom}*\n\n${guide}`)
  }
  const toast = await toastController.create({
    message: 'Guide d\'activation copié !',
    duration: 2000,
    color: 'success',
    position: 'top',
  })
  await toast.present()
}

onMounted(() => {
  fetchProducts()
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

.products-content {
  --background: #0B1120;
  --color: #F8FAFC;
}

.products-meta-bar {
  padding: 12px 16px 4px 16px;
  font-size: 0.8rem;
  color: #94A3B8;
}

.products-meta-bar b {
  color: #5EEAD4;
}

.products-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px 16px 24px 16px;
}

.product-card {
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 14px;
}

.product-top {
  display: flex;
  align-items: center;
  gap: 12px;
}

.prod-thumb {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  color: #14B8A6;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.prod-header-info {
  flex: 1;
}

.prod-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #FFFFFF;
  display: block;
}

.price-tags-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 3px;
}

.price-selling {
  font-size: 0.95rem;
  font-weight: 800;
  color: #34D399;
}

.price-cost {
  font-size: 0.72rem;
  color: #64748B;
}

.btn-edit {
  background: none;
  border: none;
  color: #64748B;
  font-size: 18px;
}

.prod-desc {
  font-size: 0.8rem;
  color: #94A3B8;
  margin: 10px 0 0 0;
  line-height: 1.4;
}

.product-actions-bar {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.btn-action-pill {
  flex: 1;
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #CBD5E1;
  padding: 8px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-action-pill.guide {
  color: #38BDF8;
}

.guide-display-box {
  margin-top: 10px;
  background: #0B1120;
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 10px;
  padding: 10px;
}

.guide-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: #38BDF8;
  margin-bottom: 6px;
}

.btn-copy-sm {
  background: #0D9488;
  color: #fff;
  border: none;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
}

.guide-content {
  font-size: 0.75rem;
  color: #CBD5E1;
  white-space: pre-wrap;
  line-height: 1.4;
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

.btn-create-product-empty {
  background: #0D9488;
  color: #fff;
  border: none;
  padding: 10px 18px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
}
</style>
