#!/usr/bin/env python3
"""
测试更新后的模型和RAG配置的问答能力
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.assistant.services.rag import RAGPipeline

def main():
    print("=== 测试更新后的配置问答能力 ===")
    
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
        
        # 测试问题列表
        test_questions = [
            {
                "question": "公司自助密码重置门户的网址是什么？",
                "type": "subjective"
            },
            {
                "question": "Python有哪些保留字？",
                "type": "subjective"
            },
            {
                "question": "如何申请安装新软件？",
                "type": "subjective"
            },
            {
                "question": "列表和元组有什么区别？",
                "type": "subjective"
            }
        ]
        
        # 测试每个问题
        for i, test_q in enumerate(test_questions):
            print(f"\n问题 {i+1}: {test_q['question']}")
            result = rag.solve(qtype=test_q['type'], question=test_q['question'])
            
            if isinstance(result, dict) and 'raw' in result:
                raw_result = result['raw']
                if isinstance(raw_result, dict) and 'final_answer' in raw_result:
                    answer = raw_result['final_answer']
                else:
                    answer = str(raw_result)
            else:
                answer = str(result)
            
            print(f"回答: {answer}")
        
        print("\n✓ 问答测试完成")
        
    except Exception as e:
        print(f"\n✗ 问答测试失败: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())