<template>
    <div style="margin-top:20px;">
      <el-switch
        v-model="autoMode"
        active-text="自动模式"
        inactive-text="手动模式"
        @change="$emit('toggle-auto', autoMode)"
      />
      <el-button-group style="margin-top:10px;">
        <el-button type="primary" @click="$emit('restore')">批量恢复</el-button>
        <el-button type="danger" @click="$emit('clear')">清空队列</el-button>
      </el-button-group>
    </div>
  </template>
  
  <script setup>
  import { ref, watch } from 'vue'
  const props = defineProps({ autoMode: Boolean })
  const autoMode = ref(props.autoMode)
  watch(() => props.autoMode, v => autoMode.value = v)
  </script>
  