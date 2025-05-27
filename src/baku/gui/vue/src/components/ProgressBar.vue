<template>
  <div v-if="visible" :class="`p-4 bg-white rounded-lg shadow-sm border border-${themeClass.primary}/20 mt-4`">
    <div class="flex items-center space-x-3">
      <!-- 旋转图标 -->
      <svg 
        :class="`animate-spin h-6 w-6 text-${themeClass.primary}`" 
        fill="none" 
        viewBox="0 0 24 24"
      >
        <circle 
          class="opacity-25" 
          cx="12" 
          cy="12" 
          r="10" 
          stroke="currentColor" 
          stroke-width="4"
        ></circle>
        <path 
          class="opacity-75" 
          fill="currentColor" 
          d="M4 12a8 8 0 018-8v8z"
        ></path>
      </svg>
      
      <!-- 进度信息 -->
      <div class="flex-1">
        <div :class="`text-${themeClass.primary} font-medium`">
          {{ message || '正在处理文件，请稍候...' }}
        </div>
        <div v-if="showProgress" class="mt-2">
          <div class="flex items-center justify-between text-sm text-gray-600 mb-1">
            <span>进度</span>
            <span>{{ progress }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div 
              :class="`bg-${themeClass.primary} h-2 rounded-full transition-all duration-300`"
              :style="{ width: progress + '%' }"
            ></div>
          </div>
        </div>
      </div>
      
      <!-- 取消按钮 -->
      <button
        v-if="showCancel"
        @click="$emit('cancel')"
        class="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
      >
        取消
      </button>
    </div>
    
    <!-- 详细信息 -->
    <div v-if="details" class="mt-3 text-sm text-gray-600 border-t border-gray-200 pt-2">
      {{ details }}
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  themeClass: {
    type: Object,
    required: true
  },
  message: {
    type: String,
    default: ''
  },
  progress: {
    type: Number,
    default: 0
  },
  showProgress: {
    type: Boolean,
    default: false
  },
  showCancel: {
    type: Boolean,
    default: false
  },
  details: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['cancel'])
</script>

<style scoped>
/* 旋转动画 */
@keyframes spin {
  0% { 
    transform: rotate(0deg);
  }
  100% { 
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* 进度条动画 */
.transition-all {
  transition: all 0.3s ease-in-out;
}

/* 脉冲效果 */
.pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
