<template>
  <div v-if="visible" class="flex items-center space-x-3 my-4">
    <svg class="animate-spin h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
    </svg>
    <span class="text-blue-700 font-medium">正在处理文件，请稍候...</span>
  </div>
</template>
<script setup>
defineProps({ visible: Boolean })
</script>

<style scoped>
.progress-bar {
  text-align: center;
  margin: 16px 0;
}
.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4a90e2;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  animation: spin 1s linear infinite;
  display: inline-block;
  margin-right: 8px;
}
@keyframes spin {
  0% { transform: rotate(0deg);}
  100% { transform: rotate(360deg);}
}
</style> 