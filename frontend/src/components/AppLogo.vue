<template>
  <img :src="logoSrc" alt="STUFF Logo" :class="['app-logo', { 'login-logo': usePng }]" />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  usePng: {
    type: Boolean,
    default: false
  }
})

const logoSrc = computed(() => {
  return props.usePng ? new URL('@/assets/images/logo.png', import.meta.url).href : new URL('@/assets/images/logo.svg', import.meta.url).href
})
</script>

<style scoped>
.app-logo {
  height: 40px;
  transition: transform 0.2s ease-in-out;
}

.app-logo:hover {
  transform: scale(1.05);
}

.login-logo {
  height: 80px;
}
</style> 