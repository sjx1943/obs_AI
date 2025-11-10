#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试RAG服务中的视频分析功能
"""

import sys
import os

# 添加项目路径到sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

# 模拟环境变量
os.environ['DATA_DIR'] = os.path.join(project_root, 'data')

from assistant.services.rag import RAGPipeline

def test_video_analysis_with_text():
    """测试使用文本进行视频分析"""
    print("=== 测试使用文本进行视频分析 ===")
    
    # 创建RAGPipeline实例
    rag_pipeline = RAGPipeline()
    
    # 模拟从视频中提取的文本
    extracted_text = """
    1. 下列关于Python的说法，错误的是？
       A. Python是开源的 B. Python是跨平台的 C. Python是面向对象的 D. Python是编译型语言
    2、哪个选项不是Python的保留字？
       A) class   B) def   C) for   D) main
    """
    
    print("模拟提取的视频文本:")
    print(extracted_text)
    
    # 模拟RAGPipeline中的analyze_video方法
    print("\n开始分析...")
    
    if not extracted_text.strip():
        print("错误: 没有从视频中提取到文本")
        return

    # 导入QA解析函数
    from assistant.services.video_processing import parse_ocr_text_to_qa
    qa_pairs = parse_ocr_text_to_qa(extracted_text)
    
    print(f"\n解析出 {len(qa_pairs)} 个问答对:")
    for i, qa in enumerate(qa_pairs):
        print(f"  {i+1}. 问题: {qa['question']}")
        print(f"     选项: {qa['options']}")
    
    if not qa_pairs:
        # 如果没有解析出问答对，将整个文本作为一个问题
        qa_pairs = [{"question": extracted_text.strip(), "options": None}]
        print("\n未解析出标准问答对，将整个文本作为问题处理")

    # 分析每个问答对
    analysis_results = []
    for i, qa in enumerate(qa_pairs):
        print(f"\n分析问题 {i+1}: {qa['question'][:50]}...")
        
        # 分类问题类型
        qtype = rag_pipeline.classify(qa["question"], qa.get("options"), is_video_content=True)
        print(f"  问题类型: {qtype}")
        
        # 解答问题
        try:
            result = rag_pipeline.solve(
                qtype=qtype, 
                question=qa["question"], 
                options=qa.get("options"), 
                top_k=5
            )
            analysis_results.append({
                "question": qa["question"],
                "options": qa.get("options"),
                "answer": result
            })
            print(f"  解答成功")
        except Exception as e:
            print(f"  解答失败: {e}")
            analysis_results.append({
                "question": qa["question"],
                "options": qa.get("options"),
                "answer": {"error": str(e)}
            })

    # 格式化结果
    all_contexts = []
    raw_answers = []
    for res in analysis_results:
        answer_data = res["answer"]
        raw_answers.append({
            "question": res["question"],
            "options": res["options"],
            "answer": answer_data.get("raw", answer_data) if isinstance(answer_data, dict) else answer_data
        })
        if isinstance(answer_data, dict) and "contexts" in answer_data:
            all_contexts.extend(answer_data["contexts"])

    result = {
        "status": "completed",
        "message": "Analysis successful",
        "raw_answers": raw_answers,
        "all_contexts": all_contexts
    }
    
    print("\n最终分析结果:")
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_video_analysis_with_text()