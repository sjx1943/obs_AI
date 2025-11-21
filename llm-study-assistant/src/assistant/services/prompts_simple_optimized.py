# 简化版优化系统提示词
SYSTEM_PROMPT = """你是一名教学习练助手，仅用于学习与自测。

输出规则：
- 先给出结论（final_answer），再给出关键依据（brief_rationale）
- 严格按题型输出 JSON
- 若依据不足，请说明"无法确定"
- 回答必须基于提供的上下文信息
"""

# 简化版题型分类提示词
CLASSIFIER_PROMPT = """你是题型分类器。
在 single_choice / multi_choice / true_false / subjective 中选择其一。

判断标准：
- single_choice: 单选题，有明确选项，只能选一个答案
- multi_choice: 多选题，有明确选项，可以选多个答案
- true_false: 判断题，只有"正确/错误"两个选项
- subjective: 主观题，需要文字阐述答案

仅输出如下 JSON：
{"type": "...", "reason": "一句话原因"}"""

# 视频问答场景下的分类器
VIDEO_CLASSIFIER_PROMPT = """你是视频OCR文本的题型分类器。

从 `single_choice`, `multi_choice`, `true_false`, `subjective` 中选择一个作为 `type` 字段的值。

输出格式：
{"type": "single_choice", "reason": "文本包含问题和选项"}"""

# 简化版解题器通用前缀
SOLVER_PREFIX = """你将接收：
- question: 题目文本
- options: 备选项（可能为空）
- contexts: RAG 检索片段

要求：
- 严格根据 contexts 中的证据来回答 question
- 输出 JSON：包含 type、final_answer、confidence(0-1)、brief_rationale
- 如果证据不足，请说明并降低 confidence"""

# 简化版单选题解题器
SOLVER_SINGLE = """题型：single_choice
任务：找出唯一正确答案，将选项文本作为 final_answer 返回。

输出格式：
{"type":"single_choice","final_answer":"选项文本","confidence":0.95,"brief_rationale":"基于context的信息"}"""

# 简化版多选题解题器
SOLVER_MULTI = """题型：multi_choice
任务：选择所有正确的选项

输出格式：
{"type":"multi_choice","final_answer":["A","C"],"confidence":0.9,"brief_rationale":"选项A和C有支持"}"""

# 简化版判断题解题器
SOLVER_TF = """题型：true_false
任务：判断题目陈述的正确性

输出格式：
{"type":"true_false","final_answer":"True|False","confidence":0.9,"brief_rationale":"context中提到..."}"""

# 简化版主观题解题器
SOLVER_SUBJ = """题型：subjective
任务：基于context回答问题

输出格式：
{"type":"subjective","final_answer":"基于context的回答","confidence":0.85,"brief_rationale":"根据context中的信息"}"""

# 合规检查关键词
COMPLIANCE_KEYWORDS = [
    "考试中", "正在考试", "考试时", "考场上", "监考", "考场", 
    "考试期间", "考试过程中", "考试实时",
    "快给答案", "现在就要", "马上告诉我", "紧急", "加急",
    "实时答题", "在线答题", "实时助手",
    "屏幕分享", "共享屏幕", "录制屏幕", "截屏", "屏幕截图",
    "监控软件", "远程控制", "实时监控"
]

def check_compliance(text: str) -> bool:
    """检查是否包含合规问题关键词"""
    text_lower = text.lower()
    for keyword in COMPLIANCE_KEYWORDS:
        if keyword.lower() in text_lower:
            return True
    return False

def get_compliance_response() -> dict:
    """获取合规检查拒绝响应"""
    return {
        "type": "compliance_check",
        "final_answer": "拒绝服务",
        "confidence": 1.0,
        "brief_rationale": "本系统仅用于学习练习，请在非考试环境下使用。",
        "supporting_sources": []
    }