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
response: {
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

### 万金油api  

这个api还是少用点好，返回的数据大得一批，但是包含了基本所有的数据，客户端只在启动时调用了一次

``` python
method: GET
url: http://s4.jr.moefantasy.com/api/initGame
response: too large to paste (analyzed by yourself)
```

### 地图api

我也不知道这是个什么api，返回数据有关地图和buff，好久没玩了，具体未知

``` python
method: GET
url: http://s4.jr.moefantasy.com/pve/getPveData
response:
{
    "pve": [{
			"id": "1",
			"last_pve_level_id": "105",
			"needPveLevelId": "0",
			"needUserLevel": "1",
			"pveId": "0",
			"pveLevelNum": "5",
			"title": "母港周边哨戒"
		},...
    ],
    "pveBuff": [{
			"buff_icon": "80003",
			"change_buff": "0",
			"change_condition": "0",
			"change_desc": "0",
			"change_id": "0",
			"desc": "^CFFFFFFFF00000000全体^C00FFEAFFFFFFFF00火力+15,命中-10^CFFFFFFFF00000000",
			"desc2": "^C454545FF00000000全体^C2997FFFFFFFFFF00火力+15,命中-10^C454545FF00000000",
			"effect": [{
					"num": 15,
					"num4": 2,
					"type": 7
				}, {
					"num": 10,
					"num4": 17,
					"type": 8
				}
			],
			"effect_desc": "舰队获得了最新的战斗情报，请谨慎选择。",
			"id": "100",
			"title": "机密情报:E",
			"type": "4"
		},...
    ],
    "pveLevel": [{
			"animation": "0",
			"arrow": "0",
			"award": "{}",
			"bossId": 0,
			"boss_bg": "0",
			"boss_ship_exp": "30",
			"boss_user_exp": "30",
			"debuff": "",
			"desc": "0",
			"difficulty": "1",
			"fleet_type": "0",
			"hard": "0",
			"hp": "0",
			"hp2": "0",
			"hp_type": "0",
			"id": "101",
			"initNodeId": "10101",
			"isRedPath": "0",
			"is_support": "0",
			"mapId": 101,
			"music": "",
			"needPveLevelId": "0",
			"needUserLevel": "1",
			"need_pve_levels": "0",
			"need_ship_ton": [],
			"need_ship_ton_desc": "0",
			"next_pve_id": "0",
			"next_pve_level": "0",
			"nodeNum": "4",
			"position": "0",
			"pruductGoods": [],
			"pveId": "1",
			"ship_exp": "30",
			"ship_ton_desc": "0",
			"subTitle": "母港附近海域",
			"sup_attack": "0",
			"support_id": "0",
			"support_next_desc": "0",
			"support_open_desc": "0",
			"support_pre_desc": "0",
			"task_cid": "0",
			"title": "1-1",
			"type": "1",
			"user_exp": "10"
		},...
    ],
    "pveNode": [{
			"award": False,
			"award2": "",
			"bg_sea": "BG_East_China_Sea",
			"bg_sea2": "0",
			"boss_hp_type": "0",
			"bubble_icon": "0",
			"buff": [],
			"cia_id": "0",
			"flag": "",
			"formation": [],
			"formation2": "0",
			"formation2_effect": "0",
			"guard_npc": "0",
			"id": "10101",
			"mapId": 0,
			"movie": "0",
			"nextNode": [10102],
			"nextNodePath": {
				"101-0-A": {
					"x": 277,
					"y": 509
				}
			},
			"night_atk": "0",
			"nodeAttribute": "1",
			"nodeHide": [],
			"nodeRounter": [],
			"nodeType": "4",
			"node_miss": [],
			"node_step": "0",
			"position": {
				"x": 228,
				"y": 536
			},
			"position_letter": {
				"x": 0,
				"y": 0
			},
			"pveLevelId": "101",
			"roundabout": "0",
			"routeNum": [],
			"score": "0",
			"shipExp": "0",
			"show_condtion": "1",
			"spoils_rate": "0",
			"support_atk": "0",
			"support_icon": "0",
			"surp_attack": "0",
			"treasure_icon": "0",
			"unlock_buy_cid": "0",
			"unlock_miss_node": "0",
			"unlock_node_id": "",
			"userExp": "0"
		},...
    ]
}
```

### 未知

``` python
method: GET
url: http://s4.jr.moefantasy.com/bsea/getData
response:
```

### 食谱厨房参数(?)

``` python
method: GET
url: http://s4.jr.moefantasy.com/live/getUserInfo
respone: {
	"boatExpBuffBuffId": 946,
	"boatExpBuffEndtime": 0,
	"buff": "",
	"chief": "1451",
	"cookbook": ["10000472"],
	"cookbookProficiency": [],
	"eatTimes": 0,
	"kitchenStyle": 11145,
	"popularity": "0"
}
```

### 用户数据

``` python
method: GET
url: http://s4.jr.moefantasy.com/active/getUserData
response: {
	"firendNumTips": 0,
	"friendVo": {
		"avatar_cid": "10001261",
		"bathhouse": "174",
		"class_num": 1,
		"fleetShips": [ ], # 旗舰舰队配置
		"level": " ", # 角色等级
		"main_music": 0,
		"medal": [1102, 101, 402, 301],
		"newApply": 0,
		"newFirend": 0,
		"recommendStatus": "0",
		"res_dis": 1,
		"room_display": [0, 10343, 0],
		"room_style": 0,
		"secretary": {
			"ship_cid": " ",
			"skin_cid": "0"
		},
		"show_room_style": 0,
		"sign": "",
		"tactics_num2": "0",
		"tactics_status": "1",
		"userMedalNum": 10,
		"username": "  ", # 用户昵称
		"wall_display": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	},
	"marketingData": {
		"activeList": [],
		"blueRibbon": 0,
		"continueLoginAward": {
			"canGetDay": -1,
			"haveGetDays": [1, 2, 3, 4, 5],
			"period": 2
		},
		"firstPayAward": {
			"canGet": 0,
			"haveGet": 0
		},
		"hideBrokenImageInAndroid": 0,
		"isBattleSeaEvent": 0,
		"isGuardEvent": 0,
		"isHasBuildEvent": 0,
		"isHasPVEEXPEvent": 0,
		"isHasPVEExploreEvent": 0,
		"isSolidStrikeEvent": 0,
		"isSpoilsShopEvent": 0,
		"isThreeYearEvent": 0,
		"isTwoYearEvent": 0,
		"mustChangePwd": 0,
		"pveEventIndex": "24",
		"pveEventOpen": 0,
		"pveEventTitle": "熔炉大混战",
		"reachLevelAward": [10, 20, 30, 50, 40],
		"showBindingOtherPlatform": 0,
		"showBrokenImageInIos": 1,
		"showCouponSetting": 0,
		"showFirstCharge": 1,
		"showForumLink": 0,
		"showIosBuyNotice": 1,
		"showRank": 0,
		"showRecentMarketing": 0,
		"showWikiLink": 1,
		"userRegStatus": 4
	},
	"newMailNum": 19,
	"shopNumTips": 0,
	"snowing": 2,
	"userResVo": {
		"aluminium": 60, # 铝
		"ammo": 10, # 弹药
		"gold": 0, # 金？？？
		"oil": 50, # 油
		"steel": 90 # 钢
	}
}
```

### 演习&攻略进度有关数据

``` python
method: GET
url: http://s4.jr.moefantasy.com/pve/getUserData
response:{
	"currentVo": {
		"pveId": 6,
		"pveLevelId":  
	},
	"missLine": [995 , 99 ],
	"passedNodes": [ ], # 剧情已经通过的节点
	"pveLevel": [{
			"hp": 0,
			"hp2": "0",
			"id": " ",
			"pveLevelId":  ,
			"status": "1",
			"support_aluminium": "0",
			"support_ammo": "0",
			"support_level": 0,
			"support_oil": "0",
			"support_status": "0",
			"uid": " "
		}....
	],
	"winNode": []
}
```

### 战役有关数据

``` python
method: GET
url: http://s4.jr.moefantasy.com/campaign/getUserData
response: {
	"campaignChallenge": [{
			"campaignId": 1,
			"passNum": 0,
			"remainNum": 2
		}, {
			"campaignId": 2,
			"passNum": 0,
			"remainNum": 2
		}, {
			"campaignId": 3,
			"passNum": 0,
			"remainNum": 2
		}, {
			"campaignId": 4,
			"passNum": 0,
			"remainNum": 2
		}
	],
	"canCampaignChallengeLevel": ["101", "102", "201", "202", "301", "302", "401", "402", "501"],
	"passInfo": {
		"passNum": 0,
		"remainNum": 8, # 剩余次数
		"totalNum": 8
	}
}

```

### 等待分析

``` python
http://s4.jr.moefantasy.com/index/login/{uid}
http://s4.jr.moefantasy.com/boat/instantFleet/4/[549] 快速编队

http://s4.jr.moefantasy.com/pve/cha11enge/{地图编号}/{舰队编号}/0/
http://s4.jr.moefantasy.com/pve/newNext
http://s4.jr.moefantasy.com/pve/spy 索敌
http://s4.jr.moefantasy.com/pve/dealto/10102/4/1 战斗
http://s4.jr.moefantasy.com/pve/getWarResult/0 结果 0对应0

http://s4.jr.moefantasy.com/task/getAward/2200132 完成任务

http://s4.jr.moefantasy.com/boat/supplyFleet/4 全舰队补给
http://s4.jr.moefantasy.com/boat/supply/160 单船只补给

http://s4.jr.moefantasy.com/boat/repair/917/0 船只修理
http://s4.jr.moefantasy.com/boat/instantRepair/1 快速修复

http://s4.jr.moefantasy.com/dock/dismantleBoat/[7567,7568]/1 分解 1不卸下装备

http://s4.jr.moefantasy.com/pvp/getChallengeList 演习列表
http://s4.jr.moefantasy.com/pvp/spy/4941767/4/ 
http://s4.jr.moefantasy.com/pvp/challenge/4941767/4/4
http://s4.jr.moefantasy.com/pvp/getWarResult/1

http://s4.jr.moefantasy.com/explore/start/5/10001 开始远征
http://s4.jr.moefantasy.com/explore/getResult/10001 完成远征

```