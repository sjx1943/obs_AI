#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模型对比测试脚本：测试不同LLM模型在相同RAG流程下的表现
"""

import os
import sys
import json
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from src.assistant.services.rag import RAGPipeline
from src.assistant.services.rag_optimized import OptimizedRAGPipeline
from src.assistant.services.rag_simple_optimized import SimpleOptimizedRAGPipeline

# 保存原始环境变量
original_env_vars = {}

def set_model(model_name):
    """设置要测试的模型"""
    global original_env_vars
    # 保存原始环境变量
    original_env_vars['LLM_MODEL'] = os.getenv('LLM_MODEL', '')
    
    # 设置新的模型
    os.environ['LLM_MODEL'] = model_name
    print(f"已设置模型: {model_name}")

def restore_original_model():
    """恢复原始模型设置"""
    global original_env_vars
    if 'LLM_MODEL' in original_env_vars:
        os.environ['LLM_MODEL'] = original_env_vars['LLM_MODEL']
        print(f"已恢复原始模型设置: {original_env_vars['LLM_MODEL']}")

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

def test_single_model(model_name, rag_pipeline, pipeline_name, test_questions):
    """测试单个模型在指定RAG流程下的表现"""
    print(f"\n[{pipeline_name} - {model_name}]")
    
    # 设置模型
    set_model(model_name)
    
    # 重新初始化RAG管道以使用新模型
    if pipeline_name == "原始RAGPipeline":
        rag = RAGPipeline()
    elif pipeline_name == "优化后RAGPipeline":
        rag = OptimizedRAGPipeline()
    elif pipeline_name == "简化版优化RAGPipeline":
        rag = SimpleOptimizedRAGPipeline()
    else:
        print(f"未知的RAG管道: {pipeline_name}")
        return 0.0
    
    total_accuracy = 0.0
    question_count = len(test_questions)
    
    # 测试每个问题
    for i, test_q in enumerate(test_questions):
        result = rag.solve(
            qtype=test_q['type'],
            question=test_q['question']
        )
        answer_text = extract_answer_text(result)
        accuracy = calculate_keyword_match(answer_text, test_q['keywords'])
        total_accuracy += accuracy
        print(f"  问题 {i+1}: {accuracy:.2%}")
    
    avg_accuracy = total_accuracy / question_count if question_count > 0 else 0.0
    print(f"  平均准确率: {avg_accuracy:.2%}")
    
    # 恢复原始模型设置
    restore_original_model()
    
    return avg_accuracy

def model_comparison_test():
    """模型对比测试"""
    print("=== 模型对比测试 ===")
    
    # 加载环境变量
    load_dotenv()
    
    # 测试模型列表
    test_models = [
        "qwen2.5:3b",
        "qwen2.5:3b-instruct-q4_0",
        "llama3.2:3b-instruct-q4_0",
        "gemma2:2b-instruct-q4_0"
    ]
    
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
    
    # RAG管道列表
    rag_pipelines = [
        "原始RAGPipeline",
        "优化后RAGPipeline",
        "简化版优化RAGPipeline"
    ]
    
    # 存储结果
    comparison_results = {}
    
    # 测试每种模型和每种RAG管道的组合
    for model in test_models:
        print(f"\n--- 测试模型: {model} ---")
        comparison_results[model] = {}
        
        for pipeline in rag_pipelines:
            avg_accuracy = test_single_model(model, None, pipeline, test_questions)
            comparison_results[model][pipeline] = avg_accuracy
    
    # 输出汇总结果
    print("\n=== 模型对比测试结果 ===")
    print(f"{'模型':<20} {'原始RAG':<12} {'优化RAG':<12} {'简化RAG':<12}")
    print("-" * 56)
    
    best_overall = None
    best_accuracy = 0.0
    
    for model in test_models:
        original_acc = comparison_results[model]["原始RAGPipeline"]
        optimized_acc = comparison_results[model]["优化后RAGPipeline"]
        simple_acc = comparison_results[model]["简化版优化RAGPipeline"]
        
        print(f"{model:<20} {original_acc:<12.2%} {optimized_acc:<12.2%} {simple_acc:<12.2%}")
        
        # 检查是否有更好的组合
        max_acc = max(original_acc, optimized_acc, simple_acc)
        if max_acc > best_accuracy:
            best_accuracy = max_acc
            if max_acc == original_acc:
                best_overall = f"{model} - 原始RAGPipeline"
            elif max_acc == optimized_acc:
                best_overall = f"{model} - 优化后RAGPipeline"
            else:
                best_overall = f"{model} - 简化版优化RAGPipeline"
    
    print(f"\n最佳组合: {best_overall} (准确率: {best_accuracy:.2%})")
    
    return comparison_results

def main():
    """主函数"""
    print("开始模型对比测试...")
    
    results = model_comparison_test()
    
    # 保存结果到文件
    with open('model_comparison_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n=== 测试完成 ===")
    print("模型对比测试已完成，结果已保存到 model_comparison_results.json")

if __name__ == "__main__":
    main()