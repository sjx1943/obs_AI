#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试QA解析功能的脚本
"""

import sys
import os
import re
from typing import List, Dict

def parse_ocr_text_to_qa(text: str) -> List[Dict[str, str]]:
    """
    使用正则表达式从OCR文本中稳健地提取问答对。
    - 采用 re.finditer 查找所有问题的起点，以处理格式混乱的文本。
    - 支持多种题号格式 (如 "1.", "1、", "一、")。
    - 能处理问题之间没有换行符的情况。
    """
    qa_pairs = []
    # 正则表达式匹配一个问题的开始：题号 + 点/顿号 + 题目内容 + 选项
    # 使用非贪婪匹配 (.*?) 来捕获问题文本
    # 使用前瞻断言 (?=...) 来找到下一个题目的起点或字符串的结尾
    pattern = re.compile(
        r"((\d+|[一二三四五六七八九十]+)[\.、])"  # 匹配题号, e.g., "1.", "1、", "一、"
        r"(.*?)"                               # 非贪婪匹配题目内容
        r"(?=\s*(\d+|[一二三四五六七八九十]+)[\.、]|\Z)", # 匹配到下一个题号或字符串结尾
        re.DOTALL  # DOTALL 模式让 '.' 可以匹配换行符
    )

    for match in pattern.finditer(text):
        full_question_block = match.group(0).strip()
        
        # 提取问题和选项
        # 问题是题号之后，第一个选项之前的内容
        question_match = re.search(r"^(.*?)(?=\s*[A-Z][\.、\)])", full_question_block, re.DOTALL)
        
        if question_match:
            question_text = question_match.group(1).strip()
            # 移除题号部分
            question_text = re.sub(r"^(\d+|[一二三四五六七八九十]+)[\.、]", "", question_text).strip()

            # 选项是问题之后的所有内容
            options_text = full_question_block[question_match.end():].strip()
            
            if question_text:
                qa_pairs.append({
                    "question": question_text,
                    "options": options_text
                })

    # 如果上面的方法没有解析出任何内容，使用备用方案：将全部文本作为一个问题
    if not qa_pairs and text.strip():
        return [{"question": text.strip(), "options": ""}]
        
    return qa_pairs

def test_ocr_parsing():
    """测试OCR文本解析功能"""
    print("=== 测试OCR文本解析功能 ===")
    
    # 测试用的OCR文本示例
    test_text = """
    1. 下列关于Python的说法，错误的是？
       A. Python是开源的 B. Python是跨平台的 C. Python是面向对象的 D. Python是编译型语言
    2、哪个选项不是Python的保留字？
       A) class   B) def   C) for   D) main
    三、 关于机器学习，以下说法正确的是：
       A. 机器学习需要大量数据 B. 机器学习模型永远不会出错 C. 监督学习不需要标签
    """
    
    print("原始文本:")
    print(test_text)
    print("\n解析结果:")
    parsed_qa = parse_ocr_text_to_qa(test_text)
    import json
    print(json.dumps(parsed_qa, indent=2, ensure_ascii=False))
    
    # 测试更复杂的示例
    print("\n" + "="*50)
    print("=== 测试更复杂的OCR文本示例 ===")
    
    complex_test_text = """
    一、 单项选择题（每题2分，共20分）
    1. 在Python中，以下哪个关键字用于定义函数？
    A) func B) function C) def D) define
    2、 下面哪个数据类型是不可变的？
    A) list B) dict C) tuple D) set
    3. 以下哪个不是Python的内置数据类型？
    A) int B) float C) char D) bool
    二、 多项选择题（每题3分，共15分）
    1. 以下哪些是Python的循环结构？
    A) for B) while C) loop D) repeat
    2、 关于Python的类和对象，下列说法正确的有？
    A) 类是对象的模板 B) 对象是类的实例 C) 一个类只能创建一个对象 D) 类可以包含属性和方法
    """
    
    print("复杂测试文本:")
    print(complex_test_text)
    print("\n解析结果:")
    parsed_qa = parse_ocr_text_to_qa(complex_test_text)
    print(json.dumps(parsed_qa, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_ocr_parsing()