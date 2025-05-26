<template>
  <div class="container">
    <h1>Baku 文件处理</h1>
    <div
      class="drop-area"
      @dragover.prevent
      @drop.prevent="onDrop"
    >
      <p>拖拽文件到此处，或</p>
      <button @click="onSelectFile">选择文件</button>
    </div>
    <div v-if="filePath" class="file-info">
      <strong>文件路径：</strong> {{ filePath }}
    </div>
    <div v-if="result" class="result">
      <strong>处理结果：</strong>
      <pre>{{ result }}</pre>
    </div>
    <div v-if="loading" class="loading">处理中...</div>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { selectAndProcessFile, listenFileDrop } from './hooks/useTauriFile'

const filePath = ref<string | null>(null)
const result = ref<string | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

async function onSelectFile() {
  error.value = null
  loading.value = true
  try {
    const res = await selectAndProcessFile()
    if (res) {
      result.value = res
      filePath.value = '（通过选择获得，见下方结果）'
    }
  } catch (e: any) {
    error.value = e?.message || '处理失败'
  } finally {
    loading.value = false
  }
}

// 拖拽文件到页面
function onDrop(e: DragEvent) {
  error.value = null
  loading.value = true
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    // 不能直接用 files[0].path，需用 tauri 事件
    // 这里直接用 listenFileDrop 监听
    // 但为体验，直接用 open 也可
    // 推荐用 tauri 事件
  }
}

// 页面挂载时监听拖拽
listenFileDrop(async (path) => {
  filePath.value = path
  loading.value = true
  error.value = null
  try {
    const { invoke } = await import('@tauri-apps/api/tauri')
    const res = await invoke<string>('process_file', { filePath: path })
    result.value = res
  } catch (e: any) {
    error.value = e?.message || '处理失败'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.container {
  max-width: 500px;
  margin: 40px auto;
  padding: 32px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 16px #0001;
  text-align: center;
}
.drop-area {
  border: 2px dashed #8884;
  border-radius: 8px;
  padding: 32px 0;
  margin-bottom: 16px;
  background: #f8f8fa;
  cursor: pointer;
  transition: border-color 0.2s;
}
.drop-area:hover {
  border-color: #42b983;
}
.file-info, .result, .loading, .error {
  margin-top: 16px;
  text-align: left;
  word-break: break-all;
}
.result pre {
  background: #f4f4f4;
  padding: 8px;
  border-radius: 4px;
}
.loading {
  color: #888;
}
.error {
  color: #d00;
}
button {
  margin-top: 8px;
  padding: 8px 24px;
  background: #42b983;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
button:hover {
  background: #369870;
}
</style>