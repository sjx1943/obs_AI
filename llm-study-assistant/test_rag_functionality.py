#!/usr/bin/env python3
"""
测试RAG功能的脚本
"""

import requests
import os
import time

# API基础URL
BASE_URL = "http://localhost:8000/api"

def check_health():
    """检查服务健康状态"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("Health Check:", response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def upload_document(file_path):
    """上传文档到知识库"""
    try:
        with open(file_path, 'rb') as f:
            files = {'files': (os.path.basename(file_path), f, 'text/markdown')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
            result = response.json()
            print("Upload Result:", result)
            return response.status_code == 200
    except Exception as e:
        print(f"Upload failed: {e}")
        return False

def ask_question(question, qtype="subjective", options=None, top_k=5):
    """向RAG系统提问"""
    try:
        payload = {
            "type": qtype,
            "question": question,
            "top_k": top_k
        }
        if options:
            payload["options"] = options
            
        response = requests.post(f"{BASE_URL}/ask", json=payload)
        result = response.json()
        print(f"Question: {question}")
        print("Answer:", result)
        return response.status_code == 200
    except Exception as e:
        print(f"Question failed: {e}")
        return False

def get_knowledge_stats():
    """获取知识库统计信息"""
    try:
        response = requests.get(f"{BASE_URL}/knowledge/stats")
        result = response.json()
        print("Knowledge Stats:", result)
        return response.status_code == 200
    except Exception as e:
        print(f"Stats retrieval failed: {e}")
        return False

def main():
    print("开始测试RAG功能...")
    
    # 1. 检查服务健康状态
    print("\n1. 检查服务健康状态")
    if not check_health():
        print("服务未运行，请先启动服务")
        return
    
    # 2. 获取初始知识库统计
    print("\n2. 获取初始知识库统计")
    get_knowledge_stats()
    
    # 3. 上传测试文档
    print("\n3. 上传测试文档")
    test_docs = [
        "/Users/sgcc-work/IdeaProjects/obs_AI/llm-study-assistant/it_support_knowledge_base.md",
        "/Users/sgcc-work/IdeaProjects/obs_AI/llm-study-assistant/test_knowledge_document.md"
    ]
    
    for doc_path in test_docs:
        if os.path.exists(doc_path):
            print(f"上传文档: {doc_path}")
            upload_document(doc_path)
            time.sleep(2)  # 等待处理完成
    
    # 4. 再次获取知识库统计
    print("\n4. 获取更新后的知识库统计")
    time.sleep(3)  # 等待索引完成
    get_knowledge_stats()
    
    # 5. 测试提问功能
    print("\n5. 测试提问功能")
    test_questions = [
        {
            "question": "公司自助密码重置门户的网址是什么？",
            "type": "single_choice"
        },
        {
            "question": "Python有哪些保留字？",
            "type": "subjective"
        },
        {
            "question": "列表和元组有什么区别？",
            "type": "subjective"
        }
    ]
    
    for q in test_questions:
        print(f"\n测试问题: {q['question']}")
        ask_question(q["question"], qtype=q["type"])
        time.sleep(2)
    
    print("\nRAG功能测试完成!")

if __name__ == "__main__":
    main()