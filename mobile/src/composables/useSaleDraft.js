import { ref } from 'vue'

const activeDraft = ref(null)
const isSaleModalOpen = ref(false)

export function useSaleDraft() {
  function setDraft(draftData) {
    activeDraft.value = draftData
    isSaleModalOpen.value = true
  }

  function clearDraft() {
    activeDraft.value = null
  }

  function openSaleModal() {
    isSaleModalOpen.value = true
  }

  function closeSaleModal() {
    isSaleModalOpen.value = false
    activeDraft.value = null
  }

  return {
    activeDraft,
    isSaleModalOpen,
    setDraft,
    clearDraft,
    openSaleModal,
    closeSaleModal,
  }
}
