#!/bin/bash

# 启动Ollama服务的脚本

echo "=== 启动Ollama服务 ==="

# 检查是否已经在运行
if pgrep -f "ollama serve" > /dev/null; then
    echo "✓ Ollama服务已在运行"
    exit 0
fi

# 设置Ollama环境变量
export OLLAMA_HOST="0.0.0.0:11434"
export OLLAMA_ORIGINS="*"

# 检查Ollama可执行文件
OLLAMA_BIN=""
if [ -f "bin/ollama" ]; then
    OLLAMA_BIN="./bin/ollama"
elif command -v ollama &> /dev/null; then
    OLLAMA_BIN="ollama"
else
    echo "✗ 找不到Ollama可执行文件"
    echo "请先安装Ollama或使用setup.sh下载"
    exit 1
fi

echo "使用Ollama: $OLLAMA_BIN"

# 启动Ollama服务器（后台运行）
echo "正在启动Ollama服务器..."
nohup $OLLAMA_BIN serve > logs/ollama.log 2>&1 &
OLLAMA_PID=$!

# 等待服务器启动
echo "等待服务器启动..."
sleep 5

# 检查服务器是否正常运行
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✓ Ollama服务器启动成功 (PID: $OLLAMA_PID)"
    echo "服务地址: http://localhost:11434"
    echo "日志文件: logs/ollama.log"
else
    echo "✗ Ollama服务器启动失败"
    echo "请检查日志: logs/ollama.log"
    exit 1
fi
