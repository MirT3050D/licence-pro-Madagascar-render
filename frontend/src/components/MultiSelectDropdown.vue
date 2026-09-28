<template>
  <div class="multi-select-dropdown" ref="dropdownRef" :class="{ 'is-open': isOpen, 'is-active': selectedCount > 0, 'is-compact': compact }">
    <!-- Trigger Button -->
    <button
      type="button"
      class="ms-trigger-btn"
      @click="toggleDropdown"
      :title="titleTooltip"
      :aria-expanded="isOpen"
    >
      <div class="ms-trigger-left">
        <component v-if="icon" :is="icon" :size="compact ? 13 : 15" class="ms-icon text-primary" />
        
        <!-- Empty / All State -->
        <span v-if="selectedCount === 0" class="ms-placeholder">
          {{ placeholder || 'Tous' }}
        </span>

        <!-- 1 Item Selected -->
        <div v-else-if="selectedCount === 1" class="ms-single-pill">
          <span class="ms-pill-dot" :style="{ backgroundColor: singleItemColor }"></span>
          <span class="ms-pill-text">{{ singleItemLabel }}</span>
        </div>

        <!-- Multiple Items Selected -->
        <div v-else class="ms-multi-preview">
          <span class="ms-count-badge">{{ selectedCount }}</span>
          <span class="ms-multi-text">
            {{ summaryText }}
          </span>
        </div>
      </div>

      <div class="ms-trigger-right">
        <!-- Quick Clear Button -->
        <span
          v-if="selectedCount > 0"
          class="ms-clear-btn"
          @click.stop="clearAll"
          title="Effacer la sélection"
        >
          <X :size="12" />
        </span>

        <!-- Chevron Toggle -->
        <ChevronDown :size="14" class="ms-chevron" :class="{ 'rotate-180': isOpen }" />
      </div>
    </button>

    <!-- Dropdown Popover Menu -->
    <Transition name="dropdown-fade">
      <div v-if="isOpen" class="ms-menu-card card">
        <!-- Header with Quick Action Buttons -->
        <div class="ms-menu-header">
          <div class="ms-header-title">
            <span class="font-bold text-xs uppercase tracking-wider text-muted">
              {{ label || 'Sélection' }}
            </span>
            <span class="ms-header-counter badge badge-primary badge-xs">
              {{ selectedCount }} / {{ options.length }}
            </span>
          </div>

          <div class="ms-header-actions">
            <button
              type="button"
              class="ms-action-link"
              @click="selectAll"
              :disabled="selectedCount === options.length"
            >
              Tout cocher
            </button>
            <span class="ms-action-sep">•</span>
            <button
              type="button"
              class="ms-action-link text-rose"
              @click="clearAll"
              :disabled="selectedCount === 0"
            >
              Effacer
            </button>
          </div>
        </div>

        <!-- Optional Search Bar inside dropdown -->
        <div v-if="showSearchInput" class="ms-search-wrap">
          <Search :size="13" class="ms-search-icon text-muted" />
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            class="ms-search-input"
            :placeholder="searchPlaceholder || 'Filtrer les options...'"
          />
          <button v-if="searchQuery" @click="searchQuery = ''" class="ms-search-clear">
            <X :size="11" />
          </button>
        </div>

        <!-- Options List -->
        <div class="ms-options-list custom-scroll">
          <div
            v-for="opt in filteredOptions"
            :key="opt.id"
            class="ms-option-item"
            :class="{ 'is-selected': isSelected(opt.id) }"
            @click="toggleItem(opt.id)"
          >
            <!-- Checkbox Box -->
            <div class="ms-checkbox" :class="{ checked: isSelected(opt.id) }">
              <Check v-if="isSelected(opt.id)" :size="11" class="check-icon" />
            </div>

            <!-- Dot / Style / Emoji Preview -->
            <span
              v-if="opt.color?.dot || opt.color?.bg"
              class="ms-opt-dot"
              :style="{ backgroundColor: opt.color?.dot || opt.color?.text || '#00d2ff' }"
            ></span>

            <!-- Label -->
            <span class="ms-opt-label">{{ opt.label }}</span>

            <!-- Optional Count / Subtitle Tag -->
            <span v-if="opt.count !== undefined" class="ms-opt-count">
              {{ opt.count }}
            </span>
          </div>

          <div v-if="filteredOptions.length === 0" class="ms-empty-state">
            <span>Aucune option trouvée</span>
          </div>
        </div>

        <!-- Footer / Apply -->
        <div class="ms-menu-footer">
          <button type="button" class="btn btn-secondary btn-xs ms-footer-close" @click="isOpen = false">
            Fermer
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ChevronDown, X, Check, Search } from '@lucide/vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  options: {
    type: Array,
    default: () => [] // Array of { id, label, color?: { bg, text, dot }, count?: number }
  },
  placeholder: {
    type: String,
    default: 'Sélectionner...'
  },
  label: {
    type: String,
    default: ''
  },
  icon: {
    type: [Object, Function],
    default: null
  },
  searchable: {
    type: Boolean,
    default: true
  },
  searchPlaceholder: {
    type: String,
    default: 'Rechercher...'
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const isOpen = ref(false)
const searchQuery = ref('')
const dropdownRef = ref(null)
const searchInputRef = ref(null)

const showSearchInput = computed(() => {
  return props.searchable && props.options.length > 5
})

const selectedCount = computed(() => {
  return (props.modelValue || []).length
})

const filteredOptions = computed(() => {
  if (!searchQuery.value.trim()) return props.options
  const q = searchQuery.value.toLowerCase().trim()
  return props.options.filter(opt =>
    (opt.label || '').toLowerCase().includes(q)
  )
})

const singleItem = computed(() => {
  if (selectedCount.value !== 1) return null
  const selectedId = props.modelValue[0]
  return props.options.find(opt => String(opt.id) === String(selectedId)) || null
})

const singleItemLabel = computed(() => {
  return singleItem.value?.label || '1 sélectionné'
})

const singleItemColor = computed(() => {
  return singleItem.value?.color?.dot || singleItem.value?.color?.text || '#00d2ff'
})

const summaryText = computed(() => {
  if (props.label) {
    return `${selectedCount.value} ${props.label.toLowerCase()}`
  }
  return `${selectedCount.value} sélectionné(s)`
})

const titleTooltip = computed(() => {
  if (selectedCount.value === 0) return props.placeholder
  const names = props.options
    .filter(opt => isSelected(opt.id))
    .map(opt => opt.label)
    .join(', ')
  return names || `${selectedCount.value} sélectionné(s)`
})

function isSelected(id) {
  return (props.modelValue || []).some(v => String(v) === String(id))
}

function toggleDropdown() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    searchQuery.value = ''
    nextTick(() => {
      if (searchInputRef.value) {
        searchInputRef.value.focus()
      }
    })
  }
}

function toggleItem(id) {
  const current = [...(props.modelValue || [])]
  const idx = current.findIndex(v => String(v) === String(id))
  if (idx >= 0) {
    current.splice(idx, 1)
  } else {
    // Keep raw type of id from option if possible
    const opt = props.options.find(o => String(o.id) === String(id))
    current.push(opt ? opt.id : id)
  }
  emit('update:modelValue', current)
  emit('change', current)
}

function selectAll() {
  const allIds = props.options.map(opt => opt.id)
  emit('update:modelValue', allIds)
  emit('change', allIds)
}

function clearAll() {
  emit('update:modelValue', [])
  emit('change', [])
}

function handleClickOutside(event) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

function handleKeyDown(event) {
  if (event.key === 'Escape' && isOpen.value) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeyDown)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.multi-select-dropdown {
  position: relative;
  display: inline-block;
  min-width: 175px;
}

.ms-trigger-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 0.5rem;
  background: var(--bg-input, rgba(10, 20, 36, 0.7));
  border: 1px solid var(--border-card, rgba(0, 210, 255, 0.12));
  border-radius: var(--radius-md, 12px);
  padding: 0.65rem 0.9rem;
  color: var(--text-main, #f8fafc);
  font-family: var(--font-sans);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
}

.is-compact .ms-trigger-btn {
  padding: 0.45rem 0.75rem;
  font-size: 0.8rem;
}

.ms-trigger-btn:hover {
  border-color: rgba(0, 210, 255, 0.35);
  background: rgba(14, 28, 50, 0.85);
}

.multi-select-dropdown.is-open .ms-trigger-btn,
.multi-select-dropdown.is-active .ms-trigger-btn {
  border-color: var(--primary, #00d2ff);
  box-shadow: 0 0 0 2px rgba(0, 210, 255, 0.2);
}

.multi-select-dropdown.is-active .ms-trigger-btn {
  background: rgba(0, 210, 255, 0.06);
}

.ms-trigger-left {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  flex: 1;
  overflow: hidden;
  white-space: nowrap;
}

.ms-placeholder {
  color: var(--text-secondary, #94a3b8);
  font-size: 0.84rem;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ms-single-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  overflow: hidden;
}

.ms-pill-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.ms-pill-text {
  font-weight: 600;
  color: var(--text-main, #f8fafc);
  overflow: hidden;
  text-overflow: ellipsis;
}

.ms-multi-preview {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  overflow: hidden;
}

.ms-count-badge {
  background: var(--gradient-brand, linear-gradient(135deg, #00d2ff 0%, #0066ff 100%));
  color: #fff;
  font-weight: 700;
  font-size: 0.7rem;
  padding: 0.15rem 0.45rem;
  border-radius: 9999px;
  line-height: 1;
}

.ms-multi-text {
  font-weight: 600;
  color: var(--text-main, #f8fafc);
  overflow: hidden;
  text-overflow: ellipsis;
}

.ms-trigger-right {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-shrink: 0;
}

.ms-clear-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 17px;
  height: 17px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  color: var(--text-secondary);
  transition: all 0.15s;
}

.ms-clear-btn:hover {
  background: rgba(244, 63, 94, 0.3);
  color: #f43f5e;
}

.ms-chevron {
  color: var(--text-muted, #64748b);
  transition: transform 0.2s ease;
}

.rotate-180 {
  transform: rotate(180deg);
}

/* Dropdown Menu Popover */
.ms-menu-card {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  z-index: 100;
  min-width: 250px;
  max-width: 320px;
  width: max-content;
  padding: 0.8rem;
  background: #091322 !important;
  border: 1px solid rgba(0, 210, 255, 0.25) !important;
  border-radius: var(--radius-lg, 16px);
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.75), 0 0 20px rgba(0, 210, 255, 0.15);
  backdrop-filter: blur(20px);
}

.ms-menu-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  margin-bottom: 0.6rem;
}

.ms-header-title {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.ms-header-counter {
  font-size: 0.65rem;
  padding: 0.1rem 0.4rem;
}

.ms-header-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.ms-action-link {
  background: none;
  border: none;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--primary, #00d2ff);
  cursor: pointer;
  padding: 0;
  transition: opacity 0.15s;
}

.ms-action-link:hover:not(:disabled) {
  text-decoration: underline;
}

.ms-action-link:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.ms-action-sep {
  color: var(--text-muted);
  font-size: 0.65rem;
}

/* Search input */
.ms-search-wrap {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.ms-search-icon {
  position: absolute;
  left: 0.65rem;
  pointer-events: none;
}

.ms-search-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-sm, 8px);
  padding: 0.4rem 1.6rem 0.4rem 1.8rem;
  font-size: 0.78rem;
  color: #fff;
  outline: none;
  transition: border-color 0.15s;
}

.ms-search-input:focus {
  border-color: var(--primary, #00d2ff);
  background: rgba(255, 255, 255, 0.08);
}

.ms-search-clear {
  position: absolute;
  right: 0.5rem;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
}

/* Options List */
.ms-options-list {
  max-height: 220px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding-right: 0.2rem;
}

.ms-option-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.45rem 0.6rem;
  border-radius: var(--radius-sm, 8px);
  cursor: pointer;
  user-select: none;
  transition: all 0.15s ease;
}

.ms-option-item:hover {
  background: rgba(255, 255, 255, 0.07);
}

.ms-option-item.is-selected {
  background: rgba(0, 210, 255, 0.12);
}

.ms-checkbox {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1.5px solid rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.25);
  flex-shrink: 0;
  transition: all 0.15s;
}

.ms-checkbox.checked {
  background: var(--primary, #00d2ff);
  border-color: var(--primary, #00d2ff);
}

.check-icon {
  color: #060d19;
  stroke-width: 3;
}

.ms-opt-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.ms-opt-label {
  font-size: 0.825rem;
  font-weight: 500;
  color: var(--text-main, #f8fafc);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ms-option-item.is-selected .ms-opt-label {
  font-weight: 600;
  color: #fff;
}

.ms-opt-count {
  font-size: 0.7rem;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.06);
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  font-variant-numeric: tabular-nums;
}

.ms-empty-state {
  padding: 1rem;
  text-align: center;
  font-size: 0.78rem;
  color: var(--text-muted);
}

.ms-menu-footer {
  margin-top: 0.6rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  justify-content: flex-end;
}

.ms-footer-close {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
}

/* Animations */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
