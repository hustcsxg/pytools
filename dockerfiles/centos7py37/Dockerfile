FROM centos:centos7
LABEL maintainer=hustcsxg@163.com

#设置时区的终端
ENV TZ "Asia/Shanghai"
RUN yum install -y  kde-l10n-Chinese  glibc-common
RUN localedef -c -f UTF-8 -i zh_CN zh_CN.utf8
ENV LANG C.UTF-8
ENV LC_ALL zh_CN.UTF-8
ENV TERM xterm
ENV PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
WORKDIR /opt
ADD . .

RUN yum install -y wget java-1.8.0-openjdk-devel.x86_64  maven git unzip && yum clean -y all && rm -rfv /tmp/*
# 安装python3.7.5及项目依赖
RUN ln -sf /opt/sonar-scanner-cli/bin/sonar-scanner  /usr/bin/sonar-scanner
RUN bash install_python3.sh && pip3 install --upgrade pip && yum clean -y all
CMD ['/bin/bash']
