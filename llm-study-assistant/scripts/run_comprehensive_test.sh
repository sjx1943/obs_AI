#!/bin/bash

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 激活虚拟环境
echo "激活虚拟环境..."
source "$PROJECT_ROOT/venv/bin/activate"

# 检查是否成功激活虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "错误: 未能激活虚拟环境"
    exit 1
fi

echo "虚拟环境已激活: $VIRTUAL_ENV"

# 运行综合RAG测试
echo "运行综合RAG测试..."
cd "$PROJECT_ROOT"
python test_comprehensive_rag.py

echo "测试完成!"