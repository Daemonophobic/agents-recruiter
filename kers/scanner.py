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
            print(result)
            results[ip] = result

        return results

    def scan(self,
             host,
             ports: list):
        for port in self._nmap.scan_command(host, arg="-p 80,22").findall('host/ports')[0].iter('port'):
            print({'port': port.attrib['portid'], 'state': port.findall('state')[0].attrib['state']})
        return ""
