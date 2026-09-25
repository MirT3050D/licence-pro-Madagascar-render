<template>
  <!-- Fullscreen Login Layout -->
  <div v-if="$route.name === 'login'" class="app-fullscreen">
    <router-view />
  </div>

  <!-- Authenticated Dashboard Layout -->
  <div v-else class="app-layout">
    <!-- Sidebar Navigation -->
    <Sidebar />

    <!-- Main Content Container -->
    <div class="main-wrapper">
      <TopNavbar />

      <main class="page-content animate-fade">
        <router-view />
      </main>
    </div>

    <!-- Universal Floating AI Assistant Drawer -->
    <AIAssistantDrawer />
  </div>
</template>

<script setup>
import Sidebar from './components/Sidebar.vue'
import TopNavbar from './components/TopNavbar.vue'
import AIAssistantDrawer from './components/AIAssistantDrawer.vue'
</script>

<style scoped>
.app-fullscreen {
  min-height: 100vh;
  width: 100%;
}

.app-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--bg-app);
  position: relative;
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 100vh;
}

.page-content {
  flex: 1;
  padding: 2rem;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .page-content {
    padding: 1rem;
  }
}
</style>
