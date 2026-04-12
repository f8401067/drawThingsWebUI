#!/bin/bash
# 创建分发包脚本
# 运行此脚本会生成一个可以分发的zip文件

cd "$(dirname "$0")"

echo "============================================================"
echo "  创建 DrawThings WebUI 分发包"
echo "============================================================"
echo ""

# 设置变量
APP_NAME="DrawThings WebUI"
DIST_DIR="dist"
APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
LAUNCHER="Launch_DrawThings_WebUI.command"
PACKAGE_NAME="DrawThings_WebUI_MacOS"
PACKAGE_DIR="/tmp/$PACKAGE_NAME"

# 检查必要文件是否存在
if [ ! -d "$APP_BUNDLE" ]; then
    echo "[错误] 找不到应用包: $APP_BUNDLE"
    echo "请先运行: python build_standalone.py"
    exit 1
fi

if [ ! -f "$LAUNCHER" ]; then
    echo "[错误] 找不到启动器: $LAUNCHER"
    exit 1
fi

# 清理旧的临时目录
if [ -d "$PACKAGE_DIR" ]; then
    rm -rf "$PACKAGE_DIR"
fi

# 创建分发包目录结构
echo "[1/4] 创建目录结构..."
mkdir -p "$PACKAGE_DIR"

# 复制应用包
echo "[2/4] 复制应用包..."
cp -R "$APP_BUNDLE" "$PACKAGE_DIR/"

# 复制启动器
echo "[3/4] 复制启动器..."
cp "$LAUNCHER" "$PACKAGE_DIR/"

# 创建README
echo "[4/4] 创建使用说明..."
cat > "$PACKAGE_DIR/README.md" << 'EOF'
# DrawThings WebUI for macOS

## 快速开始

1. **双击** `Launch_DrawThings_WebUI.command` 文件
2. Terminal 窗口会自动打开，显示服务器日志
3. 浏览器会自动打开 http://localhost:9898
4. 开始使用！

## 停止服务器

在 Terminal 窗口中按 `Ctrl+C`

## 配置文件

首次启动会自动创建配置文件，位置：
`DrawThings WebUI.app/Contents/MacOS/config.json`

你可以编辑此文件修改端口等设置。

## 系统要求

- macOS 10.15 或更高版本
- 无需安装 Python 或其他依赖

## 问题反馈

如有问题，请联系开发者。
EOF

# 创建zip文件
echo ""
echo "正在压缩..."
cd /tmp
rm -f "$PACKAGE_NAME.zip"  # 删除旧的zip文件
zip -r "$PACKAGE_NAME.zip" "$PACKAGE_NAME" -x "*.DS_Store" -x "__MACOSX/*"

# 移动zip到项目目录
if [ -f "/tmp/$PACKAGE_NAME.zip" ]; then
    mv "/tmp/$PACKAGE_NAME.zip" "$(dirname "$0")/"
fi

# 清理
rm -rf "$PACKAGE_DIR"

echo ""
echo "============================================================"
echo "  ✅ 分发包创建完成！"
echo "============================================================"
echo ""
echo "文件位置: $(dirname "$0")/$PACKAGE_NAME.zip"
echo ""
echo "分发说明:"
echo "  1. 将 $PACKAGE_NAME.zip 发送给用户"
echo "  2. 用户解压后，双击 Launch_DrawThings_WebUI.command 即可启动"
echo ""
