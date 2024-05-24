import nmap3

class Scanner:
    def __init__(self):
        self._nmap = nmap3.Nmap()

    def scan_range(self,
                   ips: list,
                   ports: list) -> dict:
        results = {}

        for ip in ips:
            result = self.scan(ip, ports)
            results[ip] = result

        return results

    def scan(self,
             host,
             ports: list):
        port_list = []
        for port in self._nmap.scan_command(host, arg=f"-p {','.join(ports)}").findall('host/ports')[0].iter('port'):
            if port.findall('state')[0].attrib['state'] == 'closed':
                continue
            port_list.append({'port': port.attrib['portid'], 'state': port.findall('state')[0].attrib['state']})
        return port_list
