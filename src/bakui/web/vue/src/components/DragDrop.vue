<template>
    <el-upload
      drag
      multiple
      :show-file-list="false"
      :auto-upload="false"
      :before-upload="beforeUpload"
      style="width:100%;"
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">将文件拖到此处，或 <em>点击上传</em></div>
    </el-upload>
  </template>
  
  <script setup>
  const emit = defineEmits(['files-dropped'])
  function beforeUpload(file) {
    emit('files-dropped', [file])
    return false // 阻止自动上传
  }
  </script>
  