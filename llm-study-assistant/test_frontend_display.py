#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
前端展示格式测试脚本
验证按照"题号 + 答案 + 理由（知识库片段）"的格式展示分析结果
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.assistant.services.rag import RAGPipeline
from src.assistant.services.video_processing import parse_ocr_text_to_qa


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


def test_frontend_display():
    """测试前端展示格式"""
    print("=== 测试前端展示格式 ===")
    
    # 模拟视频分析结果
    mock_analysis_results = [
        {
            "question": "下列关于Python的说法，错误的是？",
            "options": ["A. Python是开源的", "B. Python是跨平台的", "C. Python是面向对象的", "D. Python是编译型语言"],
            "answer": {
                "raw": {
                    "type": "single_choice",
                    "final_answer": "D. Python是编译型语言",
                    "confidence": 0.95,
                    "brief_rationale": "Python是一种解释型语言，而不是编译型语言。"
                },
                "contexts": [
                    {
                        "doc_id": "python_guide.pdf",
                        "text": "Python是一种解释型、面向对象、动态数据类型的高级程序设计语言。Python由Guido van Rossum于1989年发明，第一个公开发行版发行于1991年。"
                    }
                ]
            }
        },
        {
            "question": "哪个选项不是Python的保留字？",
            "options": ["A) class", "B) def", "C) for", "D) main"],
            "answer": {
                "raw": {
                    "type": "single_choice",
                    "final_answer": "D) main",
                    "confidence": 0.85,
                    "brief_rationale": "main不是Python的保留字，而class、def、for都是Python的保留字。"
                },
                "contexts": [
                    {
                        "doc_id": "python_keywords.docx",
                        "text": "Python的保留字包括：and, as, assert, break, class, continue, def, del, elif, else, except, exec, finally, for, from, global, if, import, in, is, lambda, not, or, pass, print, raise, return, try, while, with, yield"
                    }
                ]
            }
        }
    ]
    
    # 格式化并显示每个答案
    for i, result in enumerate(mock_analysis_results, 1):
        formatted_answer = format_answer_for_frontend(
            question_number=i,
            question=result["question"],
            options=result["options"],
            answer_data=result["answer"]
        )
        print(formatted_answer)
        print("-" * 50)


if __name__ == "__main__":
    test_frontend_display()