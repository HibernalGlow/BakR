import webview  
  
def on_drop(event):  
    """处理文件拖拽事件"""  
    print("Drop event triggered!")  
    files = event['dataTransfer']['files']  
    for file in files:  
        print(f"文件名: {file['name']}")  
        if 'pywebviewFullPath' in file:  
            print(f"完整路径: {file['pywebviewFullPath']}")  
        else:  
            print("未找到完整路径信息")  
  
def setup_drag_drop():  
    """设置拖拽功能 - 在窗口加载完成后调用"""  
    # 等待窗口完全加载  
    window.events.loaded.wait()  
    print("窗口已加载，设置拖拽监听器...")  
      
    # 订阅document的drop事件  
    window.dom.document.events.drop += on_drop  
    print("拖拽监听器已设置")  
  
# 简化的HTML，确保拖拽区域正确  
html = """  
<!DOCTYPE html>  
<html>  
<head>  
    <title>文件拖拽Demo</title>  
    <style>  
        body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }  
        .drop-zone {  
            width: 400px;  
            height: 200px;  
            border: 2px dashed #ccc;  
            text-align: center;  
            line-height: 200px;  
            margin: 50px auto;  
            font-size: 18px;  
            background-color: #f9f9f9;  
        }  
        .drop-zone.dragover {  
            border-color: #007bff;  
            background-color: #e3f2fd;  
        }  
    </style>  
</head>  
<body>  
    <h1>文件拖拽测试</h1>  
    <div class="drop-zone" id="dropZone">  
        拖拽文件到这里  
    </div>  
      
    <script>  
        console.log('JavaScript loaded');  
          
        document.addEventListener('DOMContentLoaded', function() {  
            const dropZone = document.getElementById('dropZone');  
            console.log('Drop zone found:', dropZone);  
              
            dropZone.addEventListener('dragover', function(e) {  
                e.preventDefault();  
                dropZone.classList.add('dragover');  
                console.log('Drag over');  
            });  
              
            dropZone.addEventListener('dragleave', function() {  
                dropZone.classList.remove('dragover');  
                console.log('Drag leave');  
            });  
              
            dropZone.addEventListener('drop', function(e) {  
                e.preventDefault();  
                dropZone.classList.remove('dragover');  
                console.log('Drop event in JavaScript');  
            });  
        });  
    </script>  
</body>  
</html>  
"""  
  
if __name__ == '__main__':  
    # 创建窗口  
    window = webview.create_window(  
        'Windows文件拖拽Demo',  
        html=html,  
        width=600,  
        height=400  
    )  
      
    # 启动应用，传入回调函数  
    webview.start(setup_drag_drop, debug=True)