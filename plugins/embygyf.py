from typing import Optional
import requests
import re
import json
import pymysql
import time
import nonebot
import datetime
from nonebot import on_command, on_keyword
from nonebot.adapters.telegram import Bot
from nonebot.adapters.telegram.message import MessageSegment
from nonebot.adapters.telegram.event import MessageEvent
from nonebot.adapters import Message
from nonebot.params import Arg, CommandArg, ArgPlainText
from nonebot.params import CommandArg
from itertools import chain

from config import dbhost, dbuser, dbpassword, dbname, chat_id_list, black_list, embyserver, api_key, bot_token, emby_chat_id, white_list


def get_bot() -> Optional[Bot]:
    """
    说明：
        获取 bot 对象
    """
    try:
        return list(nonebot.get_bots().values())[0]
    except IndexError:
        return None


emby = on_command(
    "create",
)
seturl = on_command(
    "addurl",
)
addserver = on_command(
    "addserver",
)
invite = on_command(
    "invite",
)


@invite.handle()
async def _(event: MessageEvent, message: Message = CommandArg()):
    parse_mode = 'Markdown'
    db = pymysql.connect(host=dbhost, user=dbuser,password=dbpassword,db=dbname )
    cursor = db.cursor()
    bot = get_bot()
    user_id = int(event.get_user_id())
    chat_id = event.chat.id
    user_id1 = str(user_id)
    global invite_code
    invite_code = message.extract_plain_text()
    message_id = event.message_id
    # await bot.delete_message(chat_id=chat_id, message_id=message_id)
    if user_id != chat_id:
        await bot.send_message(chat_id=chat_id, text="请私聊我注册。")
        await invite.finish()
    sql = "SELECT code FROM invite"
    db.ping(reconnect=True)
    cursor.execute(sql)
    all = list(chain.from_iterable(cursor.fetchall()))
    if invite_code not in all:
        await bot.send_message(chat_id=chat_id, text="邀请码无效，禁止注册")
        await invite.finish()
        db.close()
    if invite_code in all:
        sql4 = "DELETE FROM invite WHERE code ='%s'" % (invite_code)
        cursor.execute(sql4)
        db.commit()



@invite.got("name", prompt="检测邀请码有效，邀请码回收成功，请输入你要注册的用户名[仅限字母、数字或其组合]")
async def zhuce(event: MessageEvent, name: Message = Arg(), uname: str = ArgPlainText("name")):
    if "/create" in uname:
        msg2 = f"您注册的用户名中包含 /create 字眼，为了保证您的体验，请去除 /create 字眼后重新输入。"
        await invite.reject(msg2)
    user = event.from_
    lastname = f" {user.last_name}" if user.last_name else ""
    tg_name =  f"{user.first_name}{lastname}"
    parse_mode = 'Markdown'
    db = pymysql.connect(host=dbhost, user=dbuser,password=dbpassword,db=dbname )
    cursor = db.cursor()
    chat_id = event.chat.id
    user_id = int(event.get_user_id())
    user_id1 = user_id
    bot = get_bot()
    sql1 = "SELECT user_id, name, id FROM users"
    db.ping(reconnect=True)
    cursor.execute(sql1)
    all1 = cursor.fetchall()
    for each in all1:
        if str(user_id) in each[0]:
            msg = f'TG-ID编号为：[{user_id1}](tg://user?id={user_id1})的用户，您已经注册过账号，不允许重复注册～'
            await bot.send_message(chat_id=chat_id, text=msg, parse_mode=parse_mode)
            await invite.finish()
            db.close()
        if uname in each[1]:
            msg1 = '您申请注册的账号用户名 ' + uname + ' 已存在，请更换其他用户名重新申请注册～'
            await invite.reject(msg1)
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    params = (
        ('api_key', api_key),
    )
    data = '{"Name":"' + uname + '","HasPassword":true}'
    response = requests.post(embyserver + '/emby/Users/New', headers=headers, params=params, data=data)
    cc = f"A user with the name '{uname}' already exists."
    if response.text == cc:
        msg1 = '您申请注册的账号用户名 ' + uname + ' 已存在，请更换其他用户名重新申请注册～'
        await invite.reject(msg1)
    if (response.status_code == 200):
        id1 = re.findall(r'"(.*?)"', response.text)
        id = id1[9]
        headers1 = {
            'accept': '*/*',
            'Content-Type': 'application/json',
        }
        params1 = (
            ('api_key', api_key),
        )
        data1 = '{"IsAdministrator":false,"IsHidden":true,"IsHiddenRemotely":true,"IsDisabled":false,"EnableRemoteControlOfOtherUsers":false,"EnableSharedDeviceControl":false,"EnableRemoteAccess":true,"EnableLiveTvManagement":false,"EnableLiveTvAccess":true,"EnableMediaPlayback":true,"EnableAudioPlaybackTranscoding":false,"EnableVideoPlaybackTranscoding":false,"EnablePlaybackRemuxing":false,"EnableContentDeletion":false,"EnableContentDownloading":false,"EnableSubtitleDownloading":false,"EnableSubtitleManagement":false,"EnableSyncTranscoding":false,"EnableMediaConversion":false,"EnableAllDevices":true}'
        requests.post(embyserver + '/emby/Users/' + id + '/Policy', headers=headers1, params=params1, data=data1)
        data_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql2 = """INSERT INTO users(tg_name, user_id, name, id, create_time) VALUES ('%s', '%s', '%s', '%s', '%s')""" % (
        tg_name, user_id, uname, id, data_time)
        try:
            # 执行sql语句
            db.ping(reconnect=True)
            cursor.execute(sql2)
            # 提交到数据库执行
            db.commit()
        except:
            # 如果发生错误则回滚
            db.rollback()
        sql3 = "SELECT * FROM line"
        db.ping(reconnect=True)
        cursor.execute(sql3)
        results1 = cursor.fetchall()
        cursor.close()
        b = ""
        for i in results1:
            b += i[2] + f'：' + i[1] + f'\n'
        db.close()
        msg1 = '**Emby账号注册成功～**\n注册用户名：`' + uname + '`\n无初始密码，请尽快登录Emby，点击右上角设置图标设置密码！\n公益服网址：\n' + b
        await bot.send_message(chat_id=user_id, text=msg1, parse_mode=parse_mode)
        await invite.finish()



@addserver.handle()
async def _(event: MessageEvent, message: Message = CommandArg()):
    parse_mode = 'Markdown'
    db = pymysql.connect(host=dbhost, user=dbuser,password=dbpassword,db=dbname )
    cursor = db.cursor()
    bot = get_bot()
    message_id = event.message_id
    user_id = int(event.get_user_id())
    chat_id = event.chat.id
    msg = message.extract_plain_text()
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    # 停服后不再执行代码开始处
    if not msg:
        msg1 = await bot.send_message(chat_id=chat_id, text = '出错了！\n正确格式为:\n/addserver 服务器名称 线路url 用户名 密码\ne.g：/addserver xxx服 http://127.0.0.1 123 123\n(本消息10秒后将自动删除)', parse_mode=parse_mode)
        msg2 = msg1["result"]["message_id"]
        time.sleep(10)
        await bot.delete_message(chat_id=chat_id, message_id=msg2)
        await addserver.finish()
    if (msg == "@embytest_bot"):
        msg1 = await bot.send_message(chat_id=chat_id, text = '出错了！\n命令后面不要跟@embytest_bot，正确格式为:\n/addserver 服务器名称 线路url 用户名 密码\ne.g：/addserver xxx服 http://127.0.0.1 123 123\n(本消息10秒后将自动删除)', parse_mode=parse_mode)
        msg2 = msg1["result"]["message_id"]
        time.sleep(10)
        await bot.delete_message(chat_id=chat_id, message_id=msg2)
        await addserver.finish()
    if len(msg.rsplit()) == 5:
        url1 = str(msg.rsplit( )[1])
        url2 = str(msg.rsplit( )[2])
        username = str(msg.rsplit( )[3])
        password1 = str(msg.rsplit( )[4])
        remarks = msg.rsplit( )[0]
    text = "http"
    if len(msg.rsplit()) == 4 and text in str(msg.rsplit( )[1]):
        url1 = str(msg.rsplit( )[1])
        url2 = ""
        username = str(msg.rsplit( )[2])
        password1 = str(msg.rsplit( )[3])
        remarks = msg.rsplit( )[0]
    else:
        msg1 = await bot.send_message(chat_id=chat_id, text = '出错了！\n命令后面不要跟@embytest_bot，正确格式为:\n/addserver 服务器名称 线路url 用户名 密码\ne.g：/addserver xxx服 http://127.0.0.1 123 123\n(本消息10秒后将自动删除)', parse_mode=parse_mode)
        msg2 = msg1["result"]["message_id"]
        time.sleep(10)
        await bot.delete_message(chat_id=chat_id, message_id=msg2)
        await addserver.finish()
    # await bot.delete_message(message_id=message_id)
    c = []
    response = requests.get('https://api.telegram.org/bot' + bot_token + '/getChatAdministrators?chat_id=' + emby_chat_id)
    b = json.loads(response.text)['result']
    for x in b:
        c.append(x['user']['id'])
    if user_id not in c:
        msg1 = await bot.send_message(chat_id=chat_id, text='你没有操作权限，别瞎搞～\n(本消息10秒后将自动删除)', parse_mode=parse_mode)
        msg2 = msg1["result"]["message_id"]
        time.sleep(10)
        await bot.delete_message(chat_id=chat_id, message_id=msg2)
        await addserver.finish()
    sql = """INSERT INTO severs(url1, url2, name, username, password ) VALUES ('%s', '%s', '%s', '%s', '%s')"""%(url1, url2, remarks, username, password1)
    try:
        db.ping(reconnect=True)
        cursor.execute(sql)
        db.commit()
        msg1 = await bot.send_message(chat_id=chat_id, text='群友公益服信息添加成功。\n(本消息10秒后将自动删除)', parse_mode=parse_mode)
        msg2 = msg1["result"]["message_id"]
        time.sleep(10)
        await bot.delete_message(chat_id=chat_id, message_id=msg2)
        await addserver.finish()
    except:
        db.rollback()
    db.close()
    # 停服后不再执行代码结束处




@seturl.handle()
async def _(event: MessageEvent, message: Message = CommandArg()):
    parse_mode = 'Markdown'
    db = pymysql.connect(host=dbhost, user=dbuser,password=dbpassword,db=dbname )
    cursor = db.cursor()
    bot = get_bot()
    message_id = event.message_id
    user_id = int(event.get_user_id())
    chat_id = event.chat.id
    msg = message.extract_plain_text()
    if not msg:
        msg1 = await bot.send_message(chat_id=chat_id, text = '出错了！\n正确格式为:\n/addurl 线路备注 线路url\ne.g：/addurl 线路1 http://127.0.0.1', parse_mode=parse_mode)
        await seturl.finish()
    if (msg == "@embystartbot"):
        msg1 = await bot.send_message(chat_id=chat_id, text = '出错了！\n命令后面不要跟@embytest_bot，正确格式为:\n/addurl 线路备注 线路url\ne.g：/addurl 线路1 http://127.0.0.1', parse_mode=parse_mode)
        await seturl.finish()
    url = msg.split( )[1]
    remarks = msg.split( )[0]
    if user_id not in white_list:
        msg1 = await bot.send_message(chat_id=chat_id, text='你没有操作权限，别瞎搞～\n', parse_mode=parse_mode)
        await seturl.finish()
    sql = """INSERT INTO line(url, remarks) VALUES ('%s', '%s')"""%(url, remarks)
    try:
        db.ping(reconnect=True)
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    db.close()
    msg1 = await bot.send_message(chat_id=chat_id, text='线路信息添加成功。\n', parse_mode=parse_mode)
    await seturl.finish()





@emby.handle()
async def _(event: MessageEvent, message: Message = CommandArg()):
    user = event.from_
    lastname = f" {user.last_name}" if user.last_name else ""
    tg_name =  f"{user.first_name}{lastname}"
    data_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parse_mode = 'Markdown'
    db = pymysql.connect(host=dbhost, user=dbuser,password=dbpassword,db=dbname )
    cursor = db.cursor()
    bot = get_bot()
    chat_id = event.chat.id
    message_id = event.message_id
    user_id = int(event.get_user_id())
    # user_name = event.get_user_first_name()
    user_id1 = str(user_id)
    await bot.send_message(chat_id=chat_id, text="已关闭注册，如有邀请码，发送/invite 邀请码 进行注册", reply_to_message_id=message_id)
    await emby.finish()
    if user_id in black_list:
        await bot.send_message(chat_id=user_id, text="黑名单用户，禁止注册")
        await emby.finish()
    name = message.extract_plain_text()
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    # # 下行代码新添加停服注册回复信息
    # await bot.send_message(chat_id=chat_id, text = '服主跑路，停止新用户注册', parse_mode=parse_mode, reply_to_message_id=message_id)
    # 停服代码注释起始处
    if chat_id == user_id:
        await emby.finish("私聊无效，请在内部群发送命令")
    if chat_id not in chat_id_list:
        await bot.send_message(chat_id=user_id, text="非内部群用户，禁止注册")
        await emby.finish()
    if not name:
        await bot.send_message(chat_id=chat_id, text = '请重新输入！\n正确格式为:\n/create 用户名(字母、数字或者其组合)', parse_mode=parse_mode)
        await emby.finish()
    sql = "SELECT user_id, name, id FROM users"
    db.ping(reconnect=True)
    cursor.execute(sql)
    all = cursor.fetchall()
    for each in all:
        if str(user_id) in each[0]:
            msg = f'TG-ID编号为：[{user_id1}](tg://user?id={user_id1})的用户，您已经注册过账号，不允许重复注册～'
            await bot.send_message(chat_id=chat_id, text = msg, parse_mode=parse_mode)
            await emby.finish()
            db.close()
        if name in each[1]:
            msg1 = '您申请注册的账号用户名`' + name + '`已存在，请更换其他用户名重新申请注册～'
            msg2 = await bot.send_message(chat_id=user_id,text = msg1, parse_mode=parse_mode)
            await emby.finish()
            db.close()
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    params = (
        ('api_key', api_key),
    )
    data = '{"Name":"' + name + '","HasPassword":true}'
    response = requests.post(embyserver + '/emby/Users/New', headers=headers, params=params, data=data)
    cc = f"A user with the name '{name}' already exists."
    if response.text == cc:
        msg1 = '您申请注册的账号用户名`' + name + '`已存在，请更换其他用户名重新申请注册～'
        await bot.send_message(chat_id=user_id,text = msg1, parse_mode=parse_mode)
        await emby.finish()
        db.close()
    if (response.status_code == 200):
        id1 = re.findall(r'"(.*?)"', response.text)
        id = id1[9]
        headers1 = {
            'accept': '*/*',
            'Content-Type': 'application/json',
        }
        params1 = (
            ('api_key', api_key),
        )
        data1 = '{"IsAdministrator":false,"IsHidden":true,"IsHiddenRemotely":true,"IsDisabled":false,"EnableRemoteControlOfOtherUsers":false,"EnableSharedDeviceControl":false,"EnableRemoteAccess":true,"EnableLiveTvManagement":false,"EnableLiveTvAccess":true,"EnableMediaPlayback":true,"EnableAudioPlaybackTranscoding":false,"EnableVideoPlaybackTranscoding":false,"EnablePlaybackRemuxing":false,"EnableContentDeletion":false,"EnableContentDownloading":false,"EnableSubtitleDownloading":false,"EnableSubtitleManagement":false,"EnableSyncTranscoding":false,"EnableMediaConversion":false,"EnableAllDevices":true}'
        requests.post(embyserver + '/emby/Users/' + id + '/Policy', headers=headers1, params=params1, data=data1)
        sql = """INSERT INTO users(tg_name, user_id, name, id, create_time) VALUES ('%s', '%s', '%s', '%s', '%s')"""%(tg_name, user_id, name, id, data_time)
        try:
            # 执行sql语句
            db.ping(reconnect=True)
            cursor.execute(sql)
            # 提交到数据库执行
            db.commit()
        except:
            # 如果发生错误则回滚
            db.rollback() 
        sql1 = "SELECT * FROM line"
        db.ping(reconnect=True)
        cursor.execute(sql1)
        results1 = cursor.fetchall()
        b = ""
        for i in results1:
            b += i[2] + f'：' + i[1] + f'\n'
        db.close()
        msg1 = '**Emby账号注册成功～**\n注册用户名：`' + name +'`\n无初始密码，请尽快登录Emby，点击右上角设置图标设置密码！\n公益服网址：\n' + b
        await bot.send_message(chat_id=user_id, text = msg1, parse_mode=parse_mode)
        await emby.finish() 
    # 停服代码注释结束处