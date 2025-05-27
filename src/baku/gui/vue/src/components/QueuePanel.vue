<template>
  <div class="h-full flex flex-col">
    <!-- 队列标题栏 -->
    <div :class="`flex items-center justify-between p-4 bg-${themeClass.secondary} border-b border-${themeClass.primary}/20`">
      <h3 :class="`text-lg font-semibold text-${themeClass.primary}`">
        📁 文件队列 ({{ fileQueue.length }})
      </h3>
      <div class="flex items-center space-x-2">
        <button
          @click="selectAll"
          :class="`px-3 py-1 text-sm bg-${themeClass.primary} text-white rounded hover:opacity-80 transition-opacity`"
        >
          全选
        </button>
        <button
          @click="clearSelection"
          :class="`px-3 py-1 text-sm bg-gray-500 text-white rounded hover:opacity-80 transition-opacity`"
        >
          取消选择
        </button>
        <button
          @click="removeSelected"
          :class="`px-3 py-1 text-sm bg-red-500 text-white rounded hover:opacity-80 transition-opacity`"
          :disabled="selectedFiles.length === 0"
        >
          移除选中 ({{ selectedFiles.length }})
        </button>
      </div>
    </div>

    <!-- 文件列表 -->
    <div class="flex-1 overflow-auto">
      <div v-if="fileQueue.length === 0" class="flex items-center justify-center h-full text-gray-500">
        <div class="text-center">
          <div class="text-6xl mb-4">📂</div>
          <div class="text-lg">队列为空</div>
          <div class="text-sm">拖拽文件到左侧区域开始使用</div>
        </div>
      </div>

      <div v-else class="divide-y divide-gray-200">
        <div
          v-for="file in fileQueue"
          :key="file.id"
          :class="`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
            selectedFiles.includes(file.id) ? `bg-${themeClass.secondary}` : ''
          }`"
          @click="toggleSelection(file.id)"
          @contextmenu.prevent="showContextMenu($event, file)"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3 flex-1 min-w-0">
              <!-- 选择框 -->
              <input
                type="checkbox"
                :checked="selectedFiles.includes(file.id)"
                @click.stop="toggleSelection(file.id)"
                :class="`h-4 w-4 text-${themeClass.primary} border-gray-300 rounded focus:ring-${themeClass.primary}`"
              />
              
              <!-- 状态图标 -->
              <div class="flex-shrink-0">
                <span v-if="file.status === 'pending'" class="text-yellow-500">⏳</span>
                <span v-else-if="file.status === 'completed'" class="text-green-500">✅</span>
                <span v-else-if="file.status === 'error'" class="text-red-500">❌</span>
                <span v-else class="text-gray-400">📄</span>
              </div>
              
              <!-- 文件信息 -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center space-x-2">
                  <span class="font-medium text-gray-900 truncate">{{ file.name }}</span>
                  <span v-if="file.status" :class="`px-2 py-1 text-xs rounded-full ${getStatusClass(file.status)}`">
                    {{ getStatusText(file.status) }}
                  </span>
                </div>
                <div class="text-sm text-gray-500 truncate">{{ file.path }}</div>
                <div v-if="file.message" class="text-xs text-gray-400 mt-1">
                  {{ file.message }}
                </div>
              </div>
            </div>
            
            <!-- 时间戳 -->
            <div v-if="file.timestamp" class="text-xs text-gray-400 ml-4">
              {{ file.timestamp }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右键菜单 -->
    <div
      v-if="contextMenu.visible"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      class="fixed z-50 bg-white border border-gray-200 rounded-lg shadow-lg py-2 min-w-48"
      @click.stop
    >
      <button
        @click="scanSelectedFile"
        class="w-full px-4 py-2 text-left hover:bg-gray-100 transition-colors"
      >
        🔍 扫描备份
      </button>
      <button
        @click="restoreSelectedFile"
        class="w-full px-4 py-2 text-left hover:bg-gray-100 transition-colors"
      >
        🔄 恢复文件
      </button>
      <hr class="my-1 border-gray-200" />
      <button
        @click="removeSelectedFile"
        class="w-full px-4 py-2 text-left hover:bg-red-50 text-red-600 transition-colors"
      >
        🗑️ 移除文件
      </button>
    </div>

    <!-- 点击其他地方关闭菜单 -->
    <div
      v-if="contextMenu.visible"
      @click="hideContextMenu"
      class="fixed inset-0 z-40"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  fileQueue: {
    type: Array,
    required: true
  },
  api: {
    type: Object,
    required: true
  },
  themeClass: {
    type: Object,
    required: true
  }
})

// 选中的文件
const selectedFiles = ref([])

// 右键菜单
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  file: null
})

// 选择操作
const selectAll = () => {
  selectedFiles.value = props.fileQueue.map(f => f.id)
}

const clearSelection = () => {
  selectedFiles.value = []
}

const toggleSelection = (fileId) => {
  const index = selectedFiles.value.indexOf(fileId)
  if (index > -1) {
    selectedFiles.value.splice(index, 1)
  } else {
    selectedFiles.value.push(fileId)
  }
}

// 批量操作
const removeSelected = () => {
  if (selectedFiles.value.length > 0) {
    props.api.removeFiles([...selectedFiles.value])
    selectedFiles.value = []
  }
}

// 右键菜单
const showContextMenu = (event, file) => {
  contextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    file: file
  }
}

const hideContextMenu = () => {
  contextMenu.value.visible = false
}

const scanSelectedFile = () => {
  if (contextMenu.value.file) {
    props.api.scanBackups([contextMenu.value.file.id])
  }
  hideContextMenu()
}

const restoreSelectedFile = () => {
  if (contextMenu.value.file) {
    props.api.restoreFiles([contextMenu.value.file.id])
  }
  hideContextMenu()
}

const removeSelectedFile = () => {
  if (contextMenu.value.file) {
    props.api.removeFiles([contextMenu.value.file.id])
  }
  hideContextMenu()
}

// 状态样式
const getStatusClass = (status) => {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'completed':
      return 'bg-green-100 text-green-800'
    case 'error':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'pending':
      return '待处理'
    case 'completed':
      return '已完成'
    case 'error':
      return '失败'
    default:
      return '未知'
  }
}
</script>

<style scoped>
/* 自定义滚动条 */
.overflow-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.overflow-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
