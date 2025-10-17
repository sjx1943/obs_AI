#!/bin/bash

# --- 脚本基本设置 ---
set -e # 遇到错误立即退出
cd "$(dirname "$0")/.." # 切换到项目根目录

# --- 颜色定义 ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== 启动本地LLM学习助手 ===${NC}"

# --- 检查Python虚拟环境 ---
echo "检查Python环境..."
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}警告：未检测到激活的Python虚拟环境。${NC}"
    echo "推荐在虚拟环境中运行以避免依赖冲突。"
    echo "您可以手动激活: source .venv/bin/activate"
    sleep 2
fi

# --- 检查Ollama服务 ---
echo "检查Ollama服务..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo -e "${RED}错误：Ollama服务未运行或无法访问。${NC}"
    echo "请在另一个终端中运行 './scripts/start_ollama.sh' 来启动它。"
    exit 1
fi
echo -e "✓ Ollama服务正在运行"

# --- 启动主应用 ---
echo "正在启动服务..."
echo "服务地址: http://$(grep API_HOST .env | cut -d '=' -f2):$(grep API_PORT .env | cut -d '=' -f2)"
echo "API文档: http://$(grep API_HOST .env | cut -d '=' -f2):$(grep API_PORT .env | cut -d '=' -f2)/docs"
echo "按 Ctrl+C 停止服务"
echo ""

# 直接执行run.py，这是新的、正确的启动方式
python run.py