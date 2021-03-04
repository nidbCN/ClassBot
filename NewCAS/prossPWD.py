import requests


class PublicKey(object):
    def __getResult(self):
        self.__result = self.__rq.get(url=self.__url).json()
        self.modulus = self.__result['modulus']
        self.exponent = self.__result['exponent']

    def __init__(self, url, rq: requests):
        self.modulus = ''
        self.exponent = ''
        self.__rq = rq

        self.__result = {}
        self.__url = url + 'cas/v2/getPubKey'

        self.__getResult()


class EncodePWD(object):
    def __init__(self, data: PublicKey, pwd):
        self.__url__BackUP = 'https://whispering-furry-charger.glitch.me/encode'
        # self.__url = 'http://127.0.0.1:6562/encode'
        self.__url = 'http://10.101.163.66:6562/encode'
        a = ''
        for i in list(reversed(pwd)):
            a += i
        pwd = a
        self.__data = {
            'e': data.exponent,
            'm': data.modulus,
            'data': pwd
        }

        self.__getResult()

    def __getResult(self):
        try:
            self.__result = requests.post(url=self.__url, json=self.__data).json()['encoded']
        except:
            self.__result = requests.post(url=self.__url__BackUP, json=self.__data, timeout=10).json()['encoded']
            print("尝试使用备用接口中...")

    def getTruePWD(self):
        return self.__result
