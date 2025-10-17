#!/bin/bash

# 下载适合的LLM模型

echo "=== 下载本地LLM模型 ==="

# 检查Ollama服务是否运行
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✗ Ollama服务未运行，请先执行 ./scripts/start_ollama.sh"
    exit 1
fi

echo "✓ Ollama服务正在运行"

# 可选模型列表（按大小排序）
echo "\n可用模型选项："
echo "1. llama3.2:1b (约1GB, 最轻量)"
echo "2. llama3.2:3b (约2GB, 推荐)"
echo "3. qwen2.5:3b (约2GB, 中文优化)"
echo "4. gemma2:2b (约2GB)"
echo "5. 自定义模型名"

# 用户选择
echo "\n请选择要下载的模型 (1-5): "
read choice

case $choice in
    1)
        MODEL="llama3.2:1b"
        INSTRUCT_MODEL="llama3.2:1b-instruct-q4_0"
        ;;
    2)
        MODEL="llama3.2:3b"
        INSTRUCT_MODEL="llama3.2:3b-instruct-q4_0"
        ;;
    3)
        MODEL="qwen2.5:3b"
        INSTRUCT_MODEL="qwen2.5:3b-instruct-q4_0"
        ;;
    4)
        MODEL="gemma2:2b"
        INSTRUCT_MODEL="gemma2:2b-instruct-q4_0"
        ;;
    5)
        echo "请输入模型名 (e.g., llama3.2:3b-instruct-q4_0): "
        read INSTRUCT_MODEL
        MODEL=$INSTRUCT_MODEL
        ;;
    *)
        echo "无效选择，使用默认模型: llama3.2:3b-instruct-q4_0"
        MODEL="llama3.2:3b"
        INSTRUCT_MODEL="llama3.2:3b-instruct-q4_0"
        ;;
esac

echo "\n将下载模型: $INSTRUCT_MODEL"
echo "请等待，这可能需要几分钟..."

# 下载模型
OLLAMA_BIN=""
if [ -f "bin/ollama" ]; then
    OLLAMA_BIN="./bin/ollama"
else
    OLLAMA_BIN="ollama"
fi

$OLLAMA_BIN pull $INSTRUCT_MODEL

if [ $? -eq 0 ]; then
    echo "\n✓ 模型下载成功: $INSTRUCT_MODEL"
    
    # 更新.env文件
    if [ -f ".env" ]; then
        sed -i "s/LLM_MODEL=.*/LLM_MODEL=$INSTRUCT_MODEL/g" .env
        echo "✓ 已更新.env文件中的LLM_MODEL设置"
    fi
    
    echo "\n模型已准备就绪！您现在可以启动服务: ./scripts/start_server.sh"
else
    echo "\n✗ 模型下载失败"
    echo "请检查网络连接或模型名称是否正确"
    exit 1
fi
