<template>
  <ion-modal :is-open="isOpen" @didDismiss="handleDismiss" :initial-breakpoint="0.95" :breakpoints="[0, 0.95, 1]">
    <ion-header>
      <ion-toolbar class="modal-toolbar">
        <ion-title>{{ isEditing ? `Modifier la Vente #${saleToEdit?.id}` : 'Nouvelle Vente' }}</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="handleDismiss">
            <ion-icon :icon="closeOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding modal-content">
      <!-- Error banner if any -->
      <div v-if="errorMessage" class="error-banner">
        {{ errorMessage }}
      </div>

      <!-- 1. DATE & HEURE DE LA VENTE -->
      <div class="form-section">
        <div class="section-title">
          <span>Date & Heure de la vente</span>
          <button type="button" @click="setDateToNow" class="btn-text-action">
            Maintenant
          </button>
        </div>
        <input
          v-model="saleDate"
          type="datetime-local"
          class="mobile-input date-input"
        />
      </div>

      <!-- 2. SÉLECTION DU CLIENT -->
      <div class="form-section">
        <div class="section-title">
          <span>Client acheteur</span>
          <button v-if="!isEditing" type="button" @click="showQuickClient = !showQuickClient" class="btn-text-action">
            {{ showQuickClient ? 'Choisir existant' : '+ Créer un client' }}
          </button>
        </div>

        <!-- Nouveau client rapide (création seule) -->
        <div v-if="showQuickClient && !isEditing" class="quick-client-box">
          <input
            v-model="newClientForm.nom"
            type="text"
            placeholder="Nom complet du client *"
            class="mobile-input"
          />
          <input
            v-model="newClientForm.numero"
            type="tel"
            placeholder="Numéro WhatsApp / Tél"
            class="mobile-input"
          />
          <select v-model="newClientForm.id_provenance" class="mobile-select">
            <option value="">Provenance (optionnel)</option>
            <option v-for="prov in provenances" :key="prov.id" :value="prov.id">
              {{ prov.label }}
            </option>
          </select>
          <button
            type="button"
            @click="createQuickClient"
            class="btn-quick-save"
            :disabled="!newClientForm.nom.trim() || clientSaving"
          >
            {{ clientSaving ? 'Création...' : 'Valider ce nouveau client' }}
          </button>
        </div>

        <!-- Sélection existant -->
        <div v-else>
          <select v-model="selectedClientId" class="mobile-select">
            <option value="">-- Sélectionnez un client --</option>
            <option v-for="c in clients" :key="c.id" :value="c.id">
              {{ c.nom }} {{ c.numero ? `(${c.numero})` : '' }}
            </option>
          </select>
        </div>
      </div>

      <!-- 3. ARTICLES DE LA COMMANDE -->
      <div class="form-section">
        <div class="section-title">
          <span>Articles commandés</span>
          <span class="badge-count">{{ orderArticles.length }} article(s)</span>
        </div>

        <div v-for="(item, idx) in orderArticles" :key="idx" class="article-row">
          <div class="article-main">
            <select
              v-model="item.produit_id"
              @change="onProductSelect(item)"
              class="mobile-select product-select"
            >
              <option value="">Sélectionner un produit...</option>
              <option v-for="p in products" :key="p.id" :value="p.id">
                {{ p.nom }} - {{ formatPrice(p.prix_actif ?? p.prix_achat) }}
              </option>
            </select>

            <div class="article-controls">
              <!-- Stepper Quantité -->
              <div class="stepper">
                <button type="button" @click="decrementQty(item)" class="step-btn">-</button>
                <span class="step-value">{{ item.quantite }}</span>
                <button type="button" @click="incrementQty(item)" class="step-btn">+</button>
              </div>

              <!-- Prix unitaire -->
              <div class="price-input-wrap">
                <input
                  v-model.number="item.prix_unitaire"
                  type="number"
                  placeholder="Prix unitaire"
                  class="mobile-input price-input"
                />
                <span class="currency-tag">Ar</span>
              </div>

              <!-- Revenir au prix catalogue si modifié -->
              <button
                type="button"
                v-if="hasDifferentPrice(item)"
                @click="resetToCatalogPrice(item)"
                class="btn-reset-price"
                title="Rétablir le prix catalogue actif"
              >
                <ion-icon :icon="refreshOutline" />
              </button>

              <!-- Delete -->
              <button
                type="button"
                @click="removeArticle(idx)"
                class="btn-del-article"
                v-if="orderArticles.length > 1"
              >
                <ion-icon :icon="trashOutline" />
              </button>
            </div>
          </div>

          <div class="subtotal-row">
            Sous-total : <strong>{{ formatPrice(item.quantite * (item.prix_unitaire || 0)) }}</strong>
          </div>
        </div>

        <button type="button" @click="addArticleRow" class="btn-add-article">
          <ion-icon :icon="addOutline" />
          <span>Ajouter un autre produit</span>
        </button>
      </div>

      <!-- 4. MÉTHODE DE PAIEMENT -->
      <div class="form-section">
        <div class="section-title">Mode de règlement</div>
        <div class="payment-grid">
          <div
            v-for="pm in paymentMethods"
            :key="pm.id"
            :class="['payment-card', selectedPaymentMethodId === pm.id ? 'active' : '']"
            @click="selectedPaymentMethodId = pm.id"
          >
            <span class="pm-name">{{ pm.label }}</span>
            <span v-if="pm.details" class="pm-detail">{{ pm.details }}</span>
          </div>
        </div>
      </div>

      <!-- 5. TOTAL & SOUMISSION -->
      <div class="total-summary-card">
        <div class="summary-line">
          <span>Nombre d'articles :</span>
          <b>{{ totalQuantity }}</b>
        </div>
        <div class="summary-line total">
          <span>Total :</span>
          <span class="grand-total">{{ formatPrice(grandTotal) }}</span>
        </div>

        <button
          type="button"
          @click="submitSale"
          :disabled="isSubmitting || !isFormValid"
          class="btn-submit-sale"
          :class="{ 'btn-submit-edit': isEditing }"
        >
          <span v-if="isSubmitting">
            {{ isEditing ? 'Mise à jour en cours...' : 'Enregistrement de la vente...' }}
          </span>
          <span v-else>
            {{ isEditing ? 'Enregistrer les modifications' : 'Valider & Enregistrer la Vente' }}
          </span>
        </button>
      </div>
    </ion-content>
  </ion-modal>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import {
  IonModal,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonButton,
  IonIcon,
  IonContent,
} from '@ionic/vue'
import { closeOutline, addOutline, trashOutline, refreshOutline } from 'ionicons/icons'
import apiClient from '../api/client'
import { useSaleDraft } from '../composables/useSaleDraft'

const props = defineProps({
  isOpen: Boolean,
  saleToEdit: {
    type: Object,
    default: null,
  },
})
const emit = defineEmits(['close', 'sale-created', 'sale-updated'])

const { activeDraft, closeSaleModal } = useSaleDraft()

const clients = ref([])
const products = ref([])
const paymentMethods = ref([])
const provenances = ref([])

function getLocalDateTimeString(date = new Date()) {
  const pad = (n) => String(n).padStart(2, '0')
  const year = date.getFullYear()
  const month = pad(date.getMonth() + 1)
  const day = pad(date.getDate())
  const hours = pad(date.getHours())
  const minutes = pad(date.getMinutes())
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

const saleDate = ref(getLocalDateTimeString())
const selectedClientId = ref('')
const selectedPaymentMethodId = ref('')
const orderArticles = ref([{ produit_id: '', quantite: 1, prix_unitaire: 0 }])

const isEditing = computed(() => !!props.saleToEdit)

const showQuickClient = ref(false)
const clientSaving = ref(false)
const newClientForm = ref({ nom: '', numero: '', id_provenance: '' })

const isSubmitting = ref(false)
const errorMessage = ref('')

function formatPrice(val) {
  if (!val && val !== 0) return '0 Ar'
  return Math.round(Number(val)).toLocaleString('fr-FR') + ' Ar'
}

function setDateToNow() {
  saleDate.value = getLocalDateTimeString()
}

function getProductActivePrice(productId) {
  const prod = products.value.find((p) => p.id === productId)
  if (!prod) return 0
  return Number(prod.prix_actif ?? prod.prix_achat ?? 0)
}

function hasDifferentPrice(item) {
  if (!item.produit_id) return false
  const activePrice = getProductActivePrice(item.produit_id)
  return item.prix_unitaire !== undefined && item.prix_unitaire !== null && Number(item.prix_unitaire) !== activePrice
}

function resetToCatalogPrice(item) {
  if (item.produit_id) {
    item.prix_unitaire = getProductActivePrice(item.produit_id)
  }
}

const totalQuantity = computed(() => {
  return orderArticles.value.reduce((acc, curr) => acc + (curr.quantite || 0), 0)
})

const grandTotal = computed(() => {
  return orderArticles.value.reduce((acc, curr) => acc + (curr.quantite || 0) * (curr.prix_unitaire || 0), 0)
})

const isFormValid = computed(() => {
  return (
    selectedClientId.value &&
    selectedPaymentMethodId.value &&
    orderArticles.value.length > 0 &&
    orderArticles.value.every((a) => a.produit_id && a.quantite > 0)
  )
})

onMounted(async () => {
  await loadReferenceData()
})

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      errorMessage.value = ''
      loadReferenceData().then(() => {
        if (props.saleToEdit) {
          populateFromSale(props.saleToEdit)
        } else {
          resetForm()
          applyDraftIfAny()
        }
      })
    }
  }
)

async function loadReferenceData() {
  try {
    const [clientsRes, prodsRes, payRes, provRes] = await Promise.all([
      apiClient.get('/clients/'),
      apiClient.get('/produits/'),
      apiClient.get('/methodes-paiement/'),
      apiClient.get('/clients/provenances/'),
    ])

    clients.value = clientsRes.data.results || clientsRes.data || []
    products.value = prodsRes.data.results || prodsRes.data || []
    paymentMethods.value = (payRes.data.results || payRes.data || []).filter((p) => p.is_active !== false)
    provenances.value = provRes.data.results || provRes.data || []

    if (!selectedPaymentMethodId.value && paymentMethods.value.length) {
      selectedPaymentMethodId.value = paymentMethods.value[0].id
    }
  } catch (err) {
    console.error('Erreur chargement données de vente:', err)
  }
}

function populateFromSale(sale) {
  selectedClientId.value = sale.client?.id || ''
  selectedPaymentMethodId.value = sale.methode_paiement?.id || (paymentMethods.value[0]?.id || '')
  saleDate.value = sale.date ? getLocalDateTimeString(new Date(sale.date)) : getLocalDateTimeString()

  if (sale.commandes && sale.commandes.length > 0) {
    orderArticles.value = sale.commandes.map((cmd) => {
      const prodId = cmd.produit?.id || cmd.produit
      return {
        produit_id: prodId,
        quantite: cmd.quantite || 1,
        prix_unitaire: Number(cmd.prix_unitaire || 0),
      }
    })
  } else {
    resetArticlesToDefault()
  }
}

function resetArticlesToDefault() {
  const firstProd = products.value[0]
  orderArticles.value = [
    {
      produit_id: firstProd ? firstProd.id : '',
      quantite: 1,
      prix_unitaire: firstProd ? Number(firstProd.prix_actif ?? firstProd.prix_achat ?? 0) : 0,
    },
  ]
}

function resetForm() {
  selectedClientId.value = clients.value[0]?.id || ''
  selectedPaymentMethodId.value = paymentMethods.value[0]?.id || ''
  saleDate.value = getLocalDateTimeString()
  resetArticlesToDefault()
  showQuickClient.value = false
  newClientForm.value = { nom: '', numero: '', id_provenance: '' }
}

function applyDraftIfAny() {
  if (!activeDraft.value) return
  const draft = activeDraft.value

  // Match or suggest client
  if (draft.client_nom) {
    const matched = clients.value.find((c) =>
      c.nom.toLowerCase().includes(draft.client_nom.toLowerCase())
    )
    if (matched) {
      selectedClientId.value = matched.id
    } else {
      showQuickClient.value = true
      newClientForm.value.nom = draft.client_nom
      if (draft.client_numero) newClientForm.value.numero = draft.client_numero
    }
  }

  // Match payment method
  if (draft.methode_paiement_id) {
    selectedPaymentMethodId.value = draft.methode_paiement_id
  }

  // Match articles
  if (draft.articles && draft.articles.length > 0) {
    const matchedArticles = []
    draft.articles.forEach((art) => {
      const p = products.value.find(
        (prod) =>
          (art.produit_id && prod.id === art.produit_id) ||
          (art.produit_nom && prod.nom.toLowerCase().includes(art.produit_nom.toLowerCase()))
      )
      if (p) {
        matchedArticles.push({
          produit_id: p.id,
          quantite: art.quantite || 1,
          prix_unitaire: art.prix_unitaire !== undefined ? Number(art.prix_unitaire) : Number(p.prix_actif ?? p.prix_achat ?? 0),
        })
      }
    })

    if (matchedArticles.length > 0) {
      orderArticles.value = matchedArticles
    }
  }
}

function onProductSelect(item) {
  const prod = products.value.find((p) => p.id === item.produit_id)
  if (prod) {
    item.prix_unitaire = Number(prod.prix_actif ?? prod.prix_achat ?? 0)
  }
}

function incrementQty(item) {
  item.quantite = (item.quantite || 1) + 1
}

function decrementQty(item) {
  if (item.quantite > 1) {
    item.quantite--
  }
}

function addArticleRow() {
  const firstProd = products.value[0]
  orderArticles.value.push({
    produit_id: firstProd ? firstProd.id : '',
    quantite: 1,
    prix_unitaire: firstProd ? Number(firstProd.prix_actif ?? firstProd.prix_achat ?? 0) : 0,
  })
}

function removeArticle(index) {
  orderArticles.value.splice(index, 1)
}

async function createQuickClient() {
  if (!newClientForm.value.nom.trim()) return
  clientSaving.value = true
  try {
    const payload = {
      nom: newClientForm.value.nom.trim(),
      numero: newClientForm.value.numero.trim() || null,
      id_provenance: newClientForm.value.id_provenance || null,
    }
    const res = await apiClient.post('/clients/', payload)
    const created = res.data
    clients.value.unshift(created)
    selectedClientId.value = created.id
    showQuickClient.value = false
    newClientForm.value = { nom: '', numero: '', id_provenance: '' }
  } catch (err) {
    alert("Impossible de créer le client. Vérifiez les informations.")
  } finally {
    clientSaving.value = false
  }
}

async function submitSale() {
  if (!isFormValid.value) return
  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const payload = {
      client_id: selectedClientId.value,
      methode_paiement_id: selectedPaymentMethodId.value,
      date: saleDate.value ? new Date(saleDate.value).toISOString() : undefined,
      articles: orderArticles.value.map((a) => ({
        produit_id: a.produit_id,
        quantite: a.quantite,
        prix_unitaire: a.prix_unitaire,
      })),
    }

    if (isEditing.value && props.saleToEdit?.id) {
      const res = await apiClient.put(`/ventes/${props.saleToEdit.id}/`, payload)
      emit('sale-updated', res.data)
    } else {
      const res = await apiClient.post('/ventes/', payload)
      emit('sale-created', res.data)
    }
    handleDismiss()
  } catch (err) {
    const errorData = err.response?.data
    if (typeof errorData === 'string') {
      errorMessage.value = errorData
    } else if (errorData?.error) {
      errorMessage.value = errorData.error
    } else if (errorData?.detail) {
      errorMessage.value = errorData.detail
    } else if (Array.isArray(errorData?.non_field_errors)) {
      errorMessage.value = errorData.non_field_errors.join(' ')
    } else if (typeof errorData === 'object' && errorData !== null) {
      const msgs = []
      for (const [k, v] of Object.entries(errorData)) {
        msgs.push(`${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
      }
      errorMessage.value = msgs.join('\n') || "Une erreur est survenue lors de l'enregistrement."
    } else {
      errorMessage.value = "Une erreur est survenue lors de l'enregistrement."
    }
  } finally {
    isSubmitting.value = false
  }
}

function handleDismiss() {
  closeSaleModal()
  emit('close')
}
</script>

<style scoped>
.modal-toolbar {
  --background: #0B1120;
  --color: #FFFFFF;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.modal-content {
  --background: #0B1120;
  --color: #F8FAFC;
}

.error-banner {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid #EF4444;
  color: #FCA5A5;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 0.85rem;
  margin-bottom: 16px;
  white-space: pre-line;
}

.form-section {
  margin-bottom: 18px;
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 14px;
  border-radius: 14px;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.88rem;
  font-weight: 700;
  color: #5EEAD4;
  margin-bottom: 12px;
}

.btn-text-action {
  background: transparent;
  color: #38BDF8;
  border: none;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.badge-count {
  background: rgba(94, 234, 212, 0.15);
  color: #5EEAD4;
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: 9999px;
  font-weight: 600;
}

.mobile-input,
.mobile-select {
  width: 100%;
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 10px 12px;
  color: #FFFFFF;
  font-size: 0.85rem;
  outline: none;
  margin-bottom: 8px;
}

.date-input {
  color-scheme: dark;
}

.quick-client-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.btn-quick-save {
  background: #0D9488;
  color: #fff;
  border: none;
  padding: 10px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.82rem;
}

.article-row {
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 10px;
  margin-bottom: 10px;
}

.product-select {
  margin-bottom: 8px;
}

.article-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stepper {
  display: flex;
  align-items: center;
  background: #1E293B;
  border-radius: 8px;
  overflow: hidden;
}

.step-btn {
  background: #334155;
  color: #FFFFFF;
  border: none;
  width: 32px;
  height: 34px;
  font-weight: bold;
}

.step-value {
  padding: 0 10px;
  font-weight: 600;
  font-size: 0.9rem;
}

.price-input-wrap {
  position: relative;
  flex: 1;
}

.price-input {
  margin-bottom: 0;
  padding-right: 28px;
}

.currency-tag {
  position: absolute;
  right: 10px;
  top: 9px;
  font-size: 0.75rem;
  color: #94A3B8;
}

.btn-reset-price {
  background: rgba(56, 189, 248, 0.15);
  color: #38BDF8;
  border: none;
  border-radius: 8px;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  cursor: pointer;
}

.btn-del-article {
  background: rgba(239, 68, 68, 0.2);
  color: #EF4444;
  border: none;
  border-radius: 8px;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.subtotal-row {
  margin-top: 6px;
  text-align: right;
  font-size: 0.78rem;
  color: #94A3B8;
}

.subtotal-row strong {
  color: #10B981;
}

.btn-add-article {
  width: 100%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px dashed rgba(255, 255, 255, 0.2);
  color: #94A3B8;
  padding: 10px;
  border-radius: 10px;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
}

.payment-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.payment-card {
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 10px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  cursor: pointer;
  transition: all 0.2s;
}

.payment-card.active {
  background: rgba(13, 148, 136, 0.15);
  border-color: #0D9488;
}

.pm-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #FFFFFF;
}

.pm-detail {
  font-size: 0.7rem;
  color: #94A3B8;
}

.total-summary-card {
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px;
  border-radius: 14px;
  margin-top: 16px;
  margin-bottom: 30px;
}

.summary-line {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  margin-bottom: 8px;
  color: #CBD5E1;
}

.summary-line.total {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 10px;
  margin-top: 10px;
  font-size: 1rem;
  font-weight: bold;
}

.grand-total {
  color: #10B981;
  font-size: 1.25rem;
}

.btn-submit-sale {
  width: 100%;
  margin-top: 14px;
  background: linear-gradient(135deg, #0D9488 0%, #0284C7 100%);
  color: #FFFFFF;
  border: none;
  padding: 14px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
}

.btn-submit-sale.btn-submit-edit {
  background: linear-gradient(135deg, #3B82F6 0%, #6366F1 100%);
}

.btn-submit-sale:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
