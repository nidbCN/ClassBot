# Import packages.
import asyncio
import logging

from graia.application import GraiaMiraiApplication, Session
from graia.application.message.elements.internal import Plain
from graia.application.message.chain import MessageChain
from graia.application.group import Group
from graia.application.friend import Friend
from graia.broadcast import Broadcast

import factory
import util

# Log config.
logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s][%(asctime)s][%(filename)s]at line:%(lineno)d %(message)s',
                    datefmt='%D %H:%M:%S')

logging.info("Starting QQ bot, please wait.")

# bot
loop = asyncio.get_event_loop()

# Config mirai bot
mirai_config = util.config_mirai
logging.info(f"Config Mirai HTTP API:{mirai_config['host']}")
bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host=mirai_config["host"],
        authKey=mirai_config["authKey"],
        account=int(mirai_config["account"]),
        websocket=mirai_config["webSocket"]
    )
)


@bcc.receiver("GroupMessage")
async def group_message_handler(bot_app: GraiaMiraiApplication, message: MessageChain, group: Group):
    # TODO(mail@gaein.cn): Use "Middle Ware"
    # Only spy groups in config file.
    if str(group.id) in util.config_group:
        logging.info(f"Detected message from group: {str(group.id)}")

        # Interpreter commands input.
        input_msg = message.asDisplay()

        # Get message to send.
        msg_send = factory.exec_bot_command_group(input_msg)

        # Anti-Dress!
        key_list_1 = ["康萱琪", "康学姐", "子康"]
        key_list_2 = ["女装", "JK", "裙子", "水手服"]

        for keyword1 in key_list_1:
            if keyword1 in input_msg:
                for keyword2 in key_list_2:
                    if keyword2 in input_msg:
                        if msg_send is not None:
                            msg_send += "\n女装个锤子，爬！"
                        else:
                            msg_send = "女装个锤子，爬！"

        # Reply message.
        if msg_send is not None:
            await bot_app.sendGroupMessage(group, message.create([Plain(msg_send)]))


@bcc.receiver("FriendMessage")
async def friend_message_listener(bot_app: GraiaMiraiApplication, message: MessageChain, friend: Friend):
    # Interpreter commands.
    input_msg = message.asDisplay()

    if util.is_admin(str(friend.id)):
        logging.info(f"Detected message from admin: {friend.id}")
        msg_send = factory.exec_bot_command_friend_admin(input_msg)

    else:
        logging.info(f"Detected message from friend: {friend.id}")
        msg_send = factory.exec_bot_command_friend(input_msg)

    if msg_send is not None:
        await bot_app.sendFriendMessage(friend, message.create([Plain(msg_send)]))


logging.info("Success start QQ bot.")
app.launch_blocking()
