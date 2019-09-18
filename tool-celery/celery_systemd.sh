#!/bin/bash
# systemd运行celery
# 拷贝celery.conf配置文件到/etc/celery.conf
rm -rf /etc/celery.conf && cp celery.conf /etc/celery.conf
rm -rf /usr/lib/systemd/system/celery.service && cp celery.service /usr/lib/systemd/system/celery.service
systemctl daemon-reload && systemctl restart celery.service
