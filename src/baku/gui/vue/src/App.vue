<script setup>
import { ref, onMounted, computed } from 'vue'
import ThemePanel from './components/ThemePanel.vue'
import QueuePanel from './components/QueuePanel.vue'
import LogPanel from './components/LogPanel.vue'
import ActionPanel from './components/ActionPanel.vue'
import DragDropZone from './components/DragDropZone.vue'
import ProgressBar from './components/ProgressBar.vue'

// 应用状态
const autoMode = ref(true)
const currentTheme = ref('blue') // 主题色
const progressVisible = ref(false)
const fileQueue = ref([])
const logs = ref([])

// 主题色配置
const themes = {
  blue: {
    primary: 'blue-600',
    secondary: 'blue-100',
    accent: 'blue-500',
    bg: 'gray-50'
  },
  green: {
    primary: 'green-600', 
    secondary: 'green-100',
    accent: 'green-500',
    bg: 'gray-50'
  },
  purple: {
    primary: 'purple-600',
    secondary: 'purple-100', 
    accent: 'purple-500',
    bg: 'gray-50'
  },
  dark: {
    primary: 'gray-800',
    secondary: 'gray-700',
    accent: 'gray-600',
    bg: 'gray-900'
  },
  custom: {
    primary: 'blue-600', // 将被自定义颜色覆盖
    secondary: 'blue-100',
    accent: 'blue-500', 
    bg: 'gray-50'
  }
}

// 计算当前主题样式
const theme = computed(() => themes[currentTheme.value])

// 统计信息
const stats = computed(() => {
  const total = fileQueue.value.length
  const pending = fileQueue.value.filter(f => f.status === 'pending').length
  const success = fileQueue.value.filter(f => f.status === 'completed').length
  const error = fileQueue.value.filter(f => f.status === 'error').length
  return { total, pending, success, error }
})

// API 接口
const api = {
  addFiles: (files) => {
    files.forEach(file => {
      const fileItem = {
        id: Date.now() + Math.random(),
        name: file.name || file.split('\\').pop().split('/').pop(),
        path: file.path || file,
        status: 'pending',
        message: '已添加到队列',
        timestamp: new Date().toLocaleTimeString()
      }
      fileQueue.value.push(fileItem)
      addLog(`添加文件: ${fileItem.name}`, 'info')
    })
  },
  
  removeFiles: (fileIds) => {
    fileQueue.value = fileQueue.value.filter(f => !fileIds.includes(f.id))
    addLog(`移除了 ${fileIds.length} 个文件`, 'info')
  },
  
  clearQueue: () => {
    fileQueue.value = []
    addLog('队列已清空', 'info')
  },
  
  scanBackups: async (fileIds = null) => {
    const targetFiles = fileIds ? 
      fileQueue.value.filter(f => fileIds.includes(f.id)) : 
      fileQueue.value.filter(f => f.status === 'pending')
    
    if (targetFiles.length === 0) {
      addLog('没有需要扫描的文件', 'warning')
      return
    }
    
    progressVisible.value = true
    addLog(`开始扫描 ${targetFiles.length} 个文件的备份...`, 'info')
    
    try {
      // 调用 Python 后端 API
      const response = await window.pywebview.api.scan_backups(targetFiles.map(f => f.path))
      
      // 更新队列状态
      targetFiles.forEach((file, index) => {
        const result = response[index]
        if (result.backup_found) {
          file.message = `找到备份: ${result.backup_path}`
          addLog(`✓ ${file.name} 找到备份`, 'success')
        } else {
          file.message = '未找到备份文件'
          addLog(`⚠ ${file.name} 未找到备份`, 'warning')
        }
      })
      
      addLog(`扫描完成！找到 ${response.filter(r => r.backup_found).length}/${targetFiles.length} 个备份`, 'success')
    } catch (error) {
      addLog(`扫描失败: ${error.message}`, 'error')
    } finally {
      progressVisible.value = false
    }
  },
  
  restoreFiles: async (fileIds = null) => {
    const targetFiles = fileIds ? 
      fileQueue.value.filter(f => fileIds.includes(f.id)) : 
      fileQueue.value.filter(f => f.status === 'pending')
    
    if (targetFiles.length === 0) {
      addLog('没有需要恢复的文件', 'warning')
      return
    }
    
    progressVisible.value = true
    addLog(`开始恢复 ${targetFiles.length} 个文件...`, 'info')
    
    try {
      // 调用 Python 后端 API
      const response = await window.pywebview.api.restore_files(targetFiles.map(f => f.path))
      
      // 更新队列状态
      let successCount = 0
      targetFiles.forEach((file, index) => {
        const result = response[index]
        file.status = result.success ? 'completed' : 'error'
        file.message = result.message
        
        if (result.success) {
          successCount++
          addLog(`✓ ${file.name} 恢复成功`, 'success')
        } else {
          addLog(`✗ ${file.name} 恢复失败: ${result.message}`, 'error')
        }
      })
      
      addLog(`恢复完成！成功: ${successCount}/${targetFiles.length}`, 'success')
    } catch (error) {
      addLog(`恢复失败: ${error.message}`, 'error')
    } finally {
      progressVisible.value = false
    }
  }
}

// 日志功能
const addLog = (message, type = 'info') => {
  const timestamp = new Date().toLocaleTimeString()
  logs.value.push({
    id: Date.now() + Math.random(),
    timestamp,
    message,
    type
  })
  
  // 限制日志数量
  if (logs.value.length > 1000) {
    logs.value = logs.value.slice(-500)
  }
}

// 拖拽处理
const handleDrop = async (files) => {
  api.addFiles(files)
  
  if (autoMode.value) {
    // 自动模式：直接恢复
    await api.restoreFiles()
  }
}

// 主题切换
const changeTheme = (themeName) => {
  currentTheme.value = themeName
  
  // 如果是自定义主题，应用自定义颜色
  if (themeName === 'custom') {
    // 这里可以从 ThemePanel 组件获取自定义颜色
    // 或者从 localStorage 读取保存的自定义颜色
    const customColor = localStorage.getItem('baku-custom-color') || '#4a90e2'
    applyCustomTheme(customColor)
  }
  
  addLog(`主题已切换为: ${themeName}`, 'info')
}

// 应用自定义主题
const applyCustomTheme = (color) => {
  try {
    // 使用 chroma.js 生成颜色变体（如果可用）
    if (window.chroma) {
      const light = window.chroma(color).brighten(1.5).hex()
      const dark = window.chroma(color).darken(1.5).hex()
      
      // 更新主题配置
      themes.custom = {
        primary: 'custom-600',
        secondary: 'custom-100', 
        accent: 'custom-500',
        bg: 'gray-50'
      }
      
      // 设置 CSS 变量
      document.documentElement.style.setProperty('--color-custom-600', color)
      document.documentElement.style.setProperty('--color-custom-500', color)
      document.documentElement.style.setProperty('--color-custom-100', light)
      
      // 保存到本地存储
      localStorage.setItem('baku-custom-color', color)
    }
  } catch (error) {
    console.warn('应用自定义主题失败:', error)
  }
}

// 挂载时设置全局 API
onMounted(() => {
  // 暴露给 Python 的接口
  window.showProcessing = () => { progressVisible.value = true }
  window.hideProcessing = () => { progressVisible.value = false }
  window.addLog = addLog
  window.clearLogs = () => { logs.value = [] }
  
  addLog('BakU Vue 界面启动成功', 'success')
})
</script>

<template>
  <div :class="`min-h-screen bg-${theme.bg} transition-colors duration-200`">
    <!-- 标题栏 -->
    <header :class="`bg-white shadow-sm border-b border-${theme.primary}/20 px-6 py-4`">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <h1 :class="`text-2xl font-bold text-${theme.primary}`">
            🎯 BakU - 智能备份文件恢复工具
          </h1>
          <div class="flex items-center space-x-2">
            <span class="text-sm text-gray-500">模式:</span>
            <label class="flex items-center cursor-pointer">
              <input 
                v-model="autoMode" 
                type="checkbox" 
                :class="`toggle toggle-${theme.primary.split('-')[0]} toggle-sm`"
              />
              <span class="ml-2 text-sm font-medium">
                {{ autoMode ? '自动模式（拖拽即恢复）' : '手动模式' }}
              </span>
            </label>
          </div>
        </div>
        
        <!-- 统计信息 -->
        <div class="flex items-center space-x-4 text-sm">
          <span :class="`px-2 py-1 rounded bg-${theme.secondary} text-${theme.primary}`">
            总计: {{ stats.total }}
          </span>
          <span class="px-2 py-1 rounded bg-yellow-100 text-yellow-700" v-if="stats.pending > 0">
            待处理: {{ stats.pending }}
          </span>
          <span class="px-2 py-1 rounded bg-green-100 text-green-700" v-if="stats.success > 0">
            成功: {{ stats.success }}
          </span>
          <span class="px-2 py-1 rounded bg-red-100 text-red-700" v-if="stats.error > 0">
            失败: {{ stats.error }}
          </span>
        </div>
      </div>
    </header>

    <div class="flex h-screen pt-0">
      <!-- 左侧面板 -->
      <div class="w-1/3 bg-white shadow-sm border-r border-gray-200 flex flex-col">
        <!-- 主题面板 -->
        <ThemePanel 
          :current-theme="currentTheme"
          :themes="Object.keys(themes)"
          @change-theme="changeTheme"
          :theme-class="theme"
        />
        
        <!-- 拖拽区域 -->
        <DragDropZone 
          :auto-mode="autoMode"
          :theme-class="theme"
          @files-dropped="handleDrop"
        />
        
        <!-- 操作面板 -->
        <ActionPanel 
          :api="api"
          :file-queue="fileQueue"
          :theme-class="theme"
        />
        
        <!-- 进度条 -->
        <ProgressBar 
          :visible="progressVisible"
          :theme-class="theme"
        />
      </div>

      <!-- 右侧面板 -->
      <div class="flex-1 flex flex-col">
        <!-- 文件队列 -->
        <div class="flex-1 bg-white">
          <QueuePanel 
            :file-queue="fileQueue"
            :api="api"
            :theme-class="theme"
          />
        </div>
        
        <!-- 日志面板 -->
        <div class="h-80 bg-gray-50 border-t border-gray-200">
          <LogPanel 
            :logs="logs"
            :theme-class="theme"
            @clear-logs="logs = []"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style>
/* 全局样式 */
.toggle {
  @apply relative inline-block w-10 h-6 bg-gray-300 rounded-full cursor-pointer transition-colors duration-200;
}

.toggle:checked {
  @apply bg-blue-500;
}

.toggle::after {
  @apply absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform duration-200;
  content: '';
}

.toggle:checked::after {
  @apply transform translate-x-4;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  @apply bg-gray-100;
}

::-webkit-scrollbar-thumb {
  @apply bg-gray-300 rounded-full;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400;
}
</style>
