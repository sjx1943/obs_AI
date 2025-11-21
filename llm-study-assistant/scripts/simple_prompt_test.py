#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化提示词模板测试脚本：测试更简单的提示词对模型表现的影响
"""

import os
import sys
import json
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from src.assistant.services.rag import RAGPipeline
from src.assistant.services.rag_optimized import OptimizedRAGPipeline

# 保存原始提示词
original_prompts = {}

def backup_original_prompts():
    """备份原始提示词"""
    global original_prompts
    
    # 导入原始提示词
    from src.assistant.services.prompts import SOLVER_SINGLE_CHOICE as orig_single
    from src.assistant.services.prompts import SOLVER_MULTI_CHOICE as orig_multi
    from src.assistant.services.prompts import SOLVER_TF as orig_tf
    from src.assistant.services.prompts import SOLVER_SUBJECTIVE as orig_subj
    
    original_prompts = {
        'single': orig_single,
        'multi': orig_multi,
        'tf': orig_tf,
        'subj': orig_subj
    }

def create_simple_prompts():
    """创建简化版提示词"""
    return {
        'single': """你是一个智能助手。请根据以下检索到的上下文信息，简洁地回答选择题。

题目类型：单项选择题
题目：{question}
选项：{options}

检索到的上下文信息：
{context}

请直接给出答案选项字母（A/B/C/D）：""",
        
        'multi': """你是一个智能助手。请根据以下检索到的上下文信息，简洁地回答多选题。

题目类型：多项选择题
题目：{question}
选项：{options}

检索到的上下文信息：
{context}

请直接给出答案选项字母（例如：A,B,C）：""",
        
        'tf': """你是一个智能助手。请根据以下检索到的上下文信息，简洁地回答判断题。

题目类型：判断题
题目：{question}

检索到的上下文信息：
{context}

请直接回答"正确"或"错误"：""",
        
        'subj': """你是一个智能助手。请根据以下检索到的上下文信息，简洁地回答主观题。

题目：{question}

检索到的上下文信息：
{context}

请直接给出答案："""
    }

def patch_prompts(simple_prompts):
    """替换提示词"""
    import src.assistant.services.prompts as prompts_module
    
    # 替换提示词
    prompts_module.SOLVER_SINGLE_CHOICE = simple_prompts['single']
    prompts_module.SOLVER_MULTI_CHOICE = simple_prompts['multi']
    prompts_module.SOLVER_TF = simple_prompts['tf']
    prompts_module.SOLVER_SUBJECTIVE = simple_prompts['subj']
    
    print("已应用简化版提示词模板")

def restore_original_prompts_in_module():
    """恢复原始提示词"""
    import src.assistant.services.prompts as prompts_module
    
    # 恢复原始提示词
    prompts_module.SOLVER_SINGLE_CHOICE = original_prompts['single']
    prompts_module.SOLVER_MULTI_CHOICE = original_prompts['multi']
    prompts_module.SOLVER_TF = original_prompts['tf']
    prompts_module.SOLVER_SUBJECTIVE = original_prompts['subj']
    
    print("已恢复原始提示词模板")

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

def test_prompt_style(rag_pipeline, pipeline_name, test_questions, is_simple=False):
    """测试提示词风格"""
    print(f"\n[{pipeline_name} - {'简化提示词' if is_simple else '原始提示词'}]")
    
    if is_simple:
        # 应用简化提示词
        simple_prompts = create_simple_prompts()
        patch_prompts(simple_prompts)
    
    # 重新初始化RAG管道
    if pipeline_name == "原始RAGPipeline":
        rag = RAGPipeline()
    elif pipeline_name == "优化后RAGPipeline":
        rag = OptimizedRAGPipeline()
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
    
    if is_simple:
        # 恢复原始提示词
        restore_original_prompts_in_module()
    
    return avg_accuracy

def simple_prompt_test():
    """简化提示词测试"""
    print("=== 简化提示词测试 ===")
    
    # 备份原始提示词
    backup_original_prompts()
    
    # 加载环境变量
    load_dotenv()
    
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
        "优化后RAGPipeline"
    ]
    
    # 存储结果
    test_results = {}
    
    # 测试每种RAG管道
    for pipeline in rag_pipelines:
        print(f"\n--- 测试 {pipeline} ---")
        
        # 测试原始提示词
        original_acc = test_prompt_style(None, pipeline, test_questions, is_simple=False)
        
        # 测试简化提示词
        simple_acc = test_prompt_style(None, pipeline, test_questions, is_simple=True)
        
        test_results[pipeline] = {
            "original_prompt": original_acc,
            "simple_prompt": simple_acc
        }
    
    # 输出汇总结果
    print("\n=== 简化提示词测试结果 ===")
    print(f"{'RAG管道':<20} {'原始提示词':<12} {'简化提示词':<12} {'提升':<10}")
    print("-" * 54)
    
    for pipeline in rag_pipelines:
        original_acc = test_results[pipeline]["original_prompt"]
        simple_acc = test_results[pipeline]["simple_prompt"]
        improvement = simple_acc - original_acc
        print(f"{pipeline:<20} {original_acc:<12.2%} {simple_acc:<12.2%} {improvement:+.2%}")
    
    return test_results

def main():
    """主函数"""
    print("开始简化提示词测试...")
    
    results = simple_prompt_test()
    
    # 保存结果到文件
    with open('simple_prompt_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n=== 测试完成 ===")
    print("简化提示词测试已完成，结果已保存到 simple_prompt_test_results.json")

if __name__ == "__main__":
    main()