import requests
import time
from mindsdb.api.executor.data_types.response_type import RESPONSE_TYPE
from tests.integration_tests.flows.conftest import HTTP_API_ROOT


class HTTPHelperMixin:
    _sql_via_http_context = {}

    @staticmethod
    def api_request(method, url, payload=None, headers=None):
        """Sends an API request to the specified URL with given method, payload, and headers."""
        method = method.lower()
        fnc = getattr(requests, method)
        url = f'{HTTP_API_ROOT}/{url.lstrip("/")}'
        response = fnc(url, json=payload, headers=headers)
        return response

    def sql_via_http(self, request: str, expected_resp_type: str = None, context: dict = None,
                     headers: dict = None, company_id: int = None) -> dict:
        """
        Executes an SQL query via HTTP and returns the response.

        Arguments:
        - request: SQL query to execute.
        - expected_resp_type: Expected response type (optional).
        - context: Context for the query (optional).
        - headers: Headers for the request (optional).
        - company_id: Company identifier (optional).

        Returns:
        - The response from the API after executing the SQL query.
        """
        if context is None:
            context = self._sql_via_http_context

        if headers is None:
            headers = {}

        if company_id is not None:
            headers['company-id'] = str(company_id)

        payload = {
            'query': request,
            'context': context
        }
        response = self.api_request('post', '/sql/query', payload, headers)

        # Validate the response status code
        assert response.status_code == 200, f"sql/query is not accessible - {response.text}"

        response_data = response.json()

        # Validate the response type
        if expected_resp_type is not None:
            assert response_data.get('type') == expected_resp_type, response_data
        else:
            assert response_data.get('type') in [RESPONSE_TYPE.OK, RESPONSE_TYPE.TABLE, RESPONSE_TYPE.ERROR], response_data

        assert isinstance(response_data.get('context'), dict)

        # Validate the response structure based on its type
        if response_data['type'] == 'table':
            assert isinstance(response_data.get('data'), list)
            assert isinstance(response_data.get('column_names'), list)
        elif response_data['type'] == 'error':
            assert isinstance(response_data.get('error_code'), int)
            assert isinstance(response_data.get('error_message'), str)

        self._sql_via_http_context = response_data['context']
        return response_data

    def await_model(self, model_name: str, project_name: str = 'mindsdb',
                    version_number: int = 1, timeout: int = 60):
        """
        Waits for the model to reach 'complete' or 'error' status.

        Arguments:
        - model_name: The name of the model.
        - project_name: The project name (default is 'mindsdb').
        - version_number: The version of the model (default is 1).
        - timeout: The timeout period in seconds (default is 60).

        Returns:
        - The final status of the model.
        """
        start = time.time()
        status = None
        while (time.time() - start) < timeout:
            query = f"""
                SELECT status
                FROM {project_name}.models
                WHERE name='{model_name}' and version = {version_number}
            """
            response = self.sql_via_http(query, RESPONSE_TYPE.TABLE)
            status = response['data'][0][0]
            if status in ['complete', 'error']:
                break
            time.sleep(1)
        return status

    def await_model_by_query(self, query, timeout=60):
        """
        Waits for a model status to reach 'complete' or 'error' based on a custom query.

        Arguments:
        - query: The SQL query to execute.
        - timeout: The timeout period in seconds (default is 60).

        Returns:
        - The final status of the model.
        """
        start = time.time()
        status = None
        while (time.time() - start) < timeout:
            resp = self.sql_via_http(query, RESPONSE_TYPE.TABLE)
            status_index = [x.lower() for x in resp['column_names']].index('status')
            status = resp['data'][0][status_index]
            if status in ['complete', 'error']:
                break
            time.sleep(1)
        return status


def get_predictors_list(company_id=None):
    """
    Fetches a list of predictors from the API.

    Arguments:
    - company_id: The company ID (optional).

    Returns:
    - A list of predictors.
    """
    headers = {}
    if company_id is not None:
        headers['company-id'] = f'{company_id}'
    response = requests.get(f'{HTTP_API_ROOT}/predictors/', headers=headers)
    assert response.status_code == 200
    return response.json()


def get_predictors_names_list(company_id=None):
    """
    Fetches a list of predictor names.

    Arguments:
    - company_id: The company ID (optional).

    Returns:
    - A list of predictor names.
    """
    predictors = get_predictors_list(company_id=company_id)
    return [x['name'] for x in predictors]


def check_predictor_exists(name):
    """
    Checks if a predictor exists.

    Arguments:
    - name: The name of the predictor to check.
    """
    assert name in get_predictors_names_list()


def check_predictor_not_exists(name):
    """
    Checks if a predictor does not exist.

    Arguments:
    - name: The name of the predictor to check.
    """
    assert name not in get_predictors_names_list()


def get_predictor_data(name):
    """
    Fetches data for a specific predictor.

    Arguments:
    - name: The name of the predictor.

    Returns:
    - The data of the predictor, or None if not found.
    """
    predictors = get_predictors_list()
    for p in predictors:
        if p['name'] == name:
            return p
    return None


def wait_predictor_learn(predictor_name):
    """
    Waits for a predictor to finish learning (status = 'complete').

    Arguments:
    - predictor_name: The name of the predictor.
    """
    start_time = time.time()
    learn_done = False
    while not learn_done and (time.time() - start_time) < 180:
        learn_done = get_predictor_data(predictor_name)['status'] == 'complete'
        time.sleep(1)
    assert learn_done


def get_integrations_names(company_id=None):
    """
    Fetches the list of integrations.

    Arguments:
    - company_id: The company ID (optional).

    Returns:
    - A list of integration names.
    """
    headers = {}
    if company_id is not None:
        headers['company-id'] = f'{company_id}'
    response = requests.get(f'{HTTP_API_ROOT}/config/integrations', headers=headers)
    assert response.status_code == 200
    return response.json()['integrations']
