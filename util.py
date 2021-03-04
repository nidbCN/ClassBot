import sys
import time
import datetime
import json
import logging
import random

import weather

# Config log format
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s][%(asctime)s][%(filename)s]at line:%(lineno)d %(message)s',
                    datefmt='%D %H:%M:%S')


# Log a warning and exit program
def program_exit() -> None:
    logging.warning("Program could not run, please fix errors and restart.")
    sys.exit()


# Read config file
try:
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

except (FileExistsError, FileNotFoundError) as ex:
    logging.error(f"Open config file error. Error message:{str(ex)}")
    program_exit()

# Read dump file
try:
    with open("dump.json", "r") as dump_file:
        dump = json.load(dump_file)
except (FileExistsError, FileNotFoundError) as ex:
    logging.warning(f"Open dump file error. Error message:{str(ex)}")

# UnSerialize config info and dumps
try:
    config_mirai: dict = config["mirai"]
    config_weather: dict = config["weather"]
    config_weather_key: str = config_weather["accessToken"]

    config_info: str = config["info"]
    config_group: list = config["groupId"]
    config_admin: list = config["adminId"]
    config_location: str = str(config["locationId"])

    dump_list: list = dump["functionList"]
    dump_classes: list = dump["classes"]
    dump_member: list = dump["member"]
    dump_todo: list = dump["toDoList"]

except KeyError as ex:
    logging.error(
        f"Can not found keys，please check the format of config.json and dump.json. Error message:{str(ex)}")
    program_exit()


# Interoperate the commands with blank or lines
def command_interpreter(input_str: str) -> dict:
    # Init vars
    body_command = []

    # Split commands
    if '\n' in input_str:
        list_command = input_str.split('\n')
        main_command = list_command[0].split()
        i = 1
        length = len(list_command)
        while i < length:
            body_command.append(list_command[i])
        count_command = i
    else:
        main_command = input_str.split()
        count_command = 1

    command_head = main_command[0]
    main_command.pop(0)
    # return commands
    ret = {"count": count_command, "head": command_head,
           "args": main_command, "body": body_command}
    return ret


# get classes table by weekday
def get_classes(day: int) -> dict:
    # init vars
    ret = {"code": 0, "msg": "Success get classes table", "value": ""}

    # offset the week index by user input
    if 0 < day <= 7 and day is not None:
        weekday_index = day - 1
    else:
        weekday_index = get_weekday()

    # get classes table by index of weekday
    try:
        classes = dump_classes[weekday_index]
        logging.info(f"Success get classes table, index {weekday_index}")
        ret["value"] = classes
    except IndexError as e:
        logging.error(f"index {weekday_index}. Error message:{str(e)}")
        ret["code"] = 1
        ret["msg"] = f"Can not get classes table, index {weekday_index}. Error message:{str(e)}"
        ret["value"] = None

    return ret


# Get today week day, if time has passed 22:00, return the next day
def get_weekday():
    # get system time
    today = datetime.datetime.now()
    week = today.weekday()

    # if time has passed 22:00, go next day
    if today.hour >= 22:
        week = week + 1 if week == 6 else 0
    return week


# If the user id is in administrator list
def is_admin(user_id: str) -> bool:
    ret = False
    if user_id in config_admin:
        ret = True
    return ret


# Get time stamp by time string
def get_time_st(time_input: str) -> dict:
    ret = {"code": 0, "msg": "Success get time stamp", "value": int}
    try:
        time_stamp = time.strptime(time_input, "%Y-%m-%d %H:%M")
        made_time = time.mktime(time_stamp)
        ret["value"] = int(made_time)
    except ValueError as e:
        logging.warning(f"Wrong time stamp format. Error message:{str(e)}")
        ret["code"] = 1
        ret["msg"] = f"Can not get time stamp, input {time_input}. Error message:{str(e)}"
        ret["value"] = None
    return ret


# Get time string by time stamp
def get_time_str(time_input: time) -> str:
    time_array = time.localtime(time_input)
    time_str = str(time.strftime("%m月%d日 %H:%M", time_array))
    return time_str


# Random a aid
def get_new_aid() -> str:
    ret_list = random.sample("ABCDEFGHIJKLMNOPQRSTUVWXYZ789456123", 6)
    return "".join(ret_list)


# Make to do item from message
def get_todo_item_from_msg(input_body: list) -> dict:
    ret = {"code": 0, "msg": "", "value": dict}

    new_aid = get_new_aid()
    new_type = input_body[0]
    new_description = input_body[1]
    new_time = input_body[2]
    new_address = None

    if new_type == "活动":
        new_address = input_body[3]

    time_stamp_pack = get_time_st(new_time)
    if time_stamp_pack["code"] != 0:
        ret["code"] = 1
        ret["msg"] = time_stamp_pack["msg"]
    else:
        todo_item = {
            "aid": new_aid,
            "type": new_type,
            "description": new_description,
            "time": time_stamp_pack["value"],
            "address": new_address
        }
        ret["value"] = todo_item

    return ret


# Search weather for location
def get_weather(location: list) -> dict:
    ret = {"code": 0, "msg": "Success get weather.", "value": ""}
    loc_id = weather.get_location_id_from_name(location)

    print(loc_id)

    if loc_id["code"] == 0:
        loc_wea = weather.get_weather_from_id(loc_id["value"])
        if loc_wea["code"] == 0:
            ret["value"] = loc_wea["value"]
        else:
            ret["code"] = 1
            ret["msg"] = "Can not get weather info."
    else:
        ret["code"] = 2
        ret["code"] = "Can not found location."
    return ret


# Make message by weather
def make_weather_msg(weather_dict: dict) -> dict:
    ret = {"code": 0, "msg": "Success get weather.", "value": ""}

    try:
        # Today weather info
        today_info = weather_dict["today"]
        today_wea = f"今日{today_info['weather']}"
        today_sun = f"{today_info['sunRise']}日出"
        today_temp = f"{today_info['tempMin']}到{today_info['tempMax']}°C"
        today_wind = f"{today_info['windDir']} {today_info['windScale']}级"

        msg = f"{today_wea},{today_temp}\n{today_wind},{today_sun}\n"

        # Tomorrow weather info
        tomorrow_info = weather_dict["tomorrow"]
        tomorrow_wea = f"明天{tomorrow_info['weather']}"
        tomorrow_temp = f"{tomorrow_info['tempMin']}到{tomorrow_info['tempMax']}°C"
        tomorrow_wind = f"{tomorrow_info['windDir']} {tomorrow_info['windScale']}级"

        msg += f"{tomorrow_wea},{tomorrow_temp},{tomorrow_wind}"

        # "Intelligence" tips
        if "雨" in today_info['weather'] or "雪" in today_info['weather']:
            msg += "\n记得出门带雨具哦"
        if "雨" in tomorrow_info['weather'] or "雪" in tomorrow_info['weather']:
            msg += "\n明天出门时记得带雨具哦"

        ret["value"] = msg

    except KeyError as e:
        ret["code"] = 1
        ret["msg"] = f"Can not make weather msg. Catch error:{str(e)}"
        logging.error(ret["msg"])

    return ret


# Dump changes.
def dump_changes() -> dict:
    ret = {"code": 0,
           "msg": "Success save changes in dump.json",
           "value": True}

    try:
        with open("dump.json", "w") as new_dump_file:
            dump["toDoList"] = dump_todo
            json.dump(dump, new_dump_file, ensure_ascii=False)
    except (FileExistsError, FileNotFoundError, KeyError) as e:
        logging.error(
            f"Can not write file file.json, changes would not be saved. Error message:{str(e)}")
        ret["code"] = 1
        ret["msg"] = f"Can not write file file.json, changes would not be saved. Error message:{str(e)}"
    return ret
