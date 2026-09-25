<template>
  <div>
    <!-- Floating Trigger Button -->
    <button 
      class="ai-trigger-btn"
      @click="isOpen = true"
      title="Assistant IA & Chatbot Licence Pro"
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
      <!-- Drawer Header -->
      <div class="drawer-header">
        <div class="drawer-title-group">
          <div class="ai-badge-icon">
            <Bot :size="20" />
          </div>
          <div>
            <h3>Assistant Virtuel IA</h3>
            <p class="drawer-subtitle">Conseiller licences, tarifs & aide aux ventes</p>
          </div>
        </div>
        <button class="btn-close" @click="isOpen = false" title="Fermer">
          <X :size="20" />
        </button>
      </div>

      <!-- Mode Switcher Tabs -->
      <div class="ai-tabs-bar">
        <button
          type="button"
          class="ai-tab-btn"
          :class="{ active: activeTab === 'chat' }"
          @click="activeTab = 'chat'"
        >
          <MessageSquare :size="16" />
          <span>Chatbot Interactif</span>
        </button>
        <button
          type="button"
          class="ai-tab-btn"
          :class="{ active: activeTab === 'extractor' }"
          @click="activeTab = 'extractor'"
        >
          <Zap :size="16" />
          <span>Extracteur Rapide</span>
        </button>
      </div>

      <!-- 1. CHATBOT INTERACTIF TAB -->
      <div v-if="activeTab === 'chat'" class="chat-tab-container">
        <!-- Chat History -->
        <div ref="chatContainerRef" class="chat-messages-area">
          <div v-for="(msg, idx) in chatMessages" :key="idx" class="chat-message-row" :class="msg.role">
            <div class="chat-avatar">
              <Bot v-if="msg.role === 'model'" :size="16" />
              <User v-else :size="16" />
            </div>

            <div class="chat-bubble-content">
              <!-- Text with formatted markdown -->
              <div class="chat-text" v-html="renderMarkdown(msg.text)"></div>

              <!-- Order Intent Card if detected -->
              <div v-if="msg.order_intent && msg.order_intent.articles?.length" class="chat-order-card animate-fade">
                <div class="order-card-header">
                  <div class="flex items-center gap-1.5">
                    <Zap :size="15" class="text-primary" />
                    <span class="font-bold text-sm">Commande détectée</span>
                  </div>
                  <span class="badge badge-success text-xs">Prêt à valider</span>
                </div>

                <div class="order-card-body">
                  <div v-if="msg.order_intent.client_nom" class="order-meta-line">
                    <span class="text-muted text-xs">Client :</span>
                    <strong class="text-xs">{{ msg.order_intent.client_nom }}</strong>
                    <span v-if="msg.order_intent.client_numero" class="text-xs text-secondary">({{ msg.order_intent.client_numero }})</span>
                  </div>

                  <div class="order-items-preview">
                    <div v-for="(art, aIdx) in msg.order_intent.articles" :key="aIdx" class="order-item-badge">
                      <span class="item-qty">{{ art.quantite }}x</span>
                      <span class="item-name">{{ art.produit_nom }}</span>
                      <span v-if="art.prix_unitaire" class="item-price">{{ formatPrice(art.prix_unitaire * art.quantite) }}</span>
                    </div>
                  </div>
                </div>

                <button @click="applyOrderIntent(msg.order_intent)" class="btn btn-primary btn-sm btn-fill-sale">
                  <ShoppingCart :size="14" />
                  <span>⚡ Ouvrir la vente pré-remplie</span>
                </button>
              </div>

              <span class="chat-time">{{ msg.time }}</span>
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="chatLoading" class="chat-message-row model animate-fade">
            <div class="chat-avatar">
              <Bot :size="16" />
            </div>
            <div class="chat-bubble-content">
              <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Suggestion Chips -->
        <div class="chat-suggestions-bar">
          <span class="suggestion-label">Suggestions :</span>
          <div class="suggestions-scroll">
            <button
              v-for="(sug, sIdx) in suggestions"
              :key="sIdx"
              @click="sendSuggestion(sug)"
              class="chip-btn"
            >
              {{ sug }}
            </button>
          </div>
        </div>

        <!-- Chat Input Form -->
        <form @submit.prevent="handleSendMessage" class="chat-input-form">
          <textarea
            v-model="chatInput"
            @keydown.enter.exact.prevent="handleSendMessage"
            rows="1"
            class="form-input chat-input"
            placeholder="Posez une question sur les licences, prix ou activation..."
            :disabled="chatLoading"
          ></textarea>

          <button
            type="submit"
            class="btn btn-primary btn-send"
            :disabled="chatLoading || !chatInput.trim()"
            title="Envoyer (Entrée)"
          >
            <Send :size="16" />
          </button>

          <button
            v-if="chatMessages.length > 1"
            type="button"
            @click="clearChat"
            class="btn-clear-chat"
            title="Réinitialiser la conversation"
          >
            <RotateCcw :size="14" />
          </button>
        </form>
      </div>

      <!-- 2. EXTRACTEUR RAPIDE TAB -->
      <div v-else class="drawer-body">
        <div class="prompt-section">
          <label class="prompt-label">
            <span>Message brut du client</span>
            <span class="prompt-hint">Ex: SMS, WhatsApp, Messenger</span>
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
            <div class="parsed-row">
              <span class="parsed-label">Client :</span>
              <span class="parsed-value highlight">{{ parsedResult.client_nom || 'Non spécifié' }}</span>
              <span v-if="parsedResult.client_numero" class="parsed-tag">{{ parsedResult.client_numero }}</span>
            </div>

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

            <div class="parsed-row" v-if="parsedResult.methode_paiement_id">
              <span class="parsed-label">Méthode de règlement :</span>
              <span class="badge badge-primary">ID: {{ parsedResult.methode_paiement_id }}</span>
            </div>
          </div>

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
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  Sparkles,
  Bot,
  User,
  MessageSquare,
  Zap,
  Send,
  RotateCcw,
  ShoppingCart,
  X,
  Check
} from '@lucide/vue'
import apiClient from '../api/client'

const router = useRouter()
const isOpen = ref(false)
const activeTab = ref('chat')

// Chatbot state
const chatContainerRef = ref(null)
const chatInput = ref('')
const chatLoading = ref(false)

const chatMessages = ref([
  {
    role: 'model',
    text: "Bonjour ! Je suis l'assistant IA officiel de **Licence Pro Madagascar**.\n\nJe peux vous renseigner sur nos tarifs, les guides d'activation des logiciels, ou extraire directement une vente à partir d'un message client.\n\nQue puis-je faire pour vous ?",
    time: formatTimeNow(),
    order_intent: null
  }
])

const suggestions = [
  "Quels sont les tarifs actuels ?",
  "Comment activer Windows 11 Pro ?",
  "Comment installer Office 365 ?",
  "Modes de paiement acceptés ?",
  "Conseils pour vendre Canva Pro"
]

// Extractor state
const rawText = ref('')
const loading = ref(false)
const parsedResult = ref(null)

function formatTimeNow() {
  const d = new Date()
  return d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

function renderMarkdown(raw) {
  if (!raw) return ''
  let html = raw
    // Escape basic html
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Headings
    .replace(/^### (.*$)/gim, '<h4 class="chat-h4">$1</h4>')
    .replace(/^## (.*$)/gim, '<h3 class="chat-h3">$1</h3>')
    // Bullet points
    .replace(/^• (.*$)/gim, '<li class="chat-bullet">$1</li>')
    .replace(/^- (.*$)/gim, '<li class="chat-bullet">$1</li>')
    // Line breaks
    .replace(/\n/g, '<br />')
  return html
}

async function scrollToBottom() {
  await nextTick()
  if (chatContainerRef.value) {
    chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight
  }
}

async function handleSendMessage() {
  const query = chatInput.value.trim()
  if (!query || chatLoading.value) return

  chatMessages.value.push({
    role: 'user',
    text: query,
    time: formatTimeNow()
  })

  chatInput.value = ''
  chatLoading.value = true
  await scrollToBottom()

  try {
    const historyPayload = chatMessages.value.slice(-8).map(m => ({
      role: m.role,
      text: m.text
    }))

    const res = await apiClient.post('/ai/chat/', {
      message: query,
      history: historyPayload
    })

    chatMessages.value.push({
      role: 'model',
      text: res.data.reply || "Je n'ai pas pu générer de réponse.",
      time: formatTimeNow(),
      order_intent: res.data.order_intent || null
    })
  } catch (err) {
    chatMessages.value.push({
      role: 'model',
      text: "Désolé, une erreur de communication est survenue avec le service IA.",
      time: formatTimeNow()
    })
  } finally {
    chatLoading.value = false
    await scrollToBottom()
  }
}

function sendSuggestion(sug) {
  chatInput.value = sug
  handleSendMessage()
}

function clearChat() {
  chatMessages.value = [
    {
      role: 'model',
      text: "Conversation réinitialisée ! Comment puis-je vous aider ?",
      time: formatTimeNow(),
      order_intent: null
    }
  ]
}

function applyOrderIntent(intent) {
  sessionStorage.setItem('prefill_sale', JSON.stringify(intent))
  isOpen.value = false
  router.push('/ventes?action=nouvelle')
}

// Extractor methods
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
  sessionStorage.setItem('prefill_sale', JSON.stringify(parsedResult.value))
  isOpen.value = false
  router.push('/ventes?action=nouvelle')
}

function formatPrice(val) {
  return new Intl.NumberFormat('fr-MG').format(val || 0) + ' Ar'
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
  box-shadow: 0 10px 25px rgba(0, 210, 255, 0.35);
  cursor: pointer;
  font-family: var(--font-sans);
  font-weight: 700;
  font-size: 0.9rem;
  transition: all var(--transition-normal);
}

.ai-trigger-btn:hover {
  transform: translateY(-3px) scale(1.03);
  box-shadow: 0 15px 35px rgba(0, 210, 255, 0.5);
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
  width: 480px;
  max-width: 95vw;
  background: #090e18;
  border-left: 1px solid var(--border-card);
  box-shadow: -15px 0 40px rgba(0, 0, 0, 0.85);
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
  padding: 1.15rem 1.5rem;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(13, 22, 41, 0.7);
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
  box-shadow: 0 0 15px rgba(0, 210, 255, 0.3);
}

.drawer-header h3 {
  font-size: 1.05rem;
  font-weight: 700;
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

/* Tabs switcher */
.ai-tabs-bar {
  display: flex;
  background: rgba(13, 22, 41, 0.5);
  border-bottom: 1px solid var(--border-subtle);
  padding: 0.35rem 0.75rem;
  gap: 0.5rem;
}

.ai-tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.55rem 0.85rem;
  border-radius: var(--radius-sm);
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ai-tab-btn.active {
  background: rgba(0, 210, 255, 0.15);
  color: #00d2ff;
  border: 1px solid rgba(0, 210, 255, 0.35);
  box-shadow: 0 0 12px rgba(0, 210, 255, 0.15);
}

/* CHATBOT AREA */
.chat-tab-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.chat-messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.chat-message-row {
  display: flex;
  gap: 0.75rem;
  max-width: 90%;
}

.chat-message-row.model {
  align-self: flex-start;
}

.chat-message-row.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.chat-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.chat-message-row.model .chat-avatar {
  background: rgba(0, 210, 255, 0.2);
  color: #00d2ff;
  border: 1px solid rgba(0, 210, 255, 0.4);
}

.chat-message-row.user .chat-avatar {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.4);
}

.chat-bubble-content {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.chat-text {
  padding: 0.85rem 1.1rem;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  line-height: 1.5;
}

.chat-message-row.model .chat-text {
  background: rgba(13, 22, 41, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--text-main);
  border-top-left-radius: 2px;
}

.chat-message-row.user .chat-text {
  background: rgba(0, 210, 255, 0.15);
  border: 1px solid rgba(0, 210, 255, 0.35);
  color: #f8fafc;
  border-top-right-radius: 2px;
}

.chat-time {
  font-size: 0.675rem;
  color: var(--text-muted);
  align-self: flex-end;
}

/* Order intent card inside chat */
.chat-order-card {
  margin-top: 0.5rem;
  background: rgba(0, 210, 255, 0.08);
  border: 1px solid rgba(0, 210, 255, 0.4);
  border-radius: var(--radius-md);
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  box-shadow: 0 0 15px rgba(0, 210, 255, 0.12);
}

.order-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-items-preview {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.order-item-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.06);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.775rem;
}

.item-qty {
  font-weight: 700;
  color: #00d2ff;
}

.item-name {
  flex: 1;
}

.item-price {
  color: #10b981;
  font-weight: 600;
}

.btn-fill-sale {
  width: 100%;
}

/* Typing animation */
.typing-dots {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.75rem 1rem;
  background: rgba(13, 22, 41, 0.8);
  border-radius: var(--radius-md);
}

.typing-dots span {
  width: 6px;
  height: 6px;
  background: #00d2ff;
  border-radius: 50%;
  animation: typing-bounce 1.4s infinite ease-in-out both;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing-bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

/* Suggestions */
.chat-suggestions-bar {
  padding: 0.5rem 1rem;
  border-top: 1px solid var(--border-subtle);
  background: rgba(13, 22, 41, 0.4);
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.suggestion-label {
  font-size: 0.675rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.suggestions-scroll {
  display: flex;
  gap: 0.4rem;
  overflow-x: auto;
  padding-bottom: 0.2rem;
}

.chip-btn {
  white-space: nowrap;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 0.725rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chip-btn:hover {
  background: rgba(0, 210, 255, 0.15);
  color: #00d2ff;
  border-color: rgba(0, 210, 255, 0.4);
}

/* Chat Input Bar */
.chat-input-form {
  padding: 0.85rem 1rem;
  border-top: 1px solid var(--border-subtle);
  background: rgba(9, 14, 24, 0.95);
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.chat-input {
  flex: 1;
  resize: none;
  font-size: 0.85rem;
  padding: 0.65rem 0.85rem;
}

.btn-send {
  padding: 0.65rem 0.9rem;
  border-radius: var(--radius-sm);
}

.btn-clear-chat {
  background: transparent;
  border: none;
  color: var(--text-muted);
  padding: 0.5rem;
  cursor: pointer;
  border-radius: 4px;
}

.btn-clear-chat:hover {
  color: var(--text-main);
  background: rgba(255, 255, 255, 0.08);
}

/* EXTRACTOR TAB BODY */
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
  background: rgba(0, 210, 255, 0.2);
  color: #00d2ff;
  border-color: rgba(0, 210, 255, 0.4);
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
  background: rgba(0, 210, 255, 0.1);
  border: 1px solid rgba(0, 210, 255, 0.25);
  padding: 0.4rem 0.65rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
}

.qty-badge {
  background: var(--primary-color);
  color: #050b14;
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
  color: #10b981;
  font-weight: 600;
}

.btn-apply {
  width: 100%;
}
</style>
