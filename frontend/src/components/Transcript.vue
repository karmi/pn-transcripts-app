<template>
  <section ref="wrap" class="transcript-root">
    <span
      v-for="(w, i) in words"
      :key="i"
      class="word"
      :class="{ active: i === activeIdx }"
      @click="$emit('seek', w.t0)"
      :data-t0="w.t0"
    >
      {{ w.text + ' ' }}
    </span>
  </section>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  words: { type: Array, required: true },
  currentTime: { type: Number, required: true }
})

const wrap = ref(null)
const activeIdx = ref(-1)

function findActiveIdx(t) {
  let lo = 0, hi = props.words.length - 1, ans = -1
  while (lo <= hi) {
    const mid = (lo + hi) >> 1
    const w = props.words[mid]
    if (t < w.t0) hi = mid - 1
    else if (t >= w.t1) lo = mid + 1
    else { ans = mid; break }
  }
  return ans
}

function updateActive(t) {
  if (!props.words.length) { activeIdx.value = -1; return }
  const idx = findActiveIdx(t)
  activeIdx.value = idx
}

onMounted(() => { updateActive(0) })
watch(() => props.currentTime, t => updateActive(t))
watch(() => props.words, () => updateActive(props.currentTime), { deep: true })
</script>
