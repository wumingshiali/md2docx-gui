import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import pyperclip
import requests
import platform
from flask import *
import winreg  # 确保这个导入存在
import asyncio
import threading  # 添加缺失的threading模块导入


# PySide6 相关导入
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                             QTextEdit, QLabel, QFileDialog, QMessageBox,
                             QHBoxLayout, QVBoxLayout, QWidget, QProgressBar,
                             QFrame, QSizePolicy)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown 转 Word")
        self.resize(700, 400)
        self.setStyleSheet(self.get_stylesheet())
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题区域
        title_label = QLabel("Markdown 转 Word 文档转换器")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFixedHeight(40)
        
        # 文件选择区域
        file_frame = QFrame()
        file_frame.setObjectName("fileFrame")
        file_layout = QHBoxLayout()
        file_layout.setSpacing(10)
        
        self.file_path = QLabel("请选择要转换的Markdown文件")
        self.file_path.setObjectName("filePathLabel")
        self.file_path.setWordWrap(True)
        self.file_path.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        
        select_btn = QPushButton("浏览...")
        select_btn.setObjectName("selectButton")
        select_btn.setFixedWidth(100)
        select_btn.clicked.connect(self.select_file)
        
        file_layout.addWidget(self.file_path, 3)
        file_layout.addWidget(select_btn, 1)
        file_frame.setLayout(file_layout)
        
        # 转换按钮
        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.setObjectName("convertButton")
        self.convert_btn.setFixedWidth(150)
        self.convert_btn.setFixedHeight(40)
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setEnabled(False)
        
        # 进度条容器
        progress_container = QFrame()
        progress_container.setObjectName("progressContainer")
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress_label = QLabel("准备就绪")
        self.progress_label.setObjectName("progressLabel")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.progress = QProgressBar()
        self.progress.setObjectName("progressBar")
        self.progress.setFixedHeight(25)
        self.progress.setVisible(False)
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress)
        progress_container.setLayout(progress_layout)
        
        # 状态信息区域
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        self.status_label = QLabel("等待用户操作...")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFixedHeight(30)
        
        status_frame.setLayout(status_layout)
        status_layout.addWidget(self.status_label)
        
        # 添加到主布局
        main_layout.addWidget(title_label)
        main_layout.addWidget(file_frame)
        main_layout.addWidget(self.convert_btn, 0, Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(progress_container)
        main_layout.addWidget(status_frame)
        
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def get_stylesheet(self):
        return """
            QMainWindow {
                background-color: #f0f2f5;
            }
            #titleLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1a73e8;
                margin-bottom: 15px;
            }
            #fileFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
            #filePathLabel {
                font-size: 14px;
                color: #333;
            }
            #selectButton {
                background-color: #1a73e8;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px 12px;
            }
            #selectButton:hover {
                background-color: #155ea0;
            }
            #convertButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2e7d32, stop:1 #66bb6a);
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            #convertButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1b5e20, stop:1 #388e3c);
            }
            #progressContainer {
                margin-top: 20px;
            }
            #progressLabel {
                font-size: 14px;
                color: #5f6368;
                margin-bottom: 8px;
            }
            #progressBar {
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                background-color: #f8f9fa;
            }
            #progressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a73e8, stop:1 #4285f4);
                border-radius: 10px;
            }
            #statusFrame {
                margin-top: 15px;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #e8e8e8;
            }
            #statusLabel {
                font-size: 14px;
                color: #5f6368;
            }
        """
    
    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择Markdown文件", "", "Markdown文件 (*.md *.txt)"
        )
        if path:
            self.file_path.setText(path)
            self.convert_btn.setEnabled(True)
    
    def start_conversion(self):
        input_path = self.file_path.text()
        if not os.path.exists(input_path):
            self.show_message("错误", "文件不存在", QMessageBox.Icon.Critical)
            return
        
        # 显示进度条
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.progress_label.setText("转换中... 0%")
        self.convert_btn.setEnabled(False)
        self.update_status("正在转换文件，请稍候...")
        
        # 创建工作线程执行转换
        self.worker = ConversionWorker(input_path)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.conversion_complete)
        self.worker.error.connect(self.conversion_error)
        self.worker.start()
    
    def update_progress(self, value):
        self.progress.setValue(value)
        self.progress_label.setText(f"转换中... {value}%")
    
    def conversion_complete(self, output_path):
        self.progress.setValue(100)
        self.progress_label.setText("转换完成！")
        self.update_status("转换已完成，文件已保存")
        
        # 显示完成消息
        self.show_message("完成", "转换已完成！", QMessageBox.Icon.Information)
        
        # 尝试打开生成的文件
        try:
            if platform.system() == 'Windows':
                os.startfile(output_path)
            elif platform.system() == 'Darwin':
                subprocess.Popen(['open', output_path])
            else:
                subprocess.Popen(['xdg-open', output_path])
        except Exception as e:
            self.show_message("警告", f"无法自动打开文件: {str(e)}", QMessageBox.Icon.Warning)
        
        self.convert_btn.setEnabled(True)
    
    def conversion_error(self, error_msg):
        self.progress.setVisible(False)
        self.progress_label.setText("转换失败")
        self.update_status(f"转换失败: {error_msg}")
        self.show_message("错误", f"转换失败: {error_msg}", QMessageBox.Icon.Critical)
        self.convert_btn.setEnabled(True)
    
    def update_status(self, message):
        self.status_label.setText(message)
    
    def show_message(self, title, message, icon=QMessageBox.Icon.Information):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

# 文件转换工作线程
class ConversionWorker(QThread):
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, input_path):
        super().__init__()
        self.input_path = input_path
    
    def run(self):
        try:
            # 模拟转换过程
            self.progress.emit(20)
            
            # 构建输出路径
            filename = os.path.splitext(os.path.basename(self.input_path))[0]
            output_path = build_output_path(None, self.input_path, None)
            self.progress.emit(50)
            
            # 调用转换接口（示例）
            response = requests.post(
                'http://127.0.0.1:2403/convert',
                json={
                    'input_path': self.input_path,
                    'output_path': output_path
                }
            )
            
            if response.status_code == 200:
                self.progress.emit(100)
                self.finished.emit(output_path)
            else:
                self.error.emit("API返回错误")
        except Exception as e:
            self.error.emit(str(e))

# 添加项目根目录到 Python 路径
# sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 导入转换器
from src.converter import BaseConverter

# 创建异步Flask应用
app = Flask(__name__)
# 启用异步支持（需要Flask 2.0+）
if hasattr(app, 'run_task'):
    app.run = lambda **kwargs: app.run_task(**kwargs)

# 全局变量声明
md_url = None  # 直接初始化为None
con = None
# 修复bug：初始化path_和pathf_，避免未定义异常
path_ = None
pathf_ = None

# 检查自启动功能
def check_autostart():
    system = platform.system()
    if system == "Windows":
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "MarkdownToWord")
            winreg.CloseKey(key)
            return value == f'"{sys.argv[0]}"'
        except WindowsError:
            return False
    elif system == "Darwin":  # macOS
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.markdowntoword.plist")
        if os.path.exists(plist_path):
            with open(plist_path, 'r') as f:
                content = f.read()
                return f'"{os.path.abspath(sys.argv[0])}"' in content
    return False

# 添加自启动功能
def add_to_autostart(enable):
    system = platform.system()
    if system == "Windows":
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            if enable:
                winreg.SetValueEx(key, "MarkdownToWord", 0, winreg.REG_SZ, f'"{sys.argv[0]}"')
            else:
                winreg.DeleteValue(key, "MarkdownToWord")
            winreg.CloseKey(key)
            return True
        except WindowsError as e:
            # 使用PySide6的QMessageBox替换tkinter弹窗
            # 需要传递一个有效的QWidget实例作为parent，这里假设有main_window全局变量
            from PySide6.QtWidgets import QApplication, QWidget
            parent_widget = QApplication.activeWindow()
            if parent_widget is None:
                parent_widget = QWidget()
            QMessageBox.critical(parent_widget, "错误", f"无法修改注册表: {str(e)}")
            return False
    elif system == "Darwin":  # macOS
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.markdowntoword</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{os.path.abspath(sys.argv[0])}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>'''
        
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.markdowntoword.plist")
        try:
            os.makedirs(os.path.dirname(plist_path), exist_ok=True)
            if enable:
                with open(plist_path, 'w') as f:
                    f.write(plist_content)
                os.chmod(plist_path, 0o644)
            else:
                if os.path.exists(plist_path):
                    os.remove(plist_path)
            return True
        except Exception as e:
            # 使用PySide6的QMessageBox替换tkinter弹窗
            from PySide6.QtWidgets import QWidget
            temp_widget = QWidget()
            QMessageBox.critical(temp_widget, "错误", f"无法创建启动项: {str(e)}")
            return False
    return False

async def run_flask():
    """独立的Flask运行函数"""
    try:
        # 配置Flask应用日志级别，禁用所有访问日志
        import logging
        app.logger.setLevel(logging.ERROR)
        
        # 禁用Flask的访问日志输出
        @app.before_request
        def disable_request_logging():
            if flask.request.endpoint == 'static':
                return
            flask.current_app.logger.disabled = True
            
        # 运行Flask服务并完全禁用浏览器相关行为
        app.run(
            port=2403, 
            debug=False, 
            use_reloader=False,
            # 禁用启动时的访问URL提示
            extra_files=[],
            threaded=True  # 使用多线程处理请求
        )
    except Exception as e:
        print(f"Flask启动失败: {e}")
        from PySide6.QtWidgets import QApplication, QWidget
        temp_widget = QWidget()
        QMessageBox.critical(temp_widget, "错误", f"Flask服务器启动失败: {str(e)}")

async def main():
    # 初始化自启动检查
    check_autostart()
    
    # 创建Qt应用程序
    qt_app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    
    # 在后台线程启动Flask应用
    flask_thread = threading.Thread(
        target=lambda: asyncio.run(run_flask()),
        daemon=True
    )
    flask_thread.start()
    
    # 运行Qt主循环
    sys.exit(qt_app.exec())

if __name__ == "__main__":
    asyncio.run(main())

@app.route('/convert', methods=['POST'])
def async_convert():  # 改为同步函数
    data = request.get_json()  # 同步获取JSON数据
    
    # 执行文件转换
    input_path = data.get('input_path')
    output_path = data.get('output_path')
    
    if not input_path or not output_path:
        return {'error': '缺少必要参数'}, 400
    
    try:
        # 确保输入文件存在
        if not os.path.exists(input_path):
            return {'error': '输入文件不存在'}, 400
        
        # 使用BaseConverter进行转换（需要实现具体转换逻辑）
        converter = BaseConverter()
        
        # 读取Markdown文件
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 执行转换
        doc = converter.convert(content)
        
        # 保存文档
        doc.save(output_path)
        
        return {'output_path': output_path}
    except Exception as e:
        return {'error': str(e)}, 500

# 获取文档目录（跨平台）
def get_documents_path():
    """获取系统文档目录，跨平台支持"""
    system = platform.system()
    if system == "Windows":
        try:
            # 使用winreg获取我的文档路径
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders")
            doc_path = winreg.QueryValueEx(key, "Personal")[0]
            winreg.CloseKey(key)
        except Exception as e:
            print(f"注册表读取失败: {e}")
            doc_path = os.path.expanduser("~")  # 出错时回退到用户目录
    elif system in ["Darwin", "Linux"]:
        # macOS和Linux使用标准文档目录
        doc_path = os.path.expanduser("~/Documents")
    else:
        # 其他系统回退到用户目录
        doc_path = os.path.expanduser("~")
    
    return doc_path

# 构建输出路径
def build_output_path(pathf_, path_, md_url):
    """构建输出文件路径"""
    if pathf_ is None:
        doc_path = get_documents_path()
        
        # 处理文件名
        if md_url is not None:
            url_filename = os.path.basename(md_url)
        else:
            url_filename = "output.md"
            
        filename_without_ext, _ = os.path.splitext(url_filename)
        output_path = os.path.join(doc_path, f"{filename_without_ext}.docx")
    else:
        # 使用选定的保存目录
        if path_:
            base_name = os.path.basename(path_)
            filename_without_ext, _ = os.path.splitext(base_name)
            output_path = os.path.join(pathf_, f"{filename_without_ext}.docx")
        else:
            # 默认文件名
            output_path = os.path.join(pathf_, "output.docx")
    
    return output_path

