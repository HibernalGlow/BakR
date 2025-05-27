<template>
    <el-table :data="fileList" style="width:100%;">
      <el-table-column prop="name" label="原文件" width="180"/>
      <el-table-column prop="backup" label="备份文件" width="180"/>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{row}">
          <el-tag :type="statusType(row.status)">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="msg" label="说明"/>
      <el-table-column label="操作" width="100">
        <template #default="{row}">
          <el-button size="small" @click="$emit('restore', row)">恢复</el-button>
        </template>
      </el-table-column>
    </el-table>
  </template>
  
  <script setup>
  const props = defineProps({ fileList: Array })
  function statusType(status) {
    if (status === 'completed') return 'success'
    if (status === 'error') return 'danger'
    if (status === 'processing') return 'info'
    return ''
  }
  </script>
  