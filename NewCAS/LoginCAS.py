from NewCAS.prossPWD import PublicKey as PKey, EncodePWD as EPwd
import requests, time
from lxml import etree


class Login(object):
    def __init__(self, userID: str, pwd: str):
        self.__user = userID
        self.__rq = requests.Session()
        self.__url = 'http://zhzb.nuc.edu.cn/cas/login'
        self.__result = self.__rq.get(url=self.__url)

        self.__pwd = EPwd(PKey('http://zhzb.nuc.edu.cn/', self.__rq), pwd).getTruePWD()

        self.__data = {
            'username': userID,
            'password': self.__pwd,
            'mobileCode': '',
            'execution': self.__getExecution(),
            'authcode': '',
            '_eventId': 'submit'
        }

        self.__loginNOW()
        self.__cookies = self.__result.cookies

    def __loginNOW(self):
        self.__result = self.__rq.post(url=self.__url, data=self.__data)

    def __getExecution(self):
        return etree.HTML(self.__rq.get(url=self.__url).text).xpath('/html/body/div/div[3]/div[2]/div/div[2]/div/div['
                                                                    '1]/form/input[1]/@value')[0]

    def getCookies(self):
        # return '; '.join([item.name + '=' + item.value for item in self.__cookies])
        return self.__rq.cookies

    def getUserID(self):
        return self.__user

    def getGrades(self):
        url = 'http://222.31.49.139/jwglxt/cjcx/cjcx_cxDgXscj.html?doType=query&gnmkdm=N305005'
        data = {
            "xnm": "",
            "xqm": "",
            "queryModel.showCount": 1000
        }
        
        ret = None

        try:
            ret = self.__rq.post(url=url, json=data).json()
        except BaseException as e:
            print("ERROR!!!" + str(e))
        return ret
