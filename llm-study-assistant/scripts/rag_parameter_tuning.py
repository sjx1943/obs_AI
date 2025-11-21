#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG参数调整测试脚本：测试不同参数组合对RAG流程的影响
"""

import os
import sys
import json
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from src.assistant.services.rag_optimized import OptimizedRAGPipeline

# 保存原始环境变量
original_env_vars = {}

def set_rag_parameters(top_k=None, chunk_size=None, chunk_overlap=None):
    """设置RAG参数"""
    global original_env_vars
    
    # 保存原始环境变量
    original_env_vars['TOP_K'] = os.getenv('TOP_K', '')
    original_env_vars['CHUNK_SIZE'] = os.getenv('CHUNK_SIZE', '')
    original_env_vars['CHUNK_OVERLAP'] = os.getenv('CHUNK_OVERLAP', '')
    
    # 设置新的参数
    if top_k is not None:
        os.environ['TOP_K'] = str(top_k)
    if chunk_size is not None:
        os.environ['CHUNK_SIZE'] = str(chunk_size)
    if chunk_overlap is not None:
        os.environ['CHUNK_OVERLAP'] = str(chunk_overlap)
    
    print(f"已设置RAG参数: TOP_K={top_k}, CHUNK_SIZE={chunk_size}, CHUNK_OVERLAP={chunk_overlap}")

def restore_original_parameters():
    """恢复原始参数设置"""
    global original_env_vars
    for key, value in original_env_vars.items():
        if value:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]
    print("已恢复原始RAG参数设置")

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

def test_with_parameters(param_config, test_questions):
    """使用指定参数配置测试RAG流程"""
    print(f"\n测试参数配置: {param_config}")
    
    # 设置参数
    set_rag_parameters(
        top_k=param_config.get('TOP_K'),
        chunk_size=param_config.get('CHUNK_SIZE'),
        chunk_overlap=param_config.get('CHUNK_OVERLAP')
    )
    
    # 重新初始化RAG管道以使用新参数
    rag = OptimizedRAGPipeline()
    
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
    
    # 恢复原始参数设置
    restore_original_parameters()
    
    return avg_accuracy

def parameter_tuning_test():
    """参数调整测试"""
    print("=== RAG参数调整测试 ===")
    
    # 加载环境变量
    load_dotenv()
    
    # 参数配置列表
    param_configs = [
        # 默认参数
        {
            "name": "默认参数",
            "TOP_K": 5,
            "CHUNK_SIZE": 500,
            "CHUNK_OVERLAP": 100
        },
        # 不同TOP_K值
        {
            "name": "TOP_K=3",
            "TOP_K": 3,
            "CHUNK_SIZE": 500,
            "CHUNK_OVERLAP": 100
        },
        {
            "name": "TOP_K=10",
            "TOP_K": 10,
            "CHUNK_SIZE": 500,
            "CHUNK_OVERLAP": 100
        },
        # 不同CHUNK_SIZE值
        {
            "name": "CHUNK_SIZE=250",
            "TOP_K": 5,
            "CHUNK_SIZE": 250,
            "CHUNK_OVERLAP": 50
        },
        {
            "name": "CHUNK_SIZE=1000",
            "TOP_K": 5,
            "CHUNK_SIZE": 1000,
            "CHUNK_OVERLAP": 200
        },
        # 不同CHUNK_OVERLAP值
        {
            "name": "CHUNK_OVERLAP=50",
            "TOP_K": 5,
            "CHUNK_SIZE": 500,
            "CHUNK_OVERLAP": 50
        },
        {
            "name": "CHUNK_OVERLAP=200",
            "TOP_K": 5,
            "CHUNK_SIZE": 500,
            "CHUNK_OVERLAP": 200
        },
        # 综合调整
        {
            "name": "综合优化",
            "TOP_K": 3,
            "CHUNK_SIZE": 250,
            "CHUNK_OVERLAP": 50
        }
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
    
    # 存储结果
    tuning_results = []
    
    # 测试每种参数配置
    for config in param_configs:
        avg_accuracy = test_with_parameters(config, test_questions)
        result = {
            "config": config,
            "average_accuracy": avg_accuracy
        }
        tuning_results.append(result)
    
    # 输出汇总结果
    print("\n=== RAG参数调整测试结果 ===")
    print(f"{'配置名称':<15} {'TOP_K':<8} {'CHUNK_SIZE':<12} {'CHUNK_OVERLAP':<15} {'平均准确率':<12}")
    print("-" * 65)
    
    best_config = None
    best_accuracy = 0.0
    
    for result in tuning_results:
        config = result['config']
        avg_accuracy = result['average_accuracy']
        print(f"{config['name']:<15} {config.get('TOP_K', 'N/A'):<8} {config.get('CHUNK_SIZE', 'N/A'):<12} {config.get('CHUNK_OVERLAP', 'N/A'):<15} {avg_accuracy:<12.2%}")
        
        if avg_accuracy > best_accuracy:
            best_accuracy = avg_accuracy
            best_config = config
    
    if best_config:
        print(f"\n最佳参数配置:")
        print(f"  名称: {best_config['name']}")
        print(f"  TOP_K: {best_config.get('TOP_K', 'N/A')}")
        print(f"  CHUNK_SIZE: {best_config.get('CHUNK_SIZE', 'N/A')}")
        print(f"  CHUNK_OVERLAP: {best_config.get('CHUNK_OVERLAP', 'N/A')}")
        print(f"  平均准确率: {best_accuracy:.2%}")
    else:
        print(f"\n未找到有效的参数配置，所有配置的平均准确率均为0.00%")
    
    return tuning_results

def main():
    """主函数"""
    print("开始RAG参数调整测试...")
    
    results = parameter_tuning_test()
    
    # 保存结果到文件
    with open('rag_parameter_tuning_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n=== 测试完成 ===")
    print("RAG参数调整测试已完成，结果已保存到 rag_parameter_tuning_results.json")

if __name__ == "__main__":
    main()