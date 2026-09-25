<template>
  <div class="products-view">
    <!-- Header with Search and New Product Action -->
    <div class="view-header">
      <div class="search-box">
        <Search :size="18" class="search-icon" />
        <input
          v-model="searchQuery"
          @input="fetchProducts"
          type="text"
          class="form-input search-input"
          placeholder="Rechercher une licence, un logiciel..."
        />
      </div>

      <button @click="openCreateModal" class="btn btn-primary">
        <Plus :size="18" />
        <span>Nouveau Produit</span>
      </button>
    </div>

    <!-- Products Grid -->
    <div v-if="loading" class="loading-state">
      <RefreshCw :size="28" class="spin-icon text-primary" />
      <span>Chargement des licences...</span>
    </div>

    <div v-else-if="products.length" class="products-grid">
      <div v-for="prod in products" :key="prod.id" class="card product-card">
        <!-- Top Card Row with Product Photo or Fallback -->
        <div class="prod-card-top">
          <div v-if="prod.image" class="prod-img-box" :title="isGoogleDriveUrl(prod.image) ? 'Photo hébergée sur Google Drive' : 'Photo du produit'">
            <img
              :src="resolveImageUrl(prod.image)"
              :alt="prod.nom"
              class="prod-img"
              loading="lazy"
              @error="onCardImageError($event, prod)"
            />
          </div>
          <div v-else class="prod-icon-box">
            <Package :size="24" />
          </div>
          <div class="prod-pricing">
            <span class="price-active">{{ formatPrice(prod.prix_actif) }}</span>
            <span class="price-buy">Achat : {{ formatPrice(prod.prix_achat) }}</span>
          </div>
        </div>

        <!-- Product Title & Description -->
        <div class="prod-body">
          <h3 class="prod-title">{{ prod.nom }}</h3>
          <p class="prod-desc">{{ prod.description || 'Aucune description spécifiée.' }}</p>
        </div>

        <!-- Links & Info -->
        <div class="prod-links">
          <a
            v-if="prod.lien_achat"
            :href="prod.lien_achat"
            target="_blank"
            rel="noopener noreferrer"
            class="buy-link"
          >
            <ExternalLink :size="14" />
            <span>Lien d'approvisionnement</span>
          </a>
          <span v-else class="text-xs text-muted">Pas de lien d'approvisionnement</span>
        </div>

        <!-- Card Footer Actions -->
        <div class="prod-card-footer">
          <button @click="openDetailModal(prod)" class="btn btn-secondary btn-sm" title="Fiche détaillée et historique">
            <Eye :size="16" />
            <span>Détails & Guide</span>
          </button>

          <button @click="openPriceModal(prod)" class="btn btn-secondary btn-sm" title="Modifier le prix actif">
            <Tag :size="16" />
            <span>Prix</span>
          </button>

          <button @click="deleteProduct(prod)" class="btn-icon btn-danger-icon" title="Supprimer">
            <Trash2 :size="16" />
          </button>
        </div>
      </div>
    </div>

    <div v-else class="empty-state card">
      <Package :size="48" class="text-muted" />
      <h3>Aucun produit trouvé</h3>
      <p class="text-muted text-sm">Ajoutez un premier produit à votre catalogue ou modifiez votre recherche.</p>
      <button @click="openCreateModal" class="btn btn-primary mt-2">
        <Plus :size="16" />
        <span>Créer un Produit</span>
      </button>
    </div>

    <!-- MODAL: Créer un Produit -->
    <div v-if="showCreateModal" class="modal-backdrop">
      <div class="modal-card card animate-fade">
        <div class="modal-header">
          <h3>Nouveau Produit & Licence</h3>
          <button @click="showCreateModal = false" class="btn-close"><X :size="20" /></button>
        </div>

        <form @submit.prevent="submitCreateProduct" class="modal-body">
          <div class="form-group">
            <label class="form-label">Nom du produit / licence *</label>
            <input v-model="form.nom" required type="text" class="form-input" placeholder="Ex: Windows 11 Pro Retail" />
          </div>

          <div class="form-group">
            <label class="form-label">Description</label>
            <textarea v-model="form.description" rows="2" class="form-textarea" placeholder="Détails, compatibilité..."></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Prix d'achat (Coût de revient) *</label>
              <input v-model.number="form.prix_achat" required type="number" step="100" class="form-input" placeholder="Ex: 15000" />
            </div>

            <div class="form-group">
              <label class="form-label">Prix de vente initial *</label>
              <input v-model.number="form.prix_initial" required type="number" step="100" class="form-input" placeholder="Ex: 35000" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Lien d'achat fournisseur / grossiste</label>
            <input v-model="form.lien_achat" type="url" class="form-input" placeholder="https://fournisseur.com/item/..." />
          </div>

          <!-- Image / Photo du produit (Lien Google Drive ou URL) -->
          <div class="form-group">
            <div class="flex items-center justify-between mb-1">
              <label class="form-label" style="margin-bottom: 0;">Photo du produit (Lien Google Drive)</label>
              <span v-if="isGoogleDriveUrl(form.image)" class="badge-drive text-xs">
                <Check :size="12" /> Google Drive détecté
              </span>
            </div>

            <div class="image-uploader-field">
              <!-- Live Preview if link entered or file chosen -->
              <div v-if="imagePreview || form.image" class="preview-container">
                <img
                  :src="imagePreview || resolveImageUrl(form.image)"
                  alt="Aperçu photo"
                  class="image-preview"
                  @error="handlePreviewError"
                />
                <button type="button" @click="clearImage" class="btn-clear-preview" title="Supprimer la photo">
                  <X :size="14" />
                </button>
              </div>

              <!-- Google Drive URL input with icon -->
              <div class="drive-input-wrapper">
                <div class="input-with-icon">
                  <Link2 :size="15" class="field-icon text-primary" />
                  <input
                    v-model="form.image"
                    type="text"
                    class="form-input drive-main-input"
                    placeholder="https://drive.google.com/file/d/.../view?usp=sharing"
                    @input="imagePreview = null"
                  />
                </div>
                <p class="drive-hint">
                  💡 <strong>Google Drive :</strong> Collez le lien de partage du fichier photo (Assurez-vous que l'accès est défini sur <em>« Tous les utilisateurs disposant du lien »</em>).
                </p>
              </div>

              <!-- Secondary local file option -->
              <div class="upload-options-secondary">
                <span class="text-xs text-muted">Ou importer un fichier local :</span>
                <label class="btn btn-secondary btn-xs upload-btn">
                  <Upload :size="13" />
                  <span>Fichier local</span>
                  <input type="file" accept="image/*" class="hidden-input" @change="onFileChange" />
                </label>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Guide d'activation (Instructions client)</label>
            <textarea v-model="form.description_activation" rows="3" class="form-textarea" placeholder="Ex: 1. Aller dans Paramètres > Activation..."></textarea>
          </div>

          <div class="modal-actions">
            <button @click="showCreateModal = false" type="button" class="btn btn-secondary">Annuler</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              <span v-if="submitting">Enregistrement...</span>
              <span v-else>Créer le produit</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL: Fiche Détaillée & Historique -->
    <div v-if="showDetailModal && selectedProduct" class="modal-backdrop">
      <div class="modal-card modal-lg card animate-fade">
        <div class="modal-header">
          <div>
            <h3>{{ selectedProduct.nom }}</h3>
            <span class="text-xs text-muted">Créé le {{ formatDate(selectedProduct.created_at) }}</span>
          </div>
          <button @click="showDetailModal = false" class="btn-close"><X :size="20" /></button>
        </div>

        <div class="modal-body detail-grid">
          <!-- Product Photo Header & Controls -->
          <div class="detail-product-photo-card">
            <div class="detail-photo-wrapper">
              <img
                v-if="selectedProduct.image"
                :src="resolveImageUrl(selectedProduct.image)"
                :alt="selectedProduct.nom"
                class="detail-photo-img"
                @error="onCardImageError($event, selectedProduct)"
              />
              <div v-else class="detail-photo-placeholder">
                <Package :size="32" class="text-muted" />
                <span class="text-xs text-muted">Sans photo</span>
              </div>
            </div>

            <div class="detail-photo-info">
              <div class="flex items-center gap-2">
                <span class="text-xs font-semibold text-muted">Illustration produit</span>
                <span v-if="isGoogleDriveUrl(selectedProduct.image)" class="badge-drive">
                  Google Drive
                </span>
              </div>

              <!-- Normal view buttons -->
              <div v-if="!editingPhotoLink" class="detail-photo-ctrls">
                <button
                  type="button"
                  @click="startEditingPhotoLink"
                  class="btn btn-secondary btn-xs"
                  title="Modifier ou coller le lien Google Drive"
                >
                  <Link2 :size="13" />
                  <span>{{ selectedProduct.image ? 'Modifier le lien' : 'Ajouter lien Google Drive' }}</span>
                </button>

                <a
                  v-if="selectedProduct.image && isGoogleDriveUrl(selectedProduct.image)"
                  :href="getGoogleDriveViewerUrl(selectedProduct.image)"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn btn-secondary btn-xs"
                  title="Ouvrir dans Google Drive"
                >
                  <ExternalLink :size="13" />
                  <span>Ouvrir sur Drive</span>
                </a>

                <label class="btn btn-secondary btn-xs upload-btn" title="Téléverser un fichier local">
                  <Upload :size="13" />
                  <span>{{ uploadingPhoto ? 'Envoi...' : 'Fichier' }}</span>
                  <input type="file" accept="image/*" class="hidden-input" @change="handleDetailPhotoUpload" :disabled="uploadingPhoto" />
                </label>

                <button
                  v-if="selectedProduct.image"
                  type="button"
                  @click="removeDetailPhoto"
                  class="btn btn-secondary btn-xs text-danger"
                  title="Supprimer la photo"
                >
                  <Trash2 :size="13" />
                </button>
              </div>

              <!-- Inline editing form for Drive link -->
              <div v-else class="photo-edit-form">
                <div class="input-with-icon">
                  <Link2 :size="14" class="field-icon text-primary" />
                  <input
                    v-model="photoLinkInput"
                    type="text"
                    class="form-input text-xs drive-input-inline"
                    placeholder="Collez le lien Google Drive..."
                    @keydown.enter.prevent="savePhotoLink"
                  />
                </div>
                <div class="photo-edit-actions">
                  <button
                    type="button"
                    @click="savePhotoLink"
                    class="btn btn-primary btn-xs"
                    :disabled="savingPhotoLink"
                  >
                    <Check :size="13" />
                    <span>{{ savingPhotoLink ? 'Enregistrement...' : 'Enregistrer' }}</span>
                  </button>
                  <button
                    type="button"
                    @click="cancelEditingPhotoLink"
                    class="btn btn-secondary btn-xs"
                  >
                    Annuler
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Guide d'activation -->
          <div class="detail-box">
            <div class="box-header">
              <div class="flex items-center gap-2">
                <FileText :size="18" class="text-primary" />
                <h4>Procédure d'activation</h4>
              </div>
              <button @click="copyActivationGuide" class="btn btn-secondary btn-xs">
                <Copy :size="14" />
                <span>{{ copied ? 'Copié !' : 'Copier guide' }}</span>
              </button>
            </div>
            <div class="activation-content">
              <p v-if="activationGuide">{{ activationGuide }}</p>
              <p v-else class="text-muted italic">Aucun guide d'activation rédigé pour ce produit.</p>
            </div>
          </div>

          <!-- Historique des Prix -->
          <div class="detail-box">
            <div class="box-header">
              <div class="flex items-center gap-2">
                <Clock :size="18" class="text-amber" />
                <h4>Historique des tarifs</h4>
              </div>
              <button @click="openPriceModal(selectedProduct)" class="btn btn-primary btn-xs">
                <Plus :size="14" />
                <span>Nouveau prix</span>
              </button>
            </div>

            <div class="price-history-list">
              <div
                v-for="p in selectedProduct.prix_historique || []"
                :key="p.id"
                class="price-history-row"
                :class="{ 'price-current': p.is_active }"
              >
                <div>
                  <span class="price-history-val">{{ formatPrice(p.prix) }}</span>
                  <span class="price-date">{{ formatDate(p.created_at) }}</span>
                </div>
                <div>
                  <span v-if="p.is_active" class="badge badge-success">Actif</span>
                  <span v-else class="badge badge-secondary">Archivé</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL: Changer Prix Actif -->
    <div v-if="showPriceModal && selectedProduct" class="modal-backdrop">
      <div class="modal-card card animate-fade" style="max-width: 400px;">
        <div class="modal-header">
          <h3>Changer le Prix Actif</h3>
          <button @click="showPriceModal = false" class="btn-close"><X :size="20" /></button>
        </div>

        <form @submit.prevent="submitChangePrice" class="modal-body">
          <p class="text-sm text-muted mb-2">
            Produit : <strong>{{ selectedProduct.nom }}</strong>
          </p>
          <div class="form-group">
            <label class="form-label">Nouveau prix de vente (Ar) *</label>
            <input v-model.number="newPrice" required type="number" step="100" class="form-input" placeholder="Ex: 40000" />
          </div>

          <div class="modal-actions">
            <button @click="showPriceModal = false" type="button" class="btn btn-secondary">Annuler</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">Appliquer</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  Package,
  Search,
  Plus,
  ExternalLink,
  Eye,
  Tag,
  Trash2,
  RefreshCw,
  X,
  FileText,
  Copy,
  Clock,
  Upload,
  Link2,
  Check
} from '@lucide/vue'
import apiClient from '../api/client'
import {
  resolveImageUrl,
  isGoogleDriveUrl,
  getGoogleDriveViewerUrl,
  getGoogleDriveThumbnailFallback
} from '../utils/imageHelper'

const products = ref([])
const loading = ref(false)
const searchQuery = ref('')
const submitting = ref(false)

// Modals & Photos
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const showPriceModal = ref(false)
const selectedProduct = ref(null)
const activationGuide = ref('')
const newPrice = ref(null)
const copied = ref(false)

const imagePreview = ref(null)
const selectedFile = ref(null)
const uploadingPhoto = ref(false)

// Inline Google Drive photo link editor in Detail Modal
const editingPhotoLink = ref(false)
const photoLinkInput = ref('')
const savingPhotoLink = ref(false)

const form = ref({
  nom: '',
  description: '',
  image: '',
  prix_achat: '',
  prix_initial: '',
  lien_achat: '',
  description_activation: '',
})

function onFileChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  selectedFile.value = file
  const reader = new FileReader()
  reader.onload = (event) => {
    imagePreview.value = event.target.result
    form.value.image = event.target.result // base64 fallback
  }
  reader.readAsDataURL(file)
}

function clearImage() {
  selectedFile.value = null
  imagePreview.value = null
  form.value.image = ''
}

function onCardImageError(event, prod) {
  const img = event.target
  if (!img) return
  if (prod?.image && isGoogleDriveUrl(prod.image) && !img.dataset.fallbackTried) {
    img.dataset.fallbackTried = 'true'
    img.src = getGoogleDriveThumbnailFallback(prod.image)
    return
  }
  img.style.display = 'none'
  if (img.parentElement) {
    img.parentElement.classList.add('img-load-failed')
  }
}

function handlePreviewError(event) {
  const img = event.target
  if (!img) return
  if (form.value.image && isGoogleDriveUrl(form.value.image) && !img.dataset.fallbackTried) {
    img.dataset.fallbackTried = 'true'
    img.src = getGoogleDriveThumbnailFallback(form.value.image)
  }
}

function startEditingPhotoLink() {
  photoLinkInput.value = selectedProduct.value?.image || ''
  editingPhotoLink.value = true
}

function cancelEditingPhotoLink() {
  editingPhotoLink.value = false
  photoLinkInput.value = ''
}

async function savePhotoLink() {
  if (!selectedProduct.value) return
  savingPhotoLink.value = true
  try {
    const trimmed = photoLinkInput.value.trim()
    const res = await apiClient.patch(`/produits/${selectedProduct.value.id}/`, {
      image: trimmed
    })
    selectedProduct.value.image = res.data.image
    editingPhotoLink.value = false
    await fetchProducts()
  } catch (err) {
    alert("Erreur lors de l'enregistrement du lien de l'image.")
  } finally {
    savingPhotoLink.value = false
  }
}

async function handleDetailPhotoUpload(e) {
  const file = e.target.files?.[0]
  if (!file || !selectedProduct.value) return
  uploadingPhoto.value = true
  try {
    const formData = new FormData()
    formData.append('image', file)
    const res = await apiClient.post(`/produits/${selectedProduct.value.id}/upload-image/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    selectedProduct.value.image = res.data.image
    await fetchProducts()
  } catch (err) {
    alert("Erreur lors de l'envoi de la photo.")
  } finally {
    uploadingPhoto.value = false
  }
}

async function removeDetailPhoto() {
  if (!confirm("Retirer la photo de ce produit ?")) return
  try {
    await apiClient.patch(`/produits/${selectedProduct.value.id}/`, { image: '' })
    selectedProduct.value.image = ''
    editingPhotoLink.value = false
    photoLinkInput.value = ''
    await fetchProducts()
  } catch (err) {
    alert("Erreur lors de la suppression de la photo.")
  }
}

async function fetchProducts() {
  loading.value = true
  try {
    const res = await apiClient.get('/produits/', {
      params: { search: searchQuery.value }
    })
    products.value = res.data
  } catch (err) {
    console.error('Erreur chargement produits:', err)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  form.value = {
    nom: '',
    description: '',
    image: '',
    prix_achat: '',
    prix_initial: '',
    lien_achat: '',
    description_activation: '',
  }
  clearImage()
  showCreateModal.value = true
}

async function submitCreateProduct() {
  submitting.value = true
  try {
    const res = await apiClient.post('/produits/', form.value)
    const newProd = res.data

    if (selectedFile.value && newProd.id) {
      try {
        const formData = new FormData()
        formData.append('image', selectedFile.value)
        await apiClient.post(`/produits/${newProd.id}/upload-image/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      } catch (uploadErr) {
        console.warn("Échec upload multipart, conservé en base64:", uploadErr)
      }
    }

    showCreateModal.value = false
    await fetchProducts()
  } catch (err) {
    alert(err.response?.data?.detail || "Erreur lors de la création du produit")
  } finally {
    submitting.value = false
  }
}

async function openDetailModal(prod) {
  selectedProduct.value = prod
  copied.value = false
  showDetailModal.value = true
  try {
    const res = await apiClient.get(`/produits/${prod.id}/activation/`)
    activationGuide.value = res.data.description_activation || ''
  } catch (err) {
    activationGuide.value = ''
  }
}

function openPriceModal(prod) {
  selectedProduct.value = prod
  newPrice.value = prod.prix_actif || ''
  showPriceModal.value = true
}

async function submitChangePrice() {
  if (!newPrice.value) return
  submitting.value = true
  try {
    await apiClient.post(`/produits/${selectedProduct.value.id}/changer-prix/`, {
      prix: newPrice.value
    })
    showPriceModal.value = false
    await fetchProducts()
    if (showDetailModal.value) {
      // Rafraîchir le produit sélectionné
      const updated = products.value.find(p => p.id === selectedProduct.value.id)
      if (updated) selectedProduct.value = updated
    }
  } catch (err) {
    alert(err.response?.data?.error || "Erreur lors de la modification du prix")
  } finally {
    submitting.value = false
  }
}

async function deleteProduct(prod) {
  if (!confirm(`Supprimer définitivement le produit "${prod.nom}" ?`)) return
  try {
    await apiClient.delete(`/produits/${prod.id}/`)
    await fetchProducts()
  } catch (err) {
    alert("Impossible de supprimer ce produit car il est lié à des ventes existantes.")
  }
}

function copyActivationGuide() {
  if (!activationGuide.value) return
  navigator.clipboard.writeText(activationGuide.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

function formatPrice(val) {
  if (val === null || val === undefined) return '-'
  return new Intl.NumberFormat('fr-MG').format(val) + ' Ar'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.products-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.view-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.search-input {
  width: 100%;
  padding-left: 2.75rem;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.25rem;
}

.product-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1.25rem;
  gap: 1rem;
}

.prod-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.prod-img-box {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid rgba(0, 210, 255, 0.35);
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 0 15px rgba(0, 210, 255, 0.15);
}

.prod-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card:hover .prod-img {
  transform: scale(1.1);
}

.badge-drive {
  background: rgba(0, 210, 255, 0.12);
  color: #00d2ff;
  border: 1px solid rgba(0, 210, 255, 0.35);
  font-size: 0.72rem;
  padding: 0.15rem 0.55rem;
  border-radius: var(--radius-full);
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-weight: 600;
}

.image-uploader-field {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.preview-container {
  position: relative;
  width: 96px;
  height: 96px;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1.5px solid var(--primary-color);
  box-shadow: 0 0 15px rgba(0, 210, 255, 0.25);
  background: rgba(0, 0, 0, 0.4);
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-clear-preview {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.75);
  color: white;
  border: none;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-clear-preview:hover {
  background: #ef4444;
}

.drive-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  width: 100%;
}

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.input-with-icon .field-icon {
  position: absolute;
  left: 0.75rem;
  pointer-events: none;
}

.input-with-icon .form-input {
  padding-left: 2.3rem;
}

.drive-main-input {
  width: 100%;
  font-family: monospace;
  font-size: 0.85rem;
}

.drive-hint {
  font-size: 0.74rem;
  color: var(--text-muted);
  line-height: 1.45;
  margin: 0;
}

.drive-hint strong {
  color: var(--primary-color);
}

.drive-hint em {
  color: #38bdf8;
  font-style: normal;
}

.upload-options-secondary {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-top: 0.15rem;
}

.hidden-input {
  display: none;
}

.detail-product-photo-card {
  grid-column: span 2;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.15rem;
  background: rgba(0, 210, 255, 0.05);
  border: 1px solid rgba(0, 210, 255, 0.2);
  border-radius: var(--radius-md);
}

.detail-photo-wrapper {
  width: 82px;
  height: 82px;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.detail-photo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-photo-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.detail-photo-info {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  flex: 1;
}

.detail-photo-ctrls {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.photo-edit-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
  max-width: 480px;
}

.photo-edit-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.drive-input-inline {
  width: 100%;
  font-family: monospace;
}

.img-load-failed {
  background: rgba(239, 68, 68, 0.1) !important;
  border-color: rgba(239, 68, 68, 0.3) !important;
}

.prod-icon-box {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  background: var(--primary-light);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.prod-pricing {
  text-align: right;
  display: flex;
  flex-direction: column;
}

.price-active {
  font-size: 1.25rem;
  font-weight: 800;
  color: #34d399;
}

.price-buy {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.prod-title {
  font-size: 1.05rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
}

.prod-desc {
  font-size: 0.825rem;
  color: var(--text-secondary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.prod-links {
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-subtle);
}

.buy-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  color: var(--primary);
  text-decoration: none;
}

.buy-link:hover {
  text-decoration: underline;
}

.prod-card-footer {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-subtle);
}

.prod-card-footer .btn-sm {
  flex: 1;
}

.btn-danger-icon {
  background: rgba(244, 63, 94, 0.1);
  border: 1px solid rgba(244, 63, 94, 0.2);
  color: var(--rose);
}

.btn-danger-icon:hover {
  background: var(--rose);
  color: white;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  gap: 1rem;
  text-align: center;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(6px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.modal-card {
  width: 100%;
  max-width: 550px;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: var(--radius-xl);
  padding: 1.75rem;
}

.modal-lg {
  max-width: 750px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}

.detail-box {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.box-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.activation-content {
  background: rgba(0, 0, 0, 0.3);
  padding: 1rem;
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: 0.8rem;
  white-space: pre-wrap;
  line-height: 1.5;
  color: #cbd5e1;
  max-height: 250px;
  overflow-y: auto;
}

.price-history-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 250px;
  overflow-y: auto;
}

.price-history-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 0.85rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

.price-current {
  border-color: rgba(16, 185, 129, 0.4);
  background: rgba(16, 185, 129, 0.05);
}

.price-history-val {
  font-weight: 700;
  font-size: 0.9rem;
  margin-right: 0.5rem;
}

.price-date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.btn-xs {
  padding: 0.3rem 0.65rem;
  font-size: 0.75rem;
}

.btn-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
}
</style>
