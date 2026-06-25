<script setup>
import AppHeader from './components/layout/AppHeader.vue'
</script>

<template>
  <div class="min-h-screen relative overflow-hidden">
    <!-- Animated gradient background -->
    <div class="fixed inset-0 -z-10 bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-100"></div>

    <!-- Floating decorative blobs -->
    <div class="fixed -z-10 top-[-10%] left-[-5%] w-[500px] h-[500px] rounded-full bg-gradient-to-br from-violet-300/30 to-fuchsia-300/30 blur-3xl animate-blob pointer-events-none"></div>
    <div class="fixed -z-10 top-[40%] right-[-10%] w-[600px] h-[600px] rounded-full bg-gradient-to-br from-cyan-300/20 to-blue-300/20 blur-3xl animate-blob animation-delay-2000 pointer-events-none"></div>
    <div class="fixed -z-10 bottom-[-5%] left-[30%] w-[450px] h-[450px] rounded-full bg-gradient-to-br from-pink-300/25 to-rose-300/25 blur-3xl animate-blob animation-delay-4000 pointer-events-none"></div>

    <!-- Decorative grid pattern -->
    <div class="fixed -z-10 inset-0 opacity-[0.03] pointer-events-none" style="background-image: radial-gradient(circle, #6366f1 1px, transparent 1px); background-size: 30px 30px;"></div>

    <AppHeader />
    <main class="container mx-auto px-4 py-8 max-w-6xl relative">
      <router-view />
    </main>
  </div>
</template>

<style>
@keyframes blob {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -50px) scale(1.1); }
  50% { transform: translate(-20px, 20px) scale(0.95); }
  75% { transform: translate(40px, 30px) scale(1.05); }
}
.animate-blob {
  animation: blob 20s ease-in-out infinite;
}
.animation-delay-2000 {
  animation-delay: 2s;
}
.animation-delay-4000 {
  animation-delay: 4s;
}
</style>
