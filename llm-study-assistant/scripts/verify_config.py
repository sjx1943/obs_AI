#!/usr/bin/env python3
"""
验证更新后的模型和RAG配置是否正常工作
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.assistant.services.rag import RAGPipeline

def main():
    print("=== 验证更新后的配置 ===")
    
    # 加载环境变量
    load_dotenv()
    
    # 显示当前配置
    print(f"当前模型: {os.getenv('LLM_MODEL')}")
    print(f"RAG配置 - TOP_K: {os.getenv('TOP_K')}, CHUNK_SIZE: {os.getenv('CHUNK_SIZE')}, CHUNK_OVERLAP: {os.getenv('CHUNK_OVERLAP')}")
    
    # 初始化RAG管道
    try:
        print("\n初始化RAG管道...")
        rag = RAGPipeline()
        print("✓ RAG管道初始化成功")
        
        # 测试简单问题
        print("\n测试简单问题...")
        test_question = "公司自助密码重置门户的网址是什么？"
        result = rag.solve(qtype="subjective", question=test_question)
        
        print(f"问题: {test_question}")
        print(f"回答: {result.get('final_answer', '无回答')}")
        print("\n✓ 配置验证完成，系统运行正常")
        
    except Exception as e:
        print(f"\n✗ 配置验证失败: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())