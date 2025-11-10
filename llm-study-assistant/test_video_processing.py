#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试视频处理功能的脚本
"""

import sys
import os

# 添加项目路径到sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

from assistant.services.video_processing import extract_text_from_video, parse_ocr_text_to_qa

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

def test_video_extraction(video_path):
    """测试视频文本提取功能"""
    print(f"=== 测试视频文本提取功能: {video_path} ===")
    
    if not os.path.exists(video_path):
        print(f"错误: 视频文件不存在: {video_path}")
        return
    
    print("正在提取视频中的文本...")
    extracted_text = extract_text_from_video(video_path)
    print("提取的文本:")
    print(extracted_text)
    
    print("\n解析为问答对:")
    parsed_qa = parse_ocr_text_to_qa(extracted_text)
    import json
    print(json.dumps(parsed_qa, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test-parser":
            test_ocr_parsing()
        else:
            test_video_extraction(sys.argv[1])
    else:
        print("用法:")
        print("  python test_video_processing.py --test-parser  # 测试OCR文本解析")
        print("  python test_video_processing.py <video_path>    # 测试视频文本提取")