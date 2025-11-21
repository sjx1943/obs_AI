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
echo "5. 批量下载推荐模型 (选项2,3,4)"
echo "6. 自定义模型名"

# 用户选择
echo "\n请选择要下载的模型 (1-6): "
read choice

# 定义模型数组
models_to_download=()

case $choice in
    1)
        models_to_download=("llama3.2:1b-instruct-q4_0")
        ;;
    2)
        models_to_download=("llama3.2:3b-instruct-q4_0")
        ;;
    3)
        models_to_download=("qwen2.5:3b-instruct-q4_0")
        ;;
    4)
        models_to_download=("gemma2:2b-instruct-q4_0")
        ;;
    5)
        models_to_download=("llama3.2:3b-instruct-q4_0" "qwen2.5:3b-instruct-q4_0" "gemma2:2b-instruct-q4_0")
        echo "将批量下载推荐模型..."
        ;;
    6)
        echo "请输入模型名 (e.g., llama3.2:3b-instruct-q4_0): "
        read CUSTOM_MODEL
        models_to_download=("$CUSTOM_MODEL")
        ;;
    *)
        echo "无效选择，使用默认模型: llama3.2:3b-instruct-q4_0"
        models_to_download=("llama3.2:3b-instruct-q4_0")
        ;;
esac

# 获取已存在的模型列表
echo "\n检查已存在的模型..."
EXISTING_MODELS=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | sed 's/"name":"//;s/"//g')
echo "已存在的模型: $EXISTING_MODELS"

# 下载模型
OLLAMA_BIN=""
if [ -f "bin/ollama" ]; then
    OLLAMA_BIN="./bin/ollama"
else
    OLLAMA_BIN="ollama"
fi

success_count=0
total_count=${#models_to_download[@]}
skipped_count=0

for INSTRUCT_MODEL in "${models_to_download[@]}"; do
    # 检查模型是否已存在
    if echo "$EXISTING_MODELS" | grep -q "$INSTRUCT_MODEL"; then
        echo "\n⚠ 模型已存在，跳过下载: $INSTRUCT_MODEL"
        skipped_count=$((skipped_count + 1))
        success_count=$((success_count + 1))
        
        # 如果只下载了一个模型，则更新.env文件
        if [ $total_count -eq 1 ]; then
            if [ -f ".env" ]; then
                sed -i.bak "s/LLM_MODEL=.*/LLM_MODEL=$INSTRUCT_MODEL/g" .env && rm .env.bak
                echo "✓ 已更新.env文件中的LLM_MODEL设置"
            fi
        fi
        continue
    fi
    
    echo "\n将下载模型: $INSTRUCT_MODEL"
    echo "请等待，这可能需要几分钟..."
    
    $OLLAMA_BIN pull $INSTRUCT_MODEL
    
    if [ $? -eq 0 ]; then
        echo "\n✓ 模型下载成功: $INSTRUCT_MODEL"
        success_count=$((success_count + 1))
        
        # 如果只下载了一个模型，则更新.env文件
        if [ $total_count -eq 1 ]; then
            if [ -f ".env" ]; then
                sed -i.bak "s/LLM_MODEL=.*/LLM_MODEL=$INSTRUCT_MODEL/g" .env && rm .env.bak
                echo "✓ 已更新.env文件中的LLM_MODEL设置"
            fi
        fi
    else
        echo "\n✗ 模型下载失败: $INSTRUCT_MODEL"
        echo "请检查网络连接或模型名称是否正确"
    fi
done

if [ $success_count -eq $total_count ]; then
    echo "\n✓ 所有模型处理完成 ($success_count/$total_count)"
    if [ $skipped_count -gt 0 ]; then
        echo "  - 下载: $((success_count - skipped_count)) 个模型"
        echo "  - 跳过: $skipped_count 个已存在模型"
    fi
    
    if [ $total_count -eq 1 ]; then
        echo "\n模型已准备就绪！您现在可以启动服务: ./scripts/start_server.sh"
    else
        echo "\n推荐模型已准备就绪！您可以开始模型对比测试。"
    fi
elif [ $success_count -gt 0 ]; then
    echo "\n⚠ 部分模型处理完成 ($success_count/$total_count)"
    if [ $skipped_count -gt 0 ]; then
        echo "  - 下载: $((success_count - skipped_count)) 个模型"
        echo "  - 跳过: $skipped_count 个已存在模型"
    fi
else
    echo "\n✗ 所有模型处理失败"
    exit 1
fi