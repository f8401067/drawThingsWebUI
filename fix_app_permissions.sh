#!/bin/bash

echo "=========================================="
echo "  DrawThings WebUI - 修复应用启动问题"
echo "=========================================="
echo ""

APP_PATH="dist/DrawThings WebUI.app"

# 检查应用是否存在
if [ ! -d "$APP_PATH" ]; then
    echo "❌ 错误: 找不到应用 $APP_PATH"
    echo "请先运行: python build_standalone.py"
    exit 1
fi

echo "[步骤 1] 清除 macOS 隔离属性..."
xattr -cr "$APP_PATH" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 隔离属性已清除"
else
    echo "⚠️  清除隔离属性时出现警告（可忽略）"
fi
echo ""

echo "[步骤 2] 检查应用完整性..."
if [ -f "$APP_PATH/Contents/MacOS/DrawThingsWebUI" ]; then
    echo "✅ 可执行文件存在"
else
    echo "❌ 可执行文件缺失"
    exit 1
fi

if [ -f "$APP_PATH/Contents/Info.plist" ]; then
    echo "✅ Info.plist 存在"
else
    echo "❌ Info.plist 缺失"
    exit 1
fi
echo ""

echo "[步骤 3] 设置正确的权限..."
chmod +x "$APP_PATH/Contents/MacOS/DrawThingsWebUI"
echo "✅ 权限已设置"
echo ""

echo "=========================================="
echo "  修复完成！"
echo "=========================================="
echo ""
echo "现在可以尝试以下方法打开应用："
echo ""
echo "方法 1: 双击应用图标"
echo "  open \"$APP_PATH\""
echo ""
echo "方法 2: 右键点击 → 打开"
echo "  然后选择\"打开\""
echo ""
echo "方法 3: 通过系统设置"
echo "  1. 系统偏好设置 → 安全性与隐私"
echo "  2. 点击\"仍要打开\""
echo ""
echo "如果仍然无法打开，请尝试："
echo "  sudo spctl --master-disable"
echo "  （这会临时禁用 Gatekeeper，使用后建议重新启用）"
echo ""

# 询问是否立即打开
read -p "是否现在打开应用？(y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "正在打开应用..."
    open "$APP_PATH"
    echo ""
    echo "💡 提示: 如果看到安全警告，请:"
    echo "   1. 点击\"取消\""
    echo "   2. 系统偏好设置 → 安全性与隐私"
    echo "   3. 点击\"仍要打开\""
    echo "   4. 再次双击应用"
fi
