import requests

class Proxy:
    def __init__(self):
        self.username = 'lum-customer-hl_e26add8d-zone-static'
        self.parameters = '-country-us-dns-local'
        self.password = 'h9lsd1exrlcr'
        self.server = 'servercountry-us.zproxy.luminati.io:22225'
        self.session = range(10)
        self.current_session = 0

    def __get_proxy_address(self):
        proxy = 'http://' + self.username + '-session-' + str(self.session[self.current_session]) + \
        self.parameters + ':' + self.password + '@' + self.server
        self.current_session += 1
        self.current_session %= len(self.session)
        
        return {
            'http': proxy,
            'https': proxy
        }
    
    def get(self, url):
        return requests.get(url, proxies=self.__get_proxy_address(), timeout=5)

    def safe_get(self, url, headers, timeout):
        res = None
        isOk = False
        while not isOk:
            try:
                res = requests.get(url, headers=headers, timeout=timeout)
                isOk = True
            except requests.exceptions.Timeout as e:
                print('safe get: ' + url + ' exception\n' + str(e))
        
        return res
    
    def safe_post(self, url, data, headers, timeout):
        res = None
        isOk = False
        while not isOk:
            try:
                res = requests.post(url, data=data, headers=headers, timeout=timeout)
                isOk = True
            except requests.exceptions.Timeout as e:
                print('safe post: ' + url + ' exception\n' + str(e))
        
        return res
        