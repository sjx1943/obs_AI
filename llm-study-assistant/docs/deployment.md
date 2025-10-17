# 🚀 部署和使用指南

## 📋 系统要求

### 基础环境
- **操作系统**: Linux (已测试) / macOS / Windows
- **Python**: 3.10+ (已安装Python 3.12)
- **内存**: 至少 4GB RAM (推荐 8GB+)
- **硬盘**: 至少 5GB 可用空间

### 依赖软件
- **Ollama**: 本地LLM运行环境 (已下载)
- **OBS Studio**: 录屏软件 (需手动安装)
- **Chrome/Firefox**: 现代浏览器

## 🔧 安装步骤

### 1. Python环境和依赖
```bash
# 当前环境已安装以下依赖
pip install fastapi uvicorn pydantic python-dotenv
pip install numpy pandas tqdm
pip install pdfplumber python-docx openpyxl
pip install openai requests aiofiles python-multipart
pip install websocket-client Pillow

# 机器学习库 (可选，用于向量搜索优化)
pip install sentence-transformers faiss-cpu
```

### 2. 本地LLM环境
✅ **已完成**: Ollama已下载并配置
- 位置: `/workspace/llm-study-assistant/bin/ollama`
- 模型: `llama3.2:1b-instruct-q4_0` (已下载)
- API端点: `http://localhost:11434`

### 3. OBS Studio配置 (需手动完成)
```bash
# Ubuntu/Debian
sudo apt install obs-studio

# macOS
brew install --cask obs

# Windows
# 从 https://obsproject.com 下载安装
```

**OBS WebSocket配置:**
1. 启动OBS Studio
2. 进入 `工具` > `WebSocket服务器设置`
3. 启用WebSocket服务器
4. 端口: `4455` (默认)
5. 密码: 留空或设置密码(需更新.env文件)

## 🚀 启动系统

### 方式一: 自动启动 (推荐)
```bash
cd /workspace/llm-study-assistant

# 1. 启动Ollama服务
./bin/ollama serve &

# 2. 等待几秒后启动主应用
sleep 5
python run.py
```

### 方式二: 分步启动
```bash
# 终端1: 启动Ollama
cd /workspace/llm-study-assistant
export OLLAMA_HOST=0.0.0.0:11434
./bin/ollama serve

# 终端2: 启动主应用
cd /workspace/llm-study-assistant
python run.py
```

## 🌐 访问系统

启动成功后，可以通过以下方式访问:

- **Web界面**: http://localhost:8000/frontend/index.html
- **API文档**: http://localhost:8000/docs
- **系统状态**: http://localhost:8000/system/status
- **健康检查**: http://localhost:8000/health

## 📚 功能使用

### RAG学习助手
1. **上传文档**: 支持PDF/Word/Excel/文本文件
2. **智能问答**: 自动识别题型并给出结构化答案
3. **知识检索**: 基于文档内容的相关性搜索

### OBS录屏集成
1. **连接OBS**: 系统自动检测OBS连接状态
2. **录屏控制**: 开始/停止/暂停/恢复录屏
3. **文件管理**: 查看、下载、删除录屏文件
4. **场景切换**: 控制OBS场景切换

### 学习合规检查
- 自动检测考试相关关键词
- 拒绝实时答题请求
- 记录合规检查日志

## 🔍 故障排除

### 常见问题

#### 1. Ollama连接失败
**症状**: LLM状态显示"离线"
**解决方案**:
```bash
# 检查Ollama进程
ps aux | grep ollama

# 重启Ollama
pkill ollama
./bin/ollama serve &

# 测试连接
curl http://localhost:11434/api/tags
```

#### 2. OBS连接失败
**症状**: OBS状态显示"离线"
**解决方案**:
1. 确保OBS Studio正在运行
2. 检查WebSocket设置是否启用
3. 验证端口(4455)和密码配置
4. 重启OBS Studio

#### 3. 文档解析失败
**症状**: 文件上传成功但解析失败
**解决方案**:
```bash
# 安装缺失的依赖
pip install pdfplumber python-docx pandas openpyxl

# 检查文件格式是否支持
curl http://localhost:8000/system/status
```

#### 4. Python应用启动失败
**症状**: 导入错误或模块未找到
**解决方案**:
```bash
# 检查Python路径
cd /workspace/llm-study-assistant
export PYTHONPATH=$PWD:$PWD/app:$PYTHONPATH
python run.py
```

### 日志查看
```bash
# Ollama日志
tail -f logs/ollama.log

# 应用日志
# 在终端中直接显示

# 系统日志
journalctl -f
```

## ⚙️ 配置定制

### 环境变量 (.env)
```env
# LLM配置
OPENAI_API_BASE=http://localhost:11434/v1
LLM_MODEL=llama3.2:1b-instruct-q4_0

# 向量模型 (可选)
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5

# OBS配置
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=

# 服务器配置
API_HOST=0.0.0.0
API_PORT=8000

# 文档处理
CHUNK_SIZE=500
CHUNK_OVERLAP=100
TOP_K=5
```

### 模型切换
```bash
# 下载其他模型
./bin/ollama pull qwen2.5:3b-instruct-q4_0
./bin/ollama pull gemma2:2b-instruct-q4_0

# 更新.env文件中的LLM_MODEL
# 重启应用生效
```

## 🔒 安全注意事项

1. **网络访问**: 默认绑定所有接口(0.0.0.0)，生产环境请限制访问
2. **文件上传**: 系统会保存上传的文件，注意敏感信息
3. **录屏文件**: 录屏文件通过HTTP可直接访问，注意隐私
4. **OBS控制**: 可远程控制OBS，请保护好访问权限

## 🔄 系统更新

### 模型更新
```bash
# 列出已安装模型
./bin/ollama list

# 更新模型
./bin/ollama pull llama3.2:1b-instruct-q4_0

# 删除旧模型
./bin/ollama rm old_model_name
```

### 代码更新
```bash
# 备份配置
cp .env .env.backup

# 更新代码后
# 恢复配置
cp .env.backup .env

# 重启服务
python run.py
```

## 📊 性能优化

### 系统资源
- **内存使用**: 1B模型约占用2-3GB内存
- **CPU使用**: 推理时CPU使用率较高
- **硬盘空间**: 模型文件约1GB，录屏文件根据长度变化

### 优化建议
1. 使用更小的模型(1B vs 3B)
2. 限制录屏文件数量和大小
3. 定期清理上传的文档
4. 使用SSD提升I/O性能

## 📞 支持和反馈

如遇问题或需要帮助:
1. 检查本文档的故障排除部分
2. 查看系统日志和错误信息
3. 通过相关渠道反馈问题

---

**⚠️ 免责声明**: 本系统仅供学习和研究使用，请遵守相关法律法规和学术诚信原则。