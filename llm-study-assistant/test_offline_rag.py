#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
离线测试脚本
验证RAG功能，使用本地模型避免网络问题
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.assistant.services.rag import RAGPipeline
from src.assistant.services.video_processing import parse_ocr_text_to_qa
import time


def test_offline_rag():
    """测试离线RAG功能"""
    print("=== 测试离线RAG功能 ===")
    
    # 初始化RAG管道
    rag_pipeline = RAGPipeline()
    
    # 检查模型状态
    print("检查模型状态...")
    status = rag_pipeline.get_status()
    print(f"LLM可用: {status['llm_available']}")
    print(f"LLM模型: {status['llm_model']}")
    print(f"嵌入模型可用: {status['embedding_available']}")
    print(f"嵌入模型: {status['embedding_model']}")
    print(f"索引可用: {status['index_available']}")
    
    # 测试问题分类和解答
    print("\n测试问题分类和解答...")
    
    # 测试问题
    test_questions = [
        {
            "question": "下列关于Python的说法，错误的是？",
            "options": ["A. Python是开源的", "B. Python是跨平台的", "C. Python是面向对象的", "D. Python是编译型语言"]
        },
        {
            "question": "哪个选项不是Python的保留字？",
            "options": ["A) class", "B) def", "C) for", "D) main"]
        }
    ]
    
    for i, q in enumerate(test_questions, 1):
        print(f"\n问题 {i}: {q['question']}")
        print(f"选项: {q['options']}")
        
        # 分类问题
        qtype = rag_pipeline.classify(q["question"], q.get("options"), is_video_content=True)
        print(f"问题类型: {qtype}")
        
        # 解答问题
        result = rag_pipeline.solve(qtype=qtype, question=q["question"], options=q.get("options"), top_k=3)
        print(f"解答结果: {result['raw']}")


if __name__ == "__main__":
    test_offline_rag()