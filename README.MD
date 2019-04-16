# 战舰少女4.3.x加密分析&~~api分析~~  

## http Post验证方式

重点是header里面的`Authorization`, 加密方式如下  

``` python
def getSign(url):
    key = 'kHPmWZ4zQBYP24ubmJ5wA4oz0d8EgIFe'
    urls = url.split("com")[-1]
    ts = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
    sign = hmac.new(key.encode(), ('POST\n' + ts + '\n' + urls).encode(), hashlib.sha1).digest()
    sign = base64.b64encode(sign).decode()
    return "HMS 881d3SlFucX5R5hE:" + sign
```

## http Get验证方式  

&emsp;&emsp;舰R的http get，靠的是uri里面的e，如`http://s4.jr.moefantasy.com/api/initGame?&crazy=0&t=1555412535408&e=8a2d0e8ea42411250bdb80cc1c863c60&gz=1&market=2&channel=100011&version=4.3.1`,按照之前`3.x`版本的话，是`uri`里面的参数加上一个`key`然后再进行md5，这次应该也是，不过没找到。但是发现登陆后，就算不计算e的值(甚至所有参数都不加)都可以正常请求数据，也就是说，在登陆后，`header`带上`cookie`的话上面那个链接可以直接改为`http://s4.jr.moefantasy.com/api/initGame`，并且可以正常获得所有数据  
&emsp;&emsp;综合上述，直接封包以下代码  

``` python
import requests
import hashlib
import hmac
import base64
import time
header = {
    "User-Agent": "okhttp/3.4.1",
}
session = requests.session()
session.headers.update(header)
def http_req(url, data=None):
    try:
        session.headers.pop("Authorization")
        session.headers.pop("Date")
    except KeyError:
        pass
    key = 'kHPmWZ4zQBYP24ubmJ5wA4oz0d8EgIFe'
    if data is not None:
        urls = url.split("com")[-1]
        ts = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        sign = hmac.new(key.encode(), ('POST\n' + ts + '\n' + urls).encode(), hashlib.sha1).digest()
        sign = base64.b64encode(sign).decode()
        session.headers.update({"Date": ts, "Authorization": "HMS 881d3SlFucX5R5hE:" + sign})
        return session.post(url, json=data, cookies=session.cookies.get_dict())
    return session.get(url, cookies=session.cookies.get_dict())
```

&emsp;&emsp;我的session请求时不自带cookie，只好加上`cookies=session.cookies.get_dict()`  

## api分析

### 登陆

1.获取`access_token`  

``` python
Method: POST
url: http://passportapi.moefantasy.com/1.0/get/login/@self
post data: {"platform": "0", "app_server_type": "0", "appid": "0", "password": "", "username": ""}
response: {
	"error": 0,
	"access_token": "",
	"refresh_token": "",
	"expires_in": 1555426589,
	"uuid": "",
	"appid": "0",
	"platform": "0",
	"auth_type": 0,
	"bind": "0",
	"puid": "",
	"is_bind_email": 0,
	"is_ID_verified": 1,
	"bind_status": -1,
	"username": "",
	"conflict": 0
}
```

2.获取cookie  
&emsp;&emsp;这里请求时，返回的相应头会有`set-cookie`，可以直接记录`header`，返回的`json`里也有`cookie`

``` python
method: GET
url: http://login.jr.moefantasy.com/index/hmLogin/{access_token}
respone: {
	"dataret": {
		"error": 0,
		"uuid": " ",
		"appid": "0",
		"platform": "0",
		"auth_type": 0,
		"bind": "0",
		"puid": " ",
		"is_bind_email": 0,
		"is_ID_verified": 1,
		"bind_status": -1,
		"username": " ",
		"conflict": 0
	},
	"hf_skey": " ", #这玩意儿就是cookies
	"userId": " ",
	"defaultServer": " ",
	"serverList": [{
			"id": "2",
			"host": "http:\/\/s2.jr.moefantasy.com\/",
			"name": "\u80e1\u5fb7",
			"status": "0",
			"hadRole": 0
		}, {
			"id": "4",
			"host": "http:\/\/s4.jr.moefantasy.com\/",
			"name": "\u4ffe\u65af\u9ea6",
			"status": "0",
			"hadRole": 1
		}, {
			"id": "13",
			"host": "http:\/\/s13.jr.moefantasy.com\/",
			"name": "\u6606\u897f",
			"status": "0",
			"hadRole": 0
		}, {
			"id": "14",
			"host": "http:\/\/s14.jr.moefantasy.com\/",
			"name": "\u957f\u6625",
			"status": "1",
			"hadRole": 0
		}
	],
	"conflict": 0,
	"noticeHtmlUrl": "",
	"gameBBSUrl": ""
}
```

