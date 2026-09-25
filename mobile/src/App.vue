<template>
  <ion-app>
    <ion-router-outlet />
  </ion-app>
</template>

<script setup>
import { IonApp, IonRouterOutlet } from '@ionic/vue'
</script>

<style>
/* Safe area padding for notch & home indicator */
ion-app {
  background-color: #0B1120;
}
</style>
