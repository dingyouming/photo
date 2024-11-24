#!/bin/bash

# 清理环境
echo "正在清理环境..."
pkill -9 -f rclone
rm -rf /home/ubuntu/.config/rclone

# 设置环境变量
export RCLONE_CONFIG_ONEDRIVE_MAIN_AUTH_NO_OPEN_BROWSER=true
export RCLONE_CONFIG_ONEDRIVE_MAIN_AUTH_PORT=53682

echo "
==========================================================
OneDrive 配置向导 - 个人账号配置
==========================================================
重要提示：
1. 请确保使用以下账号登录：
   用户名：ym@cq365.eu.org
   密码：Ab.12345@

2. 在浏览器中打开认证 URL 后：
   - 如果已登录其他账号，请先退出
   - 点击'使用其他账号'
   - 输入上述账号信息

3. 授权步骤：
   - 复制下面显示的认证 URL
   - 在浏览器中打开该 URL
   - 使用上述账号登录
   - 在权限请求页面点击'是'
==========================================================
"

# 使用timeout命令运行rclone配置（300秒超时）
timeout 300s rclone config create onedrive_main onedrive \
    region="global" \
    drive_type="personal"

# 检查返回值
if [ $? -eq 124 ]; then
    echo "
==========================================================
配置超时！
请重新运行脚本重试。
==========================================================
"
    exit 1
fi
