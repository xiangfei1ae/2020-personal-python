import json
import os

import argparse


class Data:
    def __init__(self, dict_address: int = None, reload: int = 0):
        if reload == 1:
            self.__init(dict_address)       #使用__init函数进行处理，进行首次初始化
        if dict_address is None and not os.path.exists('1.json') and not os.path.exists('2.json') and not os.path.exists('3.json'):     #文件夹未被赋值
            raise RuntimeError('error: init failed')
        x = open('1.json', 'r', encoding='utf-8').read()
        self.__4Events4PerP = json.loads(x)
        x = open('2.json', 'r', encoding='utf-8').read()
        self.__4Events4PerR = json.loads(x)
        x = open('3.json', 'r', encoding='utf-8').read()
        self.__4Events4PerPPerR = json.loads(x)

    def __init(self, dict_address: str):        #进行数据初始化
        json_list = []      #创建列表
        for root, dic, files in os.walk(dict_address):
            for f in files:
                if f[-5:] == '.json':
                    json_path = f       #确定文件是json，进行解析
                    x = open(dict_address+'\\'+json_path,       #这里使用转义字符编辑了文件查询路径
                             'r', encoding='utf-8').read()      #得到了一个大字符串
                    str_list = [_x for _x in x.split('\n') if len(_x) > 0]      #对大字符串进行分割，每个元素是列表的一部分
                    for i, _str in enumerate(str_list):     #i是序号，_str是里面的一部分字符串，时每一次行为的信息  
                        try:
                            json_list.append(json.loads(_str))      #
                        except:
                            pass
        records = self.__listOfNestedDict2ListOfDict(json_list)
        self.__4Events4PerP = {}
        self.__4Events4PerR = {}
        self.__4Events4PerPPerR = {}
        for i in records:
            if not self.__4Events4PerP.get(i['actor__login'], 0):
                self.__4Events4PerP.update({i['actor__login']: {}})
                self.__4Events4PerPPerR.update({i['actor__login']: {}})
            self.__4Events4PerP[i['actor__login']][i['type']
                                         ] = self.__4Events4PerP[i['actor__login']].get(i['type'], 0)+1
            if not self.__4Events4PerR.get(i['repo__name'], 0):
                self.__4Events4PerR.update({i['repo__name']: {}})
            self.__4Events4PerR[i['repo__name']][i['type']
                                       ] = self.__4Events4PerR[i['repo__name']].get(i['type'], 0)+1
            if not self.__4Events4PerPPerR[i['actor__login']].get(i['repo__name'], 0):
                self.__4Events4PerPPerR[i['actor__login']].update({i['repo__name']: {}})
            self.__4Events4PerPPerR[i['actor__login']][i['repo__name']][i['type']
                                                          ] = self.__4Events4PerPPerR[i['actor__login']][i['repo__name']].get(i['type'], 0)+1
        with open('1.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerP,f)
        with open('2.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerR,f)
        with open('3.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerPPerR,f)

    def __parseDict(self, d: dict, prefix: str):
        _d = {}
        for k in d.keys():
            if str(type(d[k]))[-6:-2] == 'dict':
                _d.update(self.__parseDict(d[k], k))
            else:
                _k = f'{prefix}__{k}' if prefix != '' else k
                _d[_k] = d[k]
        return _d

    def __listOfNestedDict2ListOfDict(self, a: list):
        records = []
        for d in a:
            _d = self.__parseDict(d, '')
            records.append(_d)
        return records

    def getEventsUsers(self, username: str, event: str) -> int:
        if not self.__4Events4PerP.get(username,0):
            return 0
        else:
            return self.__4Events4PerP[username].get(event,0)

    def getEventsRepos(self, reponame: str, event: str) -> int:
        if not self.__4Events4PerR.get(reponame,0):
            return 0
        else:
            return self.__4Events4PerR[reponame].get(event,0)

    def getEventsUsersAndRepos(self, username: str, reponame: str, event: str) -> int:
        if not self.__4Events4PerP.get(username,0):
            return 0
        elif not self.__4Events4PerPPerR[username].get(reponame,0):
            return 0
        else:
            return self.__4Events4PerPPerR[username][reponame].get(event,0)


class Run:
    def __init__(self):
        self.parser = argparse.ArgumentParser()     #便于向py中传递参数
        self.data = None
        self.argInit()      #传入参数，进行初始化
        print(self.analyse())

    def argInit(self):
        self.parser.add_argument('-i', '--init')        #文件夹
        self.parser.add_argument('-u', '--user')
        self.parser.add_argument('-r', '--repo')
        self.parser.add_argument('-e', '--event')

    def analyse(self):
        if self.parser.parse_args().init:
            self.data = Data(self.parser.parse_args().init, 1)      #文件夹不为空，进行搜索，同时reload=1，进行第一次初始化
            return 0
        else:
            if self.data is None:       #初始化完成后进行统计搜索，为输入的参数进行运算
                self.data = Data()
            if self.parser.parse_args().event:
                if self.parser.parse_args().user:
                    if self.parser.parse_args().repo:
                        res = self.data.getEventsUsersAndRepos(     #运行函数事件人项目
                            self.parser.parse_args().user, self.parser.parse_args().repo, self.parser.parse_args().event)
                    else:
                        res = self.data.getEventsUsers(
                            self.parser.parse_args().user, self.parser.parse_args().event)
                elif self.parser.parse_args().repo:
                    res = self.data.getEventsRepos(
                        self.parser.parse_args().repo, self.parser.parse_args().event)
                else:
                    raise RuntimeError('error: argument -l or -c are required')
            else:
                raise RuntimeError('error: argument -e is required')
        return res


if __name__ == '__main__':
    a = Run()
