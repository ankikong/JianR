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


def login(username, password):
    data = {"platform": "0", "app_server_type": "0", "appid": "0", "password": str(username), "username": str(password)}
    return http_req("http://passportapi.moefantasy.com/1.0/get/login/@self", data=data)


rs = login("", "")
