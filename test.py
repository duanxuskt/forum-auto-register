import requests
import json

kdl_orderid = '958717863342866'
kdl_API_Key = 'vl7il4z32zxi8fi3jdbhy6h20l6a4oni'


def get_proxy():
    proxy_url_json = requests.get(
        url="https://tps.kdlapi.com/api/tpscurrentip?orderid=%s&signature=%s" % (kdl_orderid, kdl_API_Key))
    dic = json.loads(proxy_url_json.text)
    if len(dic['data']) >= 1:
        proxy_url = dic['data']['current_ip']
        return proxy_url


if __name__ == '__main__':
    get_proxy()
