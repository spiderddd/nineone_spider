import time
import requests
import sys

import datetime
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')

def south_plus_login(cookie, cid=15):
    this_host = "www.south-plus.net"

    header = {
        'Referer': f'https://{this_host}/plugin.php?H_name-tasks.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Cookie': cookie
    }
    nowtime = str(int(time.time() * 1000))
    data = {
        "H_name": "tasks",
        "action": "ajax",
        "actions": "job",
        "cid": cid,
        "nowtime": nowtime,
        "verify": "6e75dbca"
    }

    response = requests.get("https://" + this_host + "/plugin.php", headers=header,
                            params=data, verify=False)
    print(response.text)
    time.sleep(3)
    header[
        "Cookie"] = cookie

    nowtime = str(int(time.time() * 1000))
    data = {
        "H_name": "tasks",
        "action": "ajax",
        "actions": "job2",
        "cid": cid,
        "nowtime": nowtime,
        "verify": "6e75dbca"
    }

    response = requests.get("https://" + this_host + "/plugin.php", headers=header,
                            params=data, verify=False)
    print(response.text)


def run(south_plus_cookie):
    south_plus_login(south_plus_cookie)
    today = datetime.date.today()
    weekday_index = today.weekday()
    if weekday_index == 0:
        south_plus_login(cookie=south_plus_cookie, cid=14)


if __name__ == "__main__":
    south_plus_cookie = sys.argv[1]
    run(south_plus_cookie)
