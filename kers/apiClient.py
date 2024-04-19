import requests
import json


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
