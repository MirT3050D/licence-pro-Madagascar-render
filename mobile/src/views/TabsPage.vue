<template>
  <ion-page>
    <ion-tabs>
      <ion-router-outlet />
      
      <ion-tab-bar slot="bottom" class="custom-tab-bar">
        <ion-tab-button tab="dashboard" href="/tabs/dashboard">
          <ion-icon :icon="pieChartOutline" />
          <ion-label>Dashboard</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="ventes" href="/tabs/ventes">
          <ion-icon :icon="cartOutline" />
          <ion-label>Ventes</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="clients" href="/tabs/clients">
          <ion-icon :icon="peopleOutline" />
          <ion-label>Clients</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="produits" href="/tabs/produits">
          <ion-icon :icon="cubeOutline" />
          <ion-label>Produits</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="profil" href="/tabs/profil">
          <ion-icon :icon="personCircleOutline" />
          <ion-label>Profil</ion-label>
        </ion-tab-button>
      </ion-tab-bar>
    </ion-tabs>

    <!-- Floating Assistant IA Button (Fixed above bottom tabs) -->
    <ion-fab vertical="bottom" horizontal="end" slot="fixed" class="ai-fab">
      <ion-fab-button @click="isAiOpen = true" class="ai-fab-btn">
        <ion-icon :icon="sparkles" />
      </ion-fab-button>
    </ion-fab>

    <!-- AI Assistant Modal / Sheet -->
    <AIAssistantModal :is-open="isAiOpen" @close="isAiOpen = false" />
  </ion-page>
</template>

<script setup>
import { ref } from 'vue'
import {
  IonPage,
  IonTabs,
  IonRouterOutlet,
  IonTabBar,
  IonTabButton,
  IonIcon,
  IonLabel,
  IonFab,
  IonFabButton,
} from '@ionic/vue'
import {
  pieChartOutline,
  cartOutline,
  peopleOutline,
  cubeOutline,
  personCircleOutline,
  sparkles,
} from 'ionicons/icons'
import AIAssistantModal from '../components/AIAssistantModal.vue'

const isAiOpen = ref(false)
</script>

<style scoped>
.custom-tab-bar {
  background: rgba(11, 17, 32, 0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  height: 64px;
  padding-bottom: env(safe-area-inset-bottom);
}

ion-tab-button {
  --color: #64748B;
  --color-selected: #0D9488;
  font-size: 0.72rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

ion-tab-button ion-icon {
  font-size: 22px;
  margin-bottom: 2px;
}

.ai-fab {
  margin-bottom: 74px;
  margin-right: 16px;
  z-index: 99;
}

.ai-fab-btn {
  --background: linear-gradient(135deg, #0D9488 0%, #2563EB 100%);
  --color: #FFFFFF;
  --box-shadow: 0 10px 25px -5px rgba(13, 148, 136, 0.5), 0 8px 10px -6px rgba(13, 148, 136, 0.5);
  animation: pulse-glow 3s infinite ease-in-out;
}

@keyframes pulse-glow {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 8px 20px rgba(13, 148, 136, 0.4);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 12px 28px rgba(13, 148, 136, 0.65);
  }
}
</style>
