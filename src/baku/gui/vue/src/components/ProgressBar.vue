<template>
  <div v-if="visible" class="progress-bar">
    <span class="loader"></span> 正在处理文件，请稍候...
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