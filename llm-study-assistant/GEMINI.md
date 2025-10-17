# 🎨 本地LLM学习助手

一个集成RAG知识检索和OBS录屏功能的学习辅助工具。仅用于学习练习，**不支持考试期间实时答题**。

## 📝 项目当前状态 (2025-10-17)
- **核心功能**: **项目已完成重大架构重构**。前后端服务均可稳定运行，LLM和OBS服务连接正常。
- **重构概要**:
    - **架构**: 从扁平化脚本升级为采用 `src`-layout 的可安装Python包 (`assistant`)。
    - **稳定性**: 彻底解决了因原项目结构问题导致的各类导入、语法和运行时错误。
    - **调试能力**: 为核心服务连接增加了详细的日志记录。
- **已知问题**: 视频分析问答功能（OCR+RAG）的准确性有待提高，是下一阶段的优化重点。
- **开发日志**: 详细的开发和修复记录位于 `logs/development_log.md`。
- **待办事项**: 下一步的开发计划和优化点记录在 `logs/TODO.md` 中。

## 🚀 快速开始

### 1. 安装和初始化
```bash
# 克隆或下载项目
cd llm-study-assistant

# 运行初始化脚本 (只需运行一次)
# 该脚本会安装依赖并将项目以可编辑模式安装
chmod +x setup.sh scripts/*.sh
./setup.sh
```

### 2. 启动Ollama服务
```bash
# 在一个独立的终端中启动
./scripts/start_ollama.sh
```

### 3. 启动主应用
```bash
# 在另一个终端中，确保你的虚拟环境已激活
# (e.g., source .venv/bin/activate)
python run.py
# 或者使用脚本
# ./scripts/start_server.sh
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

## 💻 API使用示例 (注意: 路径已更新)

### 上传文档
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@./path/to/your/document.pdf"
```

### 提问
```bash
curl -X POST "http://localhost:8000/api/ask" \
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
curl -X POST "http://localhost:8000/api/obs/recording" \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'
```

## 🔍 故障排除
1.  **LLM/OBS服务显示“离线”**:
    - 检查后端终端的日志输出，新的日志系统会提供详细的连接失败原因。
    - 确认Ollama服务 (`./scripts/start_ollama.sh`) 和OBS Studio软件是否正在运行。
    - 检查 `.env` 中的配置是否正确。

2.  **点击“提问”后系统卡死或重启**:
    - `run.py` 中的 `OMP_NUM_THREADS=1` 设置应已解决此问题。如仍出现，请勿删除该行代码。

## ⚠️ 重要声明
**本系统仅用于学习和练习目的。严格禁止在考试期间使用。**

```