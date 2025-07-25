import requests
import json
import time
from typing import Dict, List, Any, Optional
from workflow_config import workflow_config

class WorkflowClient:
    """
    Bisheng Workflow 客户端类
    处理与工作流的交互逻辑
    """
    
    def __init__(self):
        self.base_url = workflow_config['baseurl']
        self.workflow_id = workflow_config['exam_generator']['workflow_id']
        self.session_id = None
        self.current_message_id = None
        self.current_node_id = None
        
    def start_workflow(self) -> Dict[str, Any]:
        """
        启动工作流
        """
        payload = json.dumps({
            "workflow_id": self.workflow_id,
            "stream": False
        })
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, data=payload)
            response.raise_for_status()
            result = response.json()
            
            if result.get('status_code') == 200:
                self.session_id = result['data']['session_id']
                # 解析事件，找到输入节点
                events = result['data'].get('events', [])
                for event in events:
                    if event.get('event') == 'input':
                        self.current_message_id = event.get('message_id')
                        self.current_node_id = event.get('node_id')
                        break
                        
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"工作流启动失败: {e}")
            return {"status_code": 500, "error": str(e)}
    
    def send_input(self, subject: str, question_types: List[str]) -> Dict[str, Any]:
        """
        发送用户输入到工作流
        
        Args:
            subject: 选择的学科科目
            question_types: 选择的题型列表
        """
        if not self.session_id or not self.current_node_id or not self.current_message_id:
            return {"status_code": 400, "error": "工作流未正确初始化"}
        
        # 将题型列表转换为字符串
        question_types_str = "、".join(question_types)
        
        payload = json.dumps({
            "workflow_id": self.workflow_id,
            "stream": False,
            "input": {
                self.current_node_id: {
                    "user_input": f"学科：{subject}，题型：{question_types_str}"
                }
            },
            "message_id": self.current_message_id,
            "session_id": self.session_id
        })
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, data=payload)
            response.raise_for_status()
            result = response.json()
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"发送输入失败: {e}")
            return {"status_code": 500, "error": str(e)}
    
    def extract_workflow_output(self, result: Dict[str, Any]) -> str:
        """
        从工作流结果中提取输出内容
        """
        if result.get('status_code') != 200:
            return "工作流执行失败"
        
        events = result.get('data', {}).get('events', [])
        output_content = []
        
        for event in events:
            if event.get('event') in ['output_msg', 'stream_msg']:
                output_schema = event.get('output_schema', {})
                message = output_schema.get('message', '')
                if message:
                    output_content.append(message)
        
        return '\n'.join(output_content) if output_content else "未获取到有效输出"
    
    def stop_workflow(self) -> Dict[str, Any]:
        """
        停止工作流
        """
        if not self.session_id:
            return {"status_code": 400, "error": "没有活动的工作流会话"}
        
        stop_url = "http://100.100.0.117:3001/api/v2/workflow/stop"
        payload = json.dumps({
            "session_id": self.session_id
        })
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(stop_url, headers=headers, data=payload)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"停止工作流失败: {e}")
            return {"status_code": 500, "error": str(e)}


class StreamingWorkflowClient(WorkflowClient):
    """
    流式工作流客户端
    支持流式接收工作流输出
    """
    
    def send_input_stream(self, subject: str, question_types: List[str], callback=None):
        """
        流式发送输入并接收输出
        
        Args:
            subject: 选择的学科科目
            question_types: 选择的题型列表  
            callback: 回调函数，用于处理流式输出
        """
        if not self.session_id or not self.current_node_id or not self.current_message_id:
            if callback:
                callback("工作流未正确初始化")
            return
        
        question_types_str = "、".join(question_types)
        
        payload = json.dumps({
            "workflow_id": self.workflow_id,
            # stream 参数不设置或为空，启用流式传输
            "input": {
                self.current_node_id: {
                    "user_input": f"学科：{subject}，题型：{question_types_str}"
                }
            },
            "message_id": self.current_message_id,
            "session_id": self.session_id
        })
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, data=payload, stream=True)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            current_content = ""
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            json_data = json.loads(line_str[6:])
                            event = json_data.get('data', {})
                            
                            if event.get('event') in ['output_msg', 'stream_msg']:
                                output_schema = event.get('output_schema', {})
                                message = output_schema.get('message', '')
                                if message:
                                    current_content += message
                                    if callback:
                                        callback(current_content)
                                        
                        except json.JSONDecodeError:
                            continue
                            
            return current_content
            
        except requests.exceptions.RequestException as e:
            error_msg = f"流式请求失败: {e}"
            if callback:
                callback(error_msg)
            return error_msg