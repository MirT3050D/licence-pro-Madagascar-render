<template>
  <div>
    <!-- Floating Trigger Button -->
    <button 
      class="ai-trigger-btn"
      @click="isOpen = true"
      title="Assistant IA - Pré-remplissage rapide"
    >
      <div class="ai-sparkle-icon">
        <Sparkles :size="20" />
      </div>
      <span class="ai-btn-text">Assistant IA</span>
    </button>

    <!-- Overlay Backdrop -->
    <div 
      v-if="isOpen" 
      class="drawer-backdrop"
      @click="isOpen = false"
    ></div>

    <!-- Slide-in Drawer -->
    <aside class="ai-drawer" :class="{ 'drawer-open': isOpen }">
      <div class="drawer-header">
        <div class="drawer-title-group">
          <div class="ai-badge-icon">
            <Sparkles :size="18" />
          </div>
          <div>
            <h3>Assistant IA Licence Pro</h3>
            <p class="drawer-subtitle">Collez un message client brut pour générer la vente</p>
          </div>
        </div>
        <button class="btn-close" @click="isOpen = false">
          <X :size="20" />
        </button>
      </div>

      <div class="drawer-body">
        <!-- Prompt Box -->
        <div class="prompt-section">
          <label class="prompt-label">
            <span>Message brut du client</span>
            <span class="prompt-hint">Ex: SMS, WhatsApp, Facebook Messenger</span>
          </label>
          <textarea
            v-model="rawText"
            class="form-textarea ai-textarea"
            rows="5"
            placeholder="Ex: Bonjour, je m'appelle Andry (034 12 345 67). Je voudrais commander 2 licences Windows 11 Pro et 1 Office 365, je vais payer par MVola s'il vous plaît."
          ></textarea>

          <div class="quick-examples">
            <span class="example-title">Exemples :</span>
            <button @click="fillExample(1)" class="badge-example">2x Windows 11 (MVola)</button>
            <button @click="fillExample(2)" class="badge-example">Office 365 + Canva (Orange)</button>
          </div>

          <button 
            @click="handleAnalyze" 
            class="btn btn-primary btn-analyze"
            :disabled="loading || !rawText.trim()"
          >
            <Sparkles :size="18" />
            <span v-if="loading">Analyse du texte en cours...</span>
            <span v-else>Extraire & Analyser</span>
          </button>
        </div>

        <!-- Analysis Results Preview -->
        <div v-if="parsedResult" class="results-section animate-fade">
          <div class="results-header">
            <h4>Données extraites</h4>
            <span class="badge badge-success">Prêt pour formulaire</span>
          </div>

          <div class="parsed-card">
            <!-- Client Info -->
            <div class="parsed-row">
              <span class="parsed-label">Client :</span>
              <span class="parsed-value highlight">{{ parsedResult.client_nom || 'Non spécifié' }}</span>
              <span v-if="parsedResult.client_numero" class="parsed-tag">{{ parsedResult.client_numero }}</span>
            </div>

            <!-- Products Extracted -->
            <div class="parsed-articles">
              <span class="parsed-label">Articles détectés :</span>
              <div v-if="parsedResult.articles?.length" class="articles-list">
                <div v-for="(item, idx) in parsedResult.articles" :key="idx" class="article-chip">
                  <span class="qty-badge">{{ item.quantite }}x</span>
                  <span class="prod-name">{{ item.produit_nom }}</span>
                  <span class="prod-price" v-if="item.prix_unitaire">{{ formatPrice(item.prix_unitaire * item.quantite) }}</span>
                </div>
              </div>
              <div v-else class="text-muted text-sm">
                Aucun produit du catalogue reconnu dans ce message.
              </div>
            </div>

            <!-- Payment Method -->
            <div class="parsed-row" v-if="parsedResult.methode_paiement_id">
              <span class="parsed-label">Méthode de règlement :</span>
              <span class="badge badge-primary">ID: {{ parsedResult.methode_paiement_id }}</span>
            </div>
          </div>

          <!-- Action: Pre-fill Sale Form -->
          <button @click="applyToSale" class="btn btn-success btn-apply">
            <Check :size="18" />
            <span>Ouvrir la vente pré-remplie</span>
          </button>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Sparkles, X, Check } from '@lucide/vue'
import apiClient from '../api/client'

const router = useRouter()
const isOpen = ref(false)
const rawText = ref('')
const loading = ref(false)
const parsedResult = ref(null)

const emit = defineEmits(['prefill-sale'])

function fillExample(num) {
  if (num === 1) {
    rawText.value = "Bonjour, je suis Jean Dupont, numéro 0341234567. Je souhaite acheter 2 Windows 11 Pro. Paiement par MVola."
  } else {
    rawText.value = "Salama tompoko, Izaho Rabe Andry (032 98 765 43). Mba handray 1 Microsoft Office 365 Pro Plus sy 1 Canva Pro 1 An. Amin'ny Orange Money no handoavako azy."
  }
}

async function handleAnalyze() {
  if (!rawText.value.trim()) return
  loading.value = true
  try {
    const res = await apiClient.post('/ai/parse/', { texte: rawText.value })
    parsedResult.value = res.data
  } catch (err) {
    alert(err.response?.data?.error || "Erreur lors de l'analyse du message")
  } finally {
    loading.value = false
  }
}

function applyToSale() {
  if (!parsedResult.value) return
  // Stocker dans sessionStorage pour que la page des ventes puisse l'intercepter
  sessionStorage.setItem('prefill_sale', JSON.stringify(parsedResult.value))
  isOpen.value = false
  router.push('/ventes?action=nouvelle')
}

function formatPrice(val) {
  return new Intl.NumberFormat('fr-MG').format(val) + ' Ar'
}
</script>

<style scoped>
.ai-trigger-btn {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 50;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 1.25rem;
  border-radius: 9999px;
  background: var(--gradient-brand);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 10px 25px rgba(99, 102, 241, 0.45);
  cursor: pointer;
  font-family: var(--font-sans);
  font-weight: 700;
  font-size: 0.9rem;
  transition: all var(--transition-normal);
}

.ai-trigger-btn:hover {
  transform: translateY(-3px) scale(1.03);
  box-shadow: 0 15px 35px rgba(99, 102, 241, 0.6);
}

.drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(4px);
  z-index: 90;
}

.ai-drawer {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 440px;
  max-width: 90vw;
  background: #0d131f;
  border-left: 1px solid var(--border-card);
  box-shadow: -15px 0 40px rgba(0, 0, 0, 0.7);
  z-index: 100;
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.ai-drawer.drawer-open {
  transform: translateX(0);
}

.drawer-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.drawer-title-group {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.ai-badge-icon {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-md);
  background: var(--gradient-brand);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drawer-header h3 {
  font-size: 1.05rem;
}

.drawer-subtitle {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.btn-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.3rem;
  border-radius: var(--radius-sm);
}

.btn-close:hover {
  color: var(--text-main);
  background: rgba(255, 255, 255, 0.08);
}

.drawer-body {
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.prompt-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.prompt-hint {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-weight: normal;
}

.ai-textarea {
  width: 100%;
  resize: vertical;
}

.quick-examples {
  margin-top: 0.65rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: center;
}

.example-title {
  font-size: 0.725rem;
  color: var(--text-muted);
}

.badge-example {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
  font-size: 0.725rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.badge-example:hover {
  background: rgba(99, 102, 241, 0.2);
  color: #c7d2fe;
  border-color: rgba(99, 102, 241, 0.4);
}

.btn-analyze {
  width: 100%;
  margin-top: 1rem;
}

.results-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.parsed-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.parsed-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.parsed-label {
  color: var(--text-muted);
  font-weight: 500;
}

.parsed-value.highlight {
  color: #ffffff;
  font-weight: 700;
}

.parsed-tag {
  background: rgba(255, 255, 255, 0.08);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.parsed-articles {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.articles-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.article-chip {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.25);
  padding: 0.4rem 0.65rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
}

.qty-badge {
  background: var(--primary);
  color: white;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-weight: 700;
}

.prod-name {
  flex: 1;
  color: var(--text-main);
  font-weight: 500;
}

.prod-price {
  color: #34d399;
  font-weight: 600;
}

.btn-apply {
  width: 100%;
}
</style>
