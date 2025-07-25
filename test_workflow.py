import requests
import json

url = "http://100.100.0.117:3001/api/v2/workflow/invoke"

def step1():
    payload = json.dumps({
    "workflow_id": "34b17ca951cb48938bc5392752b901a4",
    "stream": False, # 为空或者不传，都会请求流式返回工作流事件。本示例为了直观展示返回结果，所以改为非流式请求，真实场景下为了用户体验建议请求流式。
    })

    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)# 输出工作流的响应

def step2():
    payload = json.dumps({
    "workflow_id": "34b17ca951cb48938bc5392752b901a4",
    "stream": False,  # 启用流式传输
    "input": {"input_8385f": {  # 事件里的节点ID
        "system_time":"23",
            "input_shenfen":"总经理",
            "input_changhe":"年度工作会议",
            "input_core_theme":"一是巩固金融改革化险成果，二是加强战略引领，三是加速基金投资活力，四是释放金融科技实力，五是打造高素质人才队伍"
        
    }},
    "message_id": "630",
    "session_id": "f1218873cf344eb089e549a78c7e16c7_async_task_id"
})
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)# 输出工作流的响应

step2()
