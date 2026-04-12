#!/bin/bash

# DrawThings WebUI - 简化版一键启动脚本
# 适用于不想创建 .app 包的用户
# 用法: ./quick_start.sh [--port PORT]

set -e

# 默认端口
PORT=9898

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            echo "用法: ./quick_start.sh [--port PORT]"
            exit 1
            ;;
    esac
done

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  DrawThings WebUI - 快速启动${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[错误] 未找到 Python3${NC}"
    echo "请访问 https://www.python.org/downloads/ 下载安装"
    exit 1
fi

echo -e "${GREEN}[✓]${NC} Python3: $(python3 --version)"

# 检查并创建虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}[!]${NC} 创建虚拟环境..."
    python3 -m venv venv
    echo -e "${GREEN}[✓]${NC} 虚拟环境创建完成"
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}[!]${NC} 检查依赖..."
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    echo -e "${GREEN}[✓]${NC} 依赖检查完成"
fi

# 检查 DrawThings
echo -e "${YELLOW}[!]${NC} 检查 DrawThings 服务..."
DRAWTHINGS_URL="http://127.0.0.1:7888"

# 尝试从配置文件读取 URL
if [ -f "config.json" ]; then
    DRAWTHINGS_URL=$(python3 -c "import json; config=json.load(open('config.json')); print(config.get('drawthings_url', 'http://127.0.0.1:7888'))" 2>/dev/null || echo "http://127.0.0.1:7888")
fi

if curl -s --connect-timeout 2 "$DRAWTHINGS_URL" >/dev/null 2>&1; then
    echo -e "${GREEN}[✓]${NC} DrawThings 服务正常 ($DRAWTHINGS_URL)"
else
    echo -e "${YELLOW}[!]${NC} 警告: 无法连接到 DrawThings ($DRAWTHINGS_URL)"
    echo "请确保 DrawThings 已启动并启用了 HTTP Server"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  启动服务器...${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "地址: ${YELLOW}http://localhost:${PORT}${NC}"
echo -e "按 ${RED}Ctrl+C${NC} 停止"
echo ""

# 自动打开浏览器
(sleep 2 && open http://localhost:${PORT}) &

# 启动应用
python3 src/app.py --port ${PORT}
