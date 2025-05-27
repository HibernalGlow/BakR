<template>
  <ul id="result-list">
    <li v-for="item in results" :key="item.file"
        :class="{
          success: item.status === 'success',
          error: item.status === 'error'
        }">
      {{ item.file }}：{{ item.status }}
    </li>
  </ul>
</template>
<script setup>
defineProps({ results: Array })
</script>
<style scoped>
#result-list { list-style: none; padding: 0; margin: 0; }
#result-list li {
  background: #f7fafd;
  margin: 8px 0;
  padding: 10px 16px;
  border-radius: 6px;
  color: #333;
  font-size: 16px;
}
#result-list li.success { color: #388e3c; }
#result-list li.error { color: #d32f2f; }
</style> 