import base64
import random

import cv2
import numpy as np
import requests
import time
import os

current_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_path)


def base64img2file(imgsrc: str):
    suffix = imgsrc.split(';')[0][11:]
    with open("demo." + suffix, 'wb') as f:
        f.write(base64.b64decode(imgsrc.split(',')[1]))


def image_crop(image, loc):
    cv2.rectangle(image, loc[0], loc[1], (0, 0, 255))
    cv2.imwrite(str("res") + ".jpg", image)

    # cv2.imshow('Show', image)
    # # cv2.imshow('Show2', slider_pic)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


def onload_save_img(url, filename="image.png", cookie=""):
    """
    下载图片并保存
    :param url: 图片网址
    :param filename: 图片名称
    :return:
    """
    try:
        if cookie:
            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
                "cookie": cookie
            }
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url)

    except Exception as e:
        print('图片下载失败')
        raise e
    else:
        with open(filename, 'wb') as f:
            f.write(response.content)


def get_top(style_str):
    split_list = style_str.split(";")
    for item in split_list:
        if "top: " in item:
            res = item.replace("top: ", "")
            res = res.replace("px", "")
            res = res.strip()

    return int(res)


def get_slide_distance(slider_img, background_img, top_num=0, correct=0):
    slider_pic = cv2.imread(slider_img, 0)
    background_pic = cv2.imread(background_img, 0)
    # 340.81 * 199.32
    # 68 * 68
    # left 27.5
    slider_pic = cv2.resize(slider_pic, (68, 68))
    background_pic = cv2.resize(background_pic, (341, 199))
    background_pic = background_pic[top_num: 68 + top_num, 0: 341]
    # a: 左上角距离顶部
    # b: 左下角距离顶部
    # c: 左上角距离左边距离
    # d: 右上角距离左边距离
    # 获取缺口数组的形状

    # 将处理之后的图片另存
    slider01 = 'slider01.jpg'
    background01 = 'background01.jpg'

    cv2.imwrite(slider01, slider_pic)
    cv2.imwrite(background01, background_pic)

    start_poi = 26

    # 读取另存的滑块
    slider_pic = cv2.imread(slider01)

    # 读取背景图
    background_pic = cv2.imread(background01)

    width, height = 68, 68
    # 必脚两张图的重叠部分
    result = cv2.matchTemplate(slider_pic, background_pic, cv2.TM_CCOEFF_NORMED)

    # 通过数组运算，获取图片缺口位置
    top, left = np.unravel_index(result.argmax(), result.shape)

    # 背景图缺口坐标
    print('当前滑块缺口位置', (left, top, left + width, top + height))

    # 判读是否需求保存识别过程中的截图文件
    loc = [(left + correct, top + correct), (left + width - correct, top + height - correct)]
    image_crop(background_pic, loc)

    return left - start_poi - 9


def template_image():
    background_pic = cv2.imread("background01.jpg")
    slider_pic = cv2.imread("slider01.jpg")

    methods = [cv2.TM_SQDIFF_NORMED, cv2.TM_CCORR_NORMED, cv2.TM_CCOEFF_NORMED]
    th, tw = slider_pic.shape[:2]
    count = 0
    for md in methods:
        background_pic = cv2.imread("background01.jpg")
        result = cv2.matchTemplate(background_pic, slider_pic, md)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if md == cv2.TM_SQDIFF_NORMED:
            tl = min_loc
        else:
            tl = max_loc
        br = (tl[0] + tw, tl[1] + th)
        print(tl)
        cv2.rectangle(background_pic, tl, br, [0, 0, 0])
        cv2.imwrite(str(count) + ".jpg", background_pic)
        count += 1


class SliderVerification:

    def __init__(self, slider_ele=None, background_ele=None, count=1, save_image=True):
        """

        :param slider_ele:
        :param background_ele:
        :param count:  验证重试次数
        :param save_image:  是否保存验证中产生的图片， 默认 不保存
        """

        self.count = count
        self.save_images = save_image
        self.slider_ele = slider_ele
        self.background_ele = background_ele

        self.cookie_str = ""

    def set_cookie(self, cookie_json):
        cookie = [item["name"] + "=" + item["value"] for item in cookie_json]
        cookie_str = "; ".join(item for item in cookie)
        self.cookie_str = cookie_str

    def get_slide_locus(self, distance):
        distance += 8
        v = 0
        m = 0.3
        # 保存0.3内的位移
        tracks = []
        current = 0
        mid = distance * 4 / 5
        while current <= distance:
            if current < mid:
                a = 2
            else:
                a = -3
            v0 = v
            s = v0 * m + 0.5 * a * (m ** 2)
            current += s
            tracks.append(round(s))
            v = v0 + a * m
        # 由于计算机计算的误差，导致模拟人类行为时，会出现分布移动总和大于真实距离，这里就把这个差添加到tracks中，也就是最后进行一步左移。
        # tracks.append(-(sum(tracks) - distance * 0.5))
        # tracks.append(10)
        return tracks

    def slide_verification(self, driver, slide_element, distance):
        """

        :param driver: driver对象
        :param slide_element: 滑块元祖
        :type   webelement
        :param distance: 滑动距离
        :type: int
        :return:
        """
        from selenium.webdriver.common.action_chains import ActionChains

        # 获取滑动前页面的url网址
        start_url = driver.current_url
        print('滑动距离是: ', distance)
        # 根据滑动的距离生成滑动轨迹
        locus = self.get_slide_locus(distance)

        print('生成的滑动轨迹为:{},轨迹的距离之和为{}'.format(locus, distance))

        # 按下鼠标左键
        ActionChains(driver).click_and_hold(slide_element).perform()

        time.sleep(0.5)

        # 遍历轨迹进行滑动
        for loc in locus:
            time.sleep(0.01)
            ActionChains(driver).move_by_offset(loc, random.randint(-5, 5)).perform()
            ActionChains(driver).context_click(slide_element)

        # 释放鼠标
        ActionChains(driver).release(on_element=slide_element).perform()

        # # 判断是否通过验证，未通过下重新验证
        # time.sleep(2)
        # # 滑动之后的yurl链接
        # end_url = driver.current_url

        # if start_url == end_url and self.count > 0:
        #     print('第{}次验证失败，开启重试'.format(6 - self.count))
        #     self.count -= 1
        #     self.slide_verification(driver, slide_element, distance)

    def get_element_slide_distance(self, slider, background, top_num=0):
        """
        根据传入滑块， 和背景的节点， 计算滑块的距离
        :param top_num: slider from top
        :return:
        """
        # 进行色度图片, 转化为numpy 中的数组类型数据

        res = get_slide_distance(slider, background, top_num=top_num)
        return res
