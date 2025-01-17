#!/bin/bash

# 进入项目根目录
cd "$(dirname "$0")/.."

# 激活虚拟环境（如果有的话）
# source venv/bin/activate

# 设置环境变量
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 运行测试
echo "Running tests..."
pytest tests/ -v --cov=app --cov-report=term-missing

# 运行代码风格检查
echo "Running style checks..."
flake8 app/ tests/
black app/ tests/ --check
isort app/ tests/ --check-only

# 如果所有命令都成功执行，显示成功消息
if [ $? -eq 0 ]; then
    echo "All tests and checks passed successfully!"
    exit 0
else
    echo "Tests or checks failed!"
    exit 1
fi