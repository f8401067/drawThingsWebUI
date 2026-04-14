#!/bin/bash

# GitHub Hosts 配置脚本
# 此脚本会将 GitHub 相关域名添加到 /etc/hosts 文件中

echo "正在获取最新的 GitHub IP 地址..."

# 获取 GitHub 相关域名的 IP 地址
GITHUB_IP=$(nslookup github.com 8.8.8.8 2>/dev/null | grep "Address:" | tail -1 | awk '{print $2}')
API_GITHUB_IP=$(nslookup api.github.com 8.8.8.8 2>/dev/null | grep "Address:" | tail -1 | awk '{print $2}')
FASTLY_IP=$(nslookup github.global.ssl.fastly.net 8.8.8.8 2>/dev/null | grep "Address:" | tail -1 | awk '{print $2}')

echo "github.com: $GITHUB_IP"
echo "api.github.com: $API_GITHUB_IP"
echo "github.global.ssl.fastly.net: $FASTLY_IP"

# 备份原始 hosts 文件
sudo cp /etc/hosts /etc/hosts.backup.$(date +%Y%m%d%H%M%S)
echo "已备份原始 hosts 文件到 /etc/hosts.backup.*"

# 准备要添加的配置
HOSTS_CONFIG="
# GitHub hosts configuration (added on $(date))
$GITHUB_IP github.com
$GITHUB_IP www.github.com
$API_GITHUB_IP api.github.com
$FASTLY_IP github.global.ssl.fastly.net
"

# 检查是否已经存在 GitHub 配置
if grep -q "github.com" /etc/hosts; then
    echo "检测到 hosts 文件中已存在 GitHub 配置，将先删除旧配置..."
    sudo sed -i '' '/# GitHub hosts configuration/d' /etc/hosts
    sudo sed -i '' '/github\.com/d' /etc/hosts
    sudo sed -i '' '/api\.github\.com/d' /etc/hosts
    sudo sed -i '' '/github\.global\.ssl\.fastly\.net/d' /etc/hosts
fi

# 添加新的配置
echo "$HOSTS_CONFIG" | sudo tee -a /etc/hosts > /dev/null

echo ""
echo "✓ GitHub hosts 配置已更新！"
echo ""
echo "新的配置："
echo "$HOSTS_CONFIG"
echo ""
echo "请刷新 DNS 缓存以使更改生效："
echo "  sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder"
echo ""
echo "然后尝试推送："
echo "  git push origin main"
