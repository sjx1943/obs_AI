#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本：比较原始RAGPipeline和优化后的OptimizedRAGPipeline效果
"""

import os
import sys
import json
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.assistant.services.rag import RAGPipeline
from src.assistant.services.rag_optimized import OptimizedRAGPipeline

def calculate_keyword_match(answer_text, keywords):
    """
    计算回答中匹配关键词的比例
    """
    if not keywords or not answer_text:
        return 0.0
    
    matched_keywords = [kw for kw in keywords if kw.lower() in answer_text.lower()]
    return len(matched_keywords) / len(keywords)

def test_rag_comparison():
    """测试RAG效果对比"""
    print("=== RAG效果对比测试 ===")
    
    # 加载环境变量
    load_dotenv()
    
    # 初始化两个RAG管道
    original_rag = RAGPipeline()
    optimized_rag = OptimizedRAGPipeline()
    
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
        
        # 提取回答文本
        original_answer_text = ""
        if isinstance(original_result['raw'], dict) and 'final_answer' in original_result['raw']:
            original_answer_text = str(original_result['raw']['final_answer'])
        elif 'final_answer' in original_result:
            original_answer_text = str(original_result['final_answer'])
        else:
            original_answer_text = str(original_result)
        
        original_accuracy = calculate_keyword_match(original_answer_text, test_q['keywords'])
        print(f"回答: {original_answer_text}")
        print(f"关键词匹配度: {original_accuracy:.2%}")
        
        # 使用优化后的OptimizedRAGPipeline
        print("\n[优化后的OptimizedRAGPipeline]")
        optimized_result = optimized_rag.solve(
            qtype=test_q['type'],
            question=test_q['question']
        )
        
        # 提取回答文本
        optimized_answer_text = ""
        if isinstance(optimized_result['raw'], dict) and 'final_answer' in optimized_result['raw']:
            optimized_answer_text = str(optimized_result['raw']['final_answer'])
        elif 'final_answer' in optimized_result:
            optimized_answer_text = str(optimized_result['final_answer'])
        else:
            optimized_answer_text = str(optimized_result)
        
        optimized_accuracy = calculate_keyword_match(optimized_answer_text, test_q['keywords'])
        print(f"回答: {optimized_answer_text}")
        print(f"关键词匹配度: {optimized_accuracy:.2%}")
        
        # 记录结果
        comparison_results.append({
            "question": test_q['question'],
            "keywords": test_q['keywords'],
            "original_accuracy": original_accuracy,
            "optimized_accuracy": optimized_accuracy,
            "improvement": optimized_accuracy - original_accuracy
        })
    
    # 输出汇总结果
    print("\n=== 汇总结果 ===")
    total_original = sum(r['original_accuracy'] for r in comparison_results)
    total_optimized = sum(r['optimized_accuracy'] for r in comparison_results)
    avg_original = total_original / len(comparison_results)
    avg_optimized = total_optimized / len(comparison_results)
    
    print(f"原始RAGPipeline平均准确率: {avg_original:.2%}")
    print(f"优化后RAGPipeline平均准确率: {avg_optimized:.2%}")
    print(f"平均提升: {avg_optimized - avg_original:.2%}")
    
    # 详细对比
    print("\n=== 详细对比 ===")
    for result in comparison_results:
        print(f"\n问题: {result['question']}")
        print(f"  原始准确率: {result['original_accuracy']:.2%}")
        print(f"  优化后准确率: {result['optimized_accuracy']:.2%}")
        print(f"  提升: {result['improvement']:.2%}")
    
    return True

def main():
    """主函数"""
    print("开始RAG效果对比测试...")
    
    success = test_rag_comparison()
    
    if success:
        print("\n=== 测试完成 ===")
        print("RAG效果对比测试已完成，结果如上所示。")
    else:
        print("\n=== 测试失败 ===")

if __name__ == "__main__":
    main()