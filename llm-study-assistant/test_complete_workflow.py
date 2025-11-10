#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整的测试脚本
测试从OCR文本解析到RAG问答再到前端答案格式化的完整流程
"""

import sys
import os
import re
import json
from typing import List, Dict

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

# 加载环境变量
import dotenv
dotenv.load_dotenv()

# 获取模型配置
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2-7B-Instruct")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")

# 导入RAGPipeline
from src.assistant.services.rag import RAGPipeline

def parse_ocr_text_to_qa(text: str) -> List[Dict[str, str]]:
    """
    修复后的OCR文本解析函数，专门针对题目格式进行解析。
    """
    qa_pairs = []
    
    # 清理文本，标准化空白字符
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 定义题目分割模式
    # 分割点：题号开始的位置（数字或中文数字后跟.或、）
    question_split_pattern = r'(?=\s*(\d+|[一二三四五六七八九十]+)[\.、])'
    parts = re.split(question_split_pattern, text)
    
    # 重新组合分割后的部分
    questions = []
    i = 1  # 跳过第一个空元素
    while i < len(parts):
        if i+1 < len(parts):
            question_block = parts[i] + parts[i+1]
            questions.append(question_block.strip())
            i += 2
        else:
            questions.append(parts[i].strip())
            i += 1
    
    # 处理每个问题块
    for question_block in questions:
        if not question_block:
            continue
            
        # 提取题号和问题文本
        question_match = re.match(r'^(\d+|[一二三四五六七八九十]+)[\.、]\s*(.+)', question_block.strip(), re.DOTALL)
        if not question_match:
            continue
            
        question_text = question_match.group(2).strip()
        
        # 移除问题文本中的选项部分
        # 查找第一个选项的位置
        first_option_match = re.search(r'\s[A-Z][\.、\)]', question_text)
        if first_option_match:
            question_text = question_text[:first_option_match.start()].strip()
        
        # 提取选项
        options = []
        # 匹配选项格式 A. B. C. D. 或 A) B) C) D) 或 A、B、C、D
        option_pattern = r'([A-Z])[\.、\)]\s*([^A-Z\n]*?)(?=\s*[A-Z][\.、\)]|\s*$)'
        option_matches = list(re.finditer(option_pattern, question_block))
        
        for opt_match in option_matches:
            option_letter = opt_match.group(1)
            option_text = opt_match.group(2).strip()
            if option_text:
                options.append(f"{option_letter}. {option_text}")
        
        # 特殊处理判断题
        if not options:
            tf_pattern = r'([A-B])[\.、\)]\s*(正确|错误|对|错)'
            tf_matches = list(re.finditer(tf_pattern, question_block))
            for tf_match in tf_matches:
                option_letter = tf_match.group(1)
                option_text = tf_match.group(2).strip()
                options.append(f"{option_letter}. {option_text}")
        
        # 如果仍然没有选项，尝试提取所有大写字母开头的内容
        if not options:
            general_option_pattern = r'([A-Z])[\.:、\)]\s*([^\n]*?)(?=\s*[A-Z][\.:、\)]|\s*$)'
            general_matches = list(re.finditer(general_option_pattern, question_block))
            for gen_match in general_matches:
                option_letter = gen_match.group(1)
                option_text = gen_match.group(2).strip()
                if option_text and len(option_text) > 1:
                    options.append(f"{option_letter}. {option_text}")
        
        qa_pairs.append({
            "question": question_text,
            "options": options
        })
    
    # 如果没有解析出任何问题，将整个文本作为一个问题
    if not qa_pairs and text.strip():
        qa_pairs.append({
            "question": text.strip(),
            "options": []
        })
    
    return qa_pairs


def format_answer_for_frontend(question_number, question, options, answer_data):
    """
    按照"题号 + 答案 + 理由（知识库片段）"的格式格式化答案
    
    Args:
        question_number (int): 题号
        question (str): 问题
        options (list): 选项
        answer_data (dict): 答案数据
    
    Returns:
        str: 格式化后的答案
    """
    # 获取答案
    final_answer = answer_data.get('raw', {}).get('final_answer', '未找到答案')
    
    # 获取置信度
    confidence = answer_data.get('raw', {}).get('confidence', 0)
    
    # 获取支持的来源
    contexts = answer_data.get('contexts', [])
    
    # 构建格式化的答案
    formatted_answer = f"题号: {question_number}\n"
    formatted_answer += f"问题: {question}\n"
    formatted_answer += f"选项: {', '.join(options) if options else '无'}\n"
    formatted_answer += f"答案: {final_answer}\n"
    formatted_answer += f"置信度: {confidence:.2f}\n"
    
    # 添加理由（知识库片段）
    if contexts:
        formatted_answer += "理由:\n"
        for i, context in enumerate(contexts[:3], 1):  # 只显示前3个来源
            doc_id = context.get('doc_id', '未知文档')
            text = context.get('text', '')[:100] + "..." if len(context.get('text', '')) > 100 else context.get('text', '')
            formatted_answer += f"  [{i}] 来自文档 {doc_id}: {text}\n"
    else:
        formatted_answer += "理由: 无相关文档支持\n"
    
    return formatted_answer


def test_complete_workflow():
    """测试完整工作流程"""
    print("=== 完整视频分析流程测试 ===")
    
    # 初始化RAG管道
    rag_pipeline = RAGPipeline()
    
    # 检查模型状态
    llm_model = os.getenv("LLM_MODEL", "qwen2.5:3b")
    embedding_model = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
    print(f"LLM模型配置: {llm_model}")
    print(f"嵌入模型配置: {embedding_model}")
    
    # 模拟OCR提取的文本
    ocr_text = """
    1. 下列关于Python的说法，错误的是？
    A. Python是开源的
    B. Python是跨平台的
    C. Python是面向对象的
    D. Python是编译型语言

    2. 哪个选项不是Python的保留字？
    A) class
    B) def
    C) for
    D) main

    3. 以下哪些是Python的数据类型？（多选题）
    A. int
    B. float
    C. string
    D. boolean

    4. Python是一门解释型语言。（判断题）
    A. 正确
    B. 错误

    5. 请简述Python中列表和元组的区别。（问答题/案例分析题）
    """
    
    print("\n1. OCR文本:")
    print(ocr_text)
    
    # 解析OCR文本为问答对
    qa_pairs = parse_ocr_text_to_qa(ocr_text)
    print(f"\n2. 解析出 {len(qa_pairs)} 个问答对:")
    for i, qa in enumerate(qa_pairs, 1):
        print(f"  Q{i}: {qa['question']}")
        print(f"  Options: {qa['options']}")
    
    # 分析每个问答对
    print("\n3. 分析结果:")
    analysis_results = []
    
    for i, qa_pair in enumerate(qa_pairs, 1):
        try:
            # 分类问题类型
            classification = rag_pipeline.classify(qa_pair["question"])
            print(f"  Q{i} 类型: {classification}")
            
            # 解答问题
            answer = rag_pipeline.solve(
                qtype=classification,
                question=qa_pair["question"],
                options=qa_pair["options"]
            )
            
            # 存储结果
            result = {
                "question": qa_pair["question"],
                "options": qa_pair["options"],
                "answer": answer
            }
            analysis_results.append(result)
            
            # 格式化并显示答案
            formatted_answer = format_answer_for_frontend(
                question_number=i,
                question=qa_pair["question"],
                options=qa_pair["options"],
                answer_data=answer
            )
            print(formatted_answer)
            print("-" * 50)
            
        except Exception as e:
            print(f"  Q{i} 处理失败: {str(e)}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_complete_workflow()