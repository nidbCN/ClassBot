import random
import time

import util
import operator
import weather
import logging

from NewCAS.LoginCAS import Login as nLg


# bot: Function list
# Arguments: /
# Return: str:Message of bot function list.
def bot_get_functions_list() -> str:
    logging.info("Match method bot_get_functions_list.")
    msg = "未找到功能列表"
    i = 0
    length = len(util.dump_list)
    if length != 0:
        msg = "功能列表：\n"
        logging.warning("Null function list. Check file dump.json.")
    else:
        # Get list from dump file.
        for fun_str in util.dump_list:
            added_msg = f"{fun_str}\n"
            if i == length - 1:
                added_msg = fun_str
            msg += added_msg
    return msg


# bot: Get weather of config location.
# Arguments: /
# Return: str:Message of local(set in config file) weather.
def bot_get_local_weather() -> str:
    logging.info("Match method bot_get_local_weather.")
    location_id = util.config_location
    wea_info = weather.get_weather_from_id(location_id)
    msg = "无法获取天气，"
    if wea_info["code"] == 0:
        wea_msg = util.make_weather_msg(wea_info["value"])
        if wea_msg["code"] == 0:
            logging.debug(f"Success get weather of {location_id}.\nValue:{wea_info}")
            msg = wea_msg["value"]
        else:
            logging.error(f"Cannot get weather.Value:{wea_info}")
            msg += "More: " + wea_msg["msg"]
    else:
        logging.error("Default location has wrong, location id is:" + location_id)
        msg += "默认天气设置错误，请联系开发者\nMore: " + wea_info["msg"]
    return msg


# bot: Get weather of somewhere.
# Arguments: list:List of location.
# Return: str:Message of input location weather.
def bot_get_location_weather(input_args: list) -> str:
    logging.debug("Match method bot_get_local_weather.")
    msg = "无法获取天气，"
    wea_src = util.get_weather(input_args)
    if wea_src["code"] == 0:
        wea_msg = util.make_weather_msg(wea_src["value"])
        if wea_msg["code"] == 0:
            msg = wea_msg["value"]
        else:
            msg += "内部错误，请稍后重试或联系开发者\nMore: " + wea_msg["msg"]
    else:
        msg += "未找到城市，请检查输入。\n提示：行政单位用空格分割，" \
               "如“北京 东城区”或“山西 太原 迎泽“\nMore: " + wea_src["msg"]

    return msg


# bot: Random a member in dump file.
# Arguments: /
# Return: str:Message about a random member.
def bot_get_random_member():
    class_member = util.dump_member
    rand = random.randint(1, len(class_member) - 1)
    if rand != 17:
        msg = f"抽到{class_member[rand]}同学，学号：20070401" + \
              "{:0>2d}".format(rand + 1)
    else:
        msg = bot_get_random_member()
    return msg


# bot: Request marks from NUC.
# Argument: list:List of student info, contains id and password.
# Return: str:Message about scores info.
# TODO(mail@gaein.cn): Formatted return info of CAS.
def bot_get_classes_scores(input_args: list) -> str:
    func = nLg(input_args[0], input_args[1])
    json = func.getGrades()
    send_msg = "您好:"

    if json is None:
        send_msg += "查询失败，请检查帐号密码是否正确。如无误可能为服务器网络错误或教务系统出现故障。"
    elif json["totalCount"] == 0:
        send_msg += "没有查询到考试成绩，请确认考试成绩已经公布。"
    else:
        send_msg += f"{json['items'][0]['xm']}，您的考试成绩(百分制)如下:\n"
        for item in json["items"]:
            send_msg += f"{item['kcmc']}---{item['cj']}\n"
    send_msg += "\n接口by @yanlc39。一切以学校平台公布为准。"
    return send_msg


# bot: Show school class table.
# Arguments: list:Input class ebug info.
# Return: str:Message of class info.
def bot_get_classes_table(input_args: list) -> str:
    ret = "无法查询到课表\n"

    if len(input_args) > 0:
        class_info = util.get_classes(int(input_args[0]))
    else:
        class_info = util.get_classes(0)

    if class_info["code"] == 0:
        ret = class_info["value"]
    else:
        ret += class_info["msg"]

    return ret


# bot: Develop infomation.
# Arguments: /
# Return: str:Message of devinfo.
def bot_get_develop_info() -> str:
    return util.config_info


# bot-Admin: Get todoList.
# Arguments: int:How much todoItem will show.
# Return: str:Message of todoList.
# TODO(mail@gaein.cn): Add a function in util.py to get todoList.
def bot_get_todo_list(cnt: int) -> str:
    ret = "待办事项有：\n"

    to_do_list = util.dump_todo
    list_length = len(to_do_list)
    if list_length == 0:
        ret = "无待办事项，好好休息叭"
    else:
        # Sort by time.
        to_do_list_sorted = sorted(to_do_list, key=operator.itemgetter("time"))
        # Define vars.
        i = 0
        now_time = time.time()
        # A loop output tooItems.
        for item in to_do_list_sorted:
            if now_time < item["time"]:
                todo_time = util.get_time_str(item["time"])
                if item["type"] == "活动":
                    ret += f"{str(i + 1)}. {todo_time},在{item['address']}进行{item['description']}"
                elif item["type"] == "作业":
                    ret += f"{str(i + 1)}. 作业{item['description']},截至{todo_time}"

                if i != cnt - 1 and i != list_length - 1:
                    ret += "\n"
            i += 1

        util.config_todo = to_do_list_sorted
        util.dump_changes()
    return ret


# bot-Admin:  Add a todoItem to todoList.
# Arguments: list:Input body part(Split input message except line1).
# Return: str:Result message of add to todoList.
def bot_admin_add_todo_list(input_body: list) -> str:
    ret = "添加失败\n"
    new_item = util.get_todo_item_from_msg(input_body)
    if new_item["code"] == 0:
        util.dump_todo.append(new_item["value"])
        util.config_todo = sorted(util.dump_todo, key=operator.itemgetter("time"))
        util.dump_changes()
        ret = "添加成功"
    else:
        ret += new_item["msg"]
    return ret


# bot-Admin: Find item in todoList.
# Arguments: str:Keyword of what you find.
# Return: str:Result (contains aid) of the found item.
# TODO(mail@gaein.cn): Use factory to handle todoList function.
def bot_admin_find_todo(keyword: str) -> str:
    ret = "查询结果如下:\n"
    has_ret = False
    list_len = len(util.dump_todo)
    i = 0
    cnt = 0
    while i < list_len:
        todo_item = util.dump_todo[i]
        if keyword in todo_item["description"]:
            ret += f"{todo_item['aid']}:{todo_item['description']}\n"
            has_ret = True
            cnt += 1
        i += 1
    ret += f"共找到{cnt}条记录"
    if not has_ret:
        ret = f"无法找到关键字{keyword}"
    return ret


# bot-Admin: Clear todoList.
def bot_admin_clear_todo_list() -> str:
    util.config_todo = []
    ret = "保存失败\n"
    result = util.dump_changes()
    if result["code"] == 0:
        ret = "保存成功"
    else:
        ret += result["msg"]
    return ret


# bot-Admin: Change item in todoList.
def bot_admin_change_todo_list(aid_input: str, input_body: list) -> str:
    ret = "更改失败"
    cnt = 0
    for todo_item in util.dump_todo:
        if todo_item["aid"] == aid_input:
            util.dump_todo[cnt] = util.get_todo_item_from_msg(input_body)
            ret = "更改成功"
            break
        else:
            cnt += 1
    util.dump_changes()
    return ret
