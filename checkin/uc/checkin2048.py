import base64
import json
import os
import re
import time
from io import BytesIO
from PIL import Image

from lxml import etree
from retrying import retry
import requests
from driver_utils import get_driver
from slider_verificater import SliderVerification, get_top
import sys
import urllib.parse

safe_wait_time = 20
current_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_path)
slider = 'slider.jpg'
background = 'background.jpg'
js = """
        _fetch = function(i,src){
          return fetch(src).then(function(response) {
            if(!response.ok) throw new Error("No image in the response");
            var headers = response.headers;
            var ct = headers.get('Content-Type');
            var contentType = 'image/png';
            if(ct !== null){
              contentType = ct.split(';')[0];
            }

            return response.blob().then(function(blob){
              return {
                'blob': blob,
                'mime': contentType,
                'i':i,
              };
            });
          });
        };

        _read = function(response){
          return new Promise(function(resolve, reject){
            var blob = new Blob([response.blob], {type : response.mime});
            var reader = new FileReader();
            reader.onload = function(e){
              resolve({'data':e.target.result, 'i':response.i});
            };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
          });
        };

        _replace = function(){
            for (var i = 0, len = q.length; i < len; i++) {imgs[q[i].item].src = q[i].data;}
        }

        var q = [];
        var imgs = document.querySelectorAll('img');
        for (var i = 0, len = imgs.length; i < len; i++) {
                _fetch(i,imgs[i].src).then(_read).then(function(data){
            q.push({
              'data': data.data,
              'item': data.i,
            });
          });
            }
        setTimeout(_replace, 1000 );
        """


# https://data.2qssj.com/hyverify//Image.png.php?aid=2100043001&accver=1&showtype=popup&ua=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExMy4wLjAuMCBTYWZhcmkvNTM3LjM2&noheader=1&fb=1&enableDarkMode=0&fpinfo=fpsig%3Dundefined&grayscale=1&clientype=2&subsid=4&sess=&fwidth=0&sid=6FcwrpiE&forcestyle=undefined&wxLang=&tcScale=1&uid=&cap_cd=&rnd=304584&TCapIframeLoadTime=undefined&prehandleLoadTime=9491&createIframeStart=1683709891889&rand=94321702&websig=T2wS2gl4AbCKrZD2CBjO2VAMDHEPDHmW9Zo16Qt6rwGZMKQOM1dELdQPlVeocHBbgqRb7BXnxeC0pTN2Jq6VKMlwhFbAMcbtItKEvisiCuirEwjOdfjnsKZPQ1QdTsMb&vsig=cXgN6Ov90UqDGQRjv2NdCmtSdAwxs0OKWvXS0JQ9d8CjNTJ0LWdN0MfcNSQ6ReGnQe6PoMOIJQsWk2WvNz0MCepPx6LEaRsqwn7b1Kj0bRWCJtyWixjkSPzFKAKlS3SFgOgWZGW2Yt5hcs5Agdlzsa64bFeu8xzdBWzbdMS26MY6SYc&img_index=2

class Site2048:
    def __init__(self, host_name, user, pwd, answer):
        self.host_name = host_name
        self.host = f"https://{host_name}/2048/"
        self.user = user
        self.pwd = pwd
        self.answer = answer
        self.real_host = ""
        self.cookie_file = ""
        self.SliderVerification = SliderVerification()
        self.driver = get_driver()

    def _login_with_input(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        user_target = self.driver.find_element(By.XPATH,
                                               '//*[@id="main"]/form/div/table/tbody/tr[2]/td/div/dl[1]/dd/input')
        pwd_target = self.driver.find_element(By.XPATH,
                                              '//*[@id="main"]/form/div/table/tbody/tr[2]/td/div/dl[2]/dd/input')
        user_target.send_keys(self.user)
        pwd_target.send_keys(self.pwd)
        s1 = Select(
            self.driver.find_element(By.XPATH, '//*[@id="main"]/form/div/table/tbody/tr[2]/td/div/dl[3]/dd/select'))
        s1.select_by_index(8)
        answer_target = self.driver.find_element(By.XPATH,
                                                 '//*[@id="main"]/form/div/table/tbody/tr[2]/td/div/dl[4]/dd/input')
        answer_target.send_keys(self.answer)
        login_target = self.driver.find_element(By.XPATH,
                                                '//*[@id="main"]/form/div/table/tbody/tr[2]/td/div/dl[7]/dd/input')
        login_target.click()

        time.sleep(safe_wait_time)
        cookie = self.driver.get_cookies()
        cookie_json = json.dumps(cookie)
        cookie_file = os.path.join(current_path, f"{cookie[0]['domain']}.json")
        with open(f"{cookie_file}", "w") as f:
            f.write(cookie_json)

    def _login_with_cookie(self):
        if os.path.exists(self.cookie_file):
            with open(self.cookie_file, "r") as f:
                cookie_dict = json.load(f)
            self.driver.delete_all_cookies()
            for co in cookie_dict:
                self.driver.add_cookie(co)
            time.sleep(1)
            # self.driver.get(self.host)
            # time.sleep(safe_wait_time)
        else:
            self._login_with_input()

    def login(self):
        self.driver.get(self.host + "login.php")
        self.real_host = urllib.parse.urlparse(self.driver.current_url).hostname

        print(self.real_host)
        self.host = f"https://{self.real_host}/2048/"
        time.sleep(safe_wait_time)

        self.cookie_file = os.path.join(current_path, f"{self.real_host}.json")
        if os.path.exists(self.cookie_file):
            print(f"Login with {self.real_host} cookie")
            self._login_with_cookie()
        else:
            print("Login with input")
            self.driver.get(self.host + "login.php")
            time.sleep(safe_wait_time)
            self._login_with_input()

    @retry(stop_max_attempt_number=3)
    def qiandao(self):
        from selenium.webdriver.common.by import By
        self.driver.get(self.host + "hack.php?H_name=qiandao")
        time.sleep(safe_wait_time)
        choose_target = self.driver.find_element(By.XPATH,
                                                 '//*[@id="main"]/div[2]/table/tbody/tr/td[2]/div[1]/form/table/tbody/tr[2]/td/ul/li[6]/input')
        choose_target.click()
        choose_target = self.driver.find_element(By.XPATH,
                                                 '//*[@id="hy_code"]')
        choose_target.click()
        time.sleep(safe_wait_time)
        iframe = self.driver.find_element(By.ID, "tcaptcha_iframe")
        self.driver.switch_to.frame(iframe)
        self.driver.execute_script(js)
        time.sleep(10)
        background_ele = self.driver.find_element(By.ID, 'slideBg')
        slider_ele = self.driver.find_element(By.ID, 'slideBlock')
        slider_url = slider_ele.get_attribute('src')
        background_url = background_ele.get_attribute('src')

        base64_to_image(background_url, background)
        base64_to_image(slider_url, slider)
        style_str = slider_ele.get_attribute("style")
        top_num = get_top(style_str)
        self.SliderVerification.set_cookie(self.driver.get_cookies())
        dis = self.SliderVerification.get_element_slide_distance(background, slider, top_num=top_num)
        self.SliderVerification.slide_verification(self.driver, slider_ele, dis)
        time.sleep(safe_wait_time)

    def apply_jobs(self):
        from selenium.webdriver.common.by import By
        try:
            self.driver.get(self.host + "jobcenter.php?action=list")
            time.sleep(safe_wait_time)
            choose_target = self.driver.find_element(By.XPATH,
                                                     '//*[@id="apply_12"]')
            choose_target.click()
            time.sleep(1)

            self.driver.get(self.host + "jobcenter.php?action=applied")
            time.sleep(safe_wait_time)
            choose_target = self.driver.find_element(By.XPATH,
                                                     '//*[@id="gain_12"]')
            choose_target.click()
            time.sleep(1)
        except Exception as e:
            print(e)




    def __del__(self):
        self.driver.close()


def get_latest_url():
    res = requests.get("https://hjd.tw")
    tree = etree.HTML(res.text)
    urls = tree.xpath("/html/body/center/div/ul/li[2]/a/@href")
    return urls[0].replace("https://", "")


def base64_to_image(base64_str, img_name):
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    img.save(img_name)


if __name__ == '__main__':
    user_name = sys.argv[1]
    password = sys.argv[2]
    answer = sys.argv[3]
    host = get_latest_url()
    site = Site2048(host, user_name, password, answer)
    site.login()
    site.apply_jobs()
    site.qiandao()
