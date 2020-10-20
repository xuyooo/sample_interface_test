from api.wework import Wework

# 测试获取access_token能否获取成功
class TestGetToken():
    secret="YC9RRMQcQqGNxapjoeiDIn84mCY7H-aJblz_X9X073U"
    def test_get_token(self):
        a=Wework()
        print(a.get_token(self.secret).json())