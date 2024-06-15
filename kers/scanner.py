import xml.etree.ElementTree as ET
import nmap3
from tqdm import tqdm

class Scanner:
    def __init__(self):
        self._nmap = nmap3.Nmap()

    def scan_range(self,
                   ips: list,
                   ports: list) -> dict:
        results = {}

        for ip in tqdm(ips):
            result = self.scan(ip, ports)
            if result:
                results[ip] = result
            else:
                continue
        return results

    def scan(self,
             host,
             ports: list):
        try:
            port_list = []
            if host.endswith('.0') or host.endswith('.255'):
                return []
            nmap_result = self._nmap.scan_command(host, arg=f"-Pn -p {','.join(ports)}")
            up = ET.tostring(nmap_result).replace(b'\n', b'')
            if b'hosts up="0"' in up:
                return []
            for port in nmap_result.findall('host/ports')[0].iter('port'):
                if port.findall('state')[0].attrib['state'] == 'closed':
                    continue
                port_list.append({'port': port.attrib['portid'], 'state': port.findall('state')[0].attrib['state']})
            return port_list
        except Exception:
            return []