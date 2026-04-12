#!/bin/bash
# DrawThings WebUI - 桌面启动器
# 将此文件复制到桌面或其他位置，双击即可启动

# 获取脚本所在目录（支持从桌面等位置运行）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 查找应用路径（优先查找当前目录，然后是上级目录）
APP_PATH=""

if [ -d "$SCRIPT_DIR/dist/DrawThings WebUI.app" ]; then
    APP_PATH="$SCRIPT_DIR/dist/DrawThings WebUI.app"
elif [ -d "$SCRIPT_DIR/../dist/DrawThings WebUI.app" ]; then
    APP_PATH="$SCRIPT_DIR/../dist/DrawThings WebUI.app"
elif [ -d "/Volumes/MACSSD/work/drawThingsWebUI/dist/DrawThings WebUI.app" ]; then
    APP_PATH="/Volumes/MACSSD/work/drawThingsWebUI/dist/DrawThings WebUI.app"
fi

# 如果还是找不到，提示用户
if [ -z "$APP_PATH" ]; then
    osascript <<EOF
tell application "System Events"
    activate
    display dialog "找不到 DrawThings WebUI 应用！\n\n请确保应用位于以下位置之一：\n• 当前目录/dist/\n• 上级目录/dist/\n• /Volumes/MACSSD/work/drawThingsWebUI/dist/" buttons {"确定"} default button 1 with icon stop
end tell
EOF
    exit 1
fi

# 打开 Terminal 并运行应用
osascript <<EOF
tell application "Terminal"
    if not (exists window 1) then reopen
    activate
    do script "cd '$(dirname "$APP_PATH")' && './$(basename "$APP_PATH")/Contents/MacOS/DrawThingsWebUI'"
end tell
EOF
