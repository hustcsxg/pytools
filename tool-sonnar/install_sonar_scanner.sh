#!/bin/bash
cd /opt && rm -rf /opt/sonar-scanner-4.0.0.1744-linux  && wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.0.0.1744-linux.zip && unzip -o sonar-scanner-cli-4.0.0.1744-linux.zip -d /opt/
ln -sf /opt/sonar-scanner-4.0.0.1744-linux/bin/sonar-scanner  /usr/bin/sonar-scanner
rm -rf /opt/sonar-scanner-cli-4.0.0.1744-linux.zip
