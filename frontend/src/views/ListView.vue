<template>
  <div>
    <div v-if="errorMsg" class="error-banner" role="alert">
      {{ errorMsg }}
    </div>

    <div v-else-if="items.length" class="grid">
      <router-link v-for="it in items" :key="it.id" class="card" :to="'/play/' + it.id">
        <div class="title">{{ it.name }}</div>
        <div class="muted">{{ it.category }} · speech: {{ it.quality_speech }} · audio: {{ it.quality_audio }}</div>
        <div class="muted" style="margin-top:6px">{{ it.note }}</div>
      </router-link>
    </div>

    <div v-else class="muted">Loading…</div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
const API_BASE = import.meta.env.VITE_API_BASE || ''

const items = ref([])
const errorMsg = ref(null)

onMounted(async () => {
  try {
    const res = await fetch(`${API_BASE}/api/items`)

    if (!res.ok) {
      errorMsg.value = 'Error'
      if (res.status === 404) {
        errorMsg.value = 'Resource not found (404)'
      } else if (res.status >= 500) {
        errorMsg.value = 'Server error, please try again later'
      } else {
        errorMsg.value = `Error: ${res.status} ${res.statusText}`
      }
      return
    }

    items.value = await res.json()
  } catch (err) {
    errorMsg.value = `Network error (${err.message})`
    console.error('API:', err)
  }
})
</script>
