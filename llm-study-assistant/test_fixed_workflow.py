#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复后的完整测试脚本
测试从OCR文本解析到RAG问答再到前端答案格式化的完整流程
"""

import sys
import os
import re
import json
from typing import List, Dict
import dotenv

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

# 加载环境变量
dotenv.load_dotenv()

def parse_ocr_text_to_qa_fixed(text: str) -> List[Dict[str, str]]:
    """
    修复后的OCR文本解析函数，专门针对题目格式进行解析。
    """
    qa_pairs = []
    
    # 清理文本，标准化空白字符
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 定义题目分割模式
    # 分割点：题号开始的位置（数字或中文数字后跟.或、）
    question_split_pattern = r'(?=\s*(\d+|[一二三四五六七八九十]+)[\.、])'
    parts = re.split(question_split_pattern, text)
    
    # 重新组合分割后的部分
    questions = []
    i = 1  # 跳过第一个空元素
    while i < len(parts):
        if i+1 < len(parts):
            question_block = parts[i] + parts[i+1]
            questions.append(question_block.strip())
            i += 2
        else:
            questions.append(parts[i].strip())
            i += 1
    
    # 处理每个问题块
    for question_block in questions:
        if not question_block:
            continue
            
        # 提取题号和问题文本
        question_match = re.match(r'^(\d+|[一二三四五六七八九十]+)[\.、]\s*(.+)', question_block.strip(), re.DOTALL)
        if not question_match:
            continue
            
        question_text = question_match.group(2).strip()
        
        # 移除问题文本中的选项部分
        # 查找第一个选项的位置
        first_option_match = re.search(r'\s[A-Z][\.、\)]', question_text)
        if first_option_match:
            question_text = question_text[:first_option_match.start()].strip()
        
        # 提取选项
        options = []
        # 匹配选项格式 A. B. C. D. 或 A) B) C) D) 或 A、B、C、D
        option_pattern = r'([A-Z])[\.、\)]\s*([^A-Z\n]*?)(?=\s*[A-Z][\.、\)]|\s*$)'
        option_matches = list(re.finditer(option_pattern, question_block))
        
        for opt_match in option_matches:
            option_letter = opt_match.group(1)
            option_text = opt_match.group(2).strip()
            if option_text:
                options.append(f"{option_letter}. {option_text}")
        
        # 特殊处理判断题
        if not options:
            tf_pattern = r'([A-B])[\.、\)]\s*(正确|错误|对|错)'
            tf_matches = list(re.finditer(tf_pattern, question_block))
            for tf_match in tf_matches:
                option_letter = tf_match.group(1)
                option_text = tf_match.group(2).strip()
                options.append(f"{option_letter}. {option_text}")
        
        # 如果仍然没有选项，尝试提取所有大写字母开头的内容
        if not options:
            general_option_pattern = r'([A-Z])[\.:、\)]\s*([^\n]*?)(?=\s*[A-Z][\.:、\)]|\s*$)'
            general_matches = list(re.finditer(general_option_pattern, question_block))
            for gen_match in general_matches:
                option_letter = gen_match.group(1)
                option_text = gen_match.group(2).strip()
                if option_text and len(option_text) > 1:
                    options.append(f"{option_letter}. {option_text}")
        
        qa_pairs.append({
            "question": question_text,
            "options": options
        })
    
    # 如果没有解析出任何问题，将整个文本作为一个问题
    if not qa_pairs and text.strip():
        qa_pairs.append({
            "question": text.strip(),
            "options": []
        })
    
    return qa_pairs

def format_answer_for_frontend(question: str, options: List[str], answer: Dict) -> Dict:
    """
    将RAG答案格式化为前端友好的格式。
    """
    # 确保答案是字典格式
    if not isinstance(answer, dict):
        answer = {"final_answer": str(answer), "confidence": 0.0, "brief_rationale": "格式错误"}
    
    # 解析最终答案
    final_answer = answer.get("final_answer", "")
    confidence = answer.get("confidence", 0.0)
    rationale = answer.get("brief_rationale", "")
    
    # 格式化选项（如果有的话）
    formatted_options = []
    if options:
        for i, opt in enumerate(options):
            # 解析选项字母和内容
            opt_match = re.match(r'^([A-Z])\.\s*(.+)', opt)
            if opt_match:
                letter = opt_match.group(1)
                content = opt_match.group(2)
                formatted_options.append({
                    "id": letter,
                    "text": content,
                    "isCorrect": letter in final_answer
                })
            else:
                formatted_options.append({
                    "id": chr(65 + i),  # A, B, C, D...
                    "text": opt,
                    "isCorrect": False
                })
    
    return {
        "question": question,
        "options": formatted_options,
        "answer": {
            "text": final_answer,
            "confidence": round(confidence, 2),
            "rationale": rationale
        }
    }

def test_complete_workflow():
    """测试完整的视频分析工作流程"""
    print("=== 测试修复后的完整视频分析工作流程 ===")
    
    # 模拟OCR提取的文本（包含多种题型）
    ocr_text = """
    1. 下列关于Python的说法，错误的是？
    A. Python是开源的
    B. Python是跨平台的
    C. Python是面向对象的
    D. Python是编译型语言

    2. 哪个选项不是Python的保留字？
    A) class
    B) def
    C) for
    D) main

    3. 以下哪些是Python的数据类型？（多选题）
    A. int
    B. float
    C. string
    D. boolean

    4. Python是一门解释型语言。（判断题）
    A. 正确
    B. 错误

    5. 请简述Python中列表和元组的区别。（问答题/案例分析题）
    """
    
    print("原始OCR文本:")
    print(ocr_text)
    print("\n" + "="*50)
    
    # 步骤1: 解析OCR文本为问答对
    print("\n步骤1: 解析OCR文本为问答对")
    qa_pairs = parse_ocr_text_to_qa_fixed(ocr_text)
    
    print(f"解析出 {len(qa_pairs)} 个问答对:")
    for i, qa in enumerate(qa_pairs, 1):
        print(f"  Q{i}: {qa['question']}")
        if qa['options']:
            print(f"     选项: {qa['options']}")
        print()
    
    # 步骤2: 模拟RAG分类和解答过程
    print("\n步骤2: 模拟RAG分类和解答过程")
    
    # 模拟分类结果
    classifications = ["single_choice", "single_choice", "multi_choice", "true_false", "subjective"]
    
    # 模拟解答结果
    mock_answers = [
        {
            "final_answer": "D",
            "confidence": 0.95,
            "brief_rationale": "Python是解释型语言，不是编译型语言。"
        },
        {
            "final_answer": "D",
            "confidence": 0.88,
            "brief_rationale": "main不是Python的保留字。"
        },
        {
            "final_answer": "A, B, C, D",
            "confidence": 0.92,
            "brief_rationale": "int、float、string、boolean都是Python的数据类型。"
        },
        {
            "final_answer": "A",
            "confidence": 0.98,
            "brief_rationale": "Python是解释型语言。"
        },
        {
            "final_answer": "列表是可变的，元组是不可变的。列表用方括号[]，元组用圆括号()。",
            "confidence": 0.85,
            "brief_rationale": "这是Python中列表和元组的主要区别。"
        }
    ]
    
    # 步骤3: 格式化为前端友好的答案
    print("\n步骤3: 格式化为前端友好的答案")
    frontend_answers = []
    
    for i, (qa, classification, mock_answer) in enumerate(zip(qa_pairs, classifications, mock_answers)):
        print(f"\n处理问题 {i+1}: {qa['question']}")
        print(f"  分类: {classification}")
        print(f"  原始答案: {mock_answer}")
        
        # 格式化答案
        formatted_answer = format_answer_for_frontend(
            question=qa["question"],
            options=qa["options"],
            answer=mock_answer
        )
        
        frontend_answers.append(formatted_answer)
        print(f"  格式化答案: {json.dumps(formatted_answer, ensure_ascii=False, indent=2)}")
    
    print("\n" + "="*50)
    print("最终前端格式化答案:")
    final_result = {
        "status": "success",
        "data": frontend_answers,
        "message": f"成功处理 {len(frontend_answers)} 个问题"
    }
    print(json.dumps(final_result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test_complete_workflow()