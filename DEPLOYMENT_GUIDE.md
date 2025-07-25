# 智能试题生成系统 - 部署指南

本系统基于您现有的代码文件，集成了 Bisheng Workflow 和 NiceGUI，实现了一个完整的智能试题生成解决方案。

## 系统概述

该系统包含以下核心功能：
- 🎯 多学科试题生成（离散数学、数据库原理等）
- 📝 多题型支持（选择题、填空题、简答题、编程题等）
- 🔄 流式工作流交互
- 📱 现代化Web界面
- 📄 PDF文档自动生成和下载
- ⚡ 实时内容显示

## 文件结构

```
/workspace/
├── exam_app_fixed.py          # 主应用程序（推荐使用）
├── workflow_client.py         # Bisheng Workflow 客户端
├── pdf_generator.py           # PDF生成器
├── workflow_config.py         # 工作流配置
├── requirements.txt           # Python依赖
├── README.md                  # 项目说明
└── DEPLOYMENT_GUIDE.md        # 部署指南（本文件）
```

## 部署步骤

### 1. 环境准备

确保您的系统已安装：
- Python 3.8+
- pip

### 2. 安装依赖

```bash
pip install --break-system-packages -r requirements.txt
```

主要依赖包括：
- nicegui: Web界面框架
- requests: HTTP客户端
- reportlab: PDF生成
- markdown: 文档解析
- beautifulsoup4: HTML解析

### 3. 配置工作流

编辑 `workflow_config.py` 文件，设置您的工作流参数：

```python
workflow_config = {
    "baseurl": "http://100.100.0.117:3001/api/v2/workflow/invoke",
    "exam_generator": {
        "workflow_id": "your_actual_workflow_id"  # 替换为您的实际工作流ID
    }
}
```

### 4. 启动应用

```bash
python3 exam_app_fixed.py
```

应用将在以下地址启动：
- http://localhost:8080
- http://172.17.0.1:8080
- http://172.30.0.2:8080

## 使用指南

### 基本操作流程

1. **选择学科**：从下拉菜单选择目标学科
2. **选择题型**：勾选需要的题型（支持多选）
3. **启动工作流**：点击"启动工作流"按钮
4. **生成试题**：点击"生成试题"开始生成
5. **查看结果**：在右侧实时查看生成内容
6. **下载PDF**：点击"下载PDF"保存文档

### 界面说明

- **左侧控制面板**：参数设置和操作按钮
- **右侧内容区域**：实时显示生成的试题内容
- **状态信息**：显示当前操作状态和时间戳

## 工作流集成

### 启动工作流
系统会自动调用 Bisheng Workflow 的 `/invoke` 接口：

```python
payload = {
    "workflow_id": "your_workflow_id",
    "stream": False
}
```

### 发送输入
系统将学科和题型信息发送给工作流：

```python
payload = {
    "workflow_id": "your_workflow_id",
    "input": {
        "node_id": {
            "user_input": "学科：数据库原理，题型：选择题、简答题"
        }
    },
    "message_id": "message_id",
    "session_id": "session_id"
}
```

### 流式输出
系统支持流式接收工作流输出，实时更新界面：

```python
for line in response.iter_lines():
    if line.startswith('data: '):
        json_data = json.loads(line[6:])
        # 处理流式数据并更新界面
```

## PDF生成功能

### 功能特性
- 自动格式化试题布局
- 支持中文字体（如果系统可用）
- 包含生成信息和时间戳
- 支持 Markdown 格式解析
- 自动添加题号

### 生成过程
1. 解析工作流输出内容
2. 应用PDF样式和格式
3. 生成包含题号的结构化文档
4. 提供下载链接

## 配置说明

### 学科配置
在 `workflow_config.py` 中可以修改支持的学科：

```python
SUBJECTS = [
    "离散数学",
    "数据库原理", 
    "数据结构",
    "操作系统",
    "计算机网络",
    "软件工程",
    "算法设计与分析"
]
```

### 题型配置
```python
QUESTION_TYPES = [
    "选择题",
    "填空题", 
    "简答题",
    "编程题",
    "综合题",
    "案例分析题"
]
```

## 故障排除

### 常见问题

1. **工作流启动失败**
   - 检查 `workflow_config.py` 中的URL和工作流ID
   - 确认Bisheng Workflow服务正常运行
   - 检查网络连接

2. **PDF下载失败**
   - 确保系统有足够的磁盘空间
   - 检查文件写入权限
   - 查看控制台错误信息

3. **生成内容为空**
   - 检查工作流是否正确处理输入参数
   - 确认至少选择了一种题型
   - 查看工作流返回的错误信息

### 日志查看

应用会在控制台输出详细的状态信息，包括：
- 工作流启动状态
- 试题生成进度
- PDF生成状态
- 错误信息

## 扩展功能

### 添加新学科
1. 在 `workflow_config.py` 中的 `SUBJECTS` 列表添加新学科
2. 确保工作流支持该学科的处理

### 添加新题型
1. 在 `workflow_config.py` 中的 `QUESTION_TYPES` 列表添加新题型
2. 可以在PDF生成器中添加对应的格式处理

### 自定义样式
修改 `pdf_generator.py` 中的样式定义来自定义PDF外观。

## 性能优化

### 建议配置
- 使用SSD硬盘提高PDF生成速度
- 配置足够的内存处理大量试题内容
- 确保稳定的网络连接到Bisheng Workflow服务

### 清理任务
系统会自动清理24小时前的临时PDF文件，保持磁盘空间整洁。

## 安全注意事项

1. **网络安全**：确保工作流服务的网络安全
2. **文件权限**：合理设置PDF文件的访问权限
3. **数据保护**：及时清理敏感的试题内容

## 技术栈

- **前端**: NiceGUI (基于FastAPI和Vue.js)
- **后端**: Python + FastAPI
- **工作流**: Bisheng Workflow
- **PDF生成**: ReportLab
- **文档解析**: Markdown + BeautifulSoup

## 支持和维护

如需技术支持或功能扩展，请参考项目文档或联系开发团队。

---

**版本**: 1.0.0  
**更新日期**: 2024年12月  
**兼容性**: Python 3.8+, Bisheng Workflow 2.x