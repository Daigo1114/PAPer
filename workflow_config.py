workflow_config = {
    "baseurl": "http://100.100.0.117:3001/api/v2/workflow/invoke",
    "exam_generator": {
        "workflow_id": "b9178eac041a448e9726dd47dcfdee2b"  # 根据您提供的工作流ID
    }
}

# 学科科目选项
SUBJECTS = [
    "离散数学",
    "数据库原理", 
    "数据结构",
    "操作系统",
    "计算机网络",
    "软件工程",
    "算法设计与分析"
]

# 题型选项
QUESTION_TYPES = [
    "选择题",
    "填空题", 
    "简答题",
    "编程题",
    "综合题",
    "案例分析题"
]