#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本：比较原始RAGPipeline、优化版RAGPipeline和简化版优化RAGPipeline效果
"""

import os
import sys
import json
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.assistant.services.rag import RAGPipeline
from src.assistant.services.rag_optimized import OptimizedRAGPipeline
from src.assistant.services.rag_simple_optimized import SimpleOptimizedRAGPipeline

def calculate_keyword_match(answer_text, keywords):
    """
    计算回答中匹配关键词的比例
    """
    if not keywords or not answer_text:
        return 0.0
    
    matched_keywords = [kw for kw in keywords if kw.lower() in answer_text.lower()]
    return len(matched_keywords) / len(keywords)

def extract_answer_text(result):
    """
    从结果中提取回答文本
    """
    answer_text = ""
    if isinstance(result['raw'], dict) and 'final_answer' in result['raw']:
        answer_text = str(result['raw']['final_answer'])
    elif 'final_answer' in result:
        answer_text = str(result['final_answer'])
    else:
        answer_text = str(result)
    return answer_text

def test_rag_three_way():
    """测试三种RAG效果对比"""
    print("=== 三种RAG效果对比测试 ===")
    
    # 加载环境变量
    load_dotenv()
    
    # 初始化三个RAG管道
    original_rag = RAGPipeline()
    optimized_rag = OptimizedRAGPipeline()
    simple_optimized_rag = SimpleOptimizedRAGPipeline()
    
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
    
    # 存储结果
    comparison_results = []
    
    # 测试每个问题
    for i, test_q in enumerate(test_questions):
        print(f"\n--- 问题 {i+1}: {test_q['question']} ---")
        
        # 使用原始RAGPipeline
        print("\n[原始RAGPipeline]")
        original_result = original_rag.solve(
            qtype=test_q['type'],
            question=test_q['question']
        )
        original_answer_text = extract_answer_text(original_result)
        original_accuracy = calculate_keyword_match(original_answer_text, test_q['keywords'])
        print(f"回答: {original_answer_text}")
        print(f"关键词匹配度: {original_accuracy:.2%}")
        
        # 使用优化后的OptimizedRAGPipeline
        print("\n[优化后的OptimizedRAGPipeline]")
        optimized_result = optimized_rag.solve(
            qtype=test_q['type'],
            question=test_q['question']
        )
        optimized_answer_text = extract_answer_text(optimized_result)
        optimized_accuracy = calculate_keyword_match(optimized_answer_text, test_q['keywords'])
        print(f"回答: {optimized_answer_text}")
        print(f"关键词匹配度: {optimized_accuracy:.2%}")
        
        # 使用简化版优化的SimpleOptimizedRAGPipeline
        print("\n[简化版优化的SimpleOptimizedRAGPipeline]")
        simple_result = simple_optimized_rag.solve(
            qtype=test_q['type'],
            question=test_q['question']
        )
        simple_answer_text = extract_answer_text(simple_result)
        simple_accuracy = calculate_keyword_match(simple_answer_text, test_q['keywords'])
        print(f"回答: {simple_answer_text}")
        print(f"关键词匹配度: {simple_accuracy:.2%}")
        
        # 记录结果
        comparison_results.append({
            "question": test_q['question'],
            "keywords": test_q['keywords'],
            "original_accuracy": original_accuracy,
            "optimized_accuracy": optimized_accuracy,
            "simple_optimized_accuracy": simple_accuracy
        })
    
    # 输出汇总结果
    print("\n=== 汇总结果 ===")
    total_original = sum(r['original_accuracy'] for r in comparison_results)
    total_optimized = sum(r['optimized_accuracy'] for r in comparison_results)
    total_simple = sum(r['simple_optimized_accuracy'] for r in comparison_results)
    
    avg_original = total_original / len(comparison_results)
    avg_optimized = total_optimized / len(comparison_results)
    avg_simple = total_simple / len(comparison_results)
    
    print(f"原始RAGPipeline平均准确率: {avg_original:.2%}")
    print(f"优化后RAGPipeline平均准确率: {avg_optimized:.2%}")
    print(f"简化版优化RAGPipeline平均准确率: {avg_simple:.2%}")
    
    # 找出最佳方法
    methods = [
        ("原始RAGPipeline", avg_original),
        ("优化后RAGPipeline", avg_optimized),
        ("简化版优化RAGPipeline", avg_simple)
    ]
    best_method = max(methods, key=lambda x: x[1])
    print(f"\n最佳方法: {best_method[0]} (准确率: {best_method[1]:.2%})")
    
    # 详细对比
    print("\n=== 详细对比 ===")
    for result in comparison_results:
        print(f"\n问题: {result['question']}")
        print(f"  原始准确率: {result['original_accuracy']:.2%}")
        print(f"  优化后准确率: {result['optimized_accuracy']:.2%}")
        print(f"  简化版优化准确率: {result['simple_optimized_accuracy']:.2%}")
    
    return True

def main():
    """主函数"""
    print("开始三种RAG效果对比测试...")
    
    success = test_rag_three_way()
    
    if success:
        print("\n=== 测试完成 ===")
        print("三种RAG效果对比测试已完成，结果如上所示。")
    else:
        print("\n=== 测试失败 ===")

if __name__ == "__main__":
    main()