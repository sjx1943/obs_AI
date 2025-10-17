import os
# 关键修复：在导入任何torch/numpy库之前，限制CPU核心使用
# 这是防止easyocr在视频处理时导致系统崩溃的关键步骤
os.environ['OMP_NUM_THREADS'] = '1'

import cv2
import easyocr
import os
import re
from typing import List, Dict
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化OCR读取器 (仅在首次调用时加载模型)
# 支持中文简体和英文
reader = easyocr.Reader(['ch_sim', 'en'], gpu=False) 

def extract_text_from_video(video_path: str, interval_seconds: int = 3) -> str:
    """
    从视频文件中提取文本。

    Args:
        video_path (str): 视频文件的绝对路径。
        interval_seconds (int): 每隔多少秒提取一帧进行OCR。

    Returns:
        str: 从视频中提取并合并的所有唯一文本。
    """
    if not os.path.exists(video_path):
        logger.error(f"视频文件未找到: {video_path}")
        return ""

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"无法打开视频文件: {video_path}")
        return ""

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        logger.warning("无法获取视频FPS，将使用默认帧间隔。")
        frame_interval = 25 * interval_seconds # 假设一个默认值
    else:
        frame_interval = int(fps * interval_seconds)

    all_texts = set()
    frame_count = 0

    logger.info(f"开始处理视频: {os.path.basename(video_path)}, FPS: {fps}, 帧间隔: {frame_interval}")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            try:
                # EasyOCR需要BGR格式的图像
                result = reader.readtext(frame, detail=0, paragraph=True)
                
                current_frame_text = " ".join(result)
                if current_frame_text:
                    all_texts.add(current_frame_text)
                    logger.info(f"在第 {frame_count} 帧找到文本: {current_frame_text[:50]}...")

            except Exception as e:
                logger.error(f"处理第 {frame_count} 帧时发生错误: {e}")
        
        frame_count += 1

    cap.release()
    logger.info(f"视频处理完成。共处理 {frame_count} 帧，在 {len(all_texts)} 个关键帧上找到文本。")
    
    return "\n".join(sorted(list(all_texts)))

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

# --- 用于直接测试该脚本 ---
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test-parser':
        print("--- 正在测试文本解析器 ---")
        test_text = """
        1. 下列关于Python的说法，错误的是？
           A. Python是开源的 B. Python是跨平台的 C. Python是面向对象的 D. Python是编译型语言
        2、哪个选项不是Python的保留字？
           A) class   B) def   C) for   D) main
        三、 关于机器学习，以下说法正确的是：
           A. 机器学习需要大量数据 B. 机器学习模型永远不会出错 C. 监督学习不需要标签
        """
        parsed_qa = parse_ocr_text_to_qa(test_text)
        import json
        print(json.dumps(parsed_qa, indent=2, ensure_ascii=False))

    elif len(sys.argv) > 1:
        test_video_path = sys.argv[1]
        print(f"--- 正在测试视频文件: {test_video_path} ---")
        extracted_text = extract_text_from_video(test_video_path)
        print("\n--- 提取的文本 ---")
        print(extracted_text)
        print("\n--- 解析后的问答对 ---")
        parsed_qa = parse_ocr_text_to_qa(extracted_text)
        import json
        print(json.dumps(parsed_qa, indent=2, ensure_ascii=False))
    else:
        print("请提供一个视频文件路径或使用 '--test-parser' 选项进行测试。")
        print("用法 1: python app/video_processing.py /path/to/your/video.mkv")
        print("用法 2: python app/video_processing.py --test-parser")