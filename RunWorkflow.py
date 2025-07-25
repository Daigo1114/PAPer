import requests
import json
from settings import workflow_conf

def step1(workflow_id,user_id):
    payload = json.dumps({
    "workflow_id": workflow_id,
    "user_id":user_id
        #"stream": False, # 为空或者不传，都会请求流式返回工作流事件。本示例为了直观展示返回结果，所以改为非流式请求，真实场景下为了用户体验建议请求流式。

    })

    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", workflow_conf['baseurl'], headers=headers, data=payload)
    response.encoding = 'UTF-8'
    print(response.text)
    line = list(filter(lambda x:x.startswith("data: "),response.text.split("\n\n")))[-1]
    if line.startswith("data: "):
        #print("aaaaaaaaa",len(line[6:]),line[6:].rstrip(" "))# 输出工作流的响应
        return json.loads(line[6:])

def GetMessage(output_by_nodeid :dict,decode_line :dict,node_id :str,part_num :int):
    decode_line_data = decode_line['data']
    if node_id in output_by_nodeid.keys():
        if decode_line_data['status'] != 'end':
            node_execution_id = decode_line_data['node_execution_id']
            output_key =decode_line_data['output_schema']['output_key']
            msg = decode_line_data['output_schema']['message']
            if node_execution_id not in output_by_nodeid[node_id]['node_execution_id'].keys() :
                part_num += 1
                output_by_nodeid[node_id]['node_execution_id'][node_execution_id] = {"part_num":part_num,"output_key":output_key,"msg":""}
                output_by_nodeid[node_id]['node_execution_id'][node_execution_id]['msg'] += msg
                return msg
            elif output_by_nodeid[node_id]['node_execution_id'][node_execution_id] \
                and output_by_nodeid[node_id]['node_execution_id'][node_execution_id]['output_key'] == output_key:
                output_by_nodeid[node_id]['node_execution_id'][node_execution_id]['msg'] += msg
                return msg
    return ""
            
class SessionWorkFlowWGSL():
    """
    文稿思路工作流
    """
    def __init__(self,global_text_dict):
        self.global_text_dict = global_text_dict
        self.workflow_id = workflow_conf['文稿思路']['workflow_id']
        step1_json = step1(self.workflow_id ,self.global_text_dict['user_id'])
        self.session_id = step1_json['session_id']
        self.node_id = step1_json['data']['node_id']
        self.message_id = step1_json['data']['message_id']

        self.title = ""
        self.file_structs =""
        self.file_kaitou = ""
        
    def runWorkflowWGSL_step1(self):
        """
        执行“文稿思路”工作流step1
        """
        self.global_text_dict['btn_enable'] = False
        payload = json.dumps({
        "workflow_id": self.workflow_id ,
        "stream": False,  # 启用流式传输
        "input": {self.node_id: {  # 事件里的节点ID
            "system_time":"23",
            "input_shenfen":self.global_text_dict['shenfen'],
            "input_changhe":self.global_text_dict['changhe'],
            "input_core_theme":self.global_text_dict['zhuti']
            
        }},
        "message_id": self.message_id,
        "session_id": self.session_id
    })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", workflow_conf['baseurl'], headers=headers, data=payload)
        print("step1:",response.text)# 输出工作流的响应
        res_json = json.loads(response.text)
        if res_json['status_code'] == 200:
            self.title = res_json['data']['events'][0]['output_schema']['message']
            self.file_structs = res_json['data']['events'][1]['output_schema']['message']
            self.file_kaitou = res_json['data']['events'][2]['output_schema']['message']
            self.next_message_id = res_json['data']['events'][3]['message_id']
            self.next_node_id = res_json['data']['events'][3]['node_id']
            ##update global变量
            self.global_text_dict['title'] = self.title
            self.global_text_dict['struct'] = self.file_structs
            
    def runWorkflowWGSL_step1_stream(self):
        """
        流-执行“文稿思路”工作流step1
        """
        self.global_text_dict['btn_enable'] = False
        payload = json.dumps({
        "workflow_id": self.workflow_id ,
        #"stream": False,  # 启用流式传输
        "input": {self.node_id: {  # 事件里的节点ID
            "system_time":"23",
            "input_shenfen":self.global_text_dict['shenfen'],
            "input_changhe":self.global_text_dict['changhe'],
            "input_core_theme":self.global_text_dict['zhuti']
            
        }},
        "message_id": self.message_id,
        "session_id": self.session_id
    })
        headers = {
        'Content-Type': 'application/json'
        }


        try:
            response = requests.request("POST", workflow_conf['baseurl'], headers=headers, data=payload,stream=True)
            response.raise_for_status()  # 检查响应状态
            response.encoding = "utf-8"
            #设置这是输出的第几部分，每个node_execution_id对应一个部分
            part_num = 0
            # print("\nReply: \n")
            output_by_nodeid = {
                "llm_f06cc":{
                    "info":"大模型-题目",
                    "node_execution_id":{
                        "":{
                            "part_num":0,
                            "output_key":None,
                            "msg":""
                            }
                    },
                    "status":"stream"
                },
                "rag_a96be":{
                    "info":"大模型-知识库-大纲",
                    "node_execution_id":{
                        "":{
                            "part_num":0,
                            "output_key":None,
                            "msg":""
                            }
                    },
                    "status":"stream"
                },
                "llm_35900":{
                    "info":"帽儿",
                    "node_execution_id":{
                        "":{
                            "part_num":0,
                            "output_key":None,
                            "msg":""
                            }
                    },
                    "status":"stream"
                }

            }
            for line in response.iter_lines():
                if line:
                    #print("aaaaaaaaa",line[6:],"bbbbbbbbbbbbbbbb")
                    print("名",self.global_text_dict['title'],"bbbbbbbbbbbbbbbb")
                    print("结构",self.global_text_dict['struct'],"bbbbbbbbbbbbbbbb")
                    print("帽子",self.file_kaitou,"bbbbbbbbbbbbbbbb")
                    decode_line = json.loads(line[6:])
                    node_id = decode_line['data']['node_id']
                    msg =GetMessage(output_by_nodeid,decode_line,node_id,part_num)
                    if node_id  == "llm_f06cc":
                        self.title += msg
                        self.global_text_dict['title'] += msg
                    elif node_id  == "rag_a96be":
                        self.file_structs += msg
                        self.global_text_dict['struct'] += msg
                    elif node_id  == "llm_35900":
                        self.file_kaitou += msg
                    if decode_line['data']['node_id'] == "input_0b78a":
                        #取下一个输入节点、对应msgID
                        self.next_message_id = decode_line['data']['message_id']
                        self.next_node_id = "input_0b78a"
                            
                    # node_id = decode_line['data']['node_id']
                    # if node_id in output_by_nodeid.keys():
                    #     if decode_line['data']['status'] != 'end':
                    #         if output_by_nodeid[node_id]['node_execution_id'] is None :
                    #             output_by_nodeid[node_id]['node_execution_id'] = decode_line['data']['node_execution_id']
                    #             output_by_nodeid[node_id]['output_key'] = decode_line['data']['output_schema']['output_key']
                    #             msg = decode_line['data']['output_schema']['message']
                    #         elif output_by_nodeid[node_id]['node_execution_id'] == decode_line['data']['node_execution_id'] \
                    #             and output_by_nodeid[node_id]['output_key'] == decode_line['data']['output_schema']['output_key']:
                    #             msg = decode_line['data']['output_schema']['message']

                    #         if node_id  == "llm_f06cc":
                    #             self.title += msg
                    #             self.global_text_dict['title'] += msg
                    #         elif node_id  == "rag_a96be":
                    #             self.file_structs += msg
                    #             self.global_text_dict['struct'] += msg
                    #         elif node_id  == "llm_35900":
                    #             self.file_kaitou += msg
                    # elif decode_line['data']['node_id'] == "input_0b78a":
                    #     #取下一个输入节点、对应msgID
                    #     self.next_message_id = decode_line['data']['message_id']
                    #     self.next_node_id = "input_0b78a"
                  
        except:
            import traceback
            traceback.print_exc() 
        finally:
            response.close()


        
        # print("step1:",response.text)# 输出工作流的响应
        # res_json = json.loads(response.text)
        # if res_json['status_code'] == 200:
        #     self.title = res_json['data']['events'][0]['output_schema']['message']
        #     self.file_structs = res_json['data']['events'][1]['output_schema']['message']
        #     self.file_kaitou = res_json['data']['events'][2]['output_schema']['message']
        #     self.next_message_id = res_json['data']['events'][3]['message_id']
        #     self.next_node_id = res_json['data']['events'][3]['node_id']
        #     ##update global变量
        #     self.global_text_dict['title'] = self.title
        #     self.global_text_dict['struct'] = self.file_structs
            
    def runWorkflowWGSL_step2(self,):
        """
        step2
        """
        payload = json.dumps({
        "workflow_id": self.workflow_id ,
        "stream": False,  # 启用流式传输
        "input": {self.next_node_id: {  # 事件里的节点ID
            "file_struct":self.global_text_dict['struct'],
            
            
        }},
        "message_id": self.next_message_id,
        "session_id": self.session_id
    })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", workflow_conf['baseurl'], headers=headers, data=payload)
        res_json = json.loads(response.text)
      
        print("step2:",response.text)# 输出工作流的响应
        self.paragraphs = []
        if res_json['status_code'] == 200:
            for event_i in filter(lambda event:event['event'] == 'stream_msg',res_json['data']['events']):
                self.paragraphs.append(event_i['output_schema']['message'])
        self.make_output_markdown()

    def runWorkflowWGSL_step2_stream(self,):
        """
        流step2
        """
        payload = json.dumps({
        "workflow_id": self.workflow_id ,
        #"stream": False,  # 启用流式传输
        "input": {self.next_node_id: {  # 事件里的节点ID
            "file_struct":self.global_text_dict['struct'],
            
            
        }},
        "message_id": self.next_message_id,
        "session_id": self.session_id
    })
        headers = {
        'Content-Type': 'application/json'
        }

        try:
            response = requests.request("POST", workflow_conf['baseurl'], headers=headers, data=payload,stream=True)
            response.raise_for_status()  # 检查响应状态
            response.encoding = "utf-8"
           # print("\nReply: \n")
            #设置这是输出的第几部分，每个node_execution_id对应一个部分
            part_num = 0
            output_by_nodeid = {
                "rag_e97bd":{
                    "info":"循环体-生成每段话",
                    "node_execution_id":{
                        "":{
                            "part_num":0,
                            "output_key":None,
                            "msg":""
                            }
                    },
                    
                    "status":"stream"
                },
            }
            for line in response.iter_lines():
                if line:
                    #print("aaaaaaaaa",line[6:],"bbbbbbbbbbbbbbbb")
                    decode_line = json.loads(line[6:])
                    print("aaaaaaaaa",decode_line,"bbbbbbbbbbbbbbbb")
                    node_id = decode_line['data']['node_id']
                    msg =GetMessage(output_by_nodeid,decode_line,node_id,part_num)
                    self.global_text_dict['content'] += msg
                    # node_id = decode_line['data']['node_id']
                    # if node_id in output_by_nodeid.keys():
                    #     if decode_line['data']['status'] != 'end':
                    #         node_execution_id = decode_line['data']['node_execution_id']
                    #         output_key =decode_line['data']['output_schema']['output_key']
                    #         msg = decode_line['data']['output_schema']['message']
                    #         if node_execution_id not in output_by_nodeid[node_id]['node_execution_id'].keys() :
                    #             part_num += 1
                    #             output_by_nodeid[node_id]['node_execution_id'][node_execution_id] = {"part_num":part_num,"output_key":output_key,"msg":""}
                    #             output_by_nodeid[node_id]['node_execution_id'][node_execution_id]['msg'] += msg
                    #             self.global_text_dict['content'] += msg
                    #         elif output_by_nodeid[node_id]['node_execution_id'][node_execution_id] \
                    #             and output_by_nodeid[node_id]['node_execution_id'][node_execution_id]['output_key'] == output_key:
                    #             output_by_nodeid[node_id]['node_execution_id'][node_execution_id]['msg'] += msg
                    #             self.global_text_dict['content'] += msg


        except:
            import traceback
            traceback.print_exc() 
        finally:
            response.close()

        # print("step2:",response.text)# 输出工作流的响应
        self.paragraphs = []
        sorted_parts = list(output_by_nodeid["rag_e97bd"]["node_execution_id"].items())
        print(sorted_parts)
        sorted_parts.sort(key=lambda x:x[1]['part_num'])
        for part_i in sorted_parts:
            if len(part_i[0]) > 0:
                self.paragraphs.append(part_i[1]['msg'])
        # self.make_output_markdown()

    def make_output_markdown(self):
        """
        输出格式化成markdown
        """
        output_text_list = ["# "+ self.title,self.file_kaitou]
        import re
        p = re.compile("[\u4e00-\u9fff]")
        digit_list = ['一','二','三','四','五','六','七','八','九','十','十一','十二','十三','十四','十五','十六','十七','十八','十九','二十','二十一','二十二']
        titles = list(filter(lambda x:len(x) > 0,self.global_text_dict['struct'].split("\n")))
        for index,(title,input) in enumerate(zip(titles,self.paragraphs)):
            title = "## " + digit_list[index]+"、"+ title[re.search(p,title).span()[0]:]
            #title = "## " + digit_list[index]+"、"+ title
            output_text_list.append("\n".join([title,input]))

        ##update global变量
        self.global_text_dict['content'] = "\n".join(output_text_list)

class SessionWorkFlowTest:
    """
    测试工作流：测试权限
    """
    def __init__(self,global_text_dict):
        self.global_text_dict = global_text_dict
        self.workflow_id = "afc8245c6e0b4a2987c4f58ecc1df0fa"
        step1_json = step1(self.workflow_id ,self.global_text_dict['user_id'])
        self.session_id = step1_json['session_id']
        self.node_id = step1_json['data']['node_id']
        self.message_id = step1_json['data']['message_id']
    def runWorkflowTest(self):
        """
        执行测试工作流step1
        """
        self.global_text_dict['btn_enable'] = False
        payload = json.dumps({
        "workflow_id": self.workflow_id ,
        "stream": False,  # 启用流式传输
        "input": {self.node_id: {  # 事件里的节点ID
            "user_input":"你的职业是什么",
            
        }},
        "message_id": self.message_id,
        "session_id": self.session_id,
        "user_id":3
    })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST",  workflow_conf['baseurl'], headers=headers, data=payload)
        print("step1:",response.text)# 输出工作流的响应
        # res_json = json.loads(response.text)
        # if res_json['status_code'] == 200:
        #     self.title = res_json['data']['events'][0]['output_schema']['message']
        #     self.file_structs = res_json['data']['events'][1]['output_schema']['message']
        #     self.file_kaitou = res_json['data']['events'][2]['output_schema']['message']
        #     self.next_message_id = res_json['data']['events'][3]['message_id']
        #     self.next_node_id = res_json['data']['events'][3]['node_id']
        #     ##update global变量
        #     self.global_text_dict['title'] = self.title
        #     self.global_text_dict['struct'] = self.file_structs       
    def runWorkflowTestStream(self):
        """
        流式-执行测试工作流step1
        """
        self.global_text_dict['btn_enable'] = False
        payload = json.dumps({
        "workflow_id": self.workflow_id ,
        "stream": True,  # 启用流式传输
        "input": {self.node_id: {  # 事件里的节点ID
            "user_input":"你的职业是什么",
            
        }},
        "message_id": self.message_id,
        "session_id": self.session_id,
        "user_id":3
    })
        headers = {
        'Content-Type': 'application/json'
        }

        try:
            response = requests.request("POST",  workflow_conf['baseurl'], headers=headers, data=payload,stream=True)
            response.raise_for_status()  # 检查响应状态
            response.encoding = "utf-8"
           # print("\nReply: \n")
            output = {
                "node_execution_id":None,
                "output_key":None,
                "status":"stream"
            }
            for line in response.iter_lines():
                if line:
                    print("aaaaaaaaa",line[6:],"bbbbbbbbbbbbbbbb")
                    decode_line = json.loads(line[6:])
                    if decode_line['data']['status'] != 'end':
                        if output['node_execution_id'] is None :
                            output['node_execution_id'] = decode_line['data']['node_execution_id']
                            output['output_key'] = decode_line['data']['output_schema']['output_key']
                            yield decode_line['data']['output_schema']['message']
                        elif output['node_execution_id'] == decode_line['data']['node_execution_id'] \
                            and output['output_key'] == decode_line['data']['output_schema']['output_key']:
                            yield  decode_line['data']['output_schema']['message']
                  
        except:
            import traceback
            traceback.print_exc() 
        finally:
            response.close()
if __name__ =="__main__":
    # 测试：文稿思路助手
    global_text_dict = {
        "shenfen":"总经理",
        "changhe":"年终总结发言",
        "leixing":"总结",
        "zhuti":"一是巩固金融改革化险成果，二是加强战略引领，三是加速基金投资活力，四是释放金融科技实力，五是打造高素质人才队伍",
        "title":"",
        "struct":"",
        "content":"",
        "btn_enable":True,
        "user_id":3
    }
    # obj = SessionWorkFlowWGSL(global_text_dict)
    # obj.runWorkflowWGSL_step1_stream()
    # obj.runWorkflowWGSL_step2_stream()
    # obj.runWorkflowWGSL_step1()
    # obj.runWorkflowWGSL_step2()

    # #测试：测试助手
    obj = SessionWorkFlowTest(global_text_dict)
    #obj.runWorkflowTest()
    
    for chunk in obj.runWorkflowTestStream():
        print("666:",chunk)