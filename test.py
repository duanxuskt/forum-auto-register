import requests
import json
import socket
import sys
import struct

kdl_orderid = '958717863342866'
kdl_API_Key = 'vl7il4z32zxi8fi3jdbhy6h20l6a4oni'


def get_proxy():
    proxy_url_json = requests.get(
        url="https://tps.kdlapi.com/api/tpscurrentip?orderid=%s&signature=%s" % (kdl_orderid, kdl_API_Key))
    dic = json.loads(proxy_url_json.text)
    if len(dic['data']) >= 1:
        proxy_url = dic['data']['current_ip']
        return proxy_url


def update_ip():
    myname = socket.getfqdn(socket.gethostname())
    print(myname)
    url = "https://dev.kdlapi.com/api/setipwhitelist"
    resp = requests.get(url, params={'orderid': kdl_orderid, 'signature': kdl_API_Key})
    dic = json.loads(resp.text)
    print(dic['msg'])


def get_ip_address(ifname=None):
    if sys.platform == 'win32':
        return socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET, socket.SOCK_DGRAM)[-1][4][0]
    else:
        import fcntl
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])


if __name__ == '__main__':
    # test_get_proxy()
    # test_update_ip()
    my_ip = requests.get('http://ip.42.pl/raw').text
