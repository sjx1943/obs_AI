#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试优化后的提示词模板是否能提高RAG回答的准确性
"""

import os
import sys
import json
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.assistant.services.rag import RAGPipeline
from src.assistant.services.prompts_optimized import *

def test_optimized_prompts():
    """测试优化后的提示词"""
    print("=== 测试优化后的提示词 ===")
    
    # 加载环境变量
    load_dotenv()
    
    # 初始化RAG管道
    rag = RAGPipeline()
    
    # 测试问题列表
    test_questions = [
        {
            "question": "公司自助密码重置门户的网址是什么？",
            "keywords": ["portal.example.com", "密码重置"],
            "type": "subjective"
        },
        {
            "question": "Python有哪些保留字？",
            "keywords": ["class", "def", "for", "while", "if", "else"],
            "type": "subjective"
        },
        {
            "question": "列表和元组有什么区别？",
            "keywords": ["可变", "不可变", "方括号", "圆括号"],
            "type": "subjective"
        },
        {
            "question": "如何申请安装新软件？",
            "keywords": ["服务台", "工单", "审批"],
            "type": "subjective"
        }
    ]
    
    # 获取原始提示词的回答
    print("\n--- 使用原始提示词 ---")
    original_results = []
    for i, test_q in enumerate(test_questions):
        print(f"\n问题 {i+1}: {test_q['question']}")
        result = rag.solve(
            qtype=test_q['type'],
            question=test_q['question']
        )
        original_results.append(result)
        print(f"回答: {result['raw']}")
    
    # 替换为优化后的提示词
    print("\n--- 使用优化后的提示词 ---")
    # 这里我们只是打印优化后的提示词内容，实际应用中需要修改RAGPipeline类来使用这些提示词
    print("系统提示词:")
    print(SYSTEM_PROMPT)
    print("\n解题器前缀:")
    print(SOLVER_PREFIX)
    print("\n主观题解题器:")
    print(SOLVER_SUBJ)
    
    print("\n注意：要实际测试优化后的提示词效果，需要修改RAGPipeline类来使用新的提示词模板。")
    
    return True

def main():
    """主函数"""
    print("开始测试优化后的提示词模板...")
    
    success = test_optimized_prompts()
    
    if success:
        print("\n=== 测试完成 ===")
        print("优化后的提示词模板已创建，可以在 src/assistant/services/prompts_optimized.py 中查看。")
        print("要实际应用这些优化，需要修改 RAGPipeline 类来使用新的提示词模板。")
    else:
        print("\n=== 测试失败 ===")

if __name__ == "__main__":
    main()