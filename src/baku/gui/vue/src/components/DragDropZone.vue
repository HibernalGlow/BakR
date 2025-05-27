<template>
  <div
    class="drop-zone"
    :class="{ dragover: isDragover }"
    @dragover.prevent="onDragOver"
    @dragleave="onDragLeave"
    @drop="onDrop"
    @click="triggerFileInput"
  >
    拖拽文件到这里，或点击选择
    <input type="file" multiple ref="fileInput" style="display:none" @change="onFileChange" />
  </div>
</template>

<script setup>
import { ref, toRefs } from 'vue'
const props = defineProps({
  autoMode: { type: Boolean, default: true }
})
const isDragover = ref(false)
const fileInput = ref(null)

function onDragOver() { isDragover.value = true }
function onDragLeave() { isDragover.value = false }
function onDrop(e) {
  isDragover.value = false
  const files = Array.from(e.dataTransfer.files)
  // 关键：pywebview 会自动为每个 file 注入 pywebviewFullPath
  files.forEach(f => {
    console.log(f.name, f.pywebviewFullPath) // 这里能拿到完整路径
  })
  // 你可以直接传递 files 给 Python
  if (window.pywebview && window.pywebview.api && window.pywebview.api.process_files) {
    // 传递 autoMode 给后端
    window.pywebview.api.process_files(files, props.autoMode)
  }
}
function triggerFileInput() {
  fileInput.value && fileInput.value.click()
}
function onFileChange(e) {
  const files = Array.from(e.target.files)
  // 同理，pywebviewFullPath 也会有
  if (window.pywebview && window.pywebview.api && window.pywebview.api.process_files) {
    window.pywebview.api.process_files(files, props.autoMode)
  }
}
</script>

<style scoped>
.drop-zone {
  border: 2px dashed #4a90e2;
  border-radius: 10px;
  background: #f0f7ff;
  color: #4a90e2;
  text-align: center;
  padding: 40px 0;
  font-size: 20px;
  margin-bottom: 24px;
  transition: background 0.2s, border-color 0.2s;
  cursor: pointer;
}
.drop-zone.dragover {
  background: #e3f2fd;
  border-color: #1976d2;
}
</style> 