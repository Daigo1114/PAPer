# 智能试题生成系统

基于 Bisheng Workflow 和 NiceGUI 的智能试题生成系统，支持多学科、多题型的自动化试题生成和PDF导出。

## 功能特性

- 🎯 **多学科支持**: 支持离散数学、数据库原理、数据结构等多个学科
- 📝 **多题型生成**: 选择题、填空题、简答题、编程题等多种题型
- 🔄 **工作流集成**: 无缝集成 Bisheng Workflow 引擎
- 📱 **响应式界面**: 基于 NiceGUI 的现代化 Web 界面
- 📄 **PDF导出**: 一键生成格式化的PDF试题文档
- 🚀 **流式输出**: 实时显示试题生成过程

## 系统架构

```
exam_app.py          # 主应用入口和UI界面
workflow_client.py   # Bisheng Workflow 客户端
pdf_generator.py     # PDF文档生成器
workflow_config.py   # 工作流配置
requirements.txt     # 依赖包列表
```

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置工作流

编辑 `workflow_config.py` 文件，设置正确的工作流URL和ID：

```python
workflow_config = {
    "baseurl": "http://100.100.0.117:3001/api/v2/workflow/invoke",
    "exam_generator": {
        "workflow_id": "your_workflow_id_here"
    }
}
```

### 3. 运行应用

```bash
python exam_app.py
```

应用将在 http://localhost:8080 启动。

## 使用说明

### 基本流程

1. **选择学科**: 从下拉菜单中选择目标学科
2. **选择题型**: 勾选需要生成的题型（支持多选）
3. **启动工作流**: 点击"启动工作流"按钮初始化
4. **生成试题**: 点击"生成试题"开始生成过程
5. **查看内容**: 在右侧实时查看生成的试题内容
6. **下载PDF**: 点击"下载PDF"保存为文档

### 界面说明

- **左侧控制面板**: 参数选择和操作按钮
- **右侧内容区域**: 实时显示生成内容
- **状态栏**: 显示当前操作状态和时间

## 工作流交互

### 启动工作流

```python
# 发起工作流执行
payload = {
    "workflow_id": "your_workflow_id",
    "stream": False
}
```

### 发送用户输入

```python
# 发送学科和题型信息
payload = {
    "workflow_id": "your_workflow_id", 
    "stream": False,
    "input": {
        "node_id": {
            "user_input": "学科：数据库原理，题型：选择题、简答题"
        }
    },
    "message_id": "message_id",
    "session_id": "session_id"
}
```

### 流式接收输出

系统支持流式接收工作流输出，实时更新界面内容：

```python
for line in response.iter_lines():
    if line.startswith('data: '):
        json_data = json.loads(line[6:])
        # 处理流式数据
```

## PDF生成

### 功能特性

- 支持中文字体（如果系统可用）
- 自动格式化试题布局
- 包含生成信息和时间戳
- 支持 Markdown 格式解析

### 生成过程

1. 解析工作流输出内容
2. 应用PDF样式和格式
3. 生成包含题号的结构化文档
4. 提供下载链接

## 配置说明

### 学科配置

在 `workflow_config.py` 中修改可选学科：

```python
SUBJECTS = [
    "离散数学",
    "数据库原理", 
    "数据结构",
    "操作系统",
    # 添加更多学科...
]
```

### 题型配置

```python
QUESTION_TYPES = [
    "选择题",
    "填空题", 
    "简答题",
    "编程题",
    # 添加更多题型...
]
```

## 错误处理

系统包含完善的错误处理机制：

- 网络连接错误处理
- 工作流状态验证
- PDF生成异常处理
- 用户输入验证

## 技术栈

- **前端**: NiceGUI (基于FastAPI和Vue.js)
- **后端**: Python + FastAPI
- **工作流**: Bisheng Workflow
- **PDF生成**: ReportLab
- **文档解析**: Markdown + BeautifulSoup

## 开发和扩展

### 添加新学科

1. 在 `workflow_config.py` 中添加学科名称
2. 确保工作流支持该学科的处理

### 添加新题型

1. 在 `QUESTION_TYPES` 列表中添加题型
2. 在PDF生成器中添加对应的格式处理

### 自定义样式

修改 `pdf_generator.py` 中的样式定义：

```python
def create_styles(self):
    # 自定义PDF样式
    pass
```

## 注意事项

1. 确保Bisheng Workflow服务正常运行
2. 检查网络连接和防火墙设置
3. 定期清理生成的临时PDF文件
4. 根据实际需求调整工作流ID和节点配置

## 常见问题

### Q: 工作流启动失败？
A: 检查 `workflow_config.py` 中的URL和工作流ID是否正确。

### Q: PDF下载失败？
A: 确保系统有足够的磁盘空间和写入权限。

### Q: 生成内容为空？
A: 检查工作流是否正确处理输入参数。

## 更新日志

- v1.0.0: 初始版本，支持基本的试题生成和PDF导出
- 支持多学科和多题型选择
- 集成流式输出显示
- 完善的错误处理机制

## 许可证

本项目采用 MIT 许可证。