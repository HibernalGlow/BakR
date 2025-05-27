<template>
  <div class="rounded-xl shadow bg-white p-4 flex flex-col items-start mb-6">
    <label class="font-semibold mb-2 text-gray-700">主题色选择</label>
    <input type="color" v-model="mainColor" class="w-12 h-12 p-0 border-0 bg-transparent cursor-pointer" />
    <div class="flex items-center mt-2 space-x-4">
      <span class="text-sm text-gray-500">主色</span>
      <span :style="{background: mainColor}" class="w-6 h-6 rounded-full border"></span>
      <span class="text-sm text-gray-500">浅色</span>
      <span :style="{background: lightColor}" class="w-6 h-6 rounded-full border"></span>
      <span class="text-sm text-gray-500">深色</span>
      <span :style="{background: darkColor}" class="w-6 h-6 rounded-full border"></span>
    </div>
  </div>
</template>
<script setup>
import { ref, watch } from 'vue'
import chroma from 'chroma-js'
const mainColor = ref('#4a90e2')
const lightColor = ref('')
const darkColor = ref('')

function updateThemeVars() {
  lightColor.value = chroma(mainColor.value).brighten(1.5).hex()
  darkColor.value = chroma(mainColor.value).darken(1.5).hex()
  document.documentElement.style.setProperty('--theme-main', mainColor.value)
  document.documentElement.style.setProperty('--theme-light', lightColor.value)
  document.documentElement.style.setProperty('--theme-dark', darkColor.value)
}
watch(mainColor, updateThemeVars, {immediate: true})
</script> 