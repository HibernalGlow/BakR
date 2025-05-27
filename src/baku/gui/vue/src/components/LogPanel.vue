<template>
  <div class="h-full flex flex-col">
    <!-- 日志标题栏 -->
    <div :class="`flex items-center justify-between p-3 bg-${themeClass.secondary} border-b border-${themeClass.primary}/20`">
      <h3 :class="`text-lg font-semibold text-${themeClass.primary} flex items-center space-x-2`">
        <span>📋</span>
        <span>操作日志</span>
        <span v-if="logs.length > 0" class="text-sm bg-gray-200 text-gray-700 px-2 py-1 rounded-full">
          {{ logs.length }}
        </span>
      </h3>
      <div class="flex items-center space-x-2">
        <button
          @click="scrollToBottom"
          :class="`px-3 py-1 text-sm bg-${themeClass.primary} text-white rounded hover:opacity-80 transition-opacity`"
          title="滚动到底部"
        >
          ⬇️
        </button>
        <button
          @click="$emit('clearLogs')"
          :class="`px-3 py-1 text-sm bg-red-500 text-white rounded hover:opacity-80 transition-opacity`"
          title="清空日志"
        >
          🗑️
        </button>
      </div>
    </div>

    <!-- 日志内容 -->
    <div 
      ref="logContainer"
      class="flex-1 overflow-auto bg-gray-900 text-green-400 p-3 font-mono text-sm"
      @scroll="onScroll"
    >
      <div v-if="logs.length === 0" class="text-center text-gray-500 mt-8">
        <div class="text-4xl mb-2">📝</div>
        <div>暂无日志</div>
      </div>
      
      <div v-for="log in logs" :key="log.id" :class="`log-entry ${getLogClass(log.type)}`">
        <span class="timestamp">{{ log.timestamp }}</span>
        <span class="log-type">{{ getLogTypeSymbol(log.type) }}</span>
        <span class="message">{{ log.message }}</span>
      </div>
      
      <!-- 自动滚动指示器 -->
      <div v-if="!isAtBottom" class="fixed bottom-4 right-4 z-10">
        <button
          @click="scrollToBottom"
          class="bg-blue-500 text-white px-3 py-2 rounded-full shadow-lg hover:bg-blue-600 transition-colors"
          title="有新日志，点击滚动到底部"
        >
          ⬇️ 新消息
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  logs: {
    type: Array,
    required: true
  },
  themeClass: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['clearLogs'])

const logContainer = ref(null)
const isAtBottom = ref(true)

// 日志类型样式映射
const getLogClass = (type) => {
  switch (type) {
    case 'success':
      return 'text-green-400'
    case 'error':
      return 'text-red-400'
    case 'warning':
      return 'text-yellow-400'
    case 'info':
      return 'text-blue-400'
    default:
      return 'text-gray-400'
  }
}

// 日志类型图标
const getLogTypeSymbol = (type) => {
  switch (type) {
    case 'success':
      return '✅'
    case 'error':
      return '❌'
    case 'warning':
      return '⚠️'
    case 'info':
      return 'ℹ️'
    default:
      return '📝'
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
    isAtBottom.value = true
  }
}

// 监听滚动事件
const onScroll = () => {
  if (logContainer.value) {
    const { scrollTop, scrollHeight, clientHeight } = logContainer.value
    isAtBottom.value = scrollTop + clientHeight >= scrollHeight - 10
  }
}

// 当日志更新时自动滚动到底部（如果用户已经在底部）
watch(() => props.logs.length, () => {
  if (isAtBottom.value) {
    nextTick(() => {
      scrollToBottom()
    })
  }
}, { immediate: true })

// 组件挂载时滚动到底部
onMounted(() => {
  nextTick(() => {
    scrollToBottom()
  })
})
</script>

<style scoped>
.log-entry {
  display: flex;
  align-items: flex-start;
  margin-bottom: 0.5rem;
  padding: 0.25rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.timestamp {
  color: #6b7280;
  font-size: 0.75rem;
  margin-right: 0.5rem;
  min-width: 70px;
  flex-shrink: 0;
}

.log-type {
  margin-right: 0.5rem;
  flex-shrink: 0;
}

.message {
  flex: 1;
  word-break: break-word;
}

/* 滚动条样式 */
.overflow-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-auto::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.overflow-auto::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.overflow-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* 动画效果 */
.log-entry {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 