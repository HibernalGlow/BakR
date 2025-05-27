import './style.css'
import { createApp } from 'vue'
import App from './App.vue'

// 创建 Vue 应用
const app = createApp(App)

// 挂载应用
app.mount('#app')

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue Error:', err)
  console.error('Component:', vm)
  console.error('Info:', info)
}
