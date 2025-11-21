# 本地LLM学习助手

一个集成RAG知识检索和OBS录屏功能的学习辅助工具。

## 功能特性

- 基于本地LLM的智能问答
- RAG（检索增强生成）知识检索
- 文档上传和管理
- OBS录屏集成
- 视频内容分析

## 快速开始

### 环境准备

1. 确保已安装Python 3.9+
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 安装并启动Ollama服务：
   ```bash
   brew install ollama
   ollama serve
   ```

4. 下载Qwen2.5模型：
   ```bash
   ollama pull qwen2.5:3b
   ```

### 启动服务

```bash
python run.py
```

服务将在 `http://localhost:8000` 上运行。

### 运行综合测试

要运行综合RAG功能测试：

```bash
# 使用脚本自动激活虚拟环境并运行测试
./scripts/run_comprehensive_test.sh

# 或者手动激活虚拟环境后运行
source venv/bin/activate
python test_comprehensive_rag.py
```

## 项目结构

- `src/` - 核心源代码
- `data/` - 数据存储目录
- `logs/` - 日志文件
- `scripts/` - 辅助脚本
- `docs/` - 文档

## API接口

- `GET /api/health` - 健康检查
- `POST /api/upload` - 上传文档
- `POST /api/ask` - 提问
- `GET /api/knowledge/stats` - 知识库统计

## 配置

通过 `.env` 文件进行配置：

- `OPENAI_API_BASE` - LLM API地址
- `LLM_MODEL` - 使用的模型
- `EMBEDDING_MODEL` - 嵌入模型
- `API_HOST` - API主机地址
- `API_PORT` - API端口