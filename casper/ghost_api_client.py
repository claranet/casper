import urllib.parse

import copy

import requests

DEFAULT_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

DEFAULT_PAGE_SIZE = 20

METHOD_GET = 'get'
METHOD_POST = 'post'


class ApiClientException(Exception):
    pass


class ApiClient(object):
    path = None

    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def _get_url(self, path, params):
        base_url = urllib.parse.urljoin(self.host, path)
        if params:
            return "{}?{}".format(base_url, urllib.parse.urlencode(params, safe=':'))
        return base_url

    def _do_request(self, path, params=None, method=METHOD_GET):
        url = self._get_url(path, params)
        try:
            response = requests.request(method, url, auth=(self.username, self.password),
                                        headers=DEFAULT_HEADERS)
            if response.status_code >= 300:
                raise ApiClientException(
                    'Error while calling Cloud Deploy : [{}] {}'.format(response.status_code, response.text))
            ret = response.json()
        except requests.ConnectionError as e:
            raise ApiClientException('Error while sending request to {}'.format(url)) from e
        except ValueError as e:
            raise ApiClientException('Error while reading response from {}'.format(url)) from e
        return ret

    def _do_list(self, path, nb, page, sort, **extra_params):
        params = copy.deepcopy(extra_params)
        params.update({'max_results': nb, 'page': page, 'sort': sort})
        data = self._do_request(path, params)
        return data['_items'], data['_meta']['max_results'], data['_meta']['total'], data['_meta']['page']

    def list(self, nb=DEFAULT_PAGE_SIZE, page=1, sort='-_updated'):
        if not self.path:
            raise NotImplementedError('`path` variable must be defined')
        return self._do_list(self.path, nb, page, sort)


class AppsApiClient(ApiClient):
    path = '/apps/'


class JobsApiClient(ApiClient):
    path = '/jobs/'

    def list(self, nb=DEFAULT_PAGE_SIZE, page=1, sort='-_updated'):
        return self._do_list(self.path, nb, page, sort, embedded='{"app_id":1}')


class DeploymentsApiClient(ApiClient):
    path = '/deployments/'

    def list(self, nb=DEFAULT_PAGE_SIZE, page=1, sort='-timestamp'):
        return self._do_list(self.path, nb, page, sort, embedded='{"app_id":1,"job_id":1}')
