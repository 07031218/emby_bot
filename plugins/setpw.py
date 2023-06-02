from typing import Optional
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
from nonebot.params import Arg, CommandArg, ArgPlainText
from config import dbhost, dbuser, dbpassword, dbname, chat_id_list, black_list, embyserver, api_key, bot_token, emby_chat_id


def get_bot() -> Optional[Bot]:
    """
    说明：
        获取 bot 对象
    """
    try:
        return list(nonebot.get_bots().values())[0]
    except IndexError:
        return None

setpw = on_command(
    "setpw"
    )

@setpw.handle()
async def _(event: MessageEvent, message: Message = CommandArg()):
    user_id = int(event.get_user_id())
    chat_id = event.chat.id
    bot = get_bot()
    message_id = event.message_id
    if (chat_id != user_id):
        msg1 = await bot.send_message(chat_id=chat_id, text="长点心吧，难道你想把账户密码公诸于众吗？设置emby账户密码请与我私聊并发送命令/setpw")
        # await bot.delete_message(chat_id=chat_id, message_id=message_id)
        # msg2 = msg1["result"]["message_id"]
        # time.sleep(10)
        # await bot.delete_message(chat_id=chat_id, message_id=msg2)
        await setpw.finish()

@setpw.got("name", prompt="请输入你要设置的密码[仅限字母、数字或其组合]，如果要取消修改密码，请回复：cancel")
async def setpasswd(event: MessageEvent, name: Message = Arg(), pass1: str = ArgPlainText("name")):
    chat_id = event.chat.id
    user_id = int(event.get_user_id())
    db = pymysql.connect(host=dbhost, user=dbuser,password=dbpassword,db=dbname )
    cursor = db.cursor()
    bot = get_bot()
    if pass1 == "cancel":
        await setpw.finish("对话已取消，密码没有修改～")
    # user_id = int(event.get_user_id())
    # message_id = event.message_id
    # await bot.delete_message(chat_id=chat_id,message_id=message_id)
    try:
        sql="SELECT * FROM users WHERE user_id = '%s'" %(user_id)
        db.ping(reconnect=True)
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            id1 = results[0][4]
            username = results[0][3]
            await bot.send_message(chat_id=user_id, text="开始设置[" + username + "]的密码")
            cursor.close()
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
            json_data1 = {
                'Id': id1,
                'CurrentPw': '',
                'NewPw': pass1,
                'ResetPassword': False,
            }
            response = requests.post(embyserver + '/emby/Users/' + id1 + '/Password', params=params, headers=headers, json=json_data)
            if response.status_code == 204 and pass1 != '':
                response1 = requests.post(embyserver + '/emby/Users/' + id1 + '/Password', params=params, headers=headers, json=json_data1)
                if response1.status_code == 204:
                    await bot.send_message(chat_id=user_id, text="用户名:[" + username + "]的密码已成功设置为:" + pass1)
                    await setpw.finish()
            else:
                await bot.send_message(chat_id=user_id, text="用户名:[" + username + "]已被重置为空密码。")
                await setpw.finish()
        else:
            await bot.send_message(chat_id=user_id, text="未查询到您的用户名")
            await setpw.finish()
    except:
        pass