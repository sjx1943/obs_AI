#!/bin/bash

# 自动化测试流程脚本

# 检查并安装依赖项
check_and_install_dependencies() {
    echo "Checking and installing dependencies..."
    
    # 获取项目根目录
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
    
    # 激活虚拟环境（如果存在）
    if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
        source "$PROJECT_ROOT/venv/bin/activate"
        echo "Virtual environment activated."
    else
        echo "Warning: Virtual environment not found."
    fi
    
    # 检查是否安装了pip
    if ! command -v pip &> /dev/null; then
        echo "pip is not installed. Please install Python and pip."
        exit 1
    fi
    
    # 安装依赖项
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        pip install -r "$PROJECT_ROOT/requirements.txt"
        if [ $? -eq 0 ]; then
            echo "Dependencies installed successfully."
        else
            echo "Failed to install dependencies."
            exit 1
        fi
    else
        echo "Warning: requirements.txt not found."
    fi
}



# 检查Ollama服务是否正在运行
check_ollama_service() {
    if pgrep -x "ollama" > /dev/null; then
        echo "Ollama service is already running."
        return 0
    else
        echo "Ollama service is not running."
        return 1
    fi
}

# 启动Ollama服务
start_ollama_service() {
    echo "Starting Ollama service..."
    ollama serve > /dev/null 2>&1 &
    
    # 等待服务启动
    sleep 5
    
    # 检查服务是否成功启动
    if check_ollama_service; then
        echo "Ollama service started successfully."
    else
        echo "Failed to start Ollama service."
        exit 1
    fi
}

# 加载所需模型
load_model() {
    model_name="qwen2.5:3b"
    echo "Loading model: $model_name"
    
    # 尝试加载模型
    if ollama list | grep -q "$model_name"; then
        echo "Model $model_name is already loaded."
    else
        echo "Model $model_name is not loaded. Loading now..."
        ollama pull "$model_name"
        
        if [ $? -eq 0 ]; then
            echo "Model $model_name loaded successfully."
        else
            echo "Failed to load model $model_name."
            exit 1
        fi
    fi
}

# 运行测试脚本
run_tests() {
    echo "Running automated tests..."
    
    # 获取脚本所在目录的父目录（即项目根目录）
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
    
    # 运行三路对比测试
    python "$PROJECT_ROOT/test_rag_three_way.py"
    
    if [ $? -eq 0 ]; then
        echo "Automated tests completed successfully."
    else
        echo "Automated tests failed."
        exit 1
    fi
}

# 主流程
main() {
    echo "Starting automated testing workflow..."
    
    # 检查并安装依赖项（会自动激活虚拟环境）
    check_and_install_dependencies
    
    # 检查并启动Ollama服务
    if ! check_ollama_service; then
        start_ollama_service
    fi
    
    # 加载所需模型
    load_model
    
    # 运行测试
    run_tests
    
    echo "Automated testing workflow completed."
}

# 执行主流程
main