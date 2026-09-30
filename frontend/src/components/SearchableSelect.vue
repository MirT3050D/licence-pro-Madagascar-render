<template>
  <div
    class="searchable-select"
    ref="containerRef"
    :class="{
      'is-open': isOpen,
      'is-compact': compact,
      'is-disabled': disabled,
      'has-value': selectedOption !== null
    }"
  >
    <!-- Hidden native input for required form validation -->
    <input
      v-if="required"
      type="text"
      class="ss-hidden-validator"
      :value="modelValue || ''"
      required
      tabindex="-1"
      aria-hidden="true"
    />

    <!-- Main Select Trigger Button -->
    <button
      type="button"
      class="ss-trigger"
      :class="{ 'ss-trigger-compact': compact }"
      :disabled="disabled"
      @click="toggleDropdown"
      :title="selectedOption ? getLabel(selectedOption) : placeholder"
      aria-haspopup="listbox"
      :aria-expanded="isOpen"
    >
      <div class="ss-trigger-content">
        <component v-if="icon" :is="icon" :size="compact ? 13 : 15" class="ss-leading-icon text-primary" />
        
        <div v-if="selectedOption" class="ss-selected-wrap">
          <span class="ss-selected-label">{{ getLabel(selectedOption) }}</span>
          <span v-if="!hideSubtitleInTrigger && getSubtitle(selectedOption)" class="ss-selected-subtitle">
            {{ getSubtitle(selectedOption) }}
          </span>
        </div>
        <span v-else class="ss-placeholder">
          {{ placeholder }}
        </span>
      </div>

      <div class="ss-trigger-actions">
        <!-- Clear button -->
        <button
          v-if="allowClear && selectedOption && !disabled"
          type="button"
          class="ss-btn-clear"
          @click.stop="clearSelection"
          title="Effacer la sélection"
        >
          <X :size="12" />
        </button>

        <!-- Chevron -->
        <ChevronDown :size="14" class="ss-chevron" :class="{ 'rotate-180': isOpen }" />
      </div>
    </button>

    <!-- Dropdown Menu Popover -->
    <Transition name="ss-fade">
      <div v-if="isOpen" class="ss-dropdown card">
        <!-- Search Field -->
        <div class="ss-search-box">
          <Search :size="14" class="ss-search-icon" />
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            class="ss-search-input"
            :placeholder="searchPlaceholder"
            @keydown.down.prevent="navigateOptions(1)"
            @keydown.up.prevent="navigateOptions(-1)"
            @keydown.enter.prevent="selectHighlighted"
            @keydown.esc.prevent="closeDropdown"
          />
          <button
            v-if="searchQuery"
            type="button"
            class="ss-search-clear"
            @click="searchQuery = ''; focusSearch()"
            title="Effacer la recherche"
          >
            <X :size="12" />
          </button>
        </div>

        <!-- Options Counter / Status -->
        <div class="ss-status-bar">
          <span class="ss-status-count">
            {{ filteredOptions.length }} option{{ filteredOptions.length > 1 ? 's' : '' }}
          </span>
          <span v-if="searchQuery" class="ss-status-hint">Touche Entrée pour valider</span>
        </div>

        <!-- Scrollable Options List -->
        <div class="ss-options-list" ref="optionsListRef">
          <div
            v-for="(opt, idx) in filteredOptions"
            :key="getValue(opt)"
            class="ss-option-item"
            :class="{
              'is-selected': isSelected(opt),
              'is-highlighted': highlightedIndex === idx
            }"
            @click="selectOption(opt)"
            @mouseenter="highlightedIndex = idx"
            role="option"
            :aria-selected="isSelected(opt)"
          >
            <div class="ss-option-body">
              <span class="ss-option-label">{{ getLabel(opt) }}</span>
              <span v-if="getSubtitle(opt)" class="ss-option-subtitle">
                {{ getSubtitle(opt) }}
              </span>
            </div>

            <Check v-if="isSelected(opt)" :size="14" class="ss-check-icon text-primary" />
          </div>

          <!-- Empty State -->
          <div v-if="filteredOptions.length === 0" class="ss-empty-state">
            <Search :size="20" class="text-muted mb-1" />
            <span class="ss-empty-text">Aucun résultat trouvé pour "{{ searchQuery }}"</span>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { ChevronDown, Search, X, Check } from '@lucide/vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, null],
    default: null,
  },
  options: {
    type: Array,
    default: () => [],
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
  required: {
    type: Boolean,
    default: false,
  },
  allowClear: {
    type: Boolean,
    default: false,
  },
  compact: {
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
  icon: {
    type: [Object, Function],
    default: null,
  },
  hideSubtitleInTrigger: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'change'])

const containerRef = ref(null)
const searchInputRef = ref(null)
const optionsListRef = ref(null)

const isOpen = ref(false)
const searchQuery = ref('')
const highlightedIndex = ref(-1)

// Helpers to extract properties regardless of option format (object or primitive)
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

function toggleDropdown() {
  if (props.disabled) return
  if (isOpen.value) {
    closeDropdown()
  } else {
    openDropdown()
  }
}

function openDropdown() {
  isOpen.value = true
  searchQuery.value = ''
  highlightedIndex.value = -1
  nextTick(() => {
    focusSearch()
  })
}

function closeDropdown() {
  isOpen.value = false
  searchQuery.value = ''
  highlightedIndex.value = -1
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
  closeDropdown()
}

function clearSelection() {
  emit('update:modelValue', null)
  emit('change', null, null)
  closeDropdown()
}

function navigateOptions(step) {
  const len = filteredOptions.value.length
  if (len === 0) return
  highlightedIndex.value = (highlightedIndex.value + step + len) % len
  scrollHighlightedIntoView()
}

function scrollHighlightedIntoView() {
  nextTick(() => {
    if (!optionsListRef.value) return
    const el = optionsListRef.value.children[highlightedIndex.value]
    if (el && el.scrollIntoView) {
      el.scrollIntoView({ block: 'nearest' })
    }
  })
}

function selectHighlighted() {
  if (highlightedIndex.value >= 0 && highlightedIndex.value < filteredOptions.value.length) {
    selectOption(filteredOptions.value[highlightedIndex.value])
  } else if (filteredOptions.value.length === 1) {
    selectOption(filteredOptions.value[0])
  }
}

function handleClickOutside(event) {
  if (containerRef.value && !containerRef.value.contains(event.target)) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.searchable-select {
  position: relative;
  width: 100%;
}

/* Hidden validator to hook into native form validation */
.ss-hidden-validator {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
  pointer-events: none;
}

/* Trigger Button */
.ss-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  background-color: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 0.65rem 0.85rem;
  color: var(--text-main);
  font-family: inherit;
  font-size: 0.88rem;
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-fast);
  outline: none;
  min-height: 42px;
}

.ss-trigger:hover:not(:disabled) {
  border-color: rgba(0, 210, 255, 0.35);
  background-color: rgba(14, 28, 50, 0.85);
}

.searchable-select.is-open {
  z-index: 100;
}

.searchable-select.is-open .ss-trigger {
  border-color: var(--primary);
  box-shadow: 0 0 12px rgba(0, 210, 255, 0.2);
  background-color: rgba(14, 28, 50, 0.95);
}

.ss-trigger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Compact mode (for table cells, etc.) */
.ss-trigger-compact {
  padding: 0.45rem 0.75rem;
  min-height: 38px;
  font-size: 0.84rem;
  border-radius: var(--radius-sm);
}

.ss-trigger-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
}

.ss-leading-icon {
  flex-shrink: 0;
}

.ss-selected-wrap {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  min-width: 0;
  flex: 1;
  overflow: hidden;
}

.ss-selected-label {
  font-weight: 600;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
  max-width: 100%;
}

.ss-selected-subtitle {
  font-size: 0.74rem;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.25);
  padding: 0.1rem 0.45rem;
  border-radius: var(--radius-full);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 130px;
  flex-shrink: 1;
}

.ss-placeholder {
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ss-trigger-actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-shrink: 0;
}

.ss-btn-clear {
  background: none;
  border: none;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ss-btn-clear:hover {
  color: var(--rose);
  background: rgba(244, 63, 94, 0.15);
}

.ss-chevron {
  color: var(--text-muted);
  transition: transform var(--transition-fast);
}

.rotate-180 {
  transform: rotate(180deg);
}

/* Dropdown Menu Popover */
.ss-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #091322;
  border: 1px solid rgba(0, 210, 255, 0.3);
  border-radius: var(--radius-md);
  box-shadow: 0 16px 40px -5px rgba(0, 0, 0, 0.85), 0 0 25px rgba(0, 210, 255, 0.16);
  z-index: 1200;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: ss-scale 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}

.is-compact .ss-dropdown {
  min-width: max(100%, 460px);
  max-width: min(720px, 90vw);
  right: auto;
}

/* Search Box */
.ss-search-box {
  position: relative;
  display: flex;
  align-items: center;
  padding: 0.65rem 0.75rem;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid var(--border-subtle);
}

.ss-search-icon {
  position: absolute;
  left: 1rem;
  color: var(--primary);
  pointer-events: none;
}

.ss-search-input {
  width: 100%;
  background: rgba(10, 20, 36, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-sm);
  padding: 0.45rem 2rem 0.45rem 2.1rem;
  color: #ffffff;
  font-family: inherit;
  font-size: 0.82rem;
  outline: none;
  transition: border-color var(--transition-fast);
}

.ss-search-input:focus {
  border-color: var(--primary);
}

.ss-search-clear {
  position: absolute;
  right: 1.1rem;
  background: none;
  border: none;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.ss-search-clear:hover {
  color: #fff;
}

/* Status bar */
.ss-status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.3rem 0.85rem;
  font-size: 0.72rem;
  color: var(--text-muted);
  background: rgba(0, 0, 0, 0.25);
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.ss-status-hint {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.4);
}

/* Options List */
.ss-options-list {
  max-height: 360px;
  overflow-y: auto;
  padding: 0.4rem;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.ss-option-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s ease;
}

.ss-option-item:hover,
.ss-option-item.is-highlighted {
  background: rgba(0, 210, 255, 0.08);
}

.ss-option-item.is-selected {
  background: rgba(0, 210, 255, 0.14);
}

.ss-option-body {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
  flex: 1;
}

.ss-option-label {
  font-size: 0.85rem;
  color: #ffffff;
  font-weight: 500;
  line-height: 1.35;
  white-space: normal;
  word-break: break-word;
}

.ss-option-item.is-selected .ss-option-label {
  color: var(--primary);
  font-weight: 700;
}

.ss-option-subtitle {
  font-size: 0.72rem;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(56, 189, 248, 0.22);
  padding: 0.1rem 0.45rem;
  border-radius: var(--radius-full);
  width: fit-content;
  font-weight: 600;
  white-space: nowrap;
}

.ss-check-icon {
  flex-shrink: 0;
}

.ss-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem 1rem;
  text-align: center;
}

.ss-empty-text {
  font-size: 0.78rem;
  color: var(--text-muted);
}

/* Animations */
@keyframes ss-scale {
  from {
    opacity: 0;
    transform: translateY(-6px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.ss-fade-enter-active,
.ss-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.ss-fade-enter-from,
.ss-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
