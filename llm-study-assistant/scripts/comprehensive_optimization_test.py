#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
综合优化测试脚本：协调所有优化测试并生成报告
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

def run_command(command, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            timeout=300  # 5分钟超时
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"
    except Exception as e:
        return False, "", str(e)

def check_ollama_models():
    """检查已安装的Ollama模型"""
    print("检查已安装的Ollama模型...")
    success, stdout, stderr = run_command("curl -s http://localhost:11434/api/tags")
    
    if success:
        try:
            data = json.loads(stdout)
            models = [model['name'] for model in data.get('models', [])]
            print(f"已安装的模型: {', '.join(models)}")
            return models
        except json.JSONDecodeError:
            print("无法解析Ollama模型列表")
            return []
    else:
        print(f"检查Ollama模型失败: {stderr}")
        return []

def run_model_comparison_test():
    """运行模型对比测试"""
    print("\n=== 运行模型对比测试 ===")
    
    # 检查已安装的模型
    installed_models = check_ollama_models()
    
    if not installed_models:
        print("警告: 未检测到已安装的模型，将使用默认模型进行测试")
    
    # 运行模型对比测试脚本
    script_path = os.path.join(os.path.dirname(__file__), 'model_comparison_test.py')
    success, stdout, stderr = run_command(f"python3 {script_path}")
    
    if success:
        print("模型对比测试完成")
        # 尝试读取结果文件
        try:
            with open('model_comparison_results.json', 'r', encoding='utf-8') as f:
                results = json.load(f)
            return results
        except FileNotFoundError:
            print("未找到模型对比测试结果文件")
            return {}
    else:
        print(f"模型对比测试失败: {stderr}")
        return {}

def run_parameter_tuning_test():
    """运行参数调整测试"""
    print("\n=== 运行RAG参数调整测试 ===")
    
    # 运行参数调整测试脚本
    script_path = os.path.join(os.path.dirname(__file__), 'rag_parameter_tuning.py')
    success, stdout, stderr = run_command(f"python3 {script_path}")
    
    if success:
        print("RAG参数调整测试完成")
        # 尝试读取结果文件
        try:
            with open('rag_parameter_tuning_results.json', 'r', encoding='utf-8') as f:
                results = json.load(f)
            return results
        except FileNotFoundError:
            print("未找到参数调整测试结果文件")
            return {}
    else:
        print(f"RAG参数调整测试失败: {stderr}")
        return {}

def run_simple_prompt_test():
    """运行简化提示词测试"""
    print("\n=== 运行简化提示词测试 ===")
    
    # 运行简化提示词测试脚本
    script_path = os.path.join(os.path.dirname(__file__), 'simple_prompt_test.py')
    success, stdout, stderr = run_command(f"python3 {script_path}")
    
    if success:
        print("简化提示词测试完成")
        # 尝试读取结果文件
        try:
            with open('simple_prompt_test_results.json', 'r', encoding='utf-8') as f:
                results = json.load(f)
            return results
        except FileNotFoundError:
            print("未找到简化提示词测试结果文件")
            return {}
    else:
        print(f"简化提示词测试失败: {stderr}")
        return {}

def generate_report(model_results, param_results, prompt_results):
    """生成综合测试报告"""
    print("\n=== 生成综合测试报告 ===")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "model_comparison": model_results,
        "parameter_tuning": param_results,
        "prompt_simplification": prompt_results
    }
    
    # 创建报告摘要
    summary = []
    summary.append("# 综合优化测试报告")
    summary.append(f"生成时间: {report['timestamp']}")
    summary.append("")
    
    # 模型对比测试摘要
    if model_results:
        summary.append("## 模型对比测试结果")
        summary.append("| 模型 | 原始RAG | 优化RAG | 简化RAG |")
        summary.append("|------|---------|---------|---------|")
        
        for model, results in model_results.items():
            original = results.get("原始RAGPipeline", 0)
            optimized = results.get("优化后RAGPipeline", 0)
            simple = results.get("简化版优化RAGPipeline", 0)
            summary.append(f"| {model} | {original:.2%} | {optimized:.2%} | {simple:.2%} |")
        summary.append("")
    
    # 参数调整测试摘要
    if param_results:
        summary.append("## RAG参数调整测试结果")
        summary.append("| 配置名称 | TOP_K | CHUNK_SIZE | CHUNK_OVERLAP | 平均准确率 |")
        summary.append("|----------|-------|------------|---------------|------------|")
        
        # 按准确率排序
        sorted_results = sorted(param_results, key=lambda x: x['average_accuracy'], reverse=True)
        
        for result in sorted_results[:5]:  # 只显示前5个最佳结果
            config = result['config']
            accuracy = result['average_accuracy']
            summary.append(f"| {config['name']} | {config.get('TOP_K', 'N/A')} | {config.get('CHUNK_SIZE', 'N/A')} | {config.get('CHUNK_OVERLAP', 'N/A')} | {accuracy:.2%} |")
        summary.append("")
    
    # 简化提示词测试摘要
    if prompt_results:
        summary.append("## 简化提示词测试结果")
        summary.append("| RAG管道 | 原始提示词 | 简化提示词 | 提升 |")
        summary.append("|---------|------------|------------|------|")
        
        for pipeline, results in prompt_results.items():
            original = results.get("original_prompt", 0)
            simple = results.get("simple_prompt", 0)
            improvement = simple - original
            summary.append(f"| {pipeline} | {original:.2%} | {simple:.2%} | {improvement:+.2%} |")
        summary.append("")
    
    # 生成建议
    summary.append("## 优化建议")
    summary.append("1. 根据测试结果选择最佳模型和RAG管道组合")
    summary.append("2. 调整RAG参数以获得最佳性能")
    summary.append("3. 考虑使用简化版提示词以提高响应速度")
    summary.append("4. 定期重新评估模型性能，随着数据和需求的变化调整配置")
    summary.append("")
    
    # 保存完整报告
    with open('comprehensive_optimization_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 保存摘要报告
    with open('comprehensive_optimization_summary.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary))
    
    # 打印摘要
    print('\n'.join(summary))
    
    return report

def main():
    """主函数"""
    print("开始综合优化测试...")
    
    # 加载环境变量
    load_dotenv()
    
    # 检查Ollama服务是否运行
    print("检查Ollama服务状态...")
    success, _, _ = run_command("curl -s http://localhost:11434/api/tags")
    
    if not success:
        print("警告: Ollama服务未运行，部分测试可能无法正常执行")
        print("请运行 ./scripts/start_ollama.sh 启动Ollama服务")
    
    # 运行各项测试
    model_results = run_model_comparison_test()
    param_results = run_parameter_tuning_test()
    prompt_results = run_simple_prompt_test()
    
    # 生成综合报告
    report = generate_report(model_results, param_results, prompt_results)
    
    print("\n=== 综合优化测试完成 ===")
    print("完整报告已保存到 comprehensive_optimization_report.json")
    print("摘要报告已保存到 comprehensive_optimization_summary.md")

if __name__ == "__main__":
    main()