<template>
  <div :class="`p-4 bg-white rounded-lg shadow-sm border border-${themeClass.primary}/20 mb-4`">
    <h4 :class="`text-sm font-semibold text-${themeClass.primary} mb-3`">🎨 主题选择</h4>
    
    <!-- 快速主题切换 -->
    <div class="grid grid-cols-2 gap-2 mb-4">
      <button
        v-for="theme in themes"
        :key="theme"
        @click="$emit('changeTheme', theme)"
        :class="`p-2 rounded text-sm font-medium transition-all ${
          currentTheme === theme 
            ? `bg-${themeClass.primary} text-white` 
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }`"
      >
        {{ getThemeDisplayName(theme) }}
      </button>
    </div>
    
    <!-- 自定义颜色选择器 -->
    <div class="border-t border-gray-200 pt-3">
      <label :class="`text-sm font-medium text-${themeClass.primary} mb-2 block`">自定义主题色</label>
      <div class="flex items-center space-x-3">
        <input 
          type="color" 
          v-model="customColor" 
          class="w-10 h-10 border-0 bg-transparent cursor-pointer rounded"
          @change="updateCustomTheme"
        />
        <div class="flex-1 min-w-0">
          <div class="text-xs text-gray-500">主色调</div>
          <div class="text-sm font-mono">{{ customColor }}</div>
        </div>
      </div>
      
      <!-- 色彩预览 -->
      <div class="mt-3 flex items-center space-x-2">
        <div class="flex-1 grid grid-cols-3 gap-1">
          <div :style="{backgroundColor: lightColor}" class="h-6 rounded border" title="浅色"></div>
          <div :style="{backgroundColor: customColor}" class="h-6 rounded border" title="主色"></div>
          <div :style="{backgroundColor: darkColor}" class="h-6 rounded border" title="深色"></div>
        </div>
        <button
          @click="applyCustomTheme"
          class="px-3 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          应用
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import chroma from 'chroma-js'

const props = defineProps({
  currentTheme: {
    type: String,
    required: true
  },
  themes: {
    type: Array,
    required: true
  },
  themeClass: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['changeTheme'])

// 自定义颜色
const customColor = ref('#4a90e2')

// 计算衍生颜色
const lightColor = computed(() => {
  try {
    return chroma(customColor.value).brighten(1.5).hex()
  } catch {
    return '#e3f2fd'
  }
})

const darkColor = computed(() => {
  try {
    return chroma(customColor.value).darken(1.5).hex()
  } catch {
    return '#1565c0'
  }
})

// 主题显示名称
const getThemeDisplayName = (theme) => {
  const names = {
    blue: '🔵 蓝色',
    green: '🟢 绿色', 
    purple: '🟣 紫色',
    dark: '⚫ 深色'
  }
  return names[theme] || theme
}

// 更新自定义主题
const updateCustomTheme = () => {
  // 实时更新 CSS 变量用于预览
  document.documentElement.style.setProperty('--custom-main', customColor.value)
  document.documentElement.style.setProperty('--custom-light', lightColor.value)
  document.documentElement.style.setProperty('--custom-dark', darkColor.value)
}

// 应用自定义主题
const applyCustomTheme = () => {
  emit('changeTheme', 'custom')
  if (window.addLog) {
    window.addLog(`应用自定义主题: ${customColor.value}`, 'info')
  }
}

// 监听颜色变化
watch(customColor, updateCustomTheme, { immediate: true })
</script>

<style scoped>
/* 自定义颜色选择器样式 */
input[type="color"] {
  border: 2px solid #e5e7eb;
  border-radius: 0.375rem;
}

input[type="color"]::-webkit-color-swatch-wrapper {
  padding: 0;
}

input[type="color"]::-webkit-color-swatch {
  border: none;
  border-radius: 0.25rem;
}
</style>