<template>
  <div :class="`p-4 bg-white rounded-lg shadow-sm border border-${themeClass.primary}/20 mb-4`">
    <h4 :class="`text-sm font-semibold text-${themeClass.primary} mb-3`">
      {{ autoMode ? '🚀 自动模式' : '🎯 手动模式' }}
    </h4>
    
    <div
      :class="`drop-zone ${isDragover ? 'dragover' : ''}`"
      :style="{
        borderColor: `var(--${themeClass.primary.replace('-', '')})`,
        backgroundColor: isDragover ? `var(--${themeClass.secondary.replace('-', '')})` : `var(--${themeClass.secondary.replace('-', '')})/0.3`
      }"
      @dragover.prevent="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDrop"
      @click="triggerFileInput"
    >
      <div class="text-center">
        <div class="text-4xl mb-2">
          {{ isDragover ? '📂' : autoMode ? '⚡' : '📁' }}
        </div>
        <div :class="`text-lg font-medium text-${themeClass.primary} mb-1`">
          {{ isDragover ? '释放文件' : '拖拽文件到这里' }}
        </div>
        <div class="text-sm text-gray-500">
          {{ autoMode ? '拖拽即自动恢复' : '或点击选择文件' }}
        </div>
        <div class="text-xs text-gray-400 mt-2">
          支持多文件和文件夹
        </div>
      </div>
    </div>
    
    <!-- 隐藏的文件输入 -->
    <input 
      ref="fileInput" 
      type="file" 
      multiple 
      style="display: none" 
      @change="onFileChange" 
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  autoMode: { 
    type: Boolean, 
    default: true 
  },
  themeClass: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['filesDropped'])

const isDragover = ref(false)
const fileInput = ref(null)

function onDragOver() { 
  isDragover.value = true 
}

function onDragLeave() { 
  isDragover.value = false 
}

function onDrop(e) {
  isDragover.value = false
  const files = Array.from(e.dataTransfer.files)
  
  // 处理文件路径
  const filePaths = files.map(file => {
    // pywebview 会自动注入完整路径
    return file.path || file.webkitRelativePath || file.name
  })
  
  console.log('拖拽文件:', filePaths)
  emit('filesDropped', filePaths)
  
  // 如果有 pywebview API，也调用后端
  if (window.pywebview?.api?.process_files) {
    window.pywebview.api.process_files(files, props.autoMode)
  }
}

function triggerFileInput() {
  fileInput.value?.click()
}

function onFileChange(e) {
  const files = Array.from(e.target.files)
  const filePaths = files.map(file => file.name)
  
  console.log('选择文件:', filePaths)
  emit('filesDropped', filePaths)
  
  // 清空输入以允许重复选择同一文件
  e.target.value = ''
  
  // 如果有 pywebview API，也调用后端
  if (window.pywebview?.api?.process_files) {
    window.pywebview.api.process_files(files, props.autoMode)
  }
}
</script>

<style scoped>
.drop-zone {
  border: 2px dashed;
  border-radius: 12px;
  padding: 2rem 1rem;
  text-align: center;
  font-size: 16px;
  transition: all 0.3s ease;
  cursor: pointer;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-zone:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.drop-zone.dragover {
  transform: scale(1.02);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}
</style>