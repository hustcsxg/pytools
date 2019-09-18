"""
This moudle is used to get sonnar_scanner cmd and parse scanner result
use help:
ss = SonarScanner('path to your project', 'https://127.0.0.1:9000','token:xxxjife', '/usr/bin/sonar-scaner')
cmd = ss.get_scan_cmd()   # cmd likes: sonar-scaner -Dxx -Dxxx -Dxx
Attentions: cd path_to_your_project before scan
"""
from pathlib import Path

ONE_SPACE = " "

params_demo = """
-Dsonar.host.url=http://172.0.0.0:19000         # sonarqueb 平台
-Dsonar.projectKey=sonarScannerTest
-Dsonar.login=025da6f30xxxxx72133539791b7a68cebb8619 # sonarqube token
-Dsonar.projectName=sonarScannerTest
-Dsonar.version=1.0
-Dsonar.sources=.
-Dsonar.language=java
-Dsonar.sourceEncoding=UTF-8
-Dsonar.java.binaries=target"""


class SonarScanner:
    DEFAULT_RESELT_FILE = ".scannerwork/report-task.txt"
    SCANNER = "sonar-scanner"

    def __init__(self, project_abspath, sonarqube_url, sonarqube_token, scanner=SCANNER):
        """
        :param project_abspath: the absolute path of project will be scanned
        """
        self.sonarqube_url = sonarqube_url
        self.sonarqube_token = sonarqube_token
        self.project_root_path = project_abspath
        self.sonar_scanner_exist = False
        self.scanner = scanner

    def _generate_scan_cmd(self, params):
        """
        add auth releated parms to cmd
        :param params:
        :return: cmd with auth parms
        """
        exec_params = params.replace("\r\n", ONE_SPACE).replace("\n", ONE_SPACE)
        _auth_parms_str = ""
        if exec_params.find("sonar.host.url") == -1:
            _auth_parms_str = _auth_parms_str + ONE_SPACE + "-Dsonar.host.url=%s" % (self.sonarqube_url)
        if exec_params.find("sonar.login") == -1:
            _auth_parms_str = _auth_parms_str + ONE_SPACE + "-Dsonar.login=%s" % (self.sonarqube_token)
        ret = self.scanner + ONE_SPACE + exec_params + ONE_SPACE + _auth_parms_str
        return ret

    def get_scan_cmd(self, exec_params):
        cmd = self._generate_scan_cmd(exec_params)
        return cmd

    def parse_scanner_result(self):
        """
        parse scanner result file report-task.txt to dict
        :param file_path:
        :return:
        {'projectKey': 'sonarScannerTest',
        'serverUrl': 'http://172.16.7.38:19000',
        'serverVersion': '7.1.0.11001',
        'dashboardUrl': 'http://172.16.7.38:19000/dashboard/index/sonarScannerTest',
        'ceTaskId': 'AWzld-Fof4TvNRK-_GOl',
        'ceTaskUrl': 'http://172.16.7.38:19000/api/ce/task?id=AWzld-Fof4TvNRK-_GOl'
        }
        """
        result = dict()
        file = str(Path(self.project_root_path) / Path(self.DEFAULT_RESELT_FILE))
        with open(file, 'r') as f:
            lines = f.readlines()
            for i in lines:
                k, v = i.rstrip('\n').split('=', 1)
                result[k.strip()] = v.strip()
        print(result)
        return result


if __name__ == "__main__":
    # s = SonarScanner("/root/workspace", "http://172.16.7.38:19000", "xfesfsfsa")
    pass
