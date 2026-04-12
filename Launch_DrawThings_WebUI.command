#!/bin/bash
# DrawThings WebUI - 桌面启动器
# 将此文件和 DrawThings WebUI.app 放在同一目录下，双击即可启动

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 查找应用路径（在当前目录下查找）
APP_PATH="$SCRIPT_DIR/DrawThings WebUI.app"

# 如果找不到，提示用户
if [ ! -d "$APP_PATH" ]; then
    osascript <<EOF
tell application "System Events"
    activate
    display dialog "找不到 DrawThings WebUI 应用！\n\n请确保 Launch_DrawThings_WebUI.command 和 DrawThings WebUI.app 在同一目录下。" buttons {"确定"} default button 1 with icon stop
end tell
EOF
    exit 1
fi

# 设置应用根目录环境变量并启动应用
osascript <<EOF
tell application "Terminal"
    if not (exists window 1) then reopen
    activate
    do script "export APP_ROOT_DIR='$SCRIPT_DIR' && '$APP_PATH/Contents/MacOS/DrawThingsWebUI'"
end tell
EOF
