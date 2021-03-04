import logging
import util
import func

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s][%(asctime)s][%(filename)s]at line:%(lineno)d %(message)s',
                    datefmt='%D %H:%M:%S')


def exec_bot_command_group(input_msg: str) -> str:
    # Interpreter commmands input.
    commands = util.command_interpreter(input_msg)
    command_head = commands["head"]

    send_msg = None

    # Reply message.
    if command_head == "功能":
        logging.log("Match command:功能.")
        send_msg = func.bot_get_functions_list()

    elif command_head == "开学":
        logging.log("Match command:开学.")
        send_msg = "啥时候开学来着？"

    elif command_head == "天气":
        logging.log("Match command:天气.")
        length = len(commands["args"])
        if length == 0:
            # No location input.
            send_msg = func.bot_get_local_weather()
        else:
            send_msg = func.bot_get_location_weather(commands["args"])

    elif command_head == "查分":
        logging.log("Match command:查分.")
        send_msg = '因为涉及隐私请私聊发送“查分 学号 密码”进行查询（密码为教务系统密码，默认为"zbdx123"）\n接口by yanlc39, ' \
                   'https://github.com/yanlc39/NUC-Personal-portal '

    elif command_head == "抽号":
        logging.log("Match command:抽号.")
        send_msg = func.bot_get_random_member()

    elif command_head == "项目":
        logging.log("Match command:项目.")
        send_msg = func.bot_get_develop_info()

    elif command_head == "课表":
        logging.log("Match command:课表.")
        send_msg = func.bot_get_classes_table(commands["args"])

    elif command_head == "待办":
        logging.log("Match command:待办.")
        send_msg = func.bot_get_todo_list(5)

    else:
        logging.warning("Unknow command.")

    return send_msg


def exec_bot_command_friend(input_msg: str) -> str:
    commands = util.command_interpreter(input_msg)
    command_head = commands["head"]

    msg_send = None

    if command_head == "待办":
        msg_send = func.bot_get_todo_list(5)
    elif command_head == "课表":
        msg_send = func.bot_get_classes_table([])
    elif command_head == "天气":
        if len(commands["args"]) < 1:
            msg_send = func.bot_get_local_weather()
        else:
            msg_send = func.bot_get_location_weather(commands["args"])
    elif command_head == "查分":
        if len(commands["args"]) < 2:
            msg_send = '格式错误，请发送“查分 学号 密码”进行查询（密码为教务系统密码，默认为"zbdx123"）'
        else:
            msg_send = func.bot_get_classes_scores(commands["args"])

    return msg_send


def exec_bot_command_friebd_admin(input_msg: str) -> str:
    commands = util.command_interpreter(input_msg)
    command_head = commands["head"]

    msg_send = None
    print("!!!" + str(command_head))

    if command_head == "待办":
        command_args = commands["args"]
        if " 添加" in command_args:
            logging.log("Match command:待办-添加.")
            print(commands)
            if "body" in commands:
                msg_send = func.bot_admin_add_todo_list(commands["body"])
            else:
                msg_send = "格式：类型（活动/作业）\n名称\n时间\n地点"
        elif " 清除" in command_args:
            msg_send = func.bot_admin_clear_todo_list()
        elif " 修改" in commands["args"]:
            msg_send = func.bot_admin_change_todo_list(commands["args"][1], commands["body"])
        elif " 查找" in commands["args"]:
            msg_send = func.bot_admin_find_todo(commands["args"])
        msg_send = "参数：添加、清除、修改、查找"
    elif command_head == "课表":
        msg_send = func.bot_get_classes_table(commands["args"])
    return msg_send
