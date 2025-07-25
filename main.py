from nicegui import ui,app 
from MakeFile import MakeFile

from RunWorkflow import SessionWorkFlowWGSL
from fastapi.concurrency import run_in_threadpool

@ui.page("/word")
def make_word():
    global_text_dict = {
        "shenfen":"总经理",
        "changhe":"年终总结发言",
        "leixing":"总结",
        "zhuti":"一是巩固金融改革化险成果，二是加强战略引领，三是加速基金投资活力，四是释放金融科技实力，五是打造高素质人才队伍",
        "title":"",
        "struct":"",
        "content":"",
        "btn_enable":True
    }
    wgsl_obj = SessionWorkFlowWGSL(global_text_dict)
    ui.page_title("文稿思路助手")
    
    async def async_runWorkflowWGSL_step1():
        global_text_dict['btn_enable'] = False
        await run_in_threadpool(wgsl_obj.runWorkflowWGSL_step1)
        global_text_dict['btn_enable'] = True
    
    async def async_runWorkflowWGSL_step2():
        global_text_dict['btn_enable'] = False
        await run_in_threadpool(wgsl_obj.runWorkflowWGSL_step2)
        global_text_dict['btn_enable'] = True
    with ui.row().classes("w-full"):
        with ui.link(target="/"):
                ui.button("返回")
        with ui.column().classes("col-2"):
            ui.input("角色",).classes("w-full").bind_value(global_text_dict,"shenfen")
            ui.input("场合").classes("w-full").bind_value(global_text_dict,"changhe")
            ui.select(label="材料类型",options=["总结","方案","汇报"]).classes("w-full").bind_value(global_text_dict,"leixing")
            ui.textarea(label="核心主题").classes("w-full").bind_value(global_text_dict,"zhuti")
            ui.button("1.开始生成题目和大纲（比较快，别急）",on_click = async_runWorkflowWGSL_step1).classes("w-full").bind_enabled(global_text_dict,'btn_enable')
        with ui.column().classes("col-3"):
            ui.input(label="文章标题（可修改）").classes("w-full").bind_value(global_text_dict,"title")  
            ui.textarea(label="文章大纲(可修改)").classes("w-full").bind_value(global_text_dict,"struct")
        with ui.column().classes("col-5"):
            ui.button("2.根据大纲生成文章(很慢，得等，耐心)",on_click = async_runWorkflowWGSL_step2).classes("w-full").bind_enabled(global_text_dict,'btn_enable')  
            ui.textarea(label="文章").classes("w-full ").bind_value(global_text_dict,"content")
            ui.button('Download', on_click=lambda x:MakeFile(global_text_dict))
    

@ui.page("/")
def main():
    ui.page_title("材料撰写助手")
    with ui.row().classes("w-full center"):
        ui.image("老约翰v2.jpg").classes("w-[300px]")
        with ui.link(target="/word"):
            ui.button("写材料")

ui.run(host='0.0.0.0',port=1231,reload=True,reconnect_timeout=200)