from pprint import pprint
from string import Template
import requests
import yaml
from jsonpath import jsonpath

# BaseApi实现了所有公共类的需要的东西
class BaseApi():
    # 封装requests函数，需要传入请求字典类型的req请求
    def send_api(self,req:dict):
        """
        data={
            "method":"GET",
            "url":f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?",
            "params":f"corpid={self.corpid}&corpsecret={secret}"
        }
        """
        # request的参数接收method，url，params，data，json
        # 把这些参数都写在一个字典里面，**req就可以解包
        # 变成method="get",url="http://xxx"，符合request传参的需求
        res=requests.request(**req)
        r=res.json()
        return r

    @classmethod
    # 优化jsonpath代码，其他类就不用from jsonpath improt jsonpath了
    def jsonpath(cls,json,expr):
        return jsonpath(json,expr)

    @classmethod
    # 封装yaml读取的代码，通过路径直接读取yml文件并转化成python数据类型
    def load_yaml(cls,path):
        with open(path) as f:
            return yaml.safe_load(f)

    @classmethod
    # 模板技术输入yml文件路径，data是需要修改的模板变量的字典类型
    # sub是对yml的数据进行二次提取，等于是一个大字典，再提取下一层的小字典，为了让一个yml文件可以有多个接口数据
    def template(cls,path,data,sub=None):
        with open(path) as f:
            if sub is None:
                # 不需要对数据进行二次提取
                # Template(f.read()).substitute(data)先替换变量
                # yaml.safe_load把yml格式的字符串变成dict类型返回
                return yaml.safe_load(Template(f.read()).substitute(data))
            else:
                # 由于Template需要替换全部的变量，有漏的就会报错，先写Template(f.read()).substitute(data)
                # 就会报错，data只对sub下一层的数据改，并没有改其他层的数据，肯定会报错
                # 需要先yaml.safe_load(f)[sub]提取到下一层的数据，但由于是dict
                # 要通过yaml.dump转化成yml格式的字符串，经过Template来改变变量，最后在yaml.safe_load转化成dict
                return yaml.safe_load(Template(yaml.dump(yaml.safe_load(f)[sub])).substitute(data))
                # return yaml.safe_load(Template(f.read()).substitute(data))

if __name__=="__main__":
    pass