"""
This module contains the SonarQubeAPI to call SonarQube server web service API.
"""
import requests

class ClientError(Exception):
    pass


class ServerError(Exception):
    pass


class AuthError(ClientError):
    pass


class ValidationError(ClientError):
    pass


class SonarQubeAPI(object):
    """
    Adapter for SonarQube's web service API.
    """
    # Default host is local
    DEFAULT_BASE_PATH = ''

    AUTH_VALIDATION_ENDPOINT = '/api/authentication/validate'
    TASK_RESULT_ENDPOINT = '/api/ce/task'

    def __init__(self, server_url, token=None, user=None, password=None, base_path=None):
        """
        Set connection info and session, including auth (if user+password
        and/or auth token were provided).
        """
        self.url = server_url.rstrip('/')
        self._base_path = base_path if base_path else self.DEFAULT_BASE_PATH
        self._session = requests.Session()

        # Prefer revocable authentication token over username/password
        if token:
            self._session.auth = token, ''
        elif user and password:
            self._session.auth = user, password

    def _ger_full_url(self, endpoint):
        """
        Return the complete url including host and port for a given endpoint.

        :param endpoint: service endpoint as str
        :return: complete url as str
        """
        return '{}{}{}'.format(self.url, self._base_path, endpoint)

    def _make_call(self, method, endpoint, **data):
        """
        Make the call to the service with the given method, queryset and data,
        using the initial session.

        Note: data is not passed as a single dictionary for better testability
        (see https://github.com/kako-nawao/python-sonarqube-api/issues/15).

        :param method: http method (get, post, put, patch)
        :param endpoint: relative url to make the call
        :param data: queryset or body
        :return: response
        """
        # Get method and make the call
        http_method = method.lower()
        call = getattr(self._session, http_method)
        url = self._ger_full_url(endpoint)
        try:
            if http_method == "get":
                res = call(url, params=data or {})
            else:
                res = call(url, data=data or {})
        except Exception:
            raise ServerError

        # Analyse response status and return or raise exception
        # Note: redirects are followed automatically by requests
        if res.status_code < 300:
            # OK, return http response
            return res
        elif res.status_code == 400:
            # Validation error
            msg = ', '.join(e['msg'] for e in res.json()['errors'])
            raise ValidationError(msg)

        elif res.status_code in (401, 403):
            # Auth error
            raise AuthError(res.reason)

        elif res.status_code < 500:
            # Other 4xx, generic client error
            raise ClientError(res.reason)

        else:
            # 5xx is server error
            raise ServerError(res.reason)

    def get_scanner_result(self, ce_task_id):
        """
        get scanner evnent exec result.
        :param ce_task_id:
        :return: dick likes {'task':
        {'id': 'AWzld-Fof4TvNRK-_GOl', 'type': 'REPORT', 'componentId': 'AWzlSi6of4TvNRK-_GOa', 'componentKey':
        'sonarScannerTest', 'componentName': 'sonarScannerTest', 'componentQualifier': 'TRK',
        'analysisId': 'AWzld-WFqeZ7zy3lHNF3', 'status': 'SUCCESS', 'submittedAt': '2019-08-31T02:18:54+0000',
        'submitterLogin': 'admin', 'startedAt': '2019-08-31T02:18:55+0000', 'executedAt': '2019-08-31T02:18:56+0000',
        'executionTimeMs': 609, 'logs': False, 'hasScannerContext': True, 'organization': 'default-organization'}}
        """
        data = {"id": ce_task_id}
        response = self._make_call('get', self.TASK_RESULT_ENDPOINT, **data)
        res = response.json()
        return res

    def is_scanner_passed(self, ce_task_id):
        """
        if scanner passed
        :param ce_task_id:
        :return: True|False
        """
        ret = False
        result = self.get_scanner_result(ce_task_id)
        if result and result["task"]["status"].lower() in ["success", "in_progress"]:
            ret = True
        return ret

    def validate_authentication(self):
        """
        Validate the authentication credentials passed on client initialization.
        This can be used to test the connection, since API always returns 200.
        :return: True if valid
        """
        ret = False
        try:
            response = self._make_call('get', self.AUTH_VALIDATION_ENDPOINT)
            res = response.json()
            ret = res.get('valid', False)
        except Exception as e:
            print(e)
        return ret


if __name__ == "__main__":
    sonanrqube_url = "http://172.16.0.1:19000"
    token = "025da6f30c6e848e7213xx7a68cebb8619"
    sqa = SonarQubeAPI(sonanrqube_url, token=token)
    # ret = sqa.validate_authentication()
    ret = sqa.is_scanner_passed('AWzld-Fof4TvNRK-_GOl')
    print(ret)
    print((requests.Session()))
    print(sqa.get_scanner_result('AWzld-Fof4TvNRK-_GOl'))
