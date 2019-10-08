#!/bin/bash
# systemd运行celery
# 拷贝celery.conf配置文件到/etc/celery.conf
echo "1. 拷贝celery.conf到/etc/clery.conf"
rm -rf /etc/celery.conf && cp celery.conf /etc/celery.conf
echo "2. 新增服务celery.service及celerybeat.service"
rm -rf /usr/lib/systemd/system/celery.service && cp ./celery.service /usr/lib/systemd/system/celery.service
rm -rf /usr/lib/systemd/system/celerybeat.service && cp ./celerybeat.service /usr/lib/systemd/system/celerybeat.service

echo "3. 重新加载systemd服务"
systemctl daemon-reload
echo "4. 启动celery"
systemctl enable celery && systemctl restart celery.service
echo "5. 启动celerybeat"
systemctl enable celerybeat && systemctl start celerybeat.service

systemctl status celery
systemctl status celerybeat
