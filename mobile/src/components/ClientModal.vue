<template>
  <ion-modal :is-open="isOpen" @didDismiss="$emit('close')" :initial-breakpoint="0.8" :breakpoints="[0, 0.8, 1]">
    <ion-header>
      <ion-toolbar class="modal-toolbar">
        <ion-title>{{ isEditing ? 'Modifier Client' : 'Nouveau Client' }}</ion-title>
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
        <label class="form-label">Nom complet *</label>
        <input
          v-model="form.nom"
          type="text"
          placeholder="Ex: Rado Andrianina"
          class="mobile-input"
        />
      </div>

      <div class="form-group">
        <label class="form-label">Numéro WhatsApp / Téléphone</label>
        <input
          v-model="form.numero"
          type="tel"
          placeholder="Ex: 034 00 123 45"
          class="mobile-input"
        />
      </div>

      <div class="form-group">
        <label class="form-label">Provenance du client</label>
        <select v-model="form.provenance_id" class="mobile-select">
          <option :value="null">-- Non spécifié --</option>
          <option v-for="prov in provenances" :key="prov.id" :value="prov.id">
            {{ prov.label }}
          </option>
        </select>
      </div>

      <button
        type="button"
        @click="saveClient"
        :disabled="isSubmitting || !form.nom.trim()"
        class="btn-submit"
      >
        <span v-if="isSubmitting">Enregistrement...</span>
        <span v-else>{{ isEditing ? 'Mettre à jour' : 'Ajouter le client' }}</span>
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
  clientData: Object,
  provenances: {
    type: Array,
    default: () => [],
  },
})
const emit = defineEmits(['close', 'saved'])

const isEditing = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')

const form = ref({
  nom: '',
  numero: '',
  provenance_id: null,
})

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      errorMessage.value = ''
      if (props.clientData && props.clientData.id) {
        isEditing.value = true
        form.value = {
          nom: props.clientData.nom || '',
          numero: props.clientData.numero || '',
          provenance_id: props.clientData.provenance?.id || props.clientData.provenance_id || null,
        }
      } else {
        isEditing.value = false
        form.value = {
          nom: '',
          numero: '',
          provenance_id: null,
        }
      }
    }
  }
)

async function saveClient() {
  if (!form.value.nom.trim()) return
  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const payload = {
      nom: form.value.nom.trim(),
      numero: form.value.numero ? form.value.numero.trim() : null,
      provenance_id: form.value.provenance_id || null,
    }

    let res
    if (isEditing.value) {
      res = await apiClient.patch(`/clients/${props.clientData.id}/`, payload)
    } else {
      res = await apiClient.post('/clients/', payload)
    }

    emit('saved', res.data)
    emit('close')
  } catch (err) {
    errorMessage.value =
      err.response?.data?.error ||
      err.response?.data?.detail ||
      "Une erreur est survenue lors de l'enregistrement du client."
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
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: #94A3B8;
  margin-bottom: 6px;
}

.mobile-input,
.mobile-select {
  width: 100%;
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 12px 14px;
  color: #FFFFFF;
  font-size: 0.9rem;
  outline: none;
}

.btn-submit {
  width: 100%;
  margin-top: 20px;
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
