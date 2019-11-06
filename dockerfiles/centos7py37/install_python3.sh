#!/usr/bin/bash
PYTHON_VERSION=3.7.5
yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make wget libffi-devel
cd /opt && wget http://npm.taobao.org/mirrors/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && tar -zxvf Python-${PYTHON_VERSION}.tgz
cd /opt/Python-${PYTHON_VERSION}
./configure
make&&make install
rm -rf /usr/bin/python3  && ln -s /usr/local/bin/python3  /usr/bin/python3
rm -rf /usr/bin/pip3  && ln -s /usr/local/bin/pip /usr/bin/pip3

rm -rf /opt/Python-${PYTHON_VERSION}*
if [ ! -d "/root/.pip" ]; then
  mkdir ~/.pip
fi
rm -rf ~/.pip/pip.conf && touch ~/.pip/pip.conf
echo "[global]
index-url=http://mirrors.aliyun.com/pypi/simple/
trusted-host=mirrors.aliyun.com" >> ~/.pip/pip.conf
