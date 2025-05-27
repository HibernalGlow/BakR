<template>
    <el-container style="height:100vh;">
      <el-header style="font-size:22px;font-weight:bold;">BakU 智能备份恢复工具</el-header>
      <el-main>
        <el-row :gutter="20">
          <el-col :span="8">
            <DragDrop @files-dropped="onFilesDropped" />
            <ControlPanel
              :auto-mode="autoMode"
              @toggle-auto="toggleAuto"
              @restore="onRestore"
              @clear="onClear"
            />
          </el-col>
          <el-col :span="16">
            <FileTable :fileList="fileList" @restore="onRestoreSingle"/>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import axios from 'axios'
  import DragDrop from './components/DragDrop.vue'
  import FileTable from './components/FileTable.vue'
  import ControlPanel from './components/ControlPanel.vue'
  
  const fileList = ref([])
  const autoMode = ref(true)
  
  async function refreshStatus() {
    const { data } = await axios.get('/api/status')
    fileList.value = data.queue
  }
  
  async function onFilesDropped(files) {
    const form = new FormData()
    files.forEach(f => form.append('files', f.raw || f))
    await axios.post('/api/upload', form)
    await refreshStatus()
  }
  
  async function onRestore() {
    await axios.post('/api/restore', { file_ids: fileList.value.map(f => f.id) })
    await refreshStatus()
  }
  
  async function onRestoreSingle(row) {
    await axios.post('/api/restore', { file_ids: [row.id] })
    await refreshStatus()
  }
  
  async function onClear() {
    await axios.post('/api/clear')
    await refreshStatus()
  }
  
  async function toggleAuto(val) {
    await axios.post('/api/auto_mode', { on: val })
  }
  
  refreshStatus()
  </script>
  