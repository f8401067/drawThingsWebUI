#!/bin/bash
# 开发者快速启动脚本

cd "$(dirname "$0")"

# 设置应用根目录为当前目录（项目根目录）
export APP_ROOT_DIR="$(pwd)"

echo "============================================================"
echo "  DrawThings WebUI - 开发者模式"
echo "============================================================"
echo ""
echo "[信息] 应用根目录: $APP_ROOT_DIR"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[提示] 未找到虚拟环境，正在创建..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 检查并停止占用端口的进程
PORT=9898
PID=$(lsof -ti:$PORT 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "[提示] 端口 $PORT 已被占用 (PID: $PID)"
    read -p "是否停止旧进程？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill $PID 2>/dev/null
        sleep 1
        echo "[完成] 旧进程已停止"
    fi
fi

echo ""
echo "[启动] 正在启动开发服务器..."
echo "[提示] 按 Ctrl+C 停止服务器"
echo ""

# 启动应用
python launcher.py
