#-*-coding:utf8;-*-

import requests, os, json, uuid, sys

# přihlašovací údaje
user = os.environ.get('MAGIO_USERNAME', "")
password = os.environ.get('MAGIO_PASSWORD', "")

UA = "okhttp/3.12.12"
dev_id = "ab2731523db7"
dev_name = "ANDROID-STB"


def set_data(data, path):
    json_object = json.dumps(data, indent=4)
    with open(path, "w") as outfile:
        outfile.write(json_object)


def login(dev_type):
    params={"dsid": dev_id, "deviceName": dev_name, "deviceType": dev_type, "osVersion": "0.0.0", "appVersion": "0.0.0", "language": "SK"}
    headers={'Origin': 'https://www.magiogo.sk', 'Pragma': 'no-cache', 'Referer': 'https://www.magiogo.sk/', 'User-Agent': UA, 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'cross-site'}
    req = requests.post("https://skgo.magio.tv/v2/auth/init", params=params, headers=headers).json()
    accessToken = req["token"]["accessToken"]
    params = {"loginOrNickname": user, "password": password}
    headers = {"authorization": "Bearer " + accessToken, 'Origin': 'https://www.magiogo.sk', 'Pragma': 'no-cache', 'Referer': 'https://www.magiogo.sk/', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'cross-site', 'User-Agent': UA}
    req = requests.post("https://skgo.magio.tv/v2/auth/login", json = params, headers = headers).json()
    if req["success"] == True:
        return req["token"]["accessToken"], req["token"]["refreshToken"]
    else:
        print(req["errorMessage"])
        return "", ""


def reg_device(token_path = "./providers/magio/magio_token.json"):
    accesstoken, refreshtoken = login("OTT_STB")
    if accesstoken == "":
        return False
    params={"list": "LIVE", "queryScope": "LIVE"}
    headers = {"authorization": "Bearer " + accesstoken, 'Origin': 'https://www.magiogo.sk', 'Pragma': 'no-cache', 'Referer': 'https://www.magiogo.sk/', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'cross-site', 'User-Agent': UA}
    id = requests.get("https://skgo.magio.tv/v2/television/channels", params = params, headers = headers).json()["items"][0]["channel"]["channelId"]
    params={"service": "LIVE", "name": dev_name, "devtype": "OTT_STB", "id": id, "prof": "p5", "ecid": "", "drm": "verimatrix"}
    headers = {"authorization": "Bearer " + accesstoken, 'Origin': 'https://www.magiogo.sk', 'Pragma': 'no-cache', 'Referer': 'https://www.magiogo.sk/', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'cross-site', 'User-Agent': UA}
    req = requests.get("https://skgo.magio.tv/v2/television/stream-url", params = params, headers = headers).json()
    if req["success"] == True:
        accesstoken, refreshtoken = login("OTT_STB")
        set_data({"accesstoken": accesstoken, "refreshtoken": refreshtoken}, token_path)
        print("Magio: Přihlášení úspěšné")
        return True
    else:
        print(req["errorMessage"].replace("exceeded-max-device-count", "Překročen maximální počet zařízení"))
        return False


if __name__ == "__main__":
    reg_device(token_path = "magio_token.json")
    input("\nPro ukončení stiskněte klávesu Enter")
    sys.exit(0)