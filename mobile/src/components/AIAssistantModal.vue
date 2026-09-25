<template>
  <ion-modal :is-open="isOpen" @didDismiss="$emit('close')" :initial-breakpoint="0.9" :breakpoints="[0, 0.5, 0.9, 1]">
    <ion-header>
      <ion-toolbar class="modal-toolbar">
        <ion-title>
          <div class="ai-title">
            <ion-icon :icon="sparkles" class="ai-sparkle" />
            <span>Assistant Virtuel IA</span>
          </div>
        </ion-title>
        <ion-buttons slot="end">
          <ion-button @click="$emit('close')">
            <ion-icon :icon="closeOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>

      <!-- Segment Tabs -->
      <ion-segment :value="activeTab" @ionChange="activeTab = $event.detail.value" class="modal-segment">
        <ion-segment-button value="chat">
          <ion-label>Chatbot IA</ion-label>
        </ion-segment-button>
        <ion-segment-button value="extractor">
          <ion-label>Extracteur</ion-label>
        </ion-segment-button>
      </ion-segment>
    </ion-header>

    <ion-content class="ion-padding modal-content">
      <!-- 1. CHATBOT TAB -->
      <div v-if="activeTab === 'chat'" class="chat-container">
        <div ref="chatScrollRef" class="chat-messages">
          <div
            v-for="(msg, idx) in chatMessages"
            :key="idx"
            :class="['chat-bubble', msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-model']"
          >
            <div class="bubble-header">
              <span class="bubble-sender">{{ msg.role === 'user' ? 'Vous' : 'Licence Pro IA' }}</span>
              <span class="bubble-time">{{ msg.time }}</span>
            </div>

            <div class="bubble-text" v-html="renderMarkdown(msg.text)"></div>

            <!-- Order detected card -->
            <div v-if="msg.order_intent && msg.order_intent.articles?.length" class="order-intent-card">
              <div class="intent-header">
                <strong>⚡ Commande détectée</strong>
                <span class="intent-badge">Prêt</span>
              </div>
              <div v-if="msg.order_intent.client_nom" class="intent-client">
                Client : <b>{{ msg.order_intent.client_nom }}</b>
                <span v-if="msg.order_intent.client_numero"> ({{ msg.order_intent.client_numero }})</span>
              </div>
              <div class="intent-articles">
                <span v-for="(art, aIdx) in msg.order_intent.articles" :key="aIdx" class="intent-chip">
                  {{ art.quantite }}x {{ art.produit_nom }}
                </span>
              </div>
              <button class="btn-apply-intent" @click="handleApplyIntent(msg.order_intent)">
                Créer la vente avec ces infos
              </button>
            </div>
          </div>

          <div v-if="chatLoading" class="chat-bubble chat-bubble-model loading-bubble">
            <span class="dot-pulse">L'assistant réfléchit...</span>
          </div>
        </div>

        <!-- Quick suggestion chips -->
        <div class="suggestion-chips">
          <button
            v-for="(sug, sIdx) in suggestions"
            :key="sIdx"
            class="chip-btn"
            @click="sendSuggestion(sug)"
          >
            {{ sug }}
          </button>
        </div>

        <!-- Chat Input Bar -->
        <div class="chat-bar">
          <input
            v-model="chatInput"
            @keydown.enter="sendMessage"
            type="text"
            placeholder="Posez une question sur les licences..."
            class="chat-input-field"
            :disabled="chatLoading"
          />
          <button @click="sendMessage" :disabled="!chatInput.trim() || chatLoading" class="chat-send-btn">
            <ion-icon :icon="send" />
          </button>
        </div>
      </div>

      <!-- 2. EXTRACTEUR TAB -->
      <div v-else class="extractor-container">
        <p class="extractor-tip">
          Collez le message reçu d'un client (WhatsApp, SMS, Messenger). L'IA extrait automatiquement le nom, numéro, produits, quantités et méthode de règlement.
        </p>

        <textarea
          v-model="rawText"
          rows="5"
          placeholder="Ex: Bonjour, je voudrais commander 2 licences Windows 11 Pro et 1 Office 365, je m'appelle Andry (0341234567), je paye par MVola."
          class="extractor-textarea"
        ></textarea>

        <div class="example-pills">
          <button @click="setExample(1)" class="pill-btn">Exemple 1: 2x Windows 11</button>
          <button @click="setExample(2)" class="pill-btn">Exemple 2: Office + Canva</button>
        </div>

        <button @click="extractData" :disabled="!rawText.trim() || extractLoading" class="btn-analyze">
          <ion-icon :icon="sparkles" />
          <span>{{ extractLoading ? 'Analyse en cours...' : 'Extraire les données' }}</span>
        </button>

        <div v-if="parsedData" class="extracted-result">
          <h4 class="result-title">Données extraites :</h4>
          <div class="result-row">
            <span>Client :</span>
            <b>{{ parsedData.client_nom || 'Non spécifié' }}</b>
            <span v-if="parsedData.client_numero" class="tag-phone">{{ parsedData.client_numero }}</span>
          </div>

          <div class="result-articles">
            <span>Articles détectés :</span>
            <div v-for="(it, iIdx) in parsedData.articles" :key="iIdx" class="article-badge">
              {{ it.quantite }}x {{ it.produit_nom }}
            </div>
          </div>

          <button @click="handleApplyIntent(parsedData)" class="btn-apply-intent full">
            Ouvrir et pré-remplir la vente
          </button>
        </div>
      </div>
    </ion-content>
  </ion-modal>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import {
  IonModal,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonButton,
  IonIcon,
  IonSegment,
  IonSegmentButton,
  IonLabel,
  IonContent,
} from '@ionic/vue'
import { sparkles, closeOutline, send } from 'ionicons/icons'
import apiClient from '../api/client'
import { useSaleDraft } from '../composables/useSaleDraft'

defineProps({
  isOpen: Boolean,
})
const emit = defineEmits(['close'])

const { setDraft } = useSaleDraft()

const activeTab = ref('chat')
const chatScrollRef = ref(null)
const chatInput = ref('')
const chatLoading = ref(false)

const chatMessages = ref([
  {
    role: 'model',
    text: "Bonjour ! Je suis l'assistant IA de **Licence Pro Madagascar**.\nPosez-moi vos questions sur nos clés de licence, prix, ou collez les messages de vos clients.",
    time: getCurrentTime(),
    order_intent: null,
  },
])

const suggestions = [
  "Quels sont les tarifs des licences ?",
  "Comment activer Windows 11 ?",
  "Modes de paiement acceptés ?",
]

const rawText = ref('')
const extractLoading = ref(false)
const parsedData = ref(null)

function getCurrentTime() {
  const d = new Date()
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function renderMarkdown(raw) {
  if (!raw) return ''
  return raw
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br />')
}

async function scrollToBottom() {
  await nextTick()
  if (chatScrollRef.value) {
    chatScrollRef.value.scrollTop = chatScrollRef.value.scrollHeight
  }
}

async function sendMessage() {
  const text = chatInput.value.trim()
  if (!text || chatLoading.value) return

  chatMessages.value.push({
    role: 'user',
    text,
    time: getCurrentTime(),
  })
  chatInput.value = ''
  chatLoading.value = true
  await scrollToBottom()

  try {
    const historyPayload = chatMessages.value.slice(-6).map((m) => ({
      role: m.role,
      text: m.text,
    }))

    const res = await apiClient.post('/ai/chat/', {
      message: text,
      history: historyPayload,
    })

    chatMessages.value.push({
      role: 'model',
      text: res.data.reply || "Réponse non disponible.",
      time: getCurrentTime(),
      order_intent: res.data.order_intent || null,
    })
  } catch (err) {
    chatMessages.value.push({
      role: 'model',
      text: "Désolé, impossible de contacter le serveur IA pour le moment.",
      time: getCurrentTime(),
    })
  } finally {
    chatLoading.value = false
    await scrollToBottom()
  }
}

function sendSuggestion(sug) {
  chatInput.value = sug
  sendMessage()
}

function setExample(num) {
  if (num === 1) {
    rawText.value = "Bonjour, je m'appelle Andry (034 12 345 67). Je voudrais commander 2 licences Windows 11 Pro par MVola."
  } else {
    rawText.value = "Salut, c'est Sarah (032 99 888 77), 1 licence Office 365 et 1 compte Canva Pro s'il vous plaît, paiement Orange Money."
  }
}

async function extractData() {
  if (!rawText.value.trim() || extractLoading.value) return
  extractLoading.value = true
  parsedData.value = null

  try {
    const res = await apiClient.post('/ai/extract/', {
      raw_text: rawText.value,
    })
    parsedData.value = res.data
  } catch (err) {
    alert("Erreur lors de l'analyse du texte.")
  } finally {
    extractLoading.value = false
  }
}

function handleApplyIntent(intent) {
  setDraft(intent)
  emit('close')
}
</script>

<style scoped>
.modal-toolbar {
  --background: #0B1120;
  --color: #FFFFFF;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.ai-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 1rem;
}

.ai-sparkle {
  color: #14B8A6;
}

.modal-segment {
  --background: #151F32;
  margin: 8px 16px;
  border-radius: 10px;
}

.modal-content {
  --background: #0B1120;
  --color: #F8FAFC;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 16px;
  max-height: calc(70vh - 120px);
}

.chat-bubble {
  max-width: 85%;
  padding: 12px 14px;
  border-radius: 14px;
  font-size: 0.88rem;
  line-height: 1.45;
}

.chat-bubble-user {
  align-self: flex-end;
  background: #0D9488;
  color: #FFFFFF;
  border-bottom-right-radius: 4px;
}

.chat-bubble-model {
  align-self: flex-start;
  background: #151F32;
  color: #E2E8F0;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-bottom-left-radius: 4px;
}

.bubble-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  opacity: 0.7;
  margin-bottom: 4px;
}

.order-intent-card {
  margin-top: 10px;
  padding: 10px;
  background: rgba(13, 148, 136, 0.15);
  border: 1px solid rgba(13, 148, 136, 0.4);
  border-radius: 8px;
}

.intent-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
  color: #5EEAD4;
}

.intent-badge {
  background: #0D9488;
  color: #fff;
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 4px;
}

.intent-client {
  font-size: 0.78rem;
  margin: 4px 0;
}

.intent-articles {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}

.intent-chip {
  background: #1E293B;
  color: #93C5FD;
  font-size: 0.72rem;
  padding: 2px 6px;
  border-radius: 4px;
}

.btn-apply-intent {
  width: 100%;
  margin-top: 8px;
  background: #0D9488;
  color: #ffffff;
  border: none;
  padding: 8px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
}

.btn-apply-intent.full {
  margin-top: 16px;
  padding: 12px;
  font-size: 0.9rem;
}

.suggestion-chips {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 8px 0;
}

.chip-btn {
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94A3B8;
  padding: 6px 12px;
  border-radius: 9999px;
  font-size: 0.75rem;
  white-space: nowrap;
}

.chat-bar {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.chat-input-field {
  flex: 1;
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 10px 14px;
  color: #FFFFFF;
  font-size: 0.88rem;
  outline: none;
}

.chat-send-btn {
  background: #0D9488;
  color: #FFFFFF;
  border: none;
  border-radius: 12px;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.extractor-tip {
  font-size: 0.82rem;
  color: #94A3B8;
  margin-bottom: 10px;
}

.extractor-textarea {
  width: 100%;
  background: #151F32;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px;
  color: #FFFFFF;
  font-size: 0.85rem;
  outline: none;
  resize: none;
}

.example-pills {
  display: flex;
  gap: 8px;
  margin: 10px 0;
}

.pill-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px dashed rgba(255, 255, 255, 0.15);
  color: #CBD5E1;
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 0.72rem;
}

.btn-analyze {
  width: 100%;
  background: linear-gradient(135deg, #0D9488 0%, #0284C7 100%);
  color: #FFFFFF;
  border: none;
  padding: 12px;
  border-radius: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.extracted-result {
  margin-top: 16px;
  background: #151F32;
  padding: 14px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.result-title {
  margin: 0 0 10px 0;
  font-size: 0.9rem;
  color: #5EEAD4;
}

.result-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
}

.tag-phone {
  background: #1E293B;
  color: #38BDF8;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
}

.result-articles {
  margin-top: 10px;
  font-size: 0.85rem;
}

.article-badge {
  display: inline-block;
  background: rgba(13, 148, 136, 0.2);
  color: #5EEAD4;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.78rem;
  margin: 4px 4px 0 0;
}
</style>
