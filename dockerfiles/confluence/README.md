# docker部署confluence
通过docker安装confluence7.2.0并激活，nginx代理confluence .
可通过kb.your_domainname.com最终访问知识库。

## 一、前置条件

1. Docker+docker-compose
2. mysql5.7 
3. Nginx
4. 激活文件和java连接mysql包
mysql-connector-java-5.1.49.jar
atlassian-agent.jar

## 二、Mysql安装
1.安装
wget http://dev.mysql.com/get/mysql57-community-release-el7-9.noarch.rpm
yum localinstall mysql57-community-release-el7-9.noarch.rpm
yum -y install mysql-community-server
修改my.cnf, 数据存储在/data/mysqldata/mysql目录下
[mysqld]
datadir=/data/mysqldata/mysql
socket=/data/mysqldata/mysql/mysql.sock
max_allowed_packet = 512M
innodb_log_file_size = 2GB
symbolic-links=0
log-error=/data/mysqldata/log/mysqld.log
pid-file=/var/run/mysqld/mysqld.pid

systemctl enable mysqld
Systemctl daemon-reload
systemctl start mysqld

Root初始密码通过grep “password” /data/mysqldata/log/mysqld.log在文件中查找


2.用户权限设置
连接mysql: mysql -S /data/mysqldata/mysql/mysql.sock -u root
grant all privileges on *.* to 'root'@'%'  identified by ‘你的密码’;
flush privileges;


3.创建confluence数据库

CREATE USER 'confluence'@'%' IDENTIFIED BY ‘密码’;
GRANT ALL PRIVILEGES ON confluence.* TO 'confluence'@'%' IDENTIFIED BY '你的密码'
CREATE DATABASE confluence;
SET GLOBAL tx_isolation='READ-COMMITTED';
flush privileges;

## 三、Confluence安装并激活
5.创建docker目录
  mkdir -pv /data/docker-compose/kb
  cd /data/docker-compose/kb
拷贝前置条件中mysql-connector-java-5.1.49.jar及atlassian-agent.jar到当前目录下
touch /data/docker-compose/kb/docker-compose-kb.yml
Docker-compose-kb.yml文件内容
version: '3'
services:
    confluence:
        image: "atlassian/confluence-server:7.2.0"
        volumes:
            - ./atlassian-agent.jar:/var/atlassian/atlassian-agent.jar
            - ./mysql-connector-java-5.1.49.jar:/opt/atlassian/confluence/confluence/WEB-INF/lib/mysql-connector-java-5.1.49.jar
            - ./confluence:/var/atlassian/application-data/confluence
        environment:
            - JAVA_OPTS="-javaagent:/var/atlassian/atlassian-agent.jar"
            - JVM_MINIMUM_MEMORY=2048m
            - JVM_MAXIMUM_MEMORY=4096m
            - JVM_RESERVED_CODE_CACHE_SIZE=512m
        ports:
            - "8090:8090"
            - "8091:8091"
        restart: always
1.启动容器
	docker-compose -f docker-compose-kb.yml up -d
2.登陆界面配置 127.0.0.1:8090
选择mysql连接

## 四、安装confluence应用
管理员在应---用市场查找应用，并安装
安装后在应用管理，拷贝应用的密钥,BR02-x-x
java -jar atlassian-agent.jar -d -m admin@your_domainname.com -n your_domainname -p "org.swift.confluence.table" -o your_domainname -s BR02-x-x

## 五、密码信息

数据库密码：x
管理员admin
管理密码x
