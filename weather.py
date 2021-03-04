import requests
import json
import logging
import util

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s][%(asctime)s][%(filename)s]at line:%(lineno)d %(message)s',
                    datefmt='%D %H:%M:%S')


def get_location_id_from_name(locations: list) -> dict:
    base_url = "https://geoapi.qweather.com"
    ret = {"code": 0, "msg": "Success get the id of location.", "value": ""}
    length = len(locations)
    parameter = ""
    if length >= 3:
        parameter = f"adm1={locations[0]}&adm2={locations[1]}&location={locations[2]}"
    elif length == 2:
        parameter = f"adm1={locations[0]}&location={locations[1]}"
    elif length == 1:
        parameter = f"location={locations[0]}"

    version = "/v2"
    operation = "/city/lookup"
    public_param = f"key={util.config_weather['accessToken']}&range=cn&number=1"
    url = f"{base_url}{version}{operation}?{public_param}&{parameter}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            # Successful get the content
            resp.encoding = "utf8"
            text = json.loads(resp.text)
            if text["code"] == "200":
                ret["value"] = text["location"][0]["id"]
            else:
                ret["code"] = 1
                ret["msg"] = f"Can not get the location id. Error code:{text['code']}"
        else:
            ret["code"] = 2
            ret["msg"] = f"Can not get return from web API, request error. Error code:{resp.status_code}"
    except (KeyError, ConnectionError, ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError) as e:
        ret["code"] = 3
        ret["msg"] = f"Can not connect to server, network error. Error message:{str(e)}"

    return ret


def get_weather_from_id(location_id: str) -> dict:
    base_url = "https://devapi.qweather.com"
    ret = {"code": 0, "msg": "Success get the weather of today and tomorrow", "value": {}}

    version = "/v7"
    operation = "/weather/3d"
    public_param = f"key={util.config_weather['accessToken']}"
    parameter = f"location={location_id}"
    url = f"{base_url}{version}{operation}?{public_param}&{parameter}"

    try:

        resp = requests.get(url)

        if resp.status_code == 200:
            resp.encoding = "utf8"
            text = json.loads(resp.text)
            if text["code"] == "200":
                weather_info = text["daily"]

                today_weather_info = weather_info[0]
                tomorrow_weather_info = weather_info[1]

                today_weather_ret = {
                    "tempMax": today_weather_info['tempMax'],
                    "tempMin": today_weather_info['tempMin'],
                    "sunRise": today_weather_info['sunrise'],
                    "windDir": today_weather_info['windDirDay'],
                    "windScale": today_weather_info['windScaleDay'],
                    "weather": today_weather_info['textDay']
                }
                tomorrow_weather_ret = {
                    "tempMax": tomorrow_weather_info['tempMax'],
                    "tempMin": tomorrow_weather_info['tempMin'],
                    "sunRise": tomorrow_weather_info['sunrise'],
                    "windDir": tomorrow_weather_info['windDirDay'],
                    "windScale": tomorrow_weather_info['windScaleDay'],
                    "weather": tomorrow_weather_info['textDay']
                }

                ret["value"] = {"today": today_weather_ret, "tomorrow": tomorrow_weather_ret}
            else:
                ret["code"] = 1
                ret["msg"] = f"Can not get the location weather. Error code:{text['code']}"
        else:
            ret["code"] = 2
            ret["msg"] = f"Can not get return from web API, request error. Error code:{resp.status_code}"
    

    except (KeyError, ConnectionError, ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError) as e:
        ret["code"] = 3
        ret["msg"] = f"Can not connect to server, network error. Error message:{str(e)}"

    return ret
