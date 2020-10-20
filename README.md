## 接口自动化框架
#### 简介
- 仅仅对企业微信的标签进行增删改查
- 没有allure
- pytest的参数化并不完善
- 对请求的数据有做数据驱动

<br>

#### 测试框架
- api对象：完成对接口的封装
- 接口测试框架：完成对api的驱动
- 配置模块：完成配置文件的读取
- 数据封装：数据构造与测试用例的数据封装
- utils：其他功能封装，改进原生框架不足
- 测试用例：调用page/api对象实现业务并断言
- 貌似这个项目什么都没有


<br>

#### 未来改进的点
- 添加allure功能
- log日志要怎么弄好
- 装饰器怎么套用用
- 初始化的环境怎么弄
- 参数要怎么搞
- 配置文件怎么搞

<br>

## 技术特点

#### jsonpath的应用
- 非常方便的对json数据进行提取，日常的json数据的提取都是转化成字典格式，慢慢提取，但遇到复杂的json格式，提取很麻烦
- http://www.atoolbox.net/Tool.php?Id=792 线上直观工具
- 格式描述

xpath | jsonpath | 描述 
---|---|---
/ | $ | 根节点
. | @ | 现行节点
/  | .or[] | 取子节点
//  | .. | 不管位置，选择所有符合条件的条件
* | * | 匹配所有元素节点
[] | [] | 迭代器显示，比如数组下标，根据内容选值等
| \| | [,] | 支持迭代器中做多选
n/a | () | 支持表达式计算
[]| ?() | 支持过滤操作
```
from jsonpath import jsonpath
a={
  "errmsg": "ok",
  "tag_group": [
    {
      "group_id": "etMCs1DwAAg_jBNAuvGR3B21cwl4o0jg",
      "group_name": "test",
      "create_time": 1593707787,
      "tag": [
        {
          "id": "etMCs1DwAAfCApMLNagY9j3dwJyxL-zQ",
          "name": "ddd",
          "create_time": 1593760595,
          "order": 0
        },
        {
          "id": "etMCs1DwAAF_THSCKdSamOOA7ny89EEQ",
          "name": "abcde",
          "create_time": 1593854852,
          "order": 0
        }]
    }]
}
# 想要取出name为ddd的id，如果用dict的[]就非常麻烦
# $..tag先找到tag
# [?(@.name=='ddd')]可以找到这一层,这一层并不是tag的子类，tag没有父子类的关系
'''
{
          "id": "etMCs1DwAAfCApMLNagY9j3dwJyxL-zQ",
          "name": "ddd",
          "create_time": 1593760595,
          "order": 0
        }
'''
# 最后加一个.id表示这一层的id，就找到了
# jsonpath返回的是一个列表类型，需要加[0]
# 总结：$..tag找到了tag，然后[]作为下一级别，可以接收下标，或者下一层的数据，@也就是[]等价的下一层，所以才可以通过@.来找到2个元素的name，当name==ddd，就找到[]这层的全部数据，在用.id找下一层的id
id=jsonpath(a,"$..tag[?(@.name=='ddd')].id")[0]
```

<br>

#### Template 模板技术
- 当把数据存放到yaml文件中，如果yaml里面需要引用到变量的时候，通过dict[]的方式查找真的很麻烦
```
from string import Template

# 假设yaml的文件格式如下
import yaml

"""
"method": "post"
"url": "https://qyapi.weixin.qq.com/cgi-bin/externalcontact/add_corp_tag?"
"params": "access_token=$token"
"json":
  "group_id": "etMCs1DwAAg_jBNAuvGR3B21cwl4o0jg"
  "tag":
    - "name": "$name"
"""
# 读取上面的文件变成一个dict
data=yaml.safe_load("../data/tag_add.yml")
# 其中$token和$name是一个变量，我们需要替换$token和$name
token=1
name=2
# 只能通过dict找key和value慢慢找，这样子感觉有点low了，可以通过模板技术来改善
data["params"]=f"access_token={token}"
data["json"]["tag"][0]['name']=name
```

- 因此需要使用模板技术：Template
```
from string import Template

# 假设yaml的文件格式如下
import yaml

"""
"method": "post"
"url": "https://qyapi.weixin.qq.com/cgi-bin/externalcontact/add_corp_tag?"
"params": "access_token=$token"
"json":
  "group_id": "etMCs1DwAAg_jBNAuvGR3B21cwl4o0jg"
  "tag":
    - "name": "$name"
"""
# 可以把yml文件的两个变量都改变，无须管是什么数据类型
# 写法："${name}" 这样写是最好的
with open("data/tag_add.yml") as f:
  name=1
  token=2
  # Template接收一个字符串，然后通过substitute改变值
  # substitute需要包含全部的$变量的值，用字典来接收，不包含全部会报错的
  # 最终返回的类型是字符串的类型
  data=Template(f.read()).substitute({"name":name,"token":token})
  print(data)
"""
结果如下，的确改变了token和name的值
"method": "post"
"url": "https://qyapi.weixin.qq.com/cgi-bin/externalcontact/add_corp_tag?"
"params": "access_token=2"
"json":
  "group_id": "etMCs1DwAAg_jBNAuvGR3B21cwl4o0jg"
  "tag":
    - "name": "1"
"""
```

<br>
<br>


## 项目框架

#### api 保存api接口的文件夹
- base_api.py 封装通用的接口
  - send_api(self,req:dict):封装requests函数，需要传入请求字典类型的req请求
  - jsonpath(cls,json,expr):优化jsonpath代码，其他类就不用from jsonpath improt jsonpath了
  - load_yaml(cls,path):封装yaml读取的代码，通过路径直接读取yml文件并转化成python数据类型
  - template(cls,path,data,sub=None):模板技术输入yml文件路径，data是需要修改的模板变量的字典类型
```
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
```

<br>

- tag.py 存放标签的api
  - 有增加标签、删除标签、查看标签、修改标签的api
```
from api.base_api import BaseApi
from api.wework import Wework

# 企业微信标签的api类
class Tag(BaseApi):
    # 这是标签的秘钥
    secret="MDe1km8BK3AZ05Dnfw4uILuKCZDStZ2NPaokf-UE6c8"
    # 通过get_token获取到标签的access_token
    token=Wework().get_token(secret)

    # 这是增加标签的api，传一个tag_name
    def add_tag(self,name):
        # data={
        #     "method":"post",
        #     "url":"https://qyapi.weixin.qq.com/cgi-bin/externalcontact/add_corp_tag?",
        #     "params":f"access_token={self.token}",
        #     "json":{
        #         "group_id": "etMCs1DwAAg_jBNAuvGR3B21cwl4o0jg",
        #         "tag":[{"name":name}]
        #    }
        # }

        # 现在要把add_tag的数据都放到yaml文件上去
        # 但这种写法比较low，也不好控制和管理
        # data=self.load_yaml("../data/tag_add.yml")
        # print(data["params"])
        # data["params"]=f"access_token={self.token}"
        # data["json"]["tag"][0]['name']=name

        # 把请求的数据都放到yml文件，通过template模板把yml文件特定的值改成变量
        data=self.template("../data/tag_add.yml",{"token":self.token,"name":name})
        # 返回响应的dict
        return self.send_api(data)

    # 这是获取tag相关信息的api
    def get_tag(self):
        data={
            "method":"post",
            "url":"https://qyapi.weixin.qq.com/cgi-bin/externalcontact/get_corp_tag_list",
            "params":f"access_token={self.token}",
            "json":{
                "tag":[]
            }
        }
        return self.send_api(data)

    # 修改tag名字，需要传tag_id和修改后的名字
    def edit_tag(self,tag_id,edit_name):
        data={
            "method":"post",
            "url":"https://qyapi.weixin.qq.com/cgi-bin/externalcontact/edit_corp_tag",
            "params":f"access_token={self.token}",
            "json":{
                "id":tag_id,
                "name":edit_name
            }
        }
        return self.send_api(data)

    # 这是删除标签的api，需要传tag_id
    def delete_tag(self,tag_id):
        # data={
        #     "method":"post",
        #     "url":"https://qyapi.weixin.qq.com/cgi-bin/externalcontact/del_corp_tag",
        #     "params":f"access_token={self.token}",
        #     "json":{
        #         "tag_id":[tag_id]
        #     }
        # }
        data=self.template("../data/tag_all.yml",{"token":self.token,"tag_id":tag_id},"delete")
        return self.send_api(data)


if __name__=="__main__":
    pass
    # a=Tag()
    # print(a.add_tag("tongtong2"))
```

<br>

- wwwork.py 存放获取access_token的api
```
import requests
from api.base_api import BaseApi

# 封装企业微信公共的api类，继承BaseApi的公共类
class Wework(BaseApi):
    # 企业微信的id
    corpid="ww630f49269e06f865"
    # 获取access_token，不同的应用的秘钥，会产生不同的access_token，所以就封装起来了
    def get_token(self,secret):
        data={
            "method":"GET",
            "url":f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?",
            "params":f"corpid={self.corpid}&corpsecret={secret}"
        }
        # 使用send_api，传入data，相当于使用了requests了
        res= self.send_api(data)
        # 获取access_token
        token=res["access_token"]
        return token

if __name__=="__main__":
    a=Wework()
    print(a.get_token("YC9RRMQcQqGNxapjoeiDIn84mCY7H-aJblz_X9X073U"))
```

<br>

#### data 存放各种数据和yml文件
- add_contact.yml 存放add和delete的接口数据
```
add:
  "method": "post"
  "url": "https://qyapi.weixin.qq.com/cgi-bin/externalcontact/add_corp_tag"
  "params": "access_token=$token"
  "json":
    "group_id": "etMCs1DwAAg_jBNAuvGR3B21cwl4o0jg"
    "tag":
      - "name": "$name"

delete:
 "method": "post"
 "url": "https://qyapi.weixin.qq.com/cgi-bin/externalcontact/del_corp_tag"
 "params": "access_token=${token}"
 "json":
   "tag_id":
     - "$tag_id"
```
- tag_add.yml 存放add的接口数据
```
"method": "post"
"url": "https://qyapi.weixin.qq.com/cgi-bin/externalcontact/add_corp_tag?"
"params": "access_token=$token"
"json":
  "group_id": "etMCs1DwAAg_jBNAuvGR3B21cwl4o0jg"
  "tag":
    - "name": "$name"
```
- test_tag.yml testcase中test_all参数化的数据
```
-
  - tongtong
  - tongtong1
-
  - aaa
  - bbb
```

<br>

#### test_case 存放用例的文件夹
- test_get_token.py 测试access_token获取的用例
```
from api.wework import Wework

# 测试获取access_token能否获取成功
class TestGetToken():
    secret="YC9RRMQcQqGNxapjoeiDIn84mCY7H-aJblz_X9X073U"
    def test_get_token(self):
        a=Wework()
        print(a.get_token(self.secret).json())
```

<br>

- test_tag.py 测试标签的用例
```
import pytest
from api.tag import Tag

class TestTag():
    # 由于参数化的代码比classmethod更早执行，所以需要放到最外层去执行
    base_data=Tag().load_yaml("../data/test_tag.yml")

    @classmethod
    # 做测试的初始化，只需要初始化一次
    # 把tag标签都删除
    def setup_class(cls):
        # 定义好Tag()对象，cls.a，其他def test都可以用self.a使用
        cls.a=Tag()
        # 定义好要删除的的标签的名字
        name_data=["aaa","bbb","tongtong","tongtong1"]
        # 获取标签的数据
        data=cls.a.get_tag()
        # 对标签名字进行遍历
        for name in name_data:
            # 通过name去找到对应的tag_id
            tag_id=cls.a.jsonpath(data,f'$..tag[?(@.name=="{name}")].id')
            # 删除标签的api需要传tag_id
            cls.a.delete_tag(tag_id)

    # 测试获取标签的用例
    def test_get_tag(self):
        res=self.a.get_tag()
        assert res["errcode"] ==0
        # print(json.dumps(res,indent=2))

    # 使用参数化，数据都保存在yml文件，读取出来变成base_data
    @pytest.mark.parametrize(("oldname,newname"),base_data)
    # 测试一次增加标签，修改标签是否正常运行
    def test_all(self,oldname,newname):
        # 增加成功，errcode就是0
        assert self.a.add_tag(oldname)["errcode"] == 0
        tag_id=self.a.jsonpath(self.a.get_tag(),f"$..tag[?(@.name=='{oldname}')].id")[0]
        # edit_tag修改标签需要传tag_id，获取即可，修改成功后，errcode就是0
        assert self.a.edit_tag(tag_id,newname)["errcode"] == 0

    # 测试删除是否成功的用例
    def test_delete(self):
        name="tongtong1"
        # 当tag_id是一个可变的值，只要能够获取，弄成变量即可
        tag_id = self.a.jsonpath(self.a.get_tag(), f"$..tag[?(@.name=='{name}')].id")[0]
        assert self.a.delete_tag(tag_id)["errcode"] ==0
``
