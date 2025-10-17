# 🎨 本地LLM学习助手

一个集成RAG知识检索和OBS录屏功能的学习辅助工具。仅用于学习练习，**不支持考试期间实时答题**。

## 📝 项目当前状态 (2025-10-11)
- **核心功能**: 前后端服务均可稳定运行。文档上传、RAG问答、OBS录屏控制等核心功能已基本实现。
- **已知问题**: 视频分析问答功能（OCR+RAG）的准确性有待提高，是下一阶段的优化重点。
- **开发日志**: 详细的开发和修复记录位于 `logs/development_log.md`。
- **待办事项**: 下一步的开发计划和优化点记录在 `logs/TODO.md` 中。

## 🏁 功能特性

### 📚 RAG学习助手
- **文档上传**: 支持PDF/Word/Excel/文本文件
- **智能分块**: 自动文本分块和向量化存储
- **题型识别**: 自动识别单选/多选/判断/主观题
- **本地LLM**: 集成Ollama，无需依赖云端服务

### 🎥 OBS录屏集成
- **远程控制**: 通过API控制OBS录屏开始/停止/暂停
- **状态监控**: 实时监控录屏状态
- **下一步**: 优化屏幕OCR文字识别与RAG问答流程的准确性。

### 🛑 学习合规检查
- **考试检测**: 自动识别并拒绝考试相关请求
- **安全限制**: 防止在考试环境中使用

## 🚀 快速开始

### 1. 安装和初始化
```bash
# 克隆或下载项目
cd llm-study-assistant

# 运行初始化脚本 (只需运行一次)
chmod +x setup.sh scripts/*.sh
./setup.sh
```

### 2. 启动Ollama服务
```bash
./scripts/start_ollama.sh
```

### 3. 启动主应用
```bash
# 确保你的虚拟环境已激活 (e.g., source .venv/bin/activate)
python run.py
```

### 4. 访问系统
- **前端界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 🔧 关键配置 (.env)
```bash
# LLM配置
LLM_MODEL=llama3.2:1b-instruct-q4_0

# 向量模型
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5

# OBS配置
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=your_obs_websocket_password

# 服务配置
API_HOST=0.0.0.0
API_PORT=8000
```

## 💻 API使用示例

### 上传文档
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@./path/to/your/document.pdf"
```

### 提问
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d 
  {
    "type": "auto",
    "question": "什么是机器学习？",
    "top_k": 5
  }
```

### 控制录屏

```bash
# action可以是 "start", "stop", "pause", "resume"
curl -X POST "http://localhost:8000/obs/recording" \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'
```

## 🔍 故障排除

1.  **LLM服务显示“离线”**:
    - 确认已运行 `./scripts/start_ollama.sh`。
    - 检查 `logs/ollama.log` 是否有错误。
    - 运行 `curl http://localhost:11434/api/tags` 确认模型是否加载。

2.  **点击“提问”后系统卡死或重启**:
    - 这是向量化计算耗尽CPU资源的迹象。`run.py` 中的 `OMP_NUM_THREADS=1` 设置应已解决此问题。如仍出现，请勿删除该行代码。

3.  **OBS录屏失败**:
    - 确保OBS Studio软件正在运行。
    - 检查 `.env` 中的OBS密码是否与OBS WebSocket设置中的密码一致。
    - **必须**在OBS的“设置” -> “输出” -> “录像”中设置一个有效的“录像路径”。

## ⚠️ 重要声明
**本系统仅用于学习和练习目的。严格禁止在考试期间使用。
