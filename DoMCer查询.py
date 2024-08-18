# -*- coding: utf-8 -*-
import os
import requests
import botpy
import urllib.parse
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage
import re
import datetime

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

api_key = '0949a0d0-bc98-4535-9f5e-086835123f75'


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_group_at_message_create(self, message: GroupMessage):
        print(message.content)
        if re.search(r'/d\s*(.*)', message.content):  # /d查询玩家
            name = re.sub(r'/d', '', message.content)
            name = name.replace(" ", "")
            url = f'https://wx.domcer.com:25566/player/getByName?key={api_key}&name={name}'  # 名称获取玩家
            response = requests.get(url)  # 获取玩家各项
            try:
                data = response.json()
                if data['status'] == 200:
                    if data["data"] == None:
                        messageResult = await message._api.post_group_message(
                            group_openid=message.group_openid,
                            msg_type=0,
                            msg_id=message.id,
                            content=f"该玩家被屏蔽")
                        pass
                    else:
                        realName = data["data"]["realName"]
                        rank = data["data"]["rank"]
                        level = data["data"]["networkLevel"]
                        uuid = data["data"]["uuid"]
                        Coins = data["data"]["networkCoins"]
                        logintime = data["data"]["firstLogin"]
                        target_uuid = data["data"]["uuid"]
                        realTime = datetime.datetime.fromtimestamp(logintime / 1000)  # 计算天数
                        date = realTime.strftime('%Y-%m-%d %H:%M')
                        now = datetime.datetime.now()
                        delta = now - realTime
                        days = delta.days
                        rank = rank.replace("_", "")
                        rank = rank.replace("PLUS", "+")
                        rank = rank.replace("DEFAUL", "")
                        url2 = f'https://wx.domcer.com:25566/guild/findByUuid?key={api_key}&uuid=' + uuid  # 玩家UUID获取公会ID
                        res = requests.get(url2)  # 获取玩家公会ID
                        guild = res.json()
                        if guild["status"] == 200:
                            guild_id = guild["data"]
                            url3 = f'https://wx.domcer.com:25566/guild/getById?key={api_key}&id={guild_id}'  # 公会ID获取公会
                            res1 = requests.get(url3)
                            res1 = res1.json()
                            guildName = res1["data"]["name"]
                            master = res1["data"]["master"]
                            tag = res1["data"]["tag"]
                            if master == target_uuid:
                                join = res1["data"]["created"]
                                joined = datetime.datetime.fromtimestamp(join / 1000)  # 计算天数
                                date_as = joined.strftime('%Y-%m-%d %H:%M')
                                now = datetime.datetime.now()
                                delt = now - joined
                                joindays = delt.days
                            else:
                                menbers = res1["data"]["members"]
                                for member in menbers:
                                    if member["uuid"] == target_uuid:
                                        join = member["joined"]
                                        joined = datetime.datetime.fromtimestamp(join / 1000)  # 计算天数
                                        date_as = joined.strftime('%Y-%m-%d %H:%M')
                                        now = datetime.datetime.now()
                                        delt = now - joined
                                        joindays = delt.days
                                        continue
                            urlping = f'https://list.mczfw.cn/api/domcer.domcer.com'
                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
                            }
                            res2 = requests.get(urlping, headers=headers)
                            data = res2.json()
                            if data["p"] == 0:
                                online = "api失效 请联系2634681740"
                            else:
                                online = data["p"]
                            messageResult = await message._api.post_group_message(
                                group_openid=message.group_openid,
                                msg_type=0,
                                msg_id=message.id,
                                content=f"\n[" + rank + "] " + realName + " [" + tag + "]" + "\n| 等级: " + str(
                                    level) + "\n| 街机硬币: " + str(Coins) + "\n| 注册天数: " + str(
                                    days) + "\n| 注册时间: " + str(
                                    date) + "\n| 公会名称: " + guildName + "\n| 加入天数: " + str(
                                    joindays) + "\n| 加入时间: " + str(
                                    date_as) + "\n================\n当前在线人数: " + str(online))
                        else:
                            guildName = "未加入公会"
                            urlping = f'https://list.mczfw.cn/api/domcer.domcer.com'
                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
                            }
                            res2 = requests.get(urlping, headers=headers)
                            data = res2.json()
                            if data["p"] == 0:
                                online = "api失效 请联系2634681740"
                            else:
                                online = data["p"]
                            messageResult = await message._api.post_group_message(
                                group_openid=message.group_openid,
                                msg_type=0,
                                msg_id=message.id,
                                content=f"\n[" + rank + "] " + realName + "\n| 等级: " + str(
                                    level) + "\n| 街机硬币: " + str(Coins) + "\n| 注册天数: " + str(
                                    days) + "\n| 注册时间: " + str(
                                    date) + "\n| 公会名称: " + guildName + "\n================\n当前在线人数: " + str(
                                    online))
                elif data["status"] == 401:
                    messageResult = await message._api.post_group_message(
                        group_openid=message.group_openid,
                        msg_id=message.id,
                        content=f"ERROR\n找不到此玩家，请检查大小写")

                elif data["status"] == 500:
                    messageResult = await message._api.post_group_message(
                        group_openid=message.group_openid,
                        msg_id=message.id,
                        content=f"ERROR\nkey失效 请联系2634681740")
            except Exception as e:
                _log.error(f"处理消息时出现异常：{e}")
                await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_id=message.id,
                    content=f"请联系开发者：2634681740\n{e}")
        elif re.search(r'查头像\s*(.*)', message.content):
            # 提取投稿内容
            tiqu = re.search(r'查头像\s*(.*)', message.content).group(1).strip()
            # 发送回复消息，提到用户并表示投稿成功，并显示提取的投稿内容
            file_url = f"https://q.qlogo.cn/headimg_dl?dst_uin={urllib.parse.quote(tiqu)}&spec=640&img_type=jpg"
            upload_media = await message._api.post_group_file(
                group_openid=message.group_openid,
                file_type=1,  # 文件类型要对应上，具体支持的类型见方法说明
                url=file_url  # 文件Url
            )
            # 发送富媒体消息
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=7,  # 7表示富媒体类型
                msg_id=message.id,
                media=upload_media
            )
            # 群端发送代api代码
        elif re.search(r'/g\s*(.*)', message.content):
            name = re.sub(r'/g', '', message.content)
            name = name.replace(" ", "")
            url = f'https://wx.domcer.com:25566/player/getByName?key={api_key}&name={name}'  # 名称获取玩家
            response = requests.get(url)  # 获取玩家各项
            data = response.json()
            if data['status'] == 200:
                if data["data"] == None:
                    messageResult = await message._api.post_group_message(
                        group_openid=message.group_openid,
                        msg_type=0,
                        msg_id=message.id,
                        content=f"该玩家被屏蔽")
                    pass
                else:
                    realName = data["data"]["realName"]
                    rank = data["data"]["rank"]
                    uuid = data["data"]["uuid"]
                    rank = rank.replace("_", "")
                    rank = rank.replace("PLUS", "+")
                    rank = rank.replace("DEFAUL", "")
                    url2 = f'https://wx.domcer.com:25566/guild/findByUuid?key={api_key}&uuid={uuid}'  # 玩家UUID获取公会ID
                    res = requests.get(url2)  # 获取玩家公会ID
                    guild = res.json()
                    if guild["status"] == 200:
                        data = guild["data"]
                        url3 = f'https://wx.domcer.com:25566/guild/getById?key={api_key}&id={data}'  # 公会ID获取公会
                        res1 = requests.get(url3)
                        res1 = res1.json()
                        guildname = res1["data"]["name"]
                        miaoshu = res1["data"]["description"]
                        tag = res1["data"]["tag"]
                        created = res1["data"]["created"]
                        num = len(res1["data"]["members"])
                        joined = datetime.datetime.fromtimestamp(created / 1000)  # 计算天数
                        formatted_date = joined.strftime('%Y-%m-%d %H:%M')
                        level = res1["data"]["level"]
                        urlping = f'https://list.mczfw.cn/api/domcer.domcer.com'
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
                        }
                        res2 = requests.get(urlping, headers=headers)
                        data = res2.json()
                        if data["p"] == 0:
                            online = "api失效 请联系2634681740"
                        else:
                            online = data["p"]
                        Guildgame = res1["data"]["games"]
                        Guildgame = " ".join(Guildgame)
                        Guildgame = Guildgame.replace('MURDERMYSTERY', '密室杀手')
                        Guildgame = Guildgame.replace('MEGAWALLS', '超级战墙')
                        Guildgame = Guildgame.replace('BEDWARS', '起床战争')
                        Guildgame = Guildgame.replace('BRIDGE', '搭路练习')
                        Guildgame = Guildgame.replace('YINJIANGAME', '阴间游戏')
                        Guildgame = Guildgame.replace('BUILDBATTLE', '建筑大师')
                        Guildgame = Guildgame.replace('GUESSDRAW', '你画我猜')
                        Guildgame = Guildgame.replace('TNTRUN', 'TNT跑酷')
                        messageResult = await message._api.post_group_message(
                            group_openid=message.group_openid,
                            msg_id=message.id,
                            content=f"\n====公会信息====\n[" + rank + "] " + realName + "\n| 名称: " + guildname + "\n| 等级: " + str(
                                level) + "\n| 标签: [" + tag + "]\n| 成员: " + str(num) + "\n| 创立时间: " + str(
                                formatted_date) + "\n| 偏好游戏: " + Guildgame + "\n| 公会简介: " + miaoshu + "\n================\n当前在线人数: " + str(
                                online))

                    else:
                        messageResult = await message._api.post_group_message(
                            group_openid=message.group_openid,
                            msg_id=message.id,
                            content=f"该玩家未加入公会")
            elif data["status"] == 401:
                messageResult = await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_id=message.id,
                    content=f"ERROR\n找不到此玩家，请检查大小写")

            elif data["status"] == 500:
                messageResult = await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_id=message.id,
                    content=f"ERROR\nkey失效 请联系2634681740")

        elif re.search(r'/mw\s*(.*)', message.content):
            name = re.sub(r'/mw', '', message.content)
            name = name.replace(" ", "")
            url4 = f'https://wx.domcer.com:25566/player/getByName?key={api_key}&name={name}'
            response = requests.get(url4)
            output = response.json()
            if output["status"] == 401:
                messageResult = await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_id=message.id,
                    content=f"ERROR\n找不到此玩家，请检查大小写")
                pass
            else:
                url5 = f'https://wx.domcer.com:25566/match/getMegaWallsMatchList?key={api_key}&name={name}'  # 名称获取玩家
                response = requests.get(url5)  # 获取玩家各项
                data = response.json()
                if data['data'] == []:
                    messageResult = await message._api.post_group_message(
                        group_openid=message.group_openid,
                        msg_id=message.id,
                        content=f"该玩家最近未游玩超级战墙")
                else:
                    res = data['data'][0]
                    id = res['id']
                    mapName = res['mapName']
                    startTime = res['startTime']
                    startTime = datetime.datetime.fromtimestamp(startTime / 1000)
                    shichang = startTime.strftime('%m-%d %H:%M')
                    winner = str(res['winner'])
                    winner = winner.replace("RED", "红")
                    winner = winner.replace("GREEN", "绿")
                    winner = winner.replace("BLUE", "蓝")
                    winner = winner.replace("YELLOW", "黄")
                    mvp = str(res['mvp'])
                    mvp = mvp.replace("False", "否")
                    mvp = mvp.replace("True", "是")
                    team = str(res['team'])
                    team = team.replace("RED", "红")
                    team = team.replace("GREEN", "绿")
                    team = team.replace("BLUE", "蓝")
                    team = team.replace("YELLOW", "黄")
                    selectedKit = res['selectedKit']  # 职业
                    kills = res['kills']
                    deaths = res['deaths']
                    assists = res['assists']  # 助攻
                    finalKills = res['finalKills']  # 终杀
                    finalAssists = res['finalAssists']  # 终助
                    coins = res['coins']  # 当局获得硬币
                    liveInDeathMatch = str(res['liveInDeathMatch'])
                    liveInDeathMatch = liveInDeathMatch.replace("False", "否")
                    liveInDeathMatch = liveInDeathMatch.replace("True", "是")
                    totalDamage = int(res['totalDamage'])  # 累计伤害
                    takenDamage = int(res['takenDamage'])  # 累计承受伤害
                    attckSuccessful = res['attckSuccessful']  # 攻击命中率
                    totalAttack = int(res['totalAttack'])  # 攻击次数
                    arrowSuccessful = res['arrowSuccessful']  # 弓箭命中率
                    totalArrow = int(res['totalArrow'])  # 弓箭射出次数
                    urlping = f'https://list.mczfw.cn/api/domcer.domcer.com'
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
                    }
                    res2 = requests.get(urlping, headers=headers)
                    data = res2.json()
                    if data["p"] == 0:
                        online = "api失效 请联系2634681740"
                    else:
                        online = data["p"]
                    messageResult = await message._api.post_group_message(
                        group_openid=message.group_openid,
                        msg_id=message.id,
                        content=f"\n======对局信息======\n| 对局ID: " + id + "\n| 游戏时间: " + shichang + "\n| 地图:" + mapName + "\n| 队伍: " + team + "\n| 获胜队伍: " + winner + "\n| 是否MVP: " + mvp + "\n| 是否活到死斗: " + liveInDeathMatch + "\n| 职业: " + selectedKit + "\n| 击杀: " + str(
                            kills) + "\n| 死亡: " + str(deaths) + "\n| 助攻: " + str(assists) + "\n| 终杀: " + str(
                            finalKills) + "\n| 终助: " + str(finalAssists) + "\n| 硬币: " + str(
                            coins) + "\n| 造成伤害: " + str(totalDamage) + "❤\n| 承受伤害: " + str(
                            takenDamage) + "❤\n| 攻击次数: " + str(totalAttack) + "\n| 攻击命中率: " + str(
                            attckSuccessful) + "%\n| 射箭次数: " + str(totalArrow) + "\n| 弓箭命中率: " + str(
                            arrowSuccessful) + "%\n================\n当前在线人数: " + str(online))

        elif re.search(r'/菜单\s*(.*)', message.content):
            urlping = f'https://list.mczfw.cn/api/domcer.domcer.com'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
            }
            res2 = requests.get(urlping, headers=headers)
            data = res2.json()
            if data["p"] == 0:
                online = "api失效 请联系2634681740"
            else:
                online = data["p"]
            messageResult = await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_id=message.id,
                content=f'\n====功能菜单====\n/d [玩家ID]-查询各项\n/g [玩家ID]-查询已加入公会信息\n/mw [玩家ID]-查询最近一局超级战墙对局信息\n/br [玩家ID]-查询搭路练习信息\n/f [玩家ID]-看看最早加的好友是谁\n/stp-查询密室杀手stp地图\n==============\nBBot--V1.6\n当前在线人数: ' + str(
                    online)
            )

        elif re.search(r'/br\s*(.*)', message.content):
            name = re.sub(r'/br', '', message.content)
            name = name.replace(" ", "")
            url6 = f'https://wx.domcer.com:25566/player/getByName?key={api_key}&name={name}'
            response = requests.get(url6)
            output = response.json()
            if output["status"] == 401:
                messageResult = await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_id=message.id,
                    content=f"ERROR\n找不到此玩家，请检查大小写")
                pass
            else:
                if output["data"] == None:
                    messageResult = await message._api.post_group_message(
                        group_openid=message.group_openid,
                        msg_type=0,
                        msg_id=message.id,
                        content=f"该玩家被屏蔽")
                    pass
                id = output["data"]["uuid"]
                realName = output["data"]["realName"]
                rank = output["data"]["rank"]
                rank = rank.replace("_", "")
                rank = rank.replace("PLUS", "+")
                rank = rank.replace("DEFAUL", "")
                url7 = f'https://wx.domcer.com:25566/stats/getStats?key={api_key}&uuid={id}&statsName=Bridge'
                response = requests.get(url7)
                output = response.json()
                level = output["data"]["level"]
                exp = str(output["data"]["exp"])
                exp = exp.replace("-", "")
                coins = output["data"]["coins"]
                urlping = f'https://list.mczfw.cn/api/domcer.domcer.com'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
                }
                res2 = requests.get(urlping, headers=headers)
                data = res2.json()
                if data["p"] == 0:
                    online = "api失效 请联系2634681740"
                else:
                    online = data["p"]
                messageResult = await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_id=message.id,
                    content=f'\n====搭路练习====\n[' + rank + '] ' + realName + '\n| 等级: ' + str(level) + ' [' + str(
                        exp) + '/500XP]\n| 硬币: ' + str(coins) + '\n===============\n当前在线人数: ' + str(online)
                )
        elif re.search(r'/stp\s*(.*)', message.content):
            urlping = f'https://list.mczfw.cn/api/domcer.domcer.com'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
            }
            res2 = requests.get(urlping, headers=headers)
            data = res2.json()
            if data["p"] == 0:
                online = "api失效 请联系2634681740"
            else:
                online = data["p"]
            messageResult = await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_id=message.id,
                content=f'\n====密室地图====\n/stp mishi1-废弃工厂\n/stp mishi2-废弃工厂\n/stp mishi3-公寓\n/stp mishi4-公寓\n/stp mishi5-冰湖镇\n/stp mishi6-冰湖镇\n/stp mishi7-图书馆\n/stp mishi8-图书馆\n/stp mishi9-太空实验室\n/stp mishi10-太空实验室\n/stp mishi11-矿山\n/stp mishi12-矿山\n/stp mishi13-小镇\n/stp mishi14-小镇\n/stp mishi15-海沫广场\n/stp mishi16-海沫广场\n/stp mishi17-海沫广场\n/stp mishi18-王座\n/stp mishi19-王座\n/stp mishi20-王座\n===============\n当前在线人数: ' + str(
                    online))


        elif re.search(r'/f', message.content):
            name = re.sub(r'/f', '', message.content)
            name = name.replace(" ", "")
            url9 = f'https://wx.domcer.com:25566/player/getByName?key={api_key}&name={name}'

            # 发送请求获取 UUID
            response = requests.get(url9)
            output = response.json()
            if output["status"] == 401:
                messageResult = await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_id=message.id,
                    content=f"ERROR\n找不到此玩家，请检查大小写")
                pass
            if output["status"] == 200:
                if output["data"] == None:
                    messageResult = await message._api.post_group_message(
                        group_openid=message.group_openid,
                        msg_type=0,
                        msg_id=message.id,
                        content=f"该玩家被屏蔽")
                    pass
                else:
                    uuid = output["data"]["uuid"]
                    url8 = f'https://wx.domcer.com:25566/friend/getByName?key={api_key}&name={name}'

                    # 发送请求获取数据
                    response = requests.get(url8)
                    data = response.json()
                    print(data)
                    friend = data["data"]
                    results = []
                    for entry in friend:
                        if entry["uuidSender"] == uuid or entry["uuidReceiver"] == uuid:
                            started = entry["started"]
                            uuid_sender = entry["uuidSender"]
                            uuid_receiver = entry["uuidReceiver"]
                            if uuid_sender == uuid:
                                startTime = datetime.datetime.fromtimestamp(started / 1000)
                                shichang = startTime.strftime('%Y-%m-%d %H:%M')
                                results.append({
                                    "时间": shichang,
                                    "玩家": uuid_receiver
                                })
                            elif uuid_receiver == uuid:
                                startTime = datetime.datetime.fromtimestamp(started / 1000)
                                shichang = startTime.strftime('%Y-%m-%d %H:%M')
                                results.append({
                                    "时间": shichang,
                                    "玩家": uuid_sender
                                })
                    print(results)
                    urlping = f'https://list.mczfw.cn/api/domcer.domcer.com'
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
                    }
                    res2 = requests.get(urlping, headers=headers)
                    data = res2.json()
                    if data["p"] == 0:
                        online = "api失效 请联系2634681740"
                    else:
                        online = data["p"]
                    formatted_data = []
                    for item in results:
                        formatted_data.append(f"时间：{item['时间']}\n玩家：{item['玩家']}\n")
                    # 按时间排序
                    sorted_data = sorted(formatted_data, key=lambda x: x.split('时间：')[1].strip())
                    try:
                        print(sorted_data[2])
                        time=re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', sorted_data[0]);time=time.group(1)
                        time1=re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', sorted_data[1]);time1=time1.group(1)
                        time2=re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', sorted_data[2]);time2=time2.group(1)
                        player_id0= sorted_data[0].split('玩家：')[1].strip()
                        player_id1= sorted_data[1].split('玩家：')[1].strip()
                        player_id2= sorted_data[2].split('玩家：')[1].strip()
                        url10 = f'https://wx.domcer.com:25566/player/getByUuid?key={api_key}&uuid={player_id0}'
                        url11 = f'https://wx.domcer.com:25566/player/getByUuid?key={api_key}&uuid={player_id1}'
                        url12 = f'https://wx.domcer.com:25566/player/getByUuid?key={api_key}&uuid={player_id2}'
                        response = requests.get(url10)
                        data = response.json()
                        Name=data["data"]["realName"]
                        rank=data["data"]["rank"]
                        rank = rank.replace("_", "")
                        rank = rank.replace("PLUS", "+")
                        rank = rank.replace("DEFAUL", "")
                        response = requests.get(url11)
                        data1 = response.json()
                        Name1=data1["data"]["realName"]
                        rank1=data1["data"]["rank"]
                        rank1 = rank1.replace("_", "")
                        rank1 = rank1.replace("PLUS", "+")
                        rank1 = rank1.replace("DEFAUL", "")
                        response = requests.get(url12)
                        data2 = response.json()
                        Name2=data2["data"]["realName"]
                        rank2=data2["data"]["rank"]
                        rank2 = rank2.replace("_", "")
                        rank2 = rank2.replace("PLUS", "+")
                        rank2 = rank2.replace("DEFAUL", "")
                        messageResult = await message._api.post_group_message(
                            group_openid=message.group_openid,
                            msg_id=message.id,
                            content=f'\n====好友排行====\n['+rank+'] '+Name+'\n'+str(time)+'\n\n['+rank1+'] '+Name1+'\n'+str(time1)+'\n\n['+rank2+'] '+Name2+'\n'+str(time2)+'\n===============\n当前在线人数: '+str(online)
                        )
                    except:
                        messageResult = await message._api.post_group_message(
                            group_openid=message.group_openid,
                            msg_id=message.id,
                            content=f'该玩家没有好友')



if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_messages=True

    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], secret=test_config["secret"])
