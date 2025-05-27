<template>
  <div
    class="drag-drop-area"
    @dragover.prevent
    @drop.prevent="onDrop"
    style="border:2px dashed #aaa; padding:40px; text-align:center; margin-bottom:20px;"
  >
    <div>拖拽文件到此区域（桌面版可获取本地路径）</div>
  </div>
</template>

<script setup>
const emit = defineEmits(['dropped-paths'])

function onDrop(e) {
  const files = Array.from(e.dataTransfer.files)
  // pywebview 环境下，file.path 可用
  const paths = files.map(f => f.path || f.webkitRelativePath || f.name)
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.handle_drop(paths).then(result => {
      emit('dropped-paths', result)
    })
  } else {
    alert('请在桌面版（pywebview）环境下使用拖拽获取本地路径')
  }
}
</script>
  