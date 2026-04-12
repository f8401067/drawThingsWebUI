#!/bin/bash

# 测试 DrawThings WebUI.app 是否正常工作的脚本

echo "=========================================="
echo "  DrawThings WebUI.app - 诊断测试"
echo "=========================================="
echo ""

APP_PATH="/Volumes/MACSSD/work/drawThingsWebUI/DrawThings WebUI.app"

# 检查应用包是否存在
if [ ! -d "$APP_PATH" ]; then
    echo "❌ 错误: 应用包不存在"
    exit 1
fi
echo "✅ 应用包存在"

# 检查关键文件
echo ""
echo "检查关键文件..."

if [ -f "$APP_PATH/Contents/Info.plist" ]; then
    echo "  ✅ Info.plist"
else
    echo "  ❌ Info.plist (缺失)"
fi

if [ -f "$APP_PATH/Contents/MacOS/launch.sh" ]; then
    echo "  ✅ launch.sh"
else
    echo "  ❌ launch.sh (缺失)"
fi

if [ -f "$APP_PATH/Contents/Resources/requirements.txt" ]; then
    echo "  ✅ requirements.txt"
else
    echo "  ❌ requirements.txt (缺失)"
fi

if [ -d "$APP_PATH/Contents/Resources/src" ]; then
    echo "  ✅ src/ 目录"
else
    echo "  ❌ src/ 目录 (缺失)"
fi

if [ -d "$APP_PATH/Contents/Resources/static" ]; then
    echo "  ✅ static/ 目录"
else
    echo "  ❌ static/ 目录 (缺失)"
fi

# 检查 Python 环境
echo ""
echo "检查 Python 环境..."
if command -v python3 &> /dev/null; then
    echo "  ✅ Python3: $(python3 --version)"
else
    echo "  ❌ Python3 未安装"
fi

# 检查启动脚本权限
echo ""
echo "检查启动脚本权限..."
if [ -x "$APP_PATH/Contents/MacOS/launch.sh" ]; then
    echo "  ✅ launch.sh 有执行权限"
else
    echo "  ⚠️  launch.sh 缺少执行权限，正在修复..."
    chmod +x "$APP_PATH/Contents/MacOS/launch.sh"
    echo "  ✅ 已修复"
fi

# 检查日志目录
echo ""
echo "检查日志目录..."
LOG_DIR="$APP_PATH/Contents/Resources/data/logs"
if [ -d "$LOG_DIR" ]; then
    echo "  ✅ 日志目录存在"
    if [ -f "$LOG_DIR/app_launch.log" ]; then
        echo "  ✅ 启动日志文件存在"
        echo ""
        echo "最近的启动日志（最后10行）："
        echo "----------------------------------------"
        tail -10 "$LOG_DIR/app_launch.log"
        echo "----------------------------------------"
    else
        echo "  ⚠️  启动日志文件不存在（尚未启动过）"
    fi
else
    echo "  ⚠️  日志目录不存在"
fi

# 检查端口占用
echo ""
echo "检查服务器状态..."
if curl -s http://localhost:5001 >/dev/null 2>&1; then
    echo "  ⚠️  服务器已在运行 (http://localhost:5001)"
    echo "  提示: 如需重新测试，请先停止当前服务器"
else
    echo "  ✅ 服务器未运行（可以启动测试）"
fi

echo ""
echo "=========================================="
echo "  诊断完成"
echo "=========================================="
echo ""
echo "下一步操作："
echo "  1. 双击应用测试: open \"$APP_PATH\""
echo "  2. 或命令行测试: \"$APP_PATH/Contents/MacOS/launch.sh\""
echo "  3. 查看详细文档: open MACOS_APP_GUIDE.md"
echo ""
