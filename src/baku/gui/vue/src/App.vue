<script setup>
import { ref, onMounted } from 'vue'
import DragDropZone from './components/DragDropZone.vue'
import ProgressBar from './components/ProgressBar.vue'
import ResultList from './components/ResultList.vue'
import LogPanel from './components/LogPanel.vue'

const showDevtools = ref(import.meta.env.DEV)
function toggleDevtools() {
  if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__) {
    window.__VUE_DEVTOOLS_GLOBAL_HOOK__.emit('toggle')
  }
}

const progressVisible = ref(false)
const results = ref([])
const logs = ref([])

onMounted(() => {
  window.showProcessing = function() { progressVisible.value = true }
  window.showResults = function(res) { progressVisible.value = false; results.value = res }
  window.appendLog = function(msg) {
    // 日志高亮
    let color = '#0f0', icon = ''
    if (/SUCCESS|✔|✓/.test(msg)) { color = '#4caf50'; icon = '✔ ' }
    else if (/ERROR|✗|❌|失败/.test(msg)) { color = '#f44336'; icon = '✗ ' }
    else if (/WARN|警告/.test(msg)) { color = '#ff9800'; icon = '⚠ ' }
    else if (/INFO|ℹ️/.test(msg)) { color = '#2196f3'; icon = 'ℹ️ ' }
    logs.value.push(`<span style=\"color:${color}\">${icon}${msg}</span>`)
  }
})
</script>

<template>
  <header>
    <img alt="Vue logo" class="logo" src="./assets/logo.svg" width="125" height="125" />
    <div class="wrapper">
      <!-- 可保留欢迎组件或自定义 -->
    </div>
  </header>
  <main>
    <DragDropZone />
    <ProgressBar :visible="progressVisible" />
    <ResultList :results="results" />
    <LogPanel :logs="logs" />
    <button v-if="showDevtools" @click="toggleDevtools">Toggle Devtools</button>
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
}
.logo {
  display: block;
  margin: 0 auto 2rem;
}
@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }
  .logo {
    margin: 0 2rem 0 0;
  }
  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
