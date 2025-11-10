#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
更准确的QA解析测试脚本
测试更准确的OCR文本解析功能
"""

import sys
import os
import re
from typing import List, Dict

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def parse_ocr_text_to_qa_accurate(text: str) -> List[Dict[str, str]]:
    """
    更准确的OCR文本解析函数，专门针对题目格式进行解析。
    """
    qa_pairs = []
    
    # 清理文本，标准化空白字符
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 定义题目模式
    # 匹配题号格式: 1. / 1、/ 一、 等，后跟问题文本直到问号
    question_patterns = [
        r'(\d+|[一二三四五六七八九十]+)[\.、]\s*([^？?]*[？?])',  # 带问号的问题
        r'(\d+|[一二三四五六七八九十]+)[\.、]\s*([^\.、\n]*?:)',   # 带冒号的问题
        r'(\d+|[一二三四五六七八九十]+)[\.、]\s*([^\.、\n]*)'     # 一般问题
    ]
    
    # 找到所有可能的问题位置
    questions = []
    for pattern in question_patterns:
        matches = list(re.finditer(pattern, text))
        questions.extend(matches)
    
    # 按位置排序
    questions.sort(key=lambda x: x.start())
    
    if not questions:
        # 如果没有找到标准格式的问题，尝试简单分割
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        current_question = None
        current_options = []
        
        for line in lines:
            # 检查是否是问题开头
            if re.match(r'(\d+|[一二三四五六七八九十]+)[\.、]', line):
                # 保存之前的问题
                if current_question:
                    qa_pairs.append({
                        "question": current_question,
                        "options": current_options.copy()
                    })
                # 开始新问题
                # 提取问题文本
                question_text = re.sub(r'^(\d+|[一二三四五六七八九十]+)[\.、]\s*', '', line).strip()
                current_question = question_text
                current_options = []
            # 检查是否是选项
            elif re.match(r'^[A-Z][\.、\)]', line) and current_question:
                current_options.append(line)
            # 检查是否是判断题选项
            elif re.match(r'^[A-B][\.、\)]', line) and current_question:
                current_options.append(line)
        
        # 保存最后一个问题
        if current_question:
            qa_pairs.append({
                "question": current_question,
                "options": current_options
            })
        
        return qa_pairs
    
    # 处理找到的问题
    for i, match in enumerate(questions):
        question_text = match.group(2).strip()
        question_start = match.end()
        
        # 确定问题结束位置
        if i < len(questions) - 1:
            question_end = questions[i + 1].start()
        else:
            question_end = len(text)
        
        # 提取问题块
        question_block = text[question_start:question_end].strip()
        
        # 提取选项
        options = []
        # 匹配选项格式 A. B. C. D. 或 A) B) C) D)
        option_pattern = r'([A-Z])[\.、\)]\s*([^A-Z]*)'
        option_matches = list(re.finditer(option_pattern, question_block))
        
        for opt_match in option_matches:
            option_letter = opt_match.group(1)
            option_text = opt_match.group(2).strip()
            if option_text:
                # 移除下一个选项的开始部分
                option_text = re.sub(r'\s*[A-Z][\.、\)]\s*.*$', '', option_text).strip()
                if option_text:
                    options.append(f"{option_letter}. {option_text}")
        
        # 如果没有找到标准选项格式，尝试其他格式
        if not options:
            # 查找类似 (A) (B) 或 A) B) 格式的选项
            alt_option_pattern = r'[\(]?([A-Z])[\)]?[\.、\)]?\s*([^\.、\n]*?)(?=\s*[\(]?[A-Z][\)]?[\.、\)]?|\s*$)'
            alt_option_matches = list(re.finditer(alt_option_pattern, question_block))
            for opt_match in alt_option_matches:
                option_letter = opt_match.group(1)
                option_text = opt_match.group(2).strip()
                if option_text and len(option_text) > 1:  # 过滤掉太短的内容
                    options.append(f"{option_letter}. {option_text}")
        
        qa_pairs.append({
            "question": question_text,
            "options": options
        })
    
    return qa_pairs

def test_accurate_parser():
    """测试更准确的解析器"""
    print("=== 测试更准确的QA解析器 ===")
    
    # 测试文本
    test_text = """
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
    
    print("原始文本:")
    print(test_text)
    
    # 使用更准确的解析器
    qa_pairs = parse_ocr_text_to_qa_accurate(test_text)
    
    print(f"\n解析出 {len(qa_pairs)} 个问答对:")
    for i, qa in enumerate(qa_pairs, 1):
        print(f"  Q{i}: {qa['question']}")
        print(f"  Options: {qa['options']}")
        print()

if __name__ == "__main__":
    test_accurate_parser()