#!/bin/bash
# 使用letentry快速支持https
# more infomation please visist: https://letsencrypt.org/zh-cn/getting-started/
# more information about certbot please visit: https://certbot.eff.org/

echo "---------------------------安装及启动snpad---------------------------"
yum -y install snapd
sudo systemctl enable --now snapd.socket
sudo ln -s /var/lib/snapd/snap /snap

echo "---------------------------开始安装certbot---------------------------"
snap install core
snap refresh core
snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot

snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot
echo "--------------------------nginx支持https---------------------------"
sudo certbot --nginx
