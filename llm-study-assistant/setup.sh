#!/bin/bash

# 本地LLM学习助手 - 安装和初始化脚本

echo "=== 安装和配置本地LLM学习助手 ==="

# 1. 检查Python环境
echo "步骤1: 检查Python环境"
python3 --version
if [ $? -ne 0 ]; then
    echo "错误：Python3未安装或不在PATH中"
    exit 1
fi

# 2. 安装Python依赖
echo "\n步骤2: 安装Python依赖"
uv pip install -r requirements.txt

echo "--- 正在以可编辑模式安装项目 ---"
pip install -e .

if [ $? -ne 0 ]; then
    echo "错误：Python依赖安装失败"
    exit 1
fi

# 3. 创建目录结构
echo "\n步骤3: 创建目录结构"
mkdir -p data/{uploads,index,recordings}
mkdir -p config
mkdir -p logs

# 4. 检查Ollama安装
echo "\n步骤4: 检查Ollama安装"
if [ -f "bin/ollama" ]; then
    echo "✓ Ollama可执行文件已存在"
    export PATH="$PWD/bin:$PATH"
else
    echo "✗ Ollama未找到，请手动安装或检查路径"
fi

# 5. 检查.env文件
echo "\n步骤5: 检查配置文件"
if [ ! -f ".env" ]; then
    echo "复制默认配置文件"
    cp .env.example .env
fi

echo "\n=== 初始化完成 ==="
echo "接下来请执行："
echo "1. 启动Ollama: ./scripts/start_ollama.sh"
echo "2. 下载模型: ./scripts/download_model.sh"
echo "3. 启动服务: ./scripts/start_server.sh"
