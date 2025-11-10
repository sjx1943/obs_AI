#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
改进的QA解析测试脚本
测试更准确的OCR文本解析功能
"""

import sys
import os
import re
from typing import List, Dict

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def parse_ocr_text_to_qa_improved(text: str) -> List[Dict[str, str]]:
    """
    改进的OCR文本解析函数，更准确地提取问答对。
    """
    qa_pairs = []
    
    # 清理文本，移除多余的空白字符
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 正则表达式匹配问题
    # 匹配题号格式: 1. / 1、/ 一、 等
    question_pattern = r'(\d+|[一二三四五六七八九十]+)[\.、]\s*([^\.、\n]*?[？?])'
    
    # 查找所有问题
    questions = list(re.finditer(question_pattern, text))
    
    for i, match in enumerate(questions):
        question_text = match.group(2).strip()
        question_start = match.start()
        
        # 确定问题结束位置
        if i < len(questions) - 1:
            question_end = questions[i + 1].start()
        else:
            question_end = len(text)
        
        # 提取问题块
        question_block = text[question_start:question_end]
        
        # 提取选项
        options_pattern = r'([A-Z])[\.、\)]\s*([^A-Z]*)'
        options_matches = list(re.finditer(options_pattern, question_block))
        
        options = []
        for opt_match in options_matches:
            option_letter = opt_match.group(1)
            option_text = opt_match.group(2).strip()
            if option_text:
                options.append(f"{option_letter}. {option_text}")
        
        # 如果没有找到选项格式，尝试提取括号中的内容
        if not options:
            # 查找类似 (A) (B) 或 A) B) 格式的选项
            alt_options_pattern = r'[\(]?([A-Z])[\)]?[\.、\)]?\s*([^\.、\n]*?)(?=\s*[\(]?[A-Z][\)]?[\.、\)]?|\s*$)'
            alt_options_matches = list(re.finditer(alt_options_pattern, question_block))
            for opt_match in alt_options_matches:
                option_letter = opt_match.group(1)
                option_text = opt_match.group(2).strip()
                if option_text and len(option_text) > 1:  # 过滤掉太短的内容
                    options.append(f"{option_letter}. {option_text}")
        
        qa_pairs.append({
            "question": question_text,
            "options": options
        })
    
    # 如果没有解析出任何内容，使用备用方案
    if not qa_pairs and text.strip():
        # 尝试简单分割
        lines = text.split('\n')
        current_question = None
        current_options = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检查是否是问题开头
            if re.match(r'(\d+|[一二三四五六七八九十]+)[\.、]', line):
                # 保存之前的问题
                if current_question:
                    qa_pairs.append({
                        "question": current_question,
                        "options": current_options
                    })
                # 开始新问题
                question_match = re.search(r'(\d+|[一二三四五六七八九十]+)[\.、]\s*(.*)', line)
                if question_match:
                    current_question = question_match.group(2).strip()
                    current_options = []
            # 检查是否是选项
            elif re.match(r'[A-Z][\.、\)]', line) and current_question:
                current_options.append(line)
        
        # 保存最后一个问题
        if current_question:
            qa_pairs.append({
                "question": current_question,
                "options": current_options
            })
    
    return qa_pairs

def test_improved_parser():
    """测试改进的解析器"""
    print("=== 测试改进的QA解析器 ===")
    
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
    
    # 使用改进的解析器
    qa_pairs = parse_ocr_text_to_qa_improved(test_text)
    
    print(f"\n解析出 {len(qa_pairs)} 个问答对:")
    for i, qa in enumerate(qa_pairs, 1):
        print(f"  Q{i}: {qa['question']}")
        print(f"  Options: {qa['options']}")
        print()

if __name__ == "__main__":
    test_improved_parser()