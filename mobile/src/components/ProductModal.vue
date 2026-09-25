<template>
  <ion-modal :is-open="isOpen" @didDismiss="$emit('close')" :initial-breakpoint="0.95" :breakpoints="[0, 0.95, 1]">
    <ion-header>
      <ion-toolbar class="modal-toolbar">
        <ion-title>{{ isEditing ? 'Modifier Produit' : 'Nouveau Logiciel' }}</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="$emit('close')">
            <ion-icon :icon="closeOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding modal-content">
      <div v-if="errorMessage" class="error-banner">
        {{ errorMessage }}
      </div>

      <div class="form-group">
        <label class="form-label">Nom du logiciel ou de la licence *</label>
        <input
          v-model="form.nom"
          type="text"
          placeholder="Ex: Windows 11 Pro 64-bit"
          class="mobile-input"
        />
      </div>

      <div class="grid-2">
        <div class="form-group">
          <label class="form-label">Prix de vente client (Ar) *</label>
          <input
            v-model.number="form.prix_vente"
            type="number"
            placeholder="Ex: 35000"
            class="mobile-input"
          />
        </div>
        <div class="form-group">
          <label class="form-label">Coût d'achat (Ar)</label>
          <input
            v-model.number="form.prix_achat"
            type="number"
            placeholder="Ex: 10000"
            class="mobile-input"
          />
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Description commerciale</label>
        <textarea
          v-model="form.description"
          rows="2"
          placeholder="Détails, fonctionnalités, compatibilité..."
          class="mobile-textarea"
        ></textarea>
      </div>

      <div class="form-group">
        <label class="form-label">Guide d'activation (Fourni au client)</label>
        <textarea
          v-model="form.description_activation"
          rows="3"
          placeholder="Ex: 1. Télécharger l'ISO officielle. 2. Entrer la clé transmise..."
          class="mobile-textarea"
        ></textarea>
      </div>

      <div class="form-group">
        <label class="form-label">URL de l'image (optionnel)</label>
        <input
          v-model="form.image"
          type="url"
          placeholder="https://..."
          class="mobile-input"
        />
      </div>

      <button
        type="button"
        @click="saveProduct"
        :disabled="isSubmitting || !form.nom.trim() || !form.prix_vente"
        class="btn-submit"
      >
        <span v-if="isSubmitting">Enregistrement...</span>
        <span v-else>{{ isEditing ? 'Sauvegarder les modifications' : 'Créer le produit' }}</span>
      </button>
    </ion-content>
  </ion-modal>
</template>

<script setup>
import { ref, watch } from 'vue'
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
import { closeOutline } from 'ionicons/icons'
import apiClient from '../api/client'

const props = defineProps({
  isOpen: Boolean,
  productData: Object,
})
const emit = defineEmits(['close', 'saved'])

const isEditing = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')

const form = ref({
  nom: '',
  description: '',
  prix_achat: 0,
  prix_vente: 0,
  description_activation: '',
  image: '',
  lien_achat: '',
})

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      errorMessage.value = ''
      if (props.productData && props.productData.id) {
        isEditing.value = true
        const activation = props.productData.activations?.[0]?.description_activation || ''
        form.value = {
          nom: props.productData.nom || '',
          description: props.productData.description || '',
          prix_achat: Number(props.productData.prix_achat) || 0,
          prix_vente: props.productData.prix_actif ? Number(props.productData.prix_actif) : 0,
          description_activation: activation,
          image: props.productData.image || '',
          lien_achat: props.productData.lien_achat || '',
        }
      } else {
        isEditing.value = false
        form.value = {
          nom: '',
          description: '',
          prix_achat: 0,
          prix_vente: 0,
          description_activation: '',
          image: '',
          lien_achat: '',
        }
      }
    }
  }
)

async function saveProduct() {
  if (!form.value.nom.trim()) return
  isSubmitting.value = true
  errorMessage.value = ''

  try {
    if (isEditing.value) {
      // 1. Update basic product info
      const res = await apiClient.patch(`/produits/${props.productData.id}/`, {
        nom: form.value.nom.trim(),
        description: form.value.description,
        prix_achat: form.value.prix_achat,
        image: form.value.image,
        lien_achat: form.value.lien_achat,
      })

      // 2. If selling price changed, call changer-prix
      const currentPrice = props.productData.prix_actif ? Number(props.productData.prix_actif) : null
      if (form.value.prix_vente && form.value.prix_vente !== currentPrice) {
        await apiClient.post(`/produits/${props.productData.id}/changer-prix/`, {
          prix: form.value.prix_vente,
        })
      }

      // 3. Update activation guide
      if (form.value.description_activation !== undefined) {
        await apiClient.post(`/produits/${props.productData.id}/activation/`, {
          description_activation: form.value.description_activation,
        })
      }

      emit('saved', res.data)
    } else {
      // Create product
      const res = await apiClient.post('/produits/', {
        nom: form.value.nom.trim(),
        description: form.value.description,
        prix_achat: form.value.prix_achat,
        prix_initial: form.value.prix_vente,
        description_activation: form.value.description_activation,
        image: form.value.image,
        lien_achat: form.value.lien_achat,
      })
      emit('saved', res.data)
    }

    emit('close')
  } catch (err) {
    errorMessage.value =
      err.response?.data?.error ||
      err.response?.data?.detail ||
      "Une erreur est survenue lors de l'enregistrement du produit."
  } finally {
    isSubmitting.value = false
  }
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
}

.form-group {
  margin-bottom: 14px;
}

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.form-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: #94A3B8;
  margin-bottom: 6px;
}

.mobile-input,
.mobile-textarea {
  width: 100%;
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 10px 12px;
  color: #FFFFFF;
  font-size: 0.88rem;
  outline: none;
}

.mobile-textarea {
  resize: none;
}

.btn-submit {
  width: 100%;
  margin-top: 16px;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #0D9488 0%, #0284C7 100%);
  color: #FFFFFF;
  border: none;
  padding: 14px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.95rem;
}

.btn-submit:disabled {
  opacity: 0.5;
}
</style>
