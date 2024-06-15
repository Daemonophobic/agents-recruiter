import ipaddress
import string


def ip_parse(subnets: [string]) -> [string]:
    iplists = []
    for subnet in subnets:
        iplists += [str(ip) for ip in ipaddress.IPv4Network(subnet)]
    return iplists