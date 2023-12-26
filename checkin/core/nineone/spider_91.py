# coding=utf-8

import random
import re
from urllib import parse
from urllib.parse import urlparse

import js2py
import requests
from bs4 import BeautifulSoup
from lxml import etree
import sys
from core.nineone.MysqlDao import MYSQL
import os

from core.utils.constant import proxies
from core.utils.utils import check_local

requests.adapters.DEFAULT_RETRIES = 5
s = requests.session()
s.keep_alive = False

if check_local():
    s.proxies = proxies

current_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_path)

host_name = '91porn.com'

# 收藏最多 每月最热 本月最热 本月收藏 本月讨论  当前最热 最近加精
cate_order = {
    "mf": {"short_name": "mf", "level": 0},
    "top&m=-1": {"short_name": "mtop", "level": 0},
    "top": {"short_name": "monthly", "level": 1},
    "tf": {"short_name": "monthly", "level": 1},
    "md": {"short_name": "monthly", "level": 1},
    "rf": {"short_name": "rf", "level": 2},
    "hot": {"short_name": "hot", "level": 2},
}
spider_mysql = None


def update_category(video_dict):
    viewkey = video_dict["viewkey"]
    current_cate = cate_infos[viewkey]
    new_cate = video_dict["category"]
    if not current_cate or cate_order[new_cate]["level"] < cate_order[current_cate]["level"]:
        sql = f"UPDATE nineone SET category='{new_cate}', to_update_cate=1 WHERE viewkey='{viewkey}'"
        spider_mysql.ExecNonQuery(sql)


def insert_record(video_dict):
    if video_dict["viewkey"] not in cate_infos.keys():
        sql = f'INSERT into nineone(viewkey, title,img,link,video_link,update_time,upper_link,category) values ' \
              f'("{video_dict["viewkey"]}","{video_dict["title"]}","{video_dict["img"]}","{video_dict["link"]}",' \
              f'"{video_dict["video_link"]}","{video_dict["update_time"]}","{video_dict["upper_link"]}","{video_dict["category"]}")'
        spider_mysql.ExecNonQuery(sql)
        cate_infos[video_dict["viewkey"]] = video_dict["category"]
    else:
        update_category(video_dict)


# 定义随机ip地址
def random_ip():
    a = random.randint(1, 255)
    b = random.randint(1, 255)
    c = random.randint(1, 255)
    d = random.randint(1, 255)
    return str(a) + '.' + str(b) + '.' + str(c) + '.' + str(d)


def filter_str(desstr, restr=''):
    # 过滤除中英文及数字以外的其他字符
    res = re.compile("[^\\u4e00-\\u9fa5^a-z^A-Z^0-9]")
    title = res.sub(restr, desstr).replace("Chinesehomemadevideo", "")
    return title


encodedata2 = open("strencode2.js", 'r', encoding='utf8').read()
encodedata1 = open("strencode.js", 'r', encoding='utf8').read()
strencode2 = js2py.eval_js(encodedata2)
strencode = js2py.eval_js(encodedata1)


def get_viewkey(video_url):
    url = urlparse(video_url)
    paras = parse.parse_qs(url.query)
    viewkey = paras.get('viewkey')
    return viewkey


def get_video_urls(page_url, category):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name',
        'Referer': 'http://91porn.com'}
    get_page = s.get(url=page_url, headers=headers)
    divs = BeautifulSoup(get_page.text, "html.parser").find_all("div", class_="well well-sm videos-text-align")
    viewurl = []

    for div in divs:
        img_url = div.a.div.img.attrs["src"]

        viewkey = get_viewkey(div.a.attrs["href"])[0]
        viewurl.append({'link': div.a.attrs["href"], 'viewkey': viewkey, "img": img_url, "referer": page_url,
                        "category": category})

    return viewurl


def get_video_link(content):
    try:
        a = re.compile('document.write\(strencode2\("(.*)"').findall(content)
        if len(a) > 0:
            a = a[0].split(',')
            text = a[0].replace('"', '')
            video_link = BeautifulSoup(strencode2(text), "html.parser").source.attrs['src']
        else:
            a = re.compile('document.write\(strencode\("(.*)"').findall(content)
            text = a[0].split(',')
            video_link = \
                BeautifulSoup(strencode(text[0].replace('"', ''), text[1].replace('"', ''), text[2].replace('"', '')),
                              "html.parser").source.attrs['src']
        return video_link
    except Exception as e:
        print(e)
        return ""


def get_video_title(content):
    title = BeautifulSoup(content, "html.parser").title.text.replace(" ", "").replace("\n", "")
    title = filter_str(title)
    if title.startswith("0"):
        title.replace("0", "零", 1)
    return title


def get_video_update_time(content):
    a = re.compile('<span class="title-yakov">\d{4}-\d{2}-\d{2}</span>').findall(content)
    if len(a) > 0:
        update_time = a[0].replace('<span class="title-yakov">', "").replace("</span>", "")
        return update_time
    else:
        return "2000-01-01"


def get_upper_link(content):
    # a = re.compile('https://{host_name}/uprofile.php?UID=(.*)">').findall(content)
    try:
        html = etree.HTML(content)
        upper_detail_divs = html.xpath('//*[@id="videodetails-content"]')
        upper_detail_div = upper_detail_divs[1]
        title = upper_detail_div.find('.//a')
        upper_link = title.get('href')
        if 'uprofile' in upper_link:
            return upper_link
        else:
            return 'nobody'
    except:
        return ""


def get_video_detail(video_dict):
    headers = {'Accept-Language': 'zh-CN,zh;q=0.9',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:66.0) Gecko/20100101 Firefox/66.0',
               'X-Forwarded-For': random_ip(),
               'referer': video_dict["referer"],
               'Content-Type': 'multipart/form-data; session_language=cn_CN',
               'Connection': 'keep-alive',
               'Upgrade-Insecure-Requests': '1',
               }
    # base_req = s.get(url=f"https://f1105.workarea3.live/view_video.php?viewkey=f{video_dict['viewkey']}", headers=headers)
    base_req = s.get(url=video_dict['link'], headers=headers)
    content = base_req.content.decode('utf-8')
    upper_link = get_upper_link(content)
    update_time = get_video_update_time(content)
    video_link = get_video_link(content)
    title = get_video_title(content)
    videotype = urlparse(video_link).path.split(".")[1]
    video_dict["title"] = title
    video_dict["video_link"] = video_link
    video_dict["update_time"] = update_time
    video_dict["upper_link"] = upper_link
    insert_record(video_dict)


def get_video_by_category(category, page_limit=5):
    inputPage = 1
    page = int(inputPage)
    base_url = f'https://{host_name}/v.php?category={category}&viewtype=basic&page='
    while page <= page_limit:
        page_url = base_url + str(page)
        videos_dict = get_video_urls(page_url, category)
        for video_dict in videos_dict:
            get_video_detail(video_dict)
        page += 1


def update_time():
    sql = "SELECT link,viewkey FROM `nineone`"
    res = spider_mysql.ExecQuery(sql)
    headers = {'Accept-Language': 'zh-CN,zh;q=0.9',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:66.0) Gecko/20100101 Firefox/66.0',
               'X-Forwarded-For': random_ip(),
               'referer': f"https://{host_name}/v.php?category=top&viewtype=basic&page=2",
               'Content-Type': 'multipart/form-data; session_language=cn_CN',
               'Connection': 'keep-alive',
               'Upgrade-Insecure-Requests': '1',
               }
    for link, viewkey in res:
        base_req = s.get(url=link, headers=headers)
        content = base_req.content.decode('utf-8')
        update_time = get_video_update_time(content)

        update_sql = f"UPDATE nineone SET update_time='{update_time}' WHERE viewkey='{viewkey}'"
        spider_mysql.ExecNonQuery(update_sql)


def get_video_infos():
    sql = "SELECT viewkey,category FROM `nineone` order by update_time  DESC"

    res = spider_mysql.ExecQuery(sql)
    cate_infos = {}
    for viewkey, category in res:
        cate_infos[viewkey] = category

    return cate_infos


def fix_new_item():
    sql = "UPDATE nineone SET to_update_cate='0' WHERE to_update_cate='1' and file_path is null"
    spider_mysql.ExecNonQuery(sql)


def run(mysql_host,mysql_user,mysql_pwd, mysql_port):
    global spider_mysql, cate_infos
    spider_mysql = MYSQL(host=mysql_host, user=mysql_user, pwd=mysql_pwd, db="spider",port=mysql_port)
    cate_infos = get_video_infos()
    get_video_by_category("top")
    get_video_by_category("tf")
    get_video_by_category("mf")
    get_video_by_category("rf")
    get_video_by_category("md")
    get_video_by_category("top&m=-1", page_limit=17)
    get_video_by_category("hot")
    fix_new_item()


if __name__ == '__main__':
    mysql_host = sys.argv[1]
    mysql_user = sys.argv[2]
    mysql_pwd = sys.argv[3]
    mysql_port = sys.argv[4]

    run(mysql_host,mysql_user,mysql_pwd, mysql_port)
