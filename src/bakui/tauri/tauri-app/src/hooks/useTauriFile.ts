import { open } from '@tauri-apps/api/dialog';
import { invoke } from '@tauri-apps/api/tauri';

export async function selectAndProcessFile() {
  const selected = await open({ multiple: false });
  if (selected && typeof selected === 'string') {
    // 这里 selected 是完整路径
    const result = await invoke<string>('process_file', { filePath: selected });
    return result;
  }
  return null;
}

// 拖拽监听示例，可在组件中使用
import { listen } from '@tauri-apps/api/event';

export function listenFileDrop(callback: (filePath: string) => void) {
  listen<string[]>('tauri://file-drop', async (event) => {
    const filePaths = event.payload;
    if (filePaths && filePaths.length > 0) {
      callback(filePaths[0]);
    }
  });
} 