"""
utils for parse pom.xml
demos:
pom_parser = PomParser(path_to_your_pom_file)
pom.parser.get_dependencies('dev')
"""
import re
import json
import requests
import xmltodict
from collections import OrderedDict

NEXUS_SEARCH_URL = 'http://nexus.xxxx.cn/service/rest/beta/search?maven.groupId=%s&maven.artifactId=%s&maven.baseVersion=%s'
MAVEN_CENTER_SEARCH_URL = "https://search.maven.org/solrsearch/select?q=g:%s AND a:%s AND v:%s AND p:%s &start=0&rows=5&wt=json"
NEXUS_xxxx_DOMAIN_NAME = "nexus.xxxx.cn"
CENTRAL_MAVEN_DOMAIN = "central.maven.org"


class PomParser:
    """
    parse pom.xml for java project managed by maven.
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.pom_dict = self.pom_to_dict(file_path)

    @staticmethod
    def _get_variables_name(src_str):
        _str = src_str.strip()
        pattern = '\$\{(.*?)\}'
        matched = re.search(pattern, _str)
        if matched:
            ret = matched.groups()[0]
        else:
            ret = src_str
        return ret

    @staticmethod
    def pom_to_dict(pom_file):
        try:
            with open(pom_file, mode='rb') as f:
                pom_dict = xmltodict.parse(f, process_namespaces=False)
                return pom_dict
        except Exception as e:
            raise Exception('pom.xml file format error')

    def _get_dependencies(self):
        """

        :return:
        """
        ret = []
        dependencies = self.pom_dict["project"].get("dependencies", {}).get("dependency", [])
        dependency_management = self.pom_dict["project"].get("dependencyManagement", {}).get("dependencies", {}).get(
            "dependency", [])
        # 去重及继承version
        dependencie_name_list = [i["artifactId"] for i in dependency_management]
        ret.extend(dependency_management)
        for item in dependencies:
            if item["artifactId"] in dependencie_name_list:
                _index = dependencie_name_list.index(item["artifactId"])
                if not item.get("version", None):
                    item["version"] = dependency_management[_index].get("version", "")
                ret[_index] = item
            else:
                ret.append(item)
        return ret

    @staticmethod
    def gav_to_name(g, a, v, t):
        g_path = g
        a_path = a
        v_path = v
        package_name = '-'.join([g, a, v]) + '.' + t
        # package_path = '/'.join([g_path, a_path, v_path, package_name])
        return package_name

    def get_dependencies(self, env_name):
        """

        :param env_name:
        :return: {"repo_urls": url_list, "packages": packages, "packages_name_list": packages_name_list}
        """
        packages = []
        url_list = []
        packages_name_list = []
        repo_url = self._get_reposity()
        for i in repo_url:
            _repo_url = i.get("url", None)
            url_list.append(_repo_url)
        properties = self.get_env_properties(env_name)

        _all_dependencies = self._get_dependencies()
        # gavtso: groupId, artifactId, version, type, scope,optional
        # OrderedDict([('groupId', 'com.alibaba'), ('artifactId', 'fastjson'), ('version', '${fastjson.version}'),
        #              ('optional', 'true')])
        for denpendy in _all_dependencies:
            _g = denpendy.get("groupId", '')
            _a = denpendy.get("artifactId", '')
            version_parm = self._get_variables_name(denpendy.get("version", ''))
            _v = properties.get(version_parm, version_parm)
            _t = denpendy.get("type", "jar")
            _info = (_g, _a, _v, _t)
            package_name = self.gav_to_name(_g, _a, _v, _t)
            packages.append(_info)
            packages_name_list.append(package_name)
        ret = {"repo_urls": url_list, "packages": packages, "packages_name_list": packages_name_list}
        return ret

    def get_dependency_management(self):
        dm = self.pom_dict["project"].get("dependencyManagement")
        return dm

    def _get_reposity(self):
        """
        ret:
        OrderedDict([('repository', OrderedDict([('id', 'nexus'), ('name', 'Nexus Local Repository'),
        ('url', 'http://nexus.xxxx.cn/repository/maven-public/'), ('snapshots', OrderedDict([('enabled', 'true'),
         ('updatePolicy', 'always')])), ('releases', OrderedDict([('enabled', 'true')]))]))])
        :return:
        """
        ret = []
        repos = self.pom_dict["project"].get("repositories", {}).get("repository", [])
        if not isinstance(repos, list):
            ret.append(repos)
        else:
            ret = repos
        return ret

    def get_profiles(self):
        profiles = self.pom_dict["project"].get("profiles", None)
        return profiles

    def profile_properties(self):
        env_properties = OrderedDict()
        profiles = self.get_profiles()
        profile_list = profiles.get("profile", [])
        for item in profile_list:
            env_properties[item["id"]] = item.get("properties", [])
        return env_properties

    def get_properties(self):
        properties = self.pom_dict["project"].get("properties", None)
        return properties

    def get_env_properties(self, env_name):
        all_env_properties = self.profile_properties()
        _propertities_this_env = all_env_properties.get(env_name, {})

        base_properties = self.get_properties()
        base_properties.update(_propertities_this_env)
        env_properties = base_properties
        return env_properties

    def detect_dependency(self, env_name):
        """
        detect pom.xml all dependency.
        :param env_name: dev|prod
        :return: {"msg": msg, "data": not_finded_packages}
        if success: {"msg": 'succeed', "data": []} else  {"msg": 'failed', "data": [(g,a,v,t)]
        """

        all_dependencies = self.get_dependencies(env_name)
        not_finded_packages = []
        repo_url_list = all_dependencies["repo_urls"]
        repo_searcher = MavenRepoSearcher()
        for gavt in all_dependencies["packages"]:
            _is_in = repo_searcher.if_package_in_repo(repo_url_list, gavt[0], gavt[1], gavt[2], gavt[3])
            if not _is_in:
                not_finded_packages.append(gavt)

        msg = "failed, see not finded packages in data." if not_finded_packages else "successed"
        msg = "detect package " + msg
        ret = {"msg": msg, "data": not_finded_packages}
        return ret


class MavenRepoSearcher:
    """
    search package in maven repo.
    """

    def __init__(self, center_search_url=MAVEN_CENTER_SEARCH_URL, private_repo_search_url=NEXUS_SEARCH_URL):
        self.center_search_url = center_search_url
        self.private_repo_search_url = private_repo_search_url

    def maven_search(self, g, a, v, t):
        _exist = False
        search_url = self.center_search_url
        url = search_url % (g, a, v, t)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                ret = json.loads(response.content)
                if ret["response"]["numFound"] > 0:
                    _exist = True
        except Exception as e:
            print(e)
        return _exist

    def maven_search_xxxx(self, g, a, v, t):
        _exist = False
        search_url = self.private_repo_search_url
        url = search_url % (g, a, v)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                ret = json.loads(response.content)
                if ret["items"]:
                    _exist = True
        except Exception as e:
            print(e)
        return _exist

    def if_package_in_repo(self, repo_url_list, g, a, v, t):
        """
        check package exist in maven repos
        :param repo_url_list:
        :param g:
        :param a:
        :param v:
        :param t: type:pom|jar|war
        :return: True|False
        """
        _exist = False

        methods_list = []
        for url in repo_url_list:
            _search_method = None
            if NEXUS_xxxx_DOMAIN_NAME in url:
                _search_method = self.maven_search_xxxx
            elif CENTRAL_MAVEN_DOMAIN in url:
                _search_method = self.maven_search
            if _search_method:
                methods_list.append(_search_method)
        for _method in methods_list:
            if _method(g, a, v, t):
                _exist = True
                break
        return _exist


if __name__ == "__main__":
    pom_parser = PomParser('pom1.xml')
    ret = pom_parser.detect_dependency('dev')
    print(ret)
