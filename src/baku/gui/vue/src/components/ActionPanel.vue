<template>
  <div :class="`p-4 space-y-4 bg-${themeClass.secondary}/30`">
    <!-- 文件操作区 -->
    <div :class="`p-4 bg-white rounded-lg shadow-sm border border-${themeClass.primary}/20`">
      <h4 :class="`text-sm font-semibold text-${themeClass.primary} mb-3`">📁 文件操作</h4>
      <div class="grid grid-cols-2 gap-2">
        <button
          @click="addFiles"
          :class="`px-3 py-2 text-sm bg-${themeClass.primary} text-white rounded hover:opacity-80 transition-opacity flex items-center justify-center space-x-1`"
        >
          <span>📂</span>
          <span>添加文件</span>
        </button>
        <button
          @click="addFolder"
          :class="`px-3 py-2 text-sm bg-${themeClass.accent} text-white rounded hover:opacity-80 transition-opacity flex items-center justify-center space-x-1`"
        >
          <span>📁</span>
          <span>添加文件夹</span>
        </button>
      </div>
    </div>

    <!-- 队列操作区 -->
    <div :class="`p-4 bg-white rounded-lg shadow-sm border border-${themeClass.primary}/20`">
      <h4 :class="`text-sm font-semibold text-${themeClass.primary} mb-3`">🔄 队列操作</h4>
      <div class="space-y-2">
        <button
          @click="scanBackups"
          :disabled="pendingFiles.length === 0"
          :class="`w-full px-3 py-2 text-sm bg-blue-500 text-white rounded hover:opacity-80 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-1`"
        >
          <span>🔍</span>
          <span>扫描备份 ({{ pendingFiles.length }})</span>
        </button>
        <button
          @click="restoreFiles"
          :disabled="pendingFiles.length === 0"
          :class="`w-full px-3 py-2 text-sm bg-green-500 text-white rounded hover:opacity-80 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-1`"
        >
          <span>🔄</span>
          <span>恢复选中文件 ({{ pendingFiles.length }})</span>
        </button>
        <button
          @click="clearQueue"
          :disabled="fileQueue.length === 0"
          :class="`w-full px-3 py-2 text-sm bg-red-500 text-white rounded hover:opacity-80 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-1`"
        >
          <span>🗑️</span>
          <span>清空队列</span>
        </button>
      </div>
    </div>

    <!-- 管理操作区 -->
    <div :class="`p-4 bg-white rounded-lg shadow-sm border border-${themeClass.primary}/20`">
      <h4 :class="`text-sm font-semibold text-${themeClass.primary} mb-3`">⚙️ 管理操作</h4>
      <div class="space-y-2">
        <button
          @click="exportQueue"
          :disabled="fileQueue.length === 0"
          :class="`w-full px-3 py-2 text-sm bg-purple-500 text-white rounded hover:opacity-80 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-1`"
        >
          <span>📤</span>
          <span>导出队列</span>
        </button>
        <button
          @click="importQueue"
          :class="`w-full px-3 py-2 text-sm bg-indigo-500 text-white rounded hover:opacity-80 transition-opacity flex items-center justify-center space-x-1`"
        >
          <span>📥</span>
          <span>导入队列</span>
        </button>
        <button
          @click="retryFailed"
          :disabled="failedFiles.length === 0"
          :class="`w-full px-3 py-2 text-sm bg-orange-500 text-white rounded hover:opacity-80 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-1`"
        >
          <span>🔄</span>
          <span>重试失败 ({{ failedFiles.length }})</span>
        </button>
      </div>
    </div>

    <!-- 统计信息 -->
    <div :class="`p-4 bg-white rounded-lg shadow-sm border border-${themeClass.primary}/20`">
      <h4 :class="`text-sm font-semibold text-${themeClass.primary} mb-3`">📊 统计信息</h4>
      <div class="space-y-3">
        <!-- 总体统计 -->
        <div class="grid grid-cols-2 gap-2 text-sm">
          <div :class="`p-2 bg-${themeClass.secondary} rounded text-center`">
            <div :class="`text-lg font-bold text-${themeClass.primary}`">{{ fileQueue.length }}</div>
            <div class="text-gray-600">总文件数</div>
          </div>
          <div class="p-2 bg-gray-100 rounded text-center">
            <div class="text-lg font-bold text-gray-700">{{ processedFiles.length }}</div>
            <div class="text-gray-600">已处理</div>
          </div>
        </div>

        <!-- 状态分布 -->
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="flex items-center space-x-1">
              <span class="text-yellow-500">⏳</span>
              <span>待处理</span>
            </span>
            <span class="font-medium">{{ pendingFiles.length }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="flex items-center space-x-1">
              <span class="text-green-500">✅</span>
              <span>成功</span>
            </span>
            <span class="font-medium">{{ successFiles.length }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="flex items-center space-x-1">
              <span class="text-red-500">❌</span>
              <span>失败</span>
            </span>
            <span class="font-medium">{{ failedFiles.length }}</span>
          </div>
        </div>

        <!-- 成功率 -->
        <div v-if="processedFiles.length > 0" class="pt-2 border-t border-gray-200">
          <div class="flex items-center justify-between text-sm">
            <span>成功率</span>
            <span :class="`font-medium ${successRate >= 80 ? 'text-green-600' : successRate >= 50 ? 'text-yellow-600' : 'text-red-600'}`">
              {{ successRate.toFixed(1) }}%
            </span>
          </div>
          <div class="mt-1 bg-gray-200 rounded-full h-2">
            <div 
              :class="`h-2 rounded-full transition-all duration-300 ${successRate >= 80 ? 'bg-green-500' : successRate >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`"
              :style="{ width: successRate + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInput"
      type="file"
      multiple
      style="display: none"
      @change="onFileSelect"
    />
    <input
      ref="folderInput"
      type="file"
      webkitdirectory
      style="display: none"
      @change="onFolderSelect"
    />
    <input
      ref="importInput"
      type="file"
      accept=".json"
      style="display: none"
      @change="onImportSelect"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  api: {
    type: Object,
    required: true
  },
  fileQueue: {
    type: Array,
    required: true
  },
  themeClass: {
    type: Object,
    required: true
  }
})

// 引用
const fileInput = ref(null)
const folderInput = ref(null)
const importInput = ref(null)

// 计算属性
const pendingFiles = computed(() => 
  props.fileQueue.filter(f => f.status === 'pending')
)

const processedFiles = computed(() => 
  props.fileQueue.filter(f => f.status === 'completed' || f.status === 'error')
)

const successFiles = computed(() => 
  props.fileQueue.filter(f => f.status === 'completed')
)

const failedFiles = computed(() => 
  props.fileQueue.filter(f => f.status === 'error')
)

const successRate = computed(() => {
  if (processedFiles.value.length === 0) return 0
  return (successFiles.value.length / processedFiles.value.length) * 100
})

// 文件操作
const addFiles = () => {
  fileInput.value?.click()
}

const addFolder = () => {
  folderInput.value?.click()
}

const onFileSelect = (event) => {
  const files = Array.from(event.target.files)
  if (files.length > 0) {
    props.api.addFiles(files.map(f => f.webkitRelativePath || f.name))
  }
  event.target.value = '' // 清空输入
}

const onFolderSelect = (event) => {
  const files = Array.from(event.target.files)
  if (files.length > 0) {
    props.api.addFiles(files.map(f => f.webkitRelativePath))
  }
  event.target.value = '' // 清空输入
}

// 队列操作
const scanBackups = () => {
  props.api.scanBackups()
}

const restoreFiles = () => {
  props.api.restoreFiles()
}

const clearQueue = () => {
  if (confirm('确定要清空整个队列吗？此操作无法撤销。')) {
    props.api.clearQueue()
  }
}

// 管理操作
const exportQueue = async () => {
  try {
    const data = {
      timestamp: new Date().toISOString(),
      files: props.fileQueue.map(f => ({
        name: f.name,
        path: f.path,
        status: f.status,
        message: f.message
      }))
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `baku-queue-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    
    if (window.addLog) {
      window.addLog('队列已导出', 'success')
    }
  } catch (error) {
    if (window.addLog) {
      window.addLog(`导出失败: ${error.message}`, 'error')
    }
  }
}

const importQueue = () => {
  importInput.value?.click()
}

const onImportSelect = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  try {
    const text = await file.text()
    const data = JSON.parse(text)
    
    if (data.files && Array.isArray(data.files)) {
      props.api.addFiles(data.files.map(f => f.path))
      if (window.addLog) {
        window.addLog(`成功导入 ${data.files.length} 个文件`, 'success')
      }
    } else {
      throw new Error('无效的队列文件格式')
    }
  } catch (error) {
    if (window.addLog) {
      window.addLog(`导入失败: ${error.message}`, 'error')
    }
  }
  
  event.target.value = '' // 清空输入
}

const retryFailed = () => {
  const failedIds = failedFiles.value.map(f => f.id)
  if (failedIds.length > 0) {
    // 重置失败文件状态
    failedFiles.value.forEach(f => {
      f.status = 'pending'
      f.message = '准备重试'
    })
    
    // 重新尝试恢复
    props.api.restoreFiles(failedIds)
  }
}
</script>

<style scoped>
/* 进度条动画 */
.transition-all {
  transition: all 0.3s ease-in-out;
}

/* 按钮悬停效果 */
button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

button:active:not(:disabled) {
  transform: translateY(0);
}
</style>
