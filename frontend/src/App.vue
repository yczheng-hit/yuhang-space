<script setup>
import AppHeader from './components/layout/AppHeader.vue'
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <AppHeader />
    <main class="container mx-auto px-4 py-8">
      <router-view />
    </main>
  </div>
</template>
