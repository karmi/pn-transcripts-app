<template>
  <div v-if="errorMsg" class="error-banner" role="alert">
    {{ errorMsg }}
  </div>

  <div v-else-if="item" class="player-container">
    <header class="player-header">
      <div>
        <div class="title">{{ item.name }}</div>
        <div class="muted">
          <a :href="item.url" target="_blank" rel="noreferrer">{{ item.url }}</a>
        </div>
      </div>
      <audio ref="audioEl"
             :src="mediaUrl"
             @timeupdate="onTime"
             controls preload="metadata"
             class="player-audio">
      </audio>
    </header>

    <div class="player-transcript-wrapper">
      <Transcript
        :words="wordsSec"
        :current-time="currentTime"
        @seek="onSeek"
      />
    </div>
  </div>

  <div v-else class="muted">Loading…</div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useRoute } from 'vue-router'
import Transcript from '../components/Transcript.vue'

const API_BASE = import.meta.env.VITE_API_BASE || ''
const route = useRoute()
const id = route.params.id

const item = ref(null)
const transcript = ref(null)
const audioEl = ref(null)
const currentTime = ref(0)
const errorMsg = ref(null)

const mediaUrl = computed(() => `${API_BASE}/media/${id}`)

const wordsSec = computed(() => {
  const ws = transcript.value?.words || []
  return ws.map(w => {
    // If JSON has `start`/`end`, they are ms -> divide
    if (w.start != null && w.end != null) {
      return {
        t0: w.start / 1000,
        t1: w.end / 1000,
        text: w.text,
        spk: w.speaker ?? w.spk
      }
    }
    // Otherwise expect already-seconds fields
    return {
      t0: w.t0,
      t1: w.t1,
      text: w.text,
      spk: w.speaker ?? w.spk
    }
  }).filter(w => Number.isFinite(w.t0) && Number.isFinite(w.t1))
    .sort((a,b) => a.t0 - b.t0)
})

onMounted(async () => {
  try {
    const res = await fetch(`${API_BASE}/api/items/${id}`)

    if (!res.ok) {
      if (res.status === 404) {
        errorMsg.value = 'Resource not found (404)'
      } else if (res.status >= 500) {
        errorMsg.value = 'Server error, please try again later'
      } else {
        errorMsg.value = `Error: ${res.status} ${res.statusText}`
      }
      return
    }

    const data = await res.json()
    item.value = data.item
    transcript.value = data.transcript

    window.addEventListener('keydown', onKeydown)
  } catch(err) {
    errorMsg.value = `Network error (${err.message})`
    console.error('API:', err)
  }
})

function onTime(e) {
  currentTime.value = e.target.currentTime
}

function toggle() {
  const a = audioEl.value
  if (!a) return
  if (a.paused) a.play()
  else a.pause()
}

function onKeydown(e) {
  // Ignore when typing in inputs, textareas, contenteditable, etc.
  const el = e.target
  const tag = el && el.tagName
  const isEditable =
    (el && (el.isContentEditable === true)) ||
    tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || tag === 'BUTTON'
  if (isEditable) return

  // Spacebar toggles playback
  if (e.code === 'Space' || e.key === ' ') {
    e.preventDefault()
    toggle()
  }
}

function onSeek(t) {
  const a = audioEl.value
  if (!a) return
  a.currentTime = t
  a.play()
}

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>
