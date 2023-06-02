from typing import Optional
import socket
import requests
import re
import json
import pymysql
import nonebot
import time
from nonebot import on_command
from nonebot.adapters.telegram import Bot
from nonebot.adapters.telegram.message import MessageSegment
from nonebot.adapters.telegram.event import MessageEvent
from nonebot.adapters import Message
from nonebot.params import CommandArg
from config import dbhost, dbuser, dbpassword, dbname, embyserver, api_key, bot_token, emby_chat_id, chat_id_list, white_list
# from telethon.tl.types import ChannelParticipantsAdmins
import random
import string
from websocket import create_connection
from datetime import datetime
import pytz
from itertools import chain
import ssl
import socket

def renshu_gyf():
    nowplay = len([r['PlayState']['CanSeek'] for r in requests.get(embyserver + '/Sessions?api_key=' + api_key).json()if r['PlayState']['CanSeek'] == True])
    return nowplay

def ItemsCount():
    r = requests.get(f'{embyserver}/Items/Counts?api_key={api_key}').text
    r= json.loads(r)
    MovieCount = r['MovieCount']
    SeriesCount = r['SeriesCount']
    EpisodeCount = r['EpisodeCount']
    MusicCount = r['SongCount']

    return MovieCount,SeriesCount,EpisodeCount,MusicCount

def get_bot() -> Optional[Bot]:
    """
    说明：
        获取 bot 对象
    """
    try:
        return list(nonebot.get_bots().values())[0]
    except IndexError:
        return None

check = on_command(
    "account",
)
resetpw = on_command(
    "reset"
    )
counts = on_command(
    "counts"
    )
checkrul = on_command(
    "checkurl"
    )
add_invite = on_command(
    "add_code"
    )
status = on_command(
    "status"
    )
total = on_command(
    "total"
    )
checkserver =on_command(
    "checkserver"
    )
@checkserver.handle()
async def _(event: MessageEvent, message: Message = CommandArg()):
    parse_mode = 'Markdown'
    db = pymysql.connect(host=dbhost, user=dbuser,password=dbpassword,db=dbname )
    cursor = db.cursor()
    bot = get_bot()
    user_id = int(event.get_user_id())
    chat_id = event.chat.id
    message_id = event.message_id
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    if chat_id == user_id:
        await bot.send_message(chat_id=user_id, text="私聊无效，请在内部群发送命令")
        await checkserver.finish()
    if chat_id not in chat_id_list:
        await bot.send_message(chat_id=chat_id, text="当前群组非内部群，禁止查询")
        await checkserver.finish()
    sql1 = "SELECT name, url1, url2, username, password FROM severs"
    db.ping(reconnect=True)
    cursor.execute(sql1)
    results1 = cursor.fetchall()
    b = ""
    for i in results1:
        b += f'公益服名称：' + i[0] + f'\n网址：' + i[1] + f' ' + i[2]  + f'\n用户名：' + i[3] + f'\n密码：' + i[4] + f'\n\n'
    cursor.close()
    db.close()
    msg = '本群其余公益服信息如下：\n\n' + b + '\n\n客户端下载地址：https://t.me/c/1427595637/244167\n(本消息10秒后将自动删除)'
    # if user_id == 459180203:
    #     await bot.send_message(chat_id=chat_id, text = msg, parse_mode=parse_mode)
    #     await checkserver.finish()
    # 暂时下线改命令代码开始处
    # await bot.send_message(chat_id=chat_id, text="功能暂时下线")
    # await checkserver.finish()
    # 暂时下线改命令代码结束处
    msg1 = await bot.send_message(chat_id=chat_id, text = msg, parse_mode=parse_mode)
    msg2 = msg1["result"]["message_id"]
    time.sleep(10)
    await bot.delete_message(chat_id=chat_id, message_id=msg2)
    await checkserver.finish()


@total.handle()
async def _(event: MessageEvent, message: Message = CommandArg()):
    parse_mode = 'Markdown'
    bot = get_bot()
    user_id = int(event.get_user_id())
    chat_id = event.chat.id
    message_id = event.message_id
    re = ItemsCount()
    text = f'野鸡服影视资源信息如下:\n🎬电影数量：{re[0]}\n📽️剧集数量：{re[1]}\n🎼音乐数量：{re[3]}\n🎞️总集数：{re[2]}'
    await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode, reply_to_message_id=message_id)





@status.handle()
async def _(event: MessageEvent, message: Message = CommandArg()):
    parse_mode = 'Markdown'
    bot = get_bot()
    user_id = int(event.get_user_id())
    chat_id = event.chat.id
    message_id = event.message_id
    ws = create_connection("wss://tz.20120714.xyz/ws", timeout=10,sslopt={"cert_reqs": ssl.CERT_NONE})
    if ws.connected:
        ws.send('8')
        res = ws.recv()
        resjson = json.loads(res)
        gyf_CPU = resjson["servers"][0]["Host"]["CPU"][0]
        gyf_currentCPU = round(resjson["servers"][0]["State"]["CPU"],2) # %
        gyf_memtoal = round(resjson["servers"][0]["Host"]["MemTotal"]/1024/1024/1024,2) # G
        gyf_currentMem = round(resjson["servers"][0]["State"]["MemUsed"]/1024/1024/1024,2) # G
        gyf_netin = round(resjson["servers"][0]["State"]["NetInSpeed"]/1024/100,2) #Mbps
        gyf_netout = round(resjson["servers"][0]["State"]["NetOutSpeed"]/1024/100,2) #Mbps
        gyf_load = round(resjson["servers"][0]["State"]["Load1"]/12*100,2) # %
        tz = pytz.timezone('Asia/Shanghai') #东八区
        t = datetime.fromtimestamp(int(time.time()),pytz.timezone('Asia/Shanghai')).strftime('[%Y-%m-%d %H:%M:%S]')
        nowplay_gyf = renshu_gyf()
        message_gyf =t+"\n\n"+"`野鸡场私服状态播报`\n"+" - 当前观看人数："+str(nowplay_gyf)+"\n - CPU："+ gyf_CPU + "\n - 当前CPU占用："+ str(gyf_currentCPU)+"%\n - 已用内存\总内存："+ str(gyf_currentMem) + "GB\\" + str(gyf_memtoal) + "GB\n - 实时上传速率："+str(gyf_netout)+"Mbps\n - 实时下载速率："+str(gyf_netin)+"Mbps\n - 服务器实时负载："+str(gyf_load)+"%"
        await bot.send_message(chat_id=chat_id, text = message_gyf, parse_mode=parse_mode)
        await status.finish()
    else:
        message_gyf = "获取服务器状态失败，请通知管理员 @xianglingju2 检查。"
        await bot.send_message(chat_id=chat_id, text = message_gyf, parse_mode=parse_mode)
        await status.finish()







@add_invite.handle()
async def _(event: MessageEvent, message: Message = CommandArg()):
    parse_mode = 'Markdown'
    db = pymysql.connect(host=dbhost, user=dbuser,password=dbpassword,db=dbname )
    cursor = db.cursor()
    bot = get_bot()
    user_id = int(event.get_user_id())
    chat_id = event.chat.id
    message_id = event.message_id
    if message.extract_plain_text() != "":
        number = int(message.extract_plain_text())
    else:
        await bot.send_message(chat_id=chat_id, text = '⚠️ 参数错误，请输入要生成邀请码的具体数量。', parse_mode=parse_mode)
        await add_invite.finish()
    if user_id != 459180203:
        await bot.send_message(chat_id=chat_id, text = '⚠️ 你不是管理员，无法添加邀请码', parse_mode=parse_mode)
        await add_invite.finish()
    codes = []
    for i in range(1,number+1):
        code = ''.join(random.sample(string.ascii_letters + string.digits, 16))
        codes.append(code)
        sql = """INSERT INTO invite(code) VALUES ('%s')""" % (code)
        try:
            # 执行sql语句
            db.ping(reconnect=True)
            cursor.execute(sql)
            # 提交到数据库执行
            db.commit()
        except:
            # 如果发生错误则回滚
            db.rollback()
    cursor.close()
    db.close()
    b = f"成功生成{number}个邀请码，邀请码详细如下:\n"
    j = 0
    for i in codes:
        j += 1
        b += f"邀请码{j}:`" + i + f"`\n" 
    await bot.send_message(chat_id=chat_id, text = b, parse_mode=parse_mode)
    await add_invite.finish()



@checkrul.handle()
async def _(event: MessageEvent, message: Message = CommandArg()):
    parse_mode = 'Markdown'
    db = pymysql.connect(host=dbhost, user=dbuser,password=dbpassword,db=dbname )
    cursor = db.cursor()
    bot = get_bot()
    user_id = int(event.get_user_id())
    chat_id = event.chat.id
    message_id = event.message_id
    sql = "SELECT user_id FROM users"
    users= []
    db.ping(reconnect=True)
    cursor.execute(sql)
    results = cursor.fetchall()
    for i in results:
        users.append(i[0])
    # print(users)
    if chat_id != user_id:
        await checkrul.finish("请不要在群组发送线路查询命令")
    if str(user_id) not in users:
        await bot.send_message(chat_id=chat_id, text = '你不是公益服用户，无权查询线路信息！', parse_mode=parse_mode)
        cursor.close()
        db.close()
        await checkrul.finish()
    sql1 = "SELECT * FROM line"
    db.ping(reconnect=True)
    cursor.execute(sql1)
    results1 = cursor.fetchall()
    b = ""
    for i in results1:
        b += i[2] + f'：' + i[1] +f'\n'
    cursor.close()
    db.close()
    msg = '公益服网址\n' + b
    msg1 = await bot.send_message(chat_id=chat_id, text = msg, parse_mode=parse_mode)
    await checkrul.finish()



@resetpw.handle()
async def resetpw(event: MessageEvent, message: Message = CommandArg()):
    parse_mode = 'Markdown'
    db = pymysql.connect(host=dbhost, user=dbuser,password=dbpassword,db=dbname )
    cursor = db.cursor()
    bot = get_bot()
    user_id = int(event.get_user_id())
    chat_id = event.chat.id
    message_id = event.message_id
    try:
        sql="SELECT * FROM users WHERE user_id = '%s'" %(user_id)
        db.ping(reconnect=True)
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            id = results[0][4]
            username = results[0][3]
            message = await bot.send_message(chat_id=user_id, text="开始重置用户名为:[" + username + "]的密码")
            db.close()
            headers = {
                'accept': '*/*',
            }

            params = {
                'api_key': api_key,
            }

            json_data = {
                'ResetPassword': True,
            }

            response = requests.post(embyserver + '/emby/Users/' + id + '/Password', params=params, headers=headers, json=json_data)
            if response.status_code == 204:
                await bot.send_message(chat_id=user_id, text="用户名为:`" + username + "`的密码已成功重置为空密码", parse_mode=parse_mode)
                await resetpw.finish()
        else:
            await bot.send_message(chat_id=user_id, text="未查询到您的用户名")
            await resetpw.finish()
    except:
        pass



@check.handle()
async def check1(event: MessageEvent, message: Message = CommandArg()):
    parse_mode = 'Markdown'
    db = pymysql.connect(host=dbhost, user=dbuser,password=dbpassword,db=dbname )
    cursor = db.cursor()
    bot = get_bot()
    user_id = int(event.get_user_id())
    chat_id = event.chat.id
    message_id = event.message_id
    if chat_id != user_id:
        await check.finish("请不要在群组发送账户查询命令")
    # await bot.delete_message(chat_id=chat_id, message_id=message_id)
    # await bot.delete_message(chat_id=chat_id, message_id=message_id)
    try:
        message = await bot.send_message(chat_id=chat_id, text="开始查询您的Emby公益服用户名～")
        msg3 = message["result"]["message_id"]
        # text = '开始查询您的Emby公益服用户名～'
        sql="SELECT * FROM users WHERE user_id = '%s'" %(user_id)
        db.ping(reconnect=True)
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            username = results[0][3]
            create_time = str(results[0][5])
            id = results[0][4]
            headers = {
                'accept': 'application/json',
            }

            params = {
                'api_key': api_key,
            }

            response = requests.get(embyserver + '/emby/Users/' + id, params=params, headers=headers)
            id1 = re.findall(r'"(.*?)"', response.text)
            rr = json.loads(response.text)
            account_check = rr["Policy"]["IsDisabled"]
            if account_check:
                account_status = "已禁用"
            else:
                account_status = "正常"
            lastlogindate = str(id1[14])
            if lastlogindate == "PlayDefaultAudioTrack":
                lastlogindate = "⚠️ 注册至今，您从未登录过，您的账户随时可能被清理[白名单用户除外]。"
            else:
                lastlogindate = id1[16]
                # 开始将Emby获取的活动时间进行格式化为背景时间，格式为:%Y-%m-%d %H:%M:%S
                dt = datetime.strptime(lastlogindate[:26], "%Y-%m-%dT%H:%M:%S.%f")
                beijing_tz = pytz.timezone('Asia/Shanghai')
                beijing_time = dt.replace(tzinfo=pytz.utc).astimezone(beijing_tz)
                lastlogindate = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
            sql1 = "SELECT * FROM line"
            db.ping(reconnect=True)
            cursor.execute(sql1)
            results1 = cursor.fetchall()
            b = ""
            for i in results1:
                b += i[2] + f'：' + i[1] +f'\n'
            white_yn = results[0][6]
            if white_yn ==1:
                account_attribute = "白名单用户"
            else:
                account_attribute = "普通用户"
            msg = f'你的用户名是：`{username}`\n账户属性：`{account_attribute} `\n账户状态：`{account_status}`\n账户注册时间：`{create_time}`\n最后活动时间：`{lastlogindate} `\n公益服网址：\n{b}'
            msg1 = await bot.send_message(chat_id=chat_id, text = msg, parse_mode=parse_mode)
            # msg2 = msg1["result"]["message_id"]
            # time.sleep(10)
            # await bot.delete_message(chat_id=chat_id, message_id=msg3)
            # await bot.delete_message(chat_id=chat_id, message_id=msg2)
            await check.finish()
        else:
            msg1 = await bot.send_message(chat_id=chat_id, text='您未注册过Emby账户。')
            # msg2 = msg1["result"]["message_id"]
            # time.sleep(10)
            # await bot.delete_message(chat_id=chat_id, message_id=msg3)
            # await bot.delete_message(chat_id=chat_id, message_id=msg2)
            await check.finish()
        db.close()
    except:
        pass


@counts.handle()
async def count_number(event: MessageEvent, message: Message = CommandArg()):
    parse_mode = 'Markdown'
    db = pymysql.connect(host=dbhost, user=dbuser,password=dbpassword,db=dbname )
    cursor = db.cursor()
    bot = get_bot()
    user_id = int(event.get_user_id())
    chat_id = event.chat.id
    message_id = event.message_id
    if user_id not in white_list:
        msg1 = await bot.send_message(chat_id=chat_id, text='你没有查询权限，别瞎搞.', parse_mode=parse_mode)
        await counts.finish()
    sql = "SELECT name FROM users"
    db.ping(reconnect=True)
    cursor.execute(sql)
    results = cursor.fetchall()
    j = 0
    for i in results:
        j += 1
    cursor.close()
    db.close()
    text = f'野鸡服账户注册总数量为{j}个。'
    msg1 = await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
    await counts.finish()
