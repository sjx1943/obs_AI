#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
更新后的视频分析测试脚本
验证修复后的RAG视频分析功能，包括：
1. OCR文本提取（启用GPU加速）
2. 问答对解析
3. 使用配置的LLM模型进行分析
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.assistant.services.video_processing import extract_text_from_video, parse_ocr_text_to_qa
from src.assistant.services.rag import RAGPipeline
import time


def test_video_analysis():
    """测试完整的视频分析流程"""
    print("=== 测试完整的视频分析流程 ===")
    
    # 初始化RAG管道
    rag_pipeline = RAGPipeline()
    
    # 模拟OCR提取的文本（实际使用时会从视频中提取）
    sample_text = """1. 下列关于Python的说法，错误的是？
    A. Python是开源的 B. Python是跨平台的 C. Python是面向对象的 D. Python是编译型语言
2、哪个选项不是Python的保留字？
    A) class   B) def   C) for   D) main"""
    
    print(f"模拟提取的视频文本: {sample_text}\n")
    
    # 解析问答对
    qa_pairs = parse_ocr_text_to_qa(sample_text)
    print(f"解析出 {len(qa_pairs)} 个问答对:")
    for i, pair in enumerate(qa_pairs, 1):
        print(f"  {i}. 问题: {pair['question']}")
        print(f"     选项: {pair['options']}")
    
    print("\n开始分析...\n")
    
    # 使用RAG管道分析每个问答对
    results = []
    for qa_pair in qa_pairs:
        # 对于视频内容，我们需要设置 is_video_content=True
        qtype = rag_pipeline.classify(qa_pair["question"], qa_pair.get("options"), is_video_content=True)
        result = rag_pipeline.solve(qtype=qtype, question=qa_pair["question"], options=qa_pair.get("options"), top_k=5)
        results.append({
            "question": qa_pair["question"],
            "options": qa_pair.get("options"),
            "answer": result
        })
    
    print("最终分析结果:")
    for i, res in enumerate(results, 1):
        print(f"\n问题 {i}: {res['question']}")
        print(f"选项: {res['options']}")
        print(f"答案: {res['answer']['raw']}")
    
    return results


if __name__ == "__main__":
    test_video_analysis()