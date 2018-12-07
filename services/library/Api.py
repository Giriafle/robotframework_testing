"""This module is created for using with robotframework.
It gets values from config module and uses db_work module for querying a database.
The module checks connection to API, gets from it hooked services for users and adds these, takes information
about all possible services.
"""

import json
import requests
from config import HEADERS, PORT, URL


class Api:
    """This is a class for connection to API, gets and adds information to it."""

    def check_connection(self) -> int:
        """Checking connection to API.

        :return: Int - Response status code.
        """

        try:
            response = requests.get(f'{URL}:{PORT}')
            response.raise_for_status()
            return response.status_code
        except requests.exceptions.RequestException as e:
            raise Exception(f'An error occurred while accessing the service "Connection to API": {e}')

    def _get_request(self, url: str, headers: dict=None) -> requests.models.Response:
        """
        This function implements requests with 'get' method to API.

        :param url: String - Url and port of API service.
        :param headers: Dict - Headers of the request.
        :return: requests.models.Response - Information from API service for get request.
        """

        try:
            response = requests.get(url=url, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f'An error occurred while accessing the service "Request to API": {e}')

    def _post_request(self, url: str, request_json: str, headers: dict=None) -> requests.models.Response:
        """
        This function implements requests with 'post' method to API.

        :param url: String - Url and port of API service.
        :param request_json: String - Json of the request.
        :param headers: Dict - Headers of the request.
        :return: requests.models.Response - Information from API service for post request.
        """

        try:
            response = requests.post(url=url, json=request_json, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f'An error occurred while accessing the service "Post request to API": {e}')

    def get_hook_services(self, client_id: int) -> list:
        """
        This function gets user's hooked services from API.

        :param client_id: Integer - User's id which gets from the database.
        :return: Json - data of response from API: user's hooked services.
        """

        url = f'{URL}:{PORT}/client/services'
        hook_json = json.loads(f'\173"client_id": {client_id}\175')
        response = self._post_request(url=url, request_json=hook_json, headers=HEADERS).json()
        assert response, 'Nothing returned from API after trying get hooked services'
        ids_hook_services = [hook_services['id'] for hook_services in response['items']]
        return ids_hook_services

    def get_all_services(self) -> list:
        """
        This function gets information about all possible services from API.

        :return: List - data of response from API: all possible ids services from API.
        """

        url = f'{URL}:{PORT}/services'
        response = self._get_request(url=url, headers=HEADERS).json()
        assert response, 'Nothing returned from API after trying get all services'
        if response['count'] != 0:
            ids_all_services = [all_services['id'] for all_services in response['items']]
            return ids_all_services
        else:
            raise Exception('There is nothing to hook')

    def _get_cost_services(self, service_id: int) -> float or None:
        """
        This function gets service's cost from API.

        :return: Float - service's cost from API, None - if there isn't information about service's cost.
        """

        url = f'{URL}:{PORT}/services'
        response = self._get_request(url=url, headers=HEADERS).json()
        assert response, 'Nothing returned from API after trying get all services'
        if response['count'] != 0:
            for all_services in response['items']:
                if all_services['id'] == service_id:
                    service_cost = all_services['cost']
                    assert service_cost, 'There is not information about the cost'
                    return service_cost
        else:
            raise Exception(f'There is nothing to get cost')

    def find_unhooked_service(self, hooked_services: list, all_services: list) -> tuple:
        """
        This function finds first unhooked services and it cost.

        :param hooked_services: List - Hooked services from API.
        :param all_services: List - All possible services from API.
        :return: Tuple - Id of unhooked service and service's cost.
        """

        for service_id in all_services:
            if service_id not in hooked_services:
                service_cost = self._get_cost_services(service_id)
                if service_cost:
                    return service_id, service_cost
                else:
                    raise Exception(f'The service {service_id} is lost during finding the cost')
        raise Exception(f"All services are hooked. There are {len(hooked_services)} of them.")

    def find_service_in_hook_services(self, client_id: int, service_id: int) -> bool:
        """
        This function checks that the new service is hooked (gets it from API).

        :param client_id: Integer - User's id which gets from the database.
        :param service_id: Integer - The id of hooked service.
        :return: Bool - True if the new service is hooked.
        """

        services_id = self.get_hook_services(client_id)
        if service_id in services_id:
            return True
        else:
            return False

    def add_services(self, client_id: int, service_id: int) -> None:
        """
        This function adds services to users with API.

        :param client_id: Integer - User's id which gets from the database.
        :param service_id: Integer - Service's id which gets from API.
        """

        add_service_url = f'{URL}:{PORT}/client/add_service'
        add_json = json.loads(f'\173"client_id": {client_id}, "service_id": {service_id}\175')
        status_code = self._post_request(url=add_service_url, request_json=add_json, headers=HEADERS).status_code
        assert status_code, 'Nothing returned from API after trying get hooked services'
        assert status_code == 202, 'An error occurred while accessing the service "Post request to API": Status code' \
                                   ' is not equal 202'

