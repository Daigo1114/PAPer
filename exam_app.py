from nicegui import ui, app
from fastapi.concurrency import run_in_threadpool
import asyncio
import os
from datetime import datetime
from typing import Dict, List, Any

from workflow_client import WorkflowClient, StreamingWorkflowClient
from pdf_generator import PDFGenerator
from workflow_config import SUBJECTS, QUESTION_TYPES

class ExamGeneratorApp:
    """
    试题生成应用主类
    """
    
    def __init__(self):
        self.workflow_client = None
        self.streaming_client = None
        self.pdf_generator = PDFGenerator()
        
        # 应用状态
        self.state = {
            'subject': SUBJECTS[0],  # 默认选择第一个学科
            'question_types': [],
            'generated_content': '',
            'is_generating': False,
            'workflow_started': False,
            'current_pdf_file': None
        }
        
        # UI组件引用
        self.ui_components = {}
        
    def setup_ui(self):
        """
        设置用户界面
        """
        ui.page_title("智能试题生成系统")
        
        # 主容器
        with ui.row().classes("w-full min-h-screen bg-gray-50"):
            # 左侧控制面板
            with ui.column().classes("w-1/3 p-6 bg-white shadow-lg"):
                self.create_control_panel()
            
            # 右侧内容显示区域
            with ui.column().classes("w-2/3 p-6"):
                self.create_content_area()
    
    def create_control_panel(self):
        """
        创建左侧控制面板
        """
        ui.label("试题生成控制台").classes("text-2xl font-bold mb-6 text-gray-800")
        
        # 学科选择
        with ui.card().classes("w-full mb-4"):
            ui.label("选择学科科目").classes("text-lg font-semibold mb-2")
            self.ui_components['subject_select'] = ui.select(
                options=SUBJECTS,
                value=SUBJECTS[0],
                on_change=self.on_subject_change
            ).classes("w-full")
        
        # 题型选择
        with ui.card().classes("w-full mb-4"):
            ui.label("选择题型（可多选）").classes("text-lg font-semibold mb-2")
            
            # 创建题型复选框
            self.ui_components['question_checkboxes'] = {}
            for question_type in QUESTION_TYPES:
                self.ui_components['question_checkboxes'][question_type] = ui.checkbox(
                    text=question_type,
                    value=False,
                    on_change=self.on_question_type_change
                ).classes("mb-2")
        
        # 操作按钮
        with ui.card().classes("w-full mb-4"):
            ui.label("操作").classes("text-lg font-semibold mb-2")
            
            self.ui_components['start_btn'] = ui.button(
                "启动工作流",
                on_click=self.start_workflow,
                color="primary"
            ).classes("w-full mb-2").bind_enabled_from(
                self.state, 'workflow_started', backward=lambda x: not x
            )
            
            self.ui_components['generate_btn'] = ui.button(
                "生成试题",
                on_click=self.generate_questions,
                color="positive"
            ).classes("w-full mb-2").bind_enabled_from(
                self.state, 'is_generating', backward=lambda x: not x
            )
            
            self.ui_components['download_btn'] = ui.button(
                "下载PDF",
                on_click=self.download_pdf,
                color="accent"
            ).classes("w-full mb-2")
            
            self.ui_components['reset_btn'] = ui.button(
                "重置",
                on_click=self.reset_app,
                color="negative"
            ).classes("w-full")
        
        # 状态显示
        with ui.card().classes("w-full"):
            ui.label("状态信息").classes("text-lg font-semibold mb-2")
            self.ui_components['status_label'] = ui.label("就绪").classes("text-sm text-gray-600")
    
    def create_content_area(self):
        """
        创建右侧内容显示区域
        """
        ui.label("生成内容").classes("text-2xl font-bold mb-6 text-gray-800")
        
        # 参数显示
        with ui.card().classes("w-full mb-4"):
            ui.label("当前参数").classes("text-lg font-semibold mb-2")
            
            with ui.row().classes("w-full"):
                with ui.column().classes("w-1/2"):
                    ui.label("学科：").classes("font-medium")
                    self.ui_components['subject_display'] = ui.label("").bind_text_from(
                        self.state, 'subject'
                    ).classes("text-blue-600")
                
                with ui.column().classes("w-1/2"):
                    ui.label("题型：").classes("font-medium")
                    self.ui_components['types_display'] = ui.label("").classes("text-green-600")
        
        # 内容显示区域
        with ui.card().classes("w-full h-96"):
            ui.label("生成的试题内容").classes("text-lg font-semibold mb-2")
            
            self.ui_components['content_area'] = ui.textarea(
                placeholder="试题内容将在这里显示...",
                readonly=True
            ).classes("w-full h-80").bind_value_from(self.state, 'generated_content')
        
        # 进度指示
        self.ui_components['progress'] = ui.linear_progress(
            value=0,
            show_value=False
        ).classes("w-full").bind_visibility_from(self.state, 'is_generating')
    
    def on_subject_change(self, e):
        """
        学科选择变化处理
        """
        self.state['subject'] = e.value
        self.update_status("学科已选择: " + e.value)
    
    def on_question_type_change(self, e):
        """
        题型选择变化处理
        """
        selected_types = []
        for question_type, checkbox in self.ui_components['question_checkboxes'].items():
            if checkbox.value:
                selected_types.append(question_type)
        
        self.state['question_types'] = selected_types
        self.ui_components['types_display'].set_text("、".join(selected_types))
        
        if selected_types:
            self.update_status(f"已选择题型: {', '.join(selected_types)}")
        else:
            self.update_status("请至少选择一种题型")
    
    async def start_workflow(self):
        """
        启动工作流
        """
        self.update_status("正在启动工作流...")
        
        try:
            # 在线程池中运行工作流启动
            self.workflow_client = WorkflowClient()
            self.streaming_client = StreamingWorkflowClient()
            
            result = await run_in_threadpool(self.workflow_client.start_workflow)
            
            if result.get('status_code') == 200:
                self.state['workflow_started'] = True
                self.update_status("工作流启动成功，可以开始生成试题")
                
                # 同步流式客户端的会话信息
                self.streaming_client.session_id = self.workflow_client.session_id
                self.streaming_client.current_message_id = self.workflow_client.current_message_id
                self.streaming_client.current_node_id = self.workflow_client.current_node_id
                
            else:
                self.update_status(f"工作流启动失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            self.update_status(f"启动工作流时发生错误: {str(e)}")
    
    async def generate_questions(self):
        """
        生成试题
        """
        if not self.state['workflow_started']:
            self.update_status("请先启动工作流")
            return
        
        if not self.state['subject']:
            self.update_status("请选择学科科目")
            return
        
        if not self.state['question_types']:
            self.update_status("请至少选择一种题型")
            return
        
        self.state['is_generating'] = True
        self.state['generated_content'] = ""
        self.update_status("正在生成试题，请稍候...")
        
        try:
            # 使用流式客户端生成内容
            def update_content(content):
                self.state['generated_content'] = content
                ui.run_javascript('window.scrollTo(0, document.body.scrollHeight);')
            
            result = await run_in_threadpool(
                self.streaming_client.send_input_stream,
                self.state['subject'],
                self.state['question_types'],
                update_content
            )
            
            if result and not result.startswith("工作流"):
                self.update_status("试题生成完成！")
            else:
                self.update_status("试题生成失败，请重试")
                
        except Exception as e:
            self.update_status(f"生成试题时发生错误: {str(e)}")
        finally:
            self.state['is_generating'] = False
    
    async def download_pdf(self):
        """
        下载PDF文档
        """
        if not self.state['generated_content']:
            self.update_status("没有可下载的内容，请先生成试题")
            return
        
        self.update_status("正在生成PDF文档...")
        
        try:
            # 在线程池中生成PDF
            filename = await run_in_threadpool(
                self.pdf_generator.generate_pdf,
                self.state['generated_content'],
                self.state['subject'],
                self.state['question_types']
            )
            
            # 设置下载文件名
            download_name = f"{self.state['subject']}_试题_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # 提供下载
            ui.download(src=filename, filename=download_name)
            
            self.state['current_pdf_file'] = filename
            self.update_status("PDF文档已生成，开始下载...")
            
        except Exception as e:
            self.update_status(f"生成PDF时发生错误: {str(e)}")
    
    def reset_app(self):
        """
        重置应用状态
        """
        # 重置状态
        self.state['subject'] = SUBJECTS[0]
        self.state['question_types'] = []
        self.state['generated_content'] = ''
        self.state['is_generating'] = False
        self.state['workflow_started'] = False
        
        # 重置UI组件
        self.ui_components['subject_select'].set_value(SUBJECTS[0])
        
        for checkbox in self.ui_components['question_checkboxes'].values():
            checkbox.set_value(False)
        
        self.ui_components['types_display'].set_text("")
        
        # 停止工作流
        if self.workflow_client:
            try:
                self.workflow_client.stop_workflow()
            except:
                pass
        
        self.workflow_client = None
        self.streaming_client = None
        
        self.update_status("应用已重置")
    
    def update_status(self, message: str):
        """
        更新状态显示
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_message = f"[{timestamp}] {message}"
        self.ui_components['status_label'].set_text(status_message)
        print(status_message)  # 同时输出到控制台


# 创建应用实例
exam_app = ExamGeneratorApp()

@ui.page("/")
def main_page():
    """
    主页面
    """
    exam_app.setup_ui()

@ui.page("/about")
def about_page():
    """
    关于页面
    """
    ui.page_title("关于 - 智能试题生成系统")
    
    with ui.column().classes("w-full max-w-4xl mx-auto p-8"):
        ui.label("智能试题生成系统").classes("text-3xl font-bold mb-6")
        
        with ui.card().classes("w-full mb-4"):
            ui.label("系统功能").classes("text-xl font-semibold mb-4")
            ui.html("""
            <ul class="list-disc pl-6 space-y-2">
                <li>支持多种学科科目的试题生成</li>
                <li>支持多种题型组合选择</li>
                <li>集成 Bisheng Workflow 智能生成</li>
                <li>支持流式输出实时查看</li>
                <li>一键导出PDF文档</li>
                <li>响应式用户界面</li>
            </ul>
            """)
        
        with ui.card().classes("w-full mb-4"):
            ui.label("使用说明").classes("text-xl font-semibold mb-4")
            ui.html("""
            <ol class="list-decimal pl-6 space-y-2">
                <li>选择目标学科科目</li>
                <li>勾选需要的题型（可多选）</li>
                <li>点击"启动工作流"初始化</li>
                <li>点击"生成试题"开始生成</li>
                <li>查看实时生成内容</li>
                <li>点击"下载PDF"保存文档</li>
            </ol>
            """)
        
        with ui.link(target="/"):
            ui.button("返回主页", color="primary")

if __name__ == "__main__":
    # 定期清理旧PDF文件
    import threading
    import time
    
    def cleanup_old_files():
        while True:
            try:
                exam_app.pdf_generator.clean_old_files(max_age_hours=24)
            except:
                pass
            time.sleep(3600)  # 每小时清理一次
    
    cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
    cleanup_thread.start()
    
    # 启动应用
    ui.run(
        host='0.0.0.0',
        port=8080,
        title="智能试题生成系统",
        reload=True,
        show=False
    )