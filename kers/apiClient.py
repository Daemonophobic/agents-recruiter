import requests
import json
import random


class ApiClient:
    def __init__(self,
                 apiUrl,
                 jwtToken):
        self._apiUrl = apiUrl
        self._jwtToken = jwtToken

    def create_agent(self,
                     os):
        cookies = {"session": self._jwtToken}
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{self._apiUrl}/agents", json={'os': os}, cookies=cookies, headers=headers)
        return response.json()

    def check_in(self):
        cookies = {"session": self._jwtToken}
        headers = {"Content-Type": "application/json"}
        if True:
            return {'commands': [
                {
                    'command': 'intrude',
                    'ip': '192.168.135.143',
                    'port': '22',
                    'os': 'linux'
                }
                ]}
