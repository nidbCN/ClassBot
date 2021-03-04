from .LoginCAS import Login
import requests


class GetTestTime(object):
    def __init__(self, member: Login):
        self.__url = 'http://222.31.49.139/jwglxt/kwgl/kscx_cxXsksxxIndex.html?doType=query&gnmkdm=N358105&su=' + str(
            member.getUserID())

        self.__result = requests.get(url=self.__url, cookies=member.getCookies()).json()['items']

    def getResult(self):
        resultDict = {
            'items': []
        }
        for i in self.__result:
            if '不可查' not in i['kssj']:
                print(i['sjbh'] + ': ' + i['kssj'])
                tmpDict = {
                    'name': i['jxbmc'],
                    'time': i['kssj'],
                    'type': i['ksmc']
                }
                resultDict['items'].append(tmpDict)
        # return self.__result
        return resultDict
