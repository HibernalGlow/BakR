<template>
  <div id="log" class="log-panel" ref="logPanel">
    <div v-for="(line, i) in logs" :key="i" v-html="line"></div>
  </div>
</template>
<script setup>
import { ref, watch, nextTick } from 'vue'
const props = defineProps({ logs: Array })
const logPanel = ref(null)
watch(() => props.logs.length, () => {
  nextTick(() => {
    if (logPanel.value) logPanel.value.scrollTop = logPanel.value.scrollHeight
  })
})
</script>
<style scoped>
.log-panel {
  height: 180px;
  overflow: auto;
  background: #222;
  color: #0f0;
  padding: 8px;
  font-size: 13px;
  margin-top: 18px;
  border-radius: 6px;
  font-family: monospace;
}
</style> 