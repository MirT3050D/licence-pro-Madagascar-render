<template>
  <div class="mobile-searchable-select" :class="{ 'has-value': selectedOption !== null, 'is-disabled': disabled }">
    <!-- Trigger Button -->
    <button
      type="button"
      class="mss-trigger"
      :disabled="disabled"
      @click="openModal"
    >
      <div class="mss-trigger-text">
        <span v-if="selectedOption" class="mss-label-selected">
          {{ getLabel(selectedOption) }}
        </span>
        <span v-else class="mss-placeholder">
          {{ placeholder }}
        </span>
        <span v-if="selectedOption && getSubtitle(selectedOption) && !hideSubtitleInTrigger" class="mss-badge-subtitle">
          {{ getSubtitle(selectedOption) }}
        </span>
      </div>

      <div class="mss-trigger-right">
        <ion-icon :icon="chevronDownOutline" class="mss-chevron" />
      </div>
    </button>

    <!-- Selection Bottom-Sheet Modal -->
    <ion-modal
      :is-open="isOpen"
      @didDismiss="isOpen = false"
      :initial-breakpoint="0.85"
      :breakpoints="[0, 0.85, 1]"
    >
      <ion-header>
        <ion-toolbar class="mss-modal-toolbar">
          <ion-title>{{ title || placeholder }}</ion-title>
          <ion-buttons slot="end">
            <ion-button @click="isOpen = false">
              <ion-icon :icon="closeOutline" />
            </ion-button>
          </ion-buttons>
        </ion-toolbar>

        <!-- Search Bar Header -->
        <div class="mss-search-bar">
          <div class="mss-search-input-wrap">
            <ion-icon :icon="searchOutline" class="mss-search-icon" />
            <input
              ref="searchInputRef"
              v-model="searchQuery"
              type="text"
              class="mss-search-field"
              :placeholder="searchPlaceholder"
            />
            <button
              v-if="searchQuery"
              type="button"
              class="mss-search-clear-btn"
              @click="searchQuery = ''; focusSearch()"
            >
              <ion-icon :icon="closeCircle" />
            </button>
          </div>
        </div>
      </ion-header>

      <ion-content class="mss-modal-content">
        <div class="mss-options-container">
          <!-- Clear option if allowed and something selected -->
          <div
            v-if="allowClear && selectedOption"
            class="mss-option-item mss-clear-option"
            @click="clearSelection"
          >
            <div class="mss-option-text">
              <span class="mss-option-title text-muted">Désélectionner</span>
            </div>
            <ion-icon :icon="closeOutline" class="mss-item-icon text-muted" />
          </div>

          <!-- Options List -->
          <div
            v-for="opt in filteredOptions"
            :key="getValue(opt)"
            class="mss-option-item"
            :class="{ 'is-selected': isSelected(opt) }"
            @click="selectOption(opt)"
          >
            <div class="mss-option-text">
              <span class="mss-option-title">{{ getLabel(opt) }}</span>
              <span v-if="getSubtitle(opt)" class="mss-option-subtitle">
                {{ getSubtitle(opt) }}
              </span>
            </div>

            <ion-icon
              v-if="isSelected(opt)"
              :icon="checkmarkOutline"
              class="mss-check-icon"
            />
          </div>

          <!-- Empty State -->
          <div v-if="filteredOptions.length === 0" class="mss-empty-state">
            <ion-icon :icon="searchOutline" class="mss-empty-icon" />
            <p>Aucun résultat pour "{{ searchQuery }}"</p>
          </div>
        </div>
      </ion-content>
    </ion-modal>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
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
import {
  chevronDownOutline,
  closeOutline,
  searchOutline,
  closeCircle,
  checkmarkOutline,
} from 'ionicons/icons'

const props = defineProps({
  modelValue: {
    type: [String, Number, null],
    default: null,
  },
  options: {
    type: Array,
    default: () => [],
  },
  title: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: 'Sélectionner...',
  },
  searchPlaceholder: {
    type: String,
    default: 'Rechercher...',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  allowClear: {
    type: Boolean,
    default: false,
  },
  valueKey: {
    type: String,
    default: 'id',
  },
  labelKey: {
    type: String,
    default: 'label',
  },
  subtitleKey: {
    type: String,
    default: 'subtitle',
  },
  hideSubtitleInTrigger: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'change'])

const isOpen = ref(false)
const searchQuery = ref('')
const searchInputRef = ref(null)

function getValue(opt) {
  if (opt === null || opt === undefined) return null
  if (typeof opt === 'object') return opt[props.valueKey]
  return opt
}

function getLabel(opt) {
  if (opt === null || opt === undefined) return ''
  if (typeof opt === 'object') return opt[props.labelKey] ?? opt.nom ?? opt.label ?? opt.name ?? ''
  return String(opt)
}

function getSubtitle(opt) {
  if (opt === null || opt === undefined || typeof opt !== 'object') return ''
  return opt[props.subtitleKey] ?? opt.subtitle ?? opt.description ?? opt.details ?? ''
}

const selectedOption = computed(() => {
  if (props.modelValue === null || props.modelValue === undefined || props.modelValue === '') {
    return null
  }
  return props.options.find((opt) => String(getValue(opt)) === String(props.modelValue)) || null
})

function isSelected(opt) {
  if (props.modelValue === null || props.modelValue === undefined || props.modelValue === '') {
    return false
  }
  return String(getValue(opt)) === String(props.modelValue)
}

const filteredOptions = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return props.options

  return props.options.filter((opt) => {
    const label = String(getLabel(opt)).toLowerCase()
    const subtitle = String(getSubtitle(opt)).toLowerCase()
    return label.includes(q) || subtitle.includes(q)
  })
})

function openModal() {
  if (props.disabled) return
  searchQuery.value = ''
  isOpen.value = true
  nextTick(() => {
    focusSearch()
  })
}

function focusSearch() {
  if (searchInputRef.value) {
    searchInputRef.value.focus()
  }
}

function selectOption(opt) {
  const val = getValue(opt)
  emit('update:modelValue', val)
  emit('change', val, opt)
  isOpen.value = false
}

function clearSelection() {
  emit('update:modelValue', null)
  emit('change', null, null)
  isOpen.value = false
}
</script>

<style scoped>
.mobile-searchable-select {
  width: 100%;
  margin-bottom: 8px;
}

.mss-trigger {
  width: 100%;
  background: #0B1120;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 10px 12px;
  color: #FFFFFF;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  text-align: left;
  outline: none;
  min-height: 42px;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.mobile-searchable-select.has-value .mss-trigger {
  border-color: rgba(20, 184, 166, 0.4);
}

.mss-trigger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mss-trigger-text {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.mss-label-selected {
  font-weight: 600;
  color: #FFFFFF;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
  max-width: 100%;
}

.mss-placeholder {
  color: #64748B;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mss-badge-subtitle {
  font-size: 0.7rem;
  color: #38BDF8;
  background: rgba(56, 189, 248, 0.15);
  padding: 2px 6px;
  border-radius: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
  flex-shrink: 1;
}

.mss-trigger-right {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.mss-chevron {
  color: #64748B;
  font-size: 16px;
}

/* Modal styles */
.mss-modal-toolbar {
  --background: #0B1120;
  --color: #FFFFFF;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.mss-search-bar {
  background: #0B1120;
  padding: 8px 16px 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.mss-search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.mss-search-icon {
  position: absolute;
  left: 12px;
  color: #14B8A6;
  font-size: 16px;
}

.mss-search-field {
  width: 100%;
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  padding: 10px 36px 10px 36px;
  color: #FFFFFF;
  font-size: 0.88rem;
  outline: none;
}

.mss-search-field:focus {
  border-color: #14B8A6;
}

.mss-search-clear-btn {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: #94A3B8;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mss-modal-content {
  --background: #0B1120;
  --color: #FFFFFF;
}

.mss-options-container {
  padding: 10px 16px 30px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mss-option-item {
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.mss-option-item:active {
  background: rgba(20, 184, 166, 0.15);
  border-color: #14B8A6;
}

.mss-option-item.is-selected {
  background: rgba(20, 184, 166, 0.12);
  border-color: #14B8A6;
}

.mss-option-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.mss-option-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #FFFFFF;
}

.mss-option-item.is-selected .mss-option-title {
  color: #5EEAD4;
}

.mss-option-subtitle {
  font-size: 0.75rem;
  color: #94A3B8;
}

.mss-check-icon {
  color: #14B8A6;
  font-size: 20px;
  flex-shrink: 0;
}

.mss-clear-option {
  border-style: dashed;
  border-color: rgba(255, 255, 255, 0.15);
}

.mss-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 10px;
  color: #64748B;
  font-size: 0.85rem;
}

.mss-empty-icon {
  font-size: 32px;
  margin-bottom: 8px;
  opacity: 0.5;
}
</style>
