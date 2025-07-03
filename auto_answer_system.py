import sqlite3
import pytesseract
import cv2
import subprocess
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import threading
import time
import numpy as np
from datetime import datetime
import os
import json
from difflib import SequenceMatcher
import re
from PIL import Image, ImageEnhance
import jieba
import string

# Flask应用配置
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = '/tmp'  # 临时存储上传文件的目录
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# 全局变量
current_ocr_text = ""  # 存储原始OCR识别结果
current_qa_pairs = []  # 存储题目-答案对
current_questions = []  # 保持兼容性
current_answers = []   # 保持兼容性
last_qa_pairs = []
last_update_time = datetime.now()
is_running = False
frame_counter = 0
process_interval = 25  # 处理间隔

# 数据库配置
DB_PATH = '/home/kennys/IdeaProjects/obs_AI/question_bank.db'

# 完整的HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>智能答题助手</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            height: 100vh;
            display: flex;
            flex-direction: column;
            font-size: 14px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
            flex: 1;
            display: flex;
            flex-direction: column;
            max-height: calc(100vh - 30px);
            overflow: hidden;
        }
        
        h1 {
            text-align: center;
            margin-bottom: 20px;
            font-size: 24px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .status {
            text-align: center;
            margin-bottom: 15px;
            font-size: 13px;
            opacity: 0.9;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            margin-bottom: 15px;
            font-size: 12px;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            font-size: 18px;
            font-weight: bold;
            color: #ffd700;
        }
        
        .ocr-raw-display {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #ff6b6b;
        }
        
        .ocr-label {
            font-weight: bold;
            color: #ffb3b3;
            margin-bottom: 8px;
            font-size: 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .ocr-text {
            font-size: 14px;
            line-height: 1.6;
            white-space: pre-wrap;
            background: rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            color: #ffffff;
            max-height: 150px;
            overflow-y: auto;
        }
        
        .qa-container {
            flex: 1;
            overflow-y: auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .qa-pair {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #ffd700;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .qa-pair:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        .qa-pair.no-answer {
            border-left-color: #ff6b6b;
        }
        
        .qa-number {
            font-size: 16px;
            font-weight: bold;
            color: #ffd700;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }
        
        .qa-number::before {
            content: "🔍";
            margin-right: 8px;
        }
        
        .question-text {
            font-size: 15px;
            line-height: 1.6;
            margin-bottom: 12px;
            color: #ffffff;
            background: rgba(255, 255, 255, 0.05);
            padding: 10px;
            border-radius: 8px;
            border-left: 3px solid #4fc3f7;
        }
        
        .answer-text {
            font-size: 15px;
            line-height: 1.6;
            color: #ffffff;
            background: rgba(76, 175, 80, 0.2);
            padding: 10px;
            border-radius: 8px;
            border-left: 3px solid #4caf50;
        }
        
        .answer-text.not-found {
            background: rgba(255, 152, 0, 0.2);
            border-left-color: #ff9800;
        }
        
        .question-label {
            font-weight: bold;
            color: #81d4fa;
            margin-bottom: 5px;
            font-size: 13px;
        }
        
        .answer-label {
            font-weight: bold;
            color: #a5d6a7;
            margin-bottom: 5px;
            font-size: 13px;
        }
        
        .answer-label.not-found {
            color: #ffcc02;
        }
        
        .no-data {
            text-align: center;
            opacity: 0.6;
            font-style: italic;
            padding: 40px;
            font-size: 16px;
        }
        
        .controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 15px;
        }
        
        button {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.3s;
            font-family: 'Microsoft YaHei', sans-serif;
        }
        
        button:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        .status-running {
            background-color: #4ade80;
        }
        
        .status-stopped {
            background-color: #ef4444;
        }
        
        .update-time {
            font-size: 11px;
            opacity: 0.7;
            text-align: center;
            margin-top: 10px;
        }
        
        .match-confidence {
            font-size: 11px;
            opacity: 0.7;
            text-align: right;
            margin-top: 5px;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .search-info {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 15px;
            text-align: center;
            font-size: 12px;
            opacity: 0.8;
        }
        
        .toggle-btn {
            background: rgba(255, 255, 255, 0.15);
            border: none;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            cursor: pointer;
            font-size: 11px;
            transition: all 0.3s;
        }
        
        .toggle-btn:hover {
            background: rgba(255, 255, 255, 0.25);
        }
        
        .collapsible {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }
        
        .collapsible.expanded {
            max-height: 200px;
        }
        
        .debug-info {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 15px;
            font-size: 12px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 智能答题助手</h1>
        <div class="status">
            <span class="status-indicator" id="statusIndicator"></span>
            <span id="statusText">等待连接...</span>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number" id="questionCount">0</div>
                <div>识别题目</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="answerCount">0</div>
                <div>匹配答案</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="successRate">0%</div>
                <div>成功率</div>
            </div>
        </div>
        
        <div class="search-info">
            <span>📚 支持中英文混合题目匹配 | 🔍 智能关键词检索 | 💡 模糊语义匹配</span>
        </div>
        
        <!-- 显示原始OCR识别结果 -->
        <div class="ocr-raw-display">
            <div class="ocr-label">
                <span>🔍 原始OCR识别结果：</span>
                <button class="toggle-btn" onclick="toggleOCRDisplay()">展开/收起</button>
            </div>
            <div class="ocr-text collapsible expanded" id="ocrText">等待OCR识别...</div>
        </div>
        
        <!-- 调试信息 -->
        <div class="debug-info" id="debugInfo">
            调试信息：等待处理...
        </div>
        
        <div class="qa-container" id="qaContainer">
            <div class="no-data">等待题目识别与答案匹配...</div>
        </div>
        
        <div class="controls">
            <button onclick="toggleRecording()">
                <span id="recordingBtn">开始录制</span>
            </button>
            <button onclick="clearDisplay()">清空显示</button>
            <button onclick="exportResults()">导出结果</button>
            <button onclick="testOCR()">测试OCR</button>
            <label class="button" style="background: rgba(255, 255, 255, 0.2); border: 1px solid rgba(255, 255, 255, 0.3); color: white; padding: 10px 20px; border-radius: 20px; cursor: pointer; font-size: 13px; transition: all 0.3s; font-family: 'Microsoft YaHei', sans-serif;">
                上传题库
                <input type="file" id="questionBankFile" accept=".csv" style="display: none;" onchange="uploadQuestionBank()">
            </label>
        </div>
        
        <div class="update-time" id="updateTime"></div>
    </div>
    
    <script>
        let isRunning = false;
        let ocrExpanded = true;
        
        function updateDisplay() {
            fetch('/get_results')
                .then(response => response.json())
                .then(data => {
                    updateOCRText(data.ocr_text);
                    updateQAPairs(data.qa_pairs);
                    updateStatus(data.is_running, data.last_update);
                    updateStats(data.qa_pairs);
                    updateDebugInfo(data.debug_info);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
        
        function updateOCRText(ocrText) {
            const ocrElement = document.getElementById('ocrText');
            if (ocrText && ocrText.trim()) {
                ocrElement.textContent = ocrText;
            } else {
                ocrElement.textContent = '等待OCR识别...';
            }
        }
        
        function updateQAPairs(qaPairs) {
            const container = document.getElementById('qaContainer');
            if (qaPairs && qaPairs.length > 0) {
                container.innerHTML = qaPairs.map((pair, index) => {
                    const isNotFound = pair.answer === "未找到答案" || pair.answer === "未在题库中找到匹配答案";
                    return `
                        <div class="qa-pair ${isNotFound ? 'no-answer' : ''}">
                            <div class="qa-number">第 ${index + 1} 题</div>
                            
                            <div class="question-label">📝 题目：</div>
                            <div class="question-text">${pair.question}</div>
                            
                            <div class="answer-label ${isNotFound ? 'not-found' : ''}">
                                ${isNotFound ? '⚠️ 答案：' : '💡 答案：'}
                            </div>
                            <div class="answer-text ${isNotFound ? 'not-found' : ''}">
                                ${pair.answer}
                            </div>
                            
                            ${pair.confidence ? `<div class="match-confidence">匹配度: ${pair.confidence}%</div>` : ''}
                        </div>
                    `;
                }).join('');
            } else {
                container.innerHTML = '<div class="no-data">等待题目识别与答案匹配...</div>';
            }
        }
        
        function updateStatus(running, lastUpdate) {
            const statusIndicator = document.getElementById('statusIndicator');
            const statusText = document.getElementById('statusText');
            const updateTime = document.getElementById('updateTime');
            const recordingBtn = document.getElementById('recordingBtn');
            
            isRunning = running;
            if (running) {
                statusIndicator.className = 'status-indicator status-running';
                statusText.textContent = '系统运行中';
                recordingBtn.textContent = '停止录制';
            } else {
                statusIndicator.className = 'status-indicator status-stopped';
                statusText.textContent = '系统已停止';
                recordingBtn.textContent = '开始录制';
            }
            
            if (lastUpdate) {
                updateTime.textContent = '最后更新: ' + lastUpdate;
            }
        }
        
        function updateStats(qaPairs) {
            const questionCount = document.getElementById('questionCount');
            const answerCount = document.getElementById('answerCount');
            const successRate = document.getElementById('successRate');
            
            const qCount = qaPairs ? qaPairs.length : 0;
            const aCount = qaPairs ? qaPairs.filter(pair => 
                pair.answer !== "未找到答案" && pair.answer !== "未在题库中找到匹配答案"
            ).length : 0;
            const rate = qCount > 0 ? Math.round((aCount / qCount) * 100) : 0;
            
            questionCount.textContent = qCount;
            answerCount.textContent = aCount;
            successRate.textContent = rate + '%';
        }
        
        function updateDebugInfo(debugInfo) {
            const debugElement = document.getElementById('debugInfo');
            if (debugInfo) {
                debugElement.textContent = debugInfo;
            } else {
                debugElement.textContent = '调试信息：等待处理...';
            }
        }
    
       function uploadQuestionBank() {
                const fileInput = document.getElementById('questionBankFile');
                const file = fileInput.files[0];
                if (file) {
                    const formData = new FormData();
                    formData.append('file', file);
                    fetch('/upload_question_bank', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('题库导入成功');
                        } else {
                            alert(`题库导入失败: ${data.message}`);
                        }
                        fileInput.value = ''; // 清空文件选择
                    })
                    .catch(error => {
                        alert(`发生错误: ${error.message}`);
                    });
                }
            }
        
        function toggleRecording() {
            fetch('/toggle_recording', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);
                });
        }
        
        function toggleOCRDisplay() {
            const ocrElement = document.getElementById('ocrText');
            if (ocrElement.classList.contains('expanded')) {
                ocrElement.classList.remove('expanded');
            } else {
                ocrElement.classList.add('expanded');
            }
        }
        
        function testOCR() {
            fetch('/test_ocr', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(`OCR测试成功！识别出${data.question_count}个问题`);
                    } else {
                        alert(`OCR测试失败：${data.error}`);
                    }
                });
        }
        
        function clearDisplay() {
            fetch('/clear_display', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('qaContainer').innerHTML = '<div class="no-data">等待题目识别与答案匹配...</div>';
                });
        }
        
        function exportResults() {
            fetch('/export_results')
                .then(response => response.blob())
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'answers_' + new Date().toISOString().slice(0,10) + '.txt';
                    a.click();
                    window.URL.revokeObjectURL(url);
                });
        }
        
        // 每秒更新一次
        setInterval(updateDisplay, 1000);
        
        // 页面加载时立即更新
        updateDisplay();
    </script>
</body>
</html>
'''
# Flask路由
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/test_ocr', methods=['POST'])
def test_ocr():
    global current_ocr_text, current_qa_pairs, last_update_time

    try:
        # 使用静态测试图像
        test_image_path = 'test_frame.png'
        if os.path.exists(test_image_path):
            img = cv2.imread(test_image_path)
            if img is None:
                return jsonify({"error": "无法读取测试图像"})

            # OCR识别
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')
            current_ocr_text = text

            # 分割问题
            questions = split_questions(text)

            # 处理每个问题
            qa_pairs = []
            for question in questions:
                if question and len(question) > 5:
                    answer, confidence = query_database_fuzzy(question)
                    qa_pairs.append({
                        'question': question,
                        'answer': answer,
                        'confidence': confidence if confidence > 0 else None
                    })

            current_qa_pairs = qa_pairs
            last_update_time = datetime.now()

            return jsonify({
                "success": True,
                "ocr_text": text,
                "question_count": len(questions)
            })
        else:
            return jsonify({"error": "测试图像不存在"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/upload_question_bank', methods=['POST'])
def upload_question_bank():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '未选择文件'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '未选择文件'}), 400
    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        success, message = import_question_bank(file_path)
        os.remove(file_path)  # 删除临时文件
        return jsonify({'success': success, 'message': message})
    else:
        return jsonify({'success': False, 'message': '只允许上传 CSV 文件'}), 400

@app.route('/get_qa_pairs')
def get_qa_pairs():
    global current_qa_pairs, last_update_time, is_running
    return jsonify({
        "qa_pairs": current_qa_pairs,
        "last_update": last_update_time.strftime("%H:%M:%S"),
        "is_running": is_running
    })

@app.route('/toggle_recording', methods=['POST'])
def toggle_recording():
    global is_running
    is_running = not is_running
    if is_running:
        video_thread = threading.Thread(target=process_video_stream)
        video_thread.daemon = True
        video_thread.start()
        return jsonify({"message": "录制已开始", "status": "running"})
    else:
        return jsonify({"message": "录制已停止", "status": "stopped"})

@app.route('/clear_display', methods=['POST'])
def clear_display():
    global current_qa_pairs, current_ocr_text, current_questions, current_answers
    current_qa_pairs = []
    current_ocr_text = ""
    current_questions = []
    current_answers = []
    return jsonify({"message": "显示已清空"})

@app.route('/export_results')
def export_results():
    global current_qa_pairs
    content = f"智能答题结果导出\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += "=" * 60 + "\n\n"

    for i, pair in enumerate(current_qa_pairs):
        content += f"【题目 {i+1}】\n"
        content += f"问题：{pair['question']}\n"
        content += f"答案：{pair['answer']}\n"
        if pair.get('confidence'):
            content += f"匹配度：{pair['confidence']}%\n"
        content += "\n" + "-" * 40 + "\n\n"

    from flask import make_response
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=qa_results.txt'
    return response

@app.route('/get_results')
def get_results():
    global current_ocr_text, current_qa_pairs, is_running, last_update_time
    # 构造返回的 JSON 数据
    response_data = {
        'ocr_text': current_ocr_text,
        'qa_pairs': current_qa_pairs,
        'is_running': is_running,
        'last_update': last_update_time.strftime('%Y-%m-%d %H:%M:%S'),
        'debug_info': ""  # 可根据实际需求添加调试信息
    }
    return jsonify(response_data)

# 检查文件扩展名是否允许
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# 导入题库函数（保留正确版本，删除重复的同名函数）
def import_question_bank(csv_file):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 统一数据库表名为 questions（与后续查询逻辑一致）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL UNIQUE,  -- 添加 UNIQUE 避免重复
            answer TEXT NOT NULL
        )
    ''')
    try:
        inserted_count = 0
        with open(csv_file, 'r', encoding='utf-8') as f:
            import csv  # 显式导入 csv 模块（原代码中末尾函数使用了 csv.reader）
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:  # 兼容 CSV 可能的多列情况
                    question = row[0].strip()
                    answer = row[1].strip()
                    if question and answer:
                        # 使用 INSERT OR IGNORE 避免重复导入
                        cursor.execute('''
                            INSERT OR IGNORE INTO questions (question, answer)
                            VALUES (?, ?)
                        ''', (question, answer))
                        if cursor.rowcount > 0:
                            inserted_count += 1
        conn.commit()
        return True, f"成功导入 {inserted_count} 条题目"
    except Exception as e:
        conn.rollback()
        return False, f"导入失败: {str(e)}"
    finally:
        conn.close()

# 改进的文本标准化函数
def normalize_text(text):
    """标准化文本，处理中英文混合"""
    if not text:
        return ""

    # 基本清理
    text = text.strip()

    # 统一空格
    text = ' '.join(text.split())

    # 转换为小写（仅限英文）
    normalized = ""
    for char in text:
        if char.isalpha() and ord(char) < 128:  # 英文字符
            normalized += char.lower()
        else:
            normalized += char

    # 移除多余标点
    normalized = re.sub(r'[^\w\s\u4e00-\u9fff]', '', normalized)

    return normalized

# 增强的模糊查询数据库函数
def query_database_fuzzy(question, threshold=0.6):
    """
    增强的模糊查询数据库函数，支持中英文混合题目匹配
    """
    if not question or len(question) < 3:
        return "未找到答案"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # 获取所有问题
        c.execute("SELECT question, answer FROM questions")
        all_questions = c.fetchall()

        if not all_questions:
            return "未找到答案"

        # 标准化输入问题
        clean_question = clean_text(question)

        # 提取关键词
        question_keywords = extract_mixed_keywords(clean_question)

        best_match = None
        best_score = 0

        print(f"正在匹配问题: {clean_question}")
        print(f"提取的关键词: {question_keywords}")

        for db_question, db_answer in all_questions:
            # 标准化数据库问题
            clean_db_question = clean_text(db_question)
            db_keywords = extract_mixed_keywords(clean_db_question)

            # 计算多种相似度得分
            scores = []

            # 1. 整体文本相似度 (权重40%)
            text_similarity = SequenceMatcher(None, clean_question, clean_db_question).ratio()
            scores.append(text_similarity * 0.4)

            # 2. 关键词匹配度 (权重30%)
            keyword_score = 0
            if question_keywords and db_keywords:
                common_keywords = set(question_keywords) & set(db_keywords)
                total_keywords = set(question_keywords) | set(db_keywords)
                keyword_score = len(common_keywords) / len(total_keywords) if total_keywords else 0
            scores.append(keyword_score * 0.3)

            # 3. 包含关系匹配 (权重20%)
            contain_score = 0
            if clean_question in clean_db_question:
                contain_score = 0.9
            elif clean_db_question in clean_question:
                contain_score = 0.8
            elif any(kw in clean_db_question for kw in question_keywords if len(kw) > 2):
                contain_score = 0.6
            scores.append(contain_score * 0.2)

            # 4. 编辑距离相似度 (权重10%)
            edit_similarity = calculate_edit_similarity(clean_question, clean_db_question)
            scores.append(edit_similarity * 0.1)

            # 综合得分
            final_score = sum(scores)

            # 特殊加分规则
            # 如果包含相同的英文单词
            question_en = extract_english_words(clean_question)
            db_en = extract_english_words(clean_db_question)
            if question_en & db_en:
                final_score += 0.15
                print(f"英文单词匹配加分: {question_en & db_en}")

            # 如果包含相同的数字
            question_nums = extract_numbers(clean_question)
            db_nums = extract_numbers(clean_db_question)
            if question_nums & db_nums:
                final_score += 0.1
                print(f"数字匹配加分: {question_nums & db_nums}")

            # 如果包含相同的中文关键词
            question_cn = extract_chinese_words(clean_question)
            db_cn = extract_chinese_words(clean_db_question)
            common_cn = question_cn & db_cn
            if common_cn:
                final_score += len(common_cn) * 0.05
                print(f"中文关键词匹配加分: {common_cn}")

            # 记录最佳匹配
            if final_score > best_score and final_score > threshold:
                best_score = final_score
                best_match = db_answer
                print(f"找到更好的匹配: {db_question} -> {db_answer} (得分: {final_score:.3f})")

        result = best_match if best_match else "未找到答案"
        print(f"最终匹配结果: {result} (最高得分: {best_score:.3f})")
        return result

    except Exception as e:
        print(f"数据库查询错误: {e}")
        return "未找到答案"
    finally:
        conn.close()

def clean_text(text):
    """清理和标准化文本"""
    if not text:
        return ""

    # 统一空格
    text = ' '.join(text.split())

    # 转换英文为小写，保持中文不变
    result = ""
    for char in text:
        if char.isalpha() and ord(char) < 128:  # 英文字符
            result += char.lower()
        else:
            result += char

    # 移除多余标点但保留基本标点
    result = re.sub(r'[^\w\s\u4e00-\u9fff？！。，、：；]', '', result)

    return result.strip()

def extract_keywords(text):
    """
    提取文本关键词，支持中英文混合文本

    Args:
        text: 输入的文本

    Returns:
        list: 关键词列表
    """
    if not text or len(text) < 2:
        return []

    keywords = []

    # 1. 提取中文关键词
    try:
        # 使用jieba分词
        chinese_words = jieba.cut(text)
        for word in chinese_words:
            # 过滤掉停用词和单个字符
            if (len(word) > 1 and
                    re.match(r'[\u4e00-\u9fff]+', word) and
                    word not in ['的', '是', '了', '在', '有', '和', '就', '不', '都', '要',
                                 '可以', '这个', '那个', '什么', '哪里', '怎么', '为什么', '因为',
                                 '所以', '但是', '然后', '如果', '或者', '而且', '还是', '虽然',
                                 '虽然', '无论', '不管', '一些', '许多', '很多', '非常', '特别',
                                 '比较', '更加', '最为', '十分', '相当', '极其', '完全', '完整',
                                 '主要', '重要', '关键', '基本', '简单', '复杂', '困难', '容易']):
                keywords.append(word)
    except Exception as e:
        print(f"中文分词错误: {e}")

    # 2. 提取英文单词
    english_words = re.findall(r'[a-zA-Z]+', text)
    for word in english_words:
        if (len(word) > 1 and
                word.lower() not in ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                                     'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through',
                                     'during', 'before', 'after', 'above', 'below', 'over', 'under',
                                     'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
                                     'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                                     'should', 'may', 'might', 'can', 'must', 'shall', 'this',
                                     'that', 'these', 'those', 'what', 'which', 'who', 'when',
                                     'where', 'why', 'how', 'very', 'much', 'many', 'most', 'more',
                                     'some', 'any', 'all', 'each', 'every', 'both', 'either', 'neither']):
            keywords.append(word.lower())

    # 3. 提取数字
    numbers = re.findall(r'\d+', text)
    keywords.extend(numbers)

    # 4. 提取特殊符号和标点（某些情况下可能重要）
    special_chars = re.findall(r'[？！。，、：；""''（）【】《》〈〉]', text)
    for char in special_chars:
        if char in ['？', '！', '。']:  # 只保留重要的标点
            keywords.append(char)

    # 5. 提取专有名词（大写字母开头的词）
    proper_nouns = re.findall(r'[A-Z][a-z]+', text)
    for noun in proper_nouns:
        if len(noun) > 1:
            keywords.append(noun.lower())

    # 6. 提取缩写词
    abbreviations = re.findall(r'[A-Z]{2,}', text)
    for abbr in abbreviations:
        keywords.append(abbr.lower())

    # 7. 去重并保持顺序
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen:
            seen.add(keyword)
            unique_keywords.append(keyword)

    # 8. 按长度排序，优先保留较长的关键词
    unique_keywords.sort(key=len, reverse=True)

    return unique_keywords[:20]  # 限制关键词数量，避免过多


def normalize_text(text):
    """
    标准化文本，配合extract_keywords使用

    Args:
        text: 输入文本

    Returns:
        str: 标准化后的文本
    """
    if not text:
        return ""

    # 1. 统一空格
    text = ' '.join(text.split())

    # 2. 转换英文为小写
    result = ""
    for char in text:
        if char.isalpha() and ord(char) < 128:  # 英文字符
            result += char.lower()
        else:
            result += char

    # 3. 统一标点符号
    punctuation_map = {
        '？': '?',
        '！': '!',
        '。': '.',
        '，': ',',
        '：': ':',
        '；': ';',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '（': '(',
        '）': ')',
        '【': '[',
        '】': ']',
        '《': '<',
        '》': '>',
        '、': ',',
    }

    for chinese_punct, english_punct in punctuation_map.items():
        result = result.replace(chinese_punct, english_punct)

    # 4. 移除多余的标点和特殊字符，但保留基本的
    result = re.sub(r'[^\w\s\u4e00-\u9fff?!.,;:()\[\]<>\'"-]', '', result)

    # 5. 合并多个空格
    result = re.sub(r'\s+', ' ', result)

    return result.strip()

def extract_mixed_keywords(text):
    """提取中英文混合文本的关键词"""
    if not text:
        return []

    keywords = []

    # 中文分词
    try:
        chinese_words = jieba.cut(text)
        for word in chinese_words:
            if len(word) > 1 and word not in ['的', '是', '了', '在', '有', '和', '就', '不', '都', '要', '可以', '这个', '那个', '什么', '哪里', '怎么']:
                keywords.append(word)
    except:
        pass

    # 英文单词提取
    english_words = re.findall(r'[a-zA-Z]+', text)
    for word in english_words:
        if len(word) > 1:
            keywords.append(word.lower())

    # 数字提取
    numbers = re.findall(r'\d+', text)
    keywords.extend(numbers)

    return list(set(keywords))

def extract_english_words(text):
    """提取英文单词"""
    if not text:
        return set()

    words = re.findall(r'[a-zA-Z]+', text.lower())
    return set(word for word in words if len(word) > 1)

def extract_numbers(text):
    """提取数字"""
    if not text:
        return set()

    numbers = re.findall(r'\d+', text)
    return set(numbers)

def extract_chinese_words(text):
    """提取中文关键词"""
    if not text:
        return set()

    try:
        words = jieba.cut(text)
        chinese_words = []
        for word in words:
            if len(word) > 1 and re.match(r'[\u4e00-\u9fff]+', word):
                if word not in ['的', '是', '了', '在', '有', '和', '就', '不', '都', '要', '可以', '这个', '那个', '什么', '哪里', '怎么', '为什么']:
                    chinese_words.append(word)
        return set(chinese_words)
    except:
        return set()

def calculate_edit_similarity(s1, s2):
    """计算编辑距离相似度"""
    if not s1 or not s2:
        return 0

    # 使用简单的编辑距离算法
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])

    max_len = max(m, n)
    return (max_len - dp[m][n]) / max_len if max_len > 0 else 0

# 改进的模糊匹配函数
def enhanced_fuzzy_match(question, threshold=0.6):
    """增强的模糊匹配，支持中英文混合"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 获取所有问题
    c.execute("SELECT question, answer FROM questions")
    all_questions = c.fetchall()
    conn.close()

    if not all_questions:
        return "未找到答案", 0

    # 标准化输入问题
    norm_question = normalize_text(question)
    question_keywords = extract_keywords(norm_question)

    best_match = None
    best_score = 0
    best_confidence = 0

    for db_question, db_answer in all_questions:
        # 标准化数据库问题
        norm_db_question = normalize_text(db_question)
        db_keywords = extract_keywords(norm_db_question)

        # 计算多种相似度
        scores = []

        # 1. 整体文本相似度
        text_similarity = SequenceMatcher(None, norm_question, norm_db_question).ratio()
        scores.append(text_similarity * 0.4)

        # 2. 关键词匹配度
        if question_keywords and db_keywords:
            common_keywords = set(question_keywords) & set(db_keywords)
            keyword_score = len(common_keywords) / len(set(question_keywords) | set(db_keywords))
            scores.append(keyword_score * 0.3)

        # 3. 包含关系匹配
        contain_score = 0
        if norm_question in norm_db_question or norm_db_question in norm_question:
            contain_score = 0.8
        scores.append(contain_score * 0.2)

        # 4. 编辑距离相似度
        import difflib
        edit_similarity = difflib.SequenceMatcher(None, norm_question, norm_db_question).ratio()
        scores.append(edit_similarity * 0.1)

        # 综合得分
        final_score = sum(scores)

        # 特殊加分：如果包含相同的英文单词或数字
        question_en = set(re.findall(r'[a-zA-Z]+', norm_question.lower()))
        db_en = set(re.findall(r'[a-zA-Z]+', norm_db_question.lower()))
        if question_en & db_en:
            final_score += 0.15

        question_nums = set(re.findall(r'\d+', norm_question))
        db_nums = set(re.findall(r'\d+', norm_db_question))
        if question_nums & db_nums:
            final_score += 0.1

        if final_score > best_score and final_score > threshold:
            best_score = final_score
            best_match = db_answer
            best_confidence = int(final_score * 100)

    return best_match if best_match else "未找到答案", best_confidence

def split_questions(text):
    """增强的问题分割函数，支持变形序号"""
    if not text or len(text) < 5:
        return []

    # 预处理：清理OCR噪声（如将"1荆"修正为"1."）
    cleaned_text = re.sub(r'(\d+)[^\d\s\.\、]', r'\1. ', text)  # 数字后接非分隔符→数字+.
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    # 分割策略1：匹配数字+分隔符（支持变形如"1荆"→"1."）
    pattern = r'(\d+[\.\、\s]\s*[^\d]+?)(?=\d+[\.\、\s]|$)'
    matches = re.findall(pattern, cleaned_text, re.DOTALL)
    questions = [match.strip() for match in matches if len(match) > 5]

    # 分割策略2：按问号分割（若无序号）
    if not questions:
        questions = [q.strip() + '?' for q in cleaned_text.split('?') if q.strip()]

    # 分割策略3：按换行分割
    if not questions:
        questions = [line.strip() for line in cleaned_text.split('\n') if len(line) > 8]

    print(f"分割结果: {questions}")  # 调试用
    return questions[:5]  # 最多返回5个问题

# 问题分割和清理函数
def split_and_clean_questions(text):
    """分割和清理问题文本"""
    if not text or len(text) < 5:
        return []

    # 清理文本
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    questions = []

    # 分割策略
    patterns = [
        r'(\d+[\.\、]\s*[^\d\.\、]+?)(?=\d+[\.\、]|$)',  # 数字编号
        r'([一二三四五六七八九十]+[\、\.].*?)(?=[一二三四五六七八九十]+[\、\.]|$)',  # 中文编号
        r'([A-Z][\.\)]\s*[^A-Z\.\)]+?)(?=[A-Z][\.\)]|$)',  # 英文编号
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches and len(matches) > 1:
            questions.extend([match.strip() for match in matches])
            break

    # 如果没有找到分割模式，按问号分割
    if not questions:
        parts = text.split('？')
        questions = [part.strip() + '？' for part in parts if part.strip()]

    # 如果还是没有，按句号分割
    if not questions:
        parts = text.split('。')
        questions = [part.strip() + '。' for part in parts if part.strip() and len(part.strip()) > 8]

    # 最后尝试按长度分割
    if not questions and len(text) > 50:
        # 按照合理长度分割
        words = text.split()
        chunk_size = 15
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i+chunk_size])
            if len(chunk) > 10:
                questions.append(chunk)

    # 如果都没有成功，返回原文本
    if not questions:
        questions = [text]

    # 过滤和清理
    cleaned_questions = []
    for q in questions:
        q = q.strip()
        if len(q) > 8 and len(q) < 500:  # 合理长度范围
            cleaned_questions.append(q)

    return cleaned_questions[:5]  # 最多返回5个问题

# 图像预处理函数
def preprocess_image(image):
    """优化的图像预处理"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # 对比度增强
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # 降噪
    gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

    # 自适应阈值
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY, 11, 2)

    # 形态学操作
    kernel = np.ones((1, 1), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # 锐化
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    binary = cv2.filter2D(binary, -1, kernel)

    return binary

# 增强的OCR函数
def enhanced_ocr(image):
    """增强的OCR识别"""
    try:
        # 多种配置尝试
        configs = [
            '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,?!:;()[]{}<>/\\\'"@#$%^&*_-+= \u4e00-\u9fff',
            '--oem 3 --psm 11',
            '--oem 3 --psm 12',
            '--oem 3 --psm 4',
        ]

        best_text = ""
        for config in configs:
            try:
                text = pytesseract.image_to_string(
                    image,
                    lang='chi_sim+eng',
                    config=config
                ).strip()

                if len(text) > len(best_text):
                    best_text = text
            except:
                continue

        # 后处理：修正常见OCR错误
        corrections = {
            'wikere': 'where',
            'Cirimal': 'China',
            'SEE': 'sgg',
            'meme': 'name',
            'ont': 'cctv',
            'ILA': '中文名'
        }

        for wrong, right in corrections.items():
            best_text = best_text.replace(wrong, right)

        return best_text

    except Exception as e:
        print(f"OCR识别错误: {e}")
        return ""

# 主要的视频处理函数
def process_video_stream():
    """主要的视频处理函数"""
    global current_qa_pairs, last_qa_pairs, last_update_time, frame_counter, is_running

    # 打开视频源
    cap = None
    video_sources = [0, 1, 2, "/dev/video0", "/dev/video1", "/dev/video2"]

    for source in video_sources:
        try:
            cap = cv2.VideoCapture(source)
            if cap.isOpened():
                print(f"成功打开视频源: {source}")
                break
        except:
            continue

    if not cap or not cap.isOpened():
        print("无法打开视频源")
        is_running = False
        return

    # 设置视频参数
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    print("开始视频处理...")

    while is_running:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        frame_counter += 1

        # 定期处理
        if frame_counter % process_interval == 0:
            try:
                # 调整ROI区域
                height, width = frame.shape[:2]
                roi = frame[int(height*0.1):int(height*0.9), int(width*0.1):int(width*0.9)]

                # 旋转校正 (如果视频源需要)
                # roi = cv2.rotate(roi, cv2.ROTATE_90_CLOCKWISE)

                # 预处理
                processed_image = preprocess_image(roi)

                # 保存调试图像
                cv2.imwrite('debug_processed.png', processed_image)

                # OCR识别
                text = enhanced_ocr(processed_image)

                if text and len(text) > 10:
                    current_ocr_text = text
    # 分割问题
                    questions = split_questions(text)

                    if questions:

        # 不需要进行相似度比较，直接处理所有问题
                        qa_pairs = []

                        for question in questions:
                            if question and len(question) > 5:
                                answer = query_database_fuzzy(question)
                                qa_pairs.append({
                                    'question': question,
                                    'answer': answer,
                                    'confidence': None
                                })

                        current_qa_pairs = qa_pairs
                        last_update_time = datetime.now()

                        print(f"识别到 {len(questions)} 个问题")
                        for i, pair in enumerate(qa_pairs):
                            print(f"问题{i+1}: {pair['question'][:50]}...")
                            print(f"答案{i+1}: {pair['answer'][:50]}...")
                            if pair['confidence']:
                                print(f"匹配度: {pair['confidence']}%")
                                print("-" * 40)

            except Exception as e:
                print(f"处理错误: {e}")

        time.sleep(0.05)

    cap.release()
    print("视频处理已停止")

# 问题相似度比较
def are_qa_pairs_similar(questions1, questions2, threshold=0.8):
    """比较两组问题是否相似"""
    if len(questions1) != len(questions2):
        return False

    if not questions1 or not questions2:
        return False

    for q1, q2 in zip(questions1, questions2):
        similarity = SequenceMatcher(None, q1, q2).ratio()
        if similarity < threshold:
            return False

    return True



# 启动Flask服务器
def start_flask_server():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# 主函数
def main():
    global is_running

    # 确保数据库目录存在
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # # 导入题库
    # csv_path = 'questions.csv'
    # if os.path.exists(csv_path):
    #     print("正在导入题库...")
    #     import_question_bank(csv_path)
    # else:
    #     print(f"警告: 题库文件 {csv_path} 不存在")

    # 启动Flask服务器
    flask_thread = threading.Thread(target=start_flask_server)
    flask_thread.daemon = True
    flask_thread.start()

    print("=" * 60)
    print("优化版智能答题系统已启动")
    print("Web界面: http://localhost:5000")
    print("支持中英文混合题目识别与匹配")
    print("=" * 60)

    # 自动打开浏览器
    time.sleep(2)
    try:
        subprocess.run(['xdg-open', 'http://localhost:5000'])
    except:
        print("请手动打开浏览器访问: http://localhost:5000")

    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n程序退出")
        is_running = False

if __name__ == "__main__":
    main()
