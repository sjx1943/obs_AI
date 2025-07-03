```markdown
# OBS AI 智能答题助手

## 项目简介
OBS AI 智能答题助手是一个基于OCR技术和模糊匹配算法的智能答题系统，能够实时识别屏幕或摄像头中的题目，并从题库中查找匹配答案。系统支持中英文混合题目识别，具有高精度的模糊匹配能力。

## 功能特性
- 🎯 实时视频流题目识别
- 🔍 中英文混合OCR识别
- 📚 题库模糊匹配（支持语义相似度计算）
- 💡 智能关键词提取与匹配
- 🌐 基于Flask的Web界面
- 📊 实时统计与结果显示

## 技术栈
- Python 3.x
- OpenCV (视频处理)
- Pytesseract (OCR识别)
- Flask (Web界面)
- SQLite (题库存储)
- Jieba (中文分词)

## 安装与配置

### 前置要求
- 安装Python 3.7+
- 安装Tesseract OCR引擎

```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr tesseract-ocr-chi-sim

# Windows (使用choco)
choco install tesseract
choco install tesseract-languages
```

### 安装依赖
```bash
pip install -r requirements.txt
```

### 依赖列表
```
opencv-python
pytesseract
flask
flask-cors
jieba
numpy
```

## 使用说明

### 准备题库
编辑 `questions.csv` 文件，格式为 `问题,答案`，支持中英文。

### 启动系统
运行主程序：
```bash
python auto_answer_system.py
```

### 访问Web界面
系统启动后，在浏览器中访问：
```
http://localhost:5000
```

### 基本操作
1. 点击"开始录制"启动视频处理
2. "测试OCR"可进行单次识别测试
3. "导出结果"可保存识别记录
4. "上传题库"可更新题库内容

## 文件说明
- `auto_answer_system.py` - 主程序，包含视频处理、OCR识别和Web服务
- `question_lookup.py` - OCR测试脚本
- `questions.csv` - 示例题库文件
- `question_bank.db` - SQLite题库数据库（运行后自动生成）

## 开发指南

### 自定义配置

#### 视频源设置
修改 `process_video_stream()` 函数中的 `video_sources` 列表

#### OCR参数调整
修改 `enhanced_ocr()` 函数中的配置参数

#### 匹配算法优化
调整 `query_database_fuzzy()` 中的相似度计算权重

### 扩展功能
- 添加新的题库导入格式支持
- 集成更多OCR引擎
- 增加题目类型分类
- 开发移动端应用

## 常见问题

### Q: OCR识别率低怎么办？
**A:** 尝试：
- 调整摄像头位置和光线
- 修改 `preprocess_image()` 中的图像处理参数
- 使用更高分辨率的视频源

### Q: 匹配准确率不高？
**A:** 可以：
- 扩充题库内容
- 调整 `query_database_fuzzy()` 中的阈值
- 优化问题分割逻辑

### Q: 如何支持更多语言？
**A:** 安装对应的Tesseract语言包并修改OCR配置

## 贡献指南
欢迎提交Pull Request或Issue。主要开发方向：
- 提高OCR识别准确率
- 优化模糊匹配算法
- 增强系统稳定性

## 许可证
MIT License

## 联系方式
如有问题请联系项目维护者或提交Issue。

---

**提示：** 首次运行前请确保已安装所有依赖，并准备好题库文件。系统会自动创建数据库文件。
```
