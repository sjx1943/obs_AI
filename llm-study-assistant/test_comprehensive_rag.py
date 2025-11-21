#!/usr/bin/env python3
"""
全面测试RAG功能的脚本，包括问题回答准确性和整体功能验证
"""

import requests
import os
import time
import json

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
            return response.status_code == 200, result
    except Exception as e:
        print(f"Upload failed: {e}")
        return False, None

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
        return response.status_code == 200, result
    except Exception as e:
        print(f"Question failed: {e}")
        return False, None

def get_knowledge_stats():
    """获取知识库统计信息"""
    try:
        response = requests.get(f"{BASE_URL}/knowledge/stats")
        result = response.json()
        print("Knowledge Stats:", result)
        return response.status_code == 200, result
    except Exception as e:
        print(f"Stats retrieval failed: {e}")
        return False, None

def evaluate_answer_accuracy(question, expected_keywords, rag_response):
    """评估回答准确性（基于关键词匹配）"""
    try:
        # 提取回答内容
        if "raw" in rag_response and "final_answer" in rag_response["raw"]:
            answer = rag_response["raw"]["final_answer"]
        elif "raw" in rag_response and "answer" in rag_response["raw"]:
            answer = str(rag_response["raw"]["answer"])
        else:
            answer = str(rag_response)
        
        # 转换为小写进行比较
        answer_lower = answer.lower()
        keywords_found = [keyword for keyword in expected_keywords if keyword.lower() in answer_lower]
        
        accuracy = len(keywords_found) / len(expected_keywords) if expected_keywords else 0
        return accuracy, keywords_found
    except Exception as e:
        print(f"Accuracy evaluation failed: {e}")
        return 0, []

def main():
    print("开始全面测试RAG功能...")
    
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
    
    uploaded_files = []
    for doc_path in test_docs:
        if os.path.exists(doc_path):
            print(f"上传文档: {doc_path}")
            success, result = upload_document(doc_path)
            if success:
                uploaded_files.append((doc_path, result))
            time.sleep(2)  # 等待处理完成
    
    # 4. 再次获取知识库统计
    print("\n4. 获取更新后的知识库统计")
    time.sleep(3)  # 等待索引完成
    get_knowledge_stats()
    
    # 5. 测试提问功能和准确性
    print("\n5. 测试提问功能和准确性")
    
    # 定义测试用例（问题，预期关键词，问题类型）
    test_cases = [
        {
            "question": "公司自助密码重置门户的网址是什么？",
            "type": "single_choice",
            "expected_keywords": ["portal.example.com", "密码重置"]
        },
        {
            "question": "Python有哪些保留字？",
            "type": "subjective",
            "expected_keywords": ["class", "def", "for", "while", "if", "else"]
        },
        {
            "question": "列表和元组有什么区别？",
            "type": "subjective",
            "expected_keywords": ["可变", "不可变", "方括号", "圆括号"]
        },
        {
            "question": "如何申请安装新软件？",
            "type": "subjective",
            "expected_keywords": ["服务台", "工单", "审批"]
        }
    ]
    
    results = []
    for i, case in enumerate(test_cases):
        print(f"\n测试问题 {i+1}: {case['question']}")
        success, response = ask_question(case["question"], qtype=case["type"])
        if success and response:
            accuracy, found_keywords = evaluate_answer_accuracy(
                case["question"], 
                case["expected_keywords"], 
                response
            )
            results.append({
                "question": case["question"],
                "success": success,
                "accuracy": accuracy,
                "found_keywords": found_keywords,
                "expected_keywords": case["expected_keywords"]
            })
            print(f"准确性评估: {accuracy:.2%} (找到关键词: {found_keywords})")
        else:
            results.append({
                "question": case["question"],
                "success": False,
                "accuracy": 0,
                "found_keywords": [],
                "expected_keywords": case["expected_keywords"]
            })
        time.sleep(2)
    
    # 6. 输出测试总结
    print("\n=== 测试总结 ===")
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r["success"])
    avg_accuracy = sum(r["accuracy"] for r in results) / total_tests if total_tests > 0 else 0
    
    print(f"总测试数: {total_tests}")
    print(f"成功测试数: {successful_tests}")
    print(f"平均准确性: {avg_accuracy:.2%}")
    
    print("\n详细结果:")
    for result in results:
        print(f"- 问题: {result['question']}")
        print(f"  成功: {result['success']}")
        print(f"  准确性: {result['accuracy']:.2%}")
        print(f"  找到关键词: {result['found_keywords']}")
        print(f"  预期关键词: {result['expected_keywords']}")
        print()
    
    print("\n全面RAG功能测试完成!")

if __name__ == "__main__":
    main()