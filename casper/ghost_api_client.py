import urllib.parse

import copy
from base64 import b64encode

import requests

DEFAULT_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

DEFAULT_PAGE_SIZE = 20

METHOD_GET = 'get'
METHOD_POST = 'post'

DEPLOYMENT_STRATEGY_SERIAL = 'serial'
DEPLOYMENT_STRATEGY_PARALLEL = 'parallel'
DEPLOYMENT_STRATEGIES = (DEPLOYMENT_STRATEGY_SERIAL, DEPLOYMENT_STRATEGY_PARALLEL)

SCRIPT_EXECUTION_STRATEGY_SINGLE = 'single'
SCRIPT_EXECUTION_STRATEGY_SERIAL = 'serial'
SCRIPT_EXECUTION_STRATEGY_PARALLEL = 'parallel'
SCRIPT_EXECUTION_STRATEGIES = (
    SCRIPT_EXECUTION_STRATEGY_SINGLE, SCRIPT_EXECUTION_STRATEGY_SERIAL, SCRIPT_EXECUTION_STRATEGY_PARALLEL)

SAFE_DEPLOYMENT_STRATEGY_ONE_BY_ONE = '1by1'
SAFE_DEPLOYMENT_STRATEGY_THIRD = '1/3'
SAFE_DEPLOYMENT_STRATEGY_QUARTER = '25%'
SAFE_DEPLOYMENT_STRATEGY_HALF = '50%'
SAFE_DEPLOYMENT_STRATEGIES = (SAFE_DEPLOYMENT_STRATEGY_ONE_BY_ONE, SAFE_DEPLOYMENT_STRATEGY_THIRD,
                              SAFE_DEPLOYMENT_STRATEGY_QUARTER, SAFE_DEPLOYMENT_STRATEGY_HALF)


class ApiClientException(Exception):
    pass


class ApiClient(object):
    path = None

    def __init__(self, host, username, password):
        """
        Creates an API client instance
        :param host: str: host for API
        :param username: str: username for API
        :param password: str: password for API
        """
        self.host = host
        self.username = username
        self.password = password

    @staticmethod
    def _clean_dict_object(obj):
        """
        Clean some internal attributes of an object
        :param obj: dict:
        :return: dict:
        """
        for attr in ['_latest_version', '_links', '_version']:
            if attr in obj:
                del obj[attr]
        return obj

    def _get_url(self, path, params, object_id=None):
        """
        Construct the API URL
        :param path: str:
        :param params: dict:
        :param object_id: str:
        :return: str:
        """
        base_url = urllib.parse.urljoin(self.host, path)
        if object_id:
            base_url = urllib.parse.urljoin(base_url, object_id)
        if params:
            return "{}?{}".format(base_url, urllib.parse.urlencode(params, safe=':'))
        return base_url

    def _do_request(self, path, object_id=None, body=None, params=None, method=METHOD_GET):
        """
        Do the API requests
        :param path: str:
        :param object_id: str:
        :param body: dict:
        :param params: dict:
        :param method: str:
        :return: dict:
        """
        url = self._get_url(path, params, object_id)
        try:
            response = requests.request(method, url,
                                        json=body,
                                        auth=(self.username, self.password),
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

    def _do_retrieve(self, path, object_id, **extra_params):
        """
        Do the retrieve API call
        :param path: str:
        :param object_id: str:
        :param extra_params: dict:
        :return: dict:
        """
        data = self._do_request(path, object_id, params=extra_params)
        return self._clean_dict_object(data)

    def _do_list(self, path, nb, page, sort, **extra_params):
        """
        Do the list API call
        :param path: str:
        :param nb: int:
        :param page: int:
        :param sort: str:
        :param extra_params: dict:
        :return: tuple:
        """
        params = copy.deepcopy(extra_params)
        params.update({'max_results': nb, 'page': page, 'sort': sort})
        data = self._do_request(path, params=params)
        return ([self._clean_dict_object(item) for item in data['_items']],
                data['_meta']['max_results'], data['_meta']['total'], data['_meta']['page'])

    def _do_create(self, path, obj, **extra_params):
        """
        Do the create API call
        :param path: str:
        :param obj: dict:
        :param extra_params: dict:
        :return: str:
        """
        data = self._do_request(path, body=obj, params=extra_params, method=METHOD_POST)
        return data.get('_id')

    def retrieve(self, object_id):
        """
        Retrieve an object
        :param object_id: str: id of the object
        :return: dict:
        """
        if not self.path:
            raise NotImplementedError('`path` variable must be defined')
        return self._do_retrieve(self.path, object_id)

    def list(self, nb=DEFAULT_PAGE_SIZE, page=1, sort='-_updated'):
        """
        List objects
        :param nb: int: the number of objects to list
        :param page: int: the page to fetch
        :param sort: str: the object order
        :return: tuple: returns the tuple (objects, number of results, total number of objects, page fetched)
        """
        if not self.path:
            raise NotImplementedError('`path` variable must be defined')
        return self._do_list(self.path, nb, page, sort)

    def create(self, obj):
        """
        Create an object
        :param obj: dict: the object
        :return: str: id of the created object
        """
        if not self.path:
            raise NotImplementedError('`path` variable must be defined')
        return self._do_create(self.path, obj)


class AppsApiClient(ApiClient):
    path = '/apps/'

    def list(self, nb=DEFAULT_PAGE_SIZE, page=1, sort='-_updated', name=None, env=None, role=None):
        """
        List objects
        :param nb: int: the number of objects to list
        :param page: int: the page to fetch
        :param sort: str: the object order
        :param name: str: filter to apply on application name
        :param env: str: filter to apply on application env
        :param role: str: filter to apply on application role
        :return: tuple: returns the tuple (objects, number of results, total number of objects, page fetched)
        """
        query = []
        if role is not None:
            query.append('"role":"{role}"'.format(role=role))
        if env is not None:
            query.append('"env":"{env}"'.format(env=env))
        if name is not None:
            query.append('"name":{{"$regex":"{name}"}}'.format(name=name))
        return self._do_list(self.path, nb, page, sort, where='{' + ",".join(query) + '}')


class JobsApiClient(ApiClient):
    path = '/jobs/'

    def list(self, nb=DEFAULT_PAGE_SIZE, page=1, sort='-_updated'):
        return self._do_list(self.path, nb, page, sort, embedded='{"app_id":1}')

    def command_buildimage(self, application_id, instance_type=None, skip_bootstrap=None):
        """
        Creates a `buildimage` job
        :param application_id: str: Application ID
        :param instance_type: str: Instance type
        :param skip_bootstrap: bool: Skip provisioner bootstrap
        :return: str: id of the created job
        """
        job = {
            "command": "buildimage",
            "app_id": application_id,
            "options": [],
        }
        if instance_type:
            job["instance_type"] = instance_type
        if skip_bootstrap is not None:
            job["options"].append(str(skip_bootstrap))
        return self.create(job)

    def command_deploy(self, application_id, modules,
                       deployment_strategy=DEPLOYMENT_STRATEGY_SERIAL, safe_deployment_strategy=None):
        """
        Creates a `deploy` job
        :param application_id: str: Application ID
        :param modules: array: list of modules as `{"name": name, "rev": rev}`
        :param deployment_strategy: str: Deployment strategy
        :param safe_deployment_strategy: str: Safe deployment strategy to use
        :return: str: id of the created job
        """
        job = {
            "command": "deploy",
            "app_id": application_id,
            "modules": modules,
            "options": [deployment_strategy or DEPLOYMENT_STRATEGY_SERIAL],
        }
        if safe_deployment_strategy is not None:
            job["options"].append(safe_deployment_strategy)
        return self.create(job)

    def command_redeploy(self, application_id, deployment_id,
                         deployment_strategy=DEPLOYMENT_STRATEGY_SERIAL, safe_deployment_strategy=None):
        """
        Creates a `redeploy` job
        :param application_id: str: Application ID
        :param deployment_id: str: the previous deployment to replay
        :param deployment_strategy: str: Deployment strategy
        :param safe_deployment_strategy: str: Safe deployment strategy to use
        :return: str: id of the created job
        """
        job = {
            "command": "redeploy",
            "app_id": application_id,
            "options": [deployment_id, deployment_strategy or DEPLOYMENT_STRATEGY_SERIAL],
        }
        if safe_deployment_strategy is not None:
            job["options"].append(safe_deployment_strategy)
        return self.create(job)

    def command_executescript(self, application_id, script_content,
                              execution_strategy=SCRIPT_EXECUTION_STRATEGY_SERIAL,
                              safe_deployment_strategy=SAFE_DEPLOYMENT_STRATEGY_ONE_BY_ONE,
                              instance_ip=None, module_context=None):
        """
        Creates a `executescript` job
        :param application_id: str: Application ID
        :param script_content: str: The script to execute in UTF-8 encoding
        :param execution_strategy: str: The script execution strategy
        :param safe_deployment_strategy: str: The safe deployment strategy if not `single` execution strategy
        :param instance_ip: str: Instance IP on which execute the script if `single` execution strategy
        :param module_context: : str: The name of the module in which folder the script will be executed
        :return: str: id of the created job
        """
        execution_strategy = execution_strategy or SCRIPT_EXECUTION_STRATEGY_SINGLE
        safe_deployment_strategy = safe_deployment_strategy or SAFE_DEPLOYMENT_STRATEGY_ONE_BY_ONE
        if execution_strategy == SCRIPT_EXECUTION_STRATEGY_SINGLE and not instance_ip:
            raise ApiClientException('Instance IP must be specified for "single" script execution strategy')
        if execution_strategy != SCRIPT_EXECUTION_STRATEGY_SINGLE and not safe_deployment_strategy:
            raise ApiClientException(
                'Safe deployment strategy must be specified if not "single" script execution strategy')

        job = {
            "command": "executescript",
            "app_id": application_id,
            "options": [
                b64encode(script_content.replace('\r\n', '\n').encode('utf-8')).decode('utf-8'),
                module_context or '',
                execution_strategy,
                instance_ip if execution_strategy == SCRIPT_EXECUTION_STRATEGY_SINGLE else safe_deployment_strategy,
            ],
        }
        return self.create(job)

    def command_createinstance(self, application_id, subnet_id=None, private_ip_address=None):
        """
        Creates a `createinstance` job
        :param application_id: str: Application ID
        :param subnet_id: str: Subnet ID in which create the instance
        :param private_ip_address: Private IP address of the instance
        :return: str: id of the created job
        """
        if not subnet_id and private_ip_address:
            raise ApiClientException('Subnet ID is mandatory when specifying private IP address for buildimage command')
        job = {
            "command": "createinstance",
            "app_id": application_id,
            "options": [],
        }
        if subnet_id is not None:
            job["options"].append(subnet_id)
        if private_ip_address is not None:
            job["options"].append(private_ip_address)
        return self.create(job)

    def command_destroyallinstances(self, application_id):
        """
        Creates a `destroyallinstances` job
        :param application_id: str: Application ID
        :return: str: id of the created job
        """
        job = {
            "command": "destroyallinstances",
            "app_id": application_id,
            "options": [],
        }
        return self.create(job)

    def command_updatelifecyclehooks(self, application_id):
        """
        Creates a `updatelifecyclehooks` job
        :param application_id: str: Application ID
        :return: str: id of the created job
        """
        job = {
            "command": "updatelifecyclehooks",
            "app_id": application_id,
            "options": [],
        }
        return self.create(job)

    def command_updateautoscaling(self, application_id):
        """
        Creates a `updateautoscaling` job
        :param application_id: str: Application ID
        :return: str: id of the created job
        """
        job = {
            "command": "updateautoscaling",
            "app_id": application_id,
            "options": [],
        }
        return self.create(job)


class DeploymentsApiClient(ApiClient):
    path = '/deployments/'

    def list(self, nb=DEFAULT_PAGE_SIZE, page=1, sort='-timestamp'):
        return self._do_list(self.path, nb, page, sort, embedded='{"app_id":1,"job_id":1}')
