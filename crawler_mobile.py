from selenium import webdriver
import string
import random
from PIL import Image
import time
import os
from aip import AipOcr
from utils import get_bin_table, get_threshold, cut_noise
import traceback
from validcode_processor.splitter import split
from utils import deserialize
import cv2
import numpy as np
import requests
import pymysql

db = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='db_sx_crawler')  # db：库名
cursor = db.cursor()

url = ''

# 1min版
# kdl_orderid = '958717863342866'
# kdl_API_Key = 'vl7il4z32zxi8fi3jdbhy6h20l6a4oni'

# Dynamic版
kdl_orderid = '928717755392971'
kdl_API_Key = 'e31wnwx48qhkfz8kdg4lc2qny5rpkh07'


def init_model():
    print('initializing recognizer, pls wait……')
    id_label_map = deserialize("dat\\id_label_map.data")
    # print(id_label_map)
    model = cv2.ml.KNearest_create()
    samples = np.loadtxt('dat\\samples.data', np.float32)
    label_ids = np.loadtxt('dat\\label_ids.data', np.float32)
    model.train(samples, cv2.ml.ROW_SAMPLE, label_ids)
    return model, id_label_map


def init_browser(proxy):
    chrome_options = webdriver.ChromeOptions()  # 使用headless无界面浏览器模式
    mobile_emulation = {"deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
                        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D)"
                                     " AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"}

    chrome_options.add_experimental_option('mobileEmulation', mobile_emulation)
    chrome_options.set_capability('pageLoadStrategy', 'eager')
    if proxy:
        print("using proxy:  %s" % proxy)
        chrome_options.add_argument("--proxy-server=http://%s" % proxy)
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def ocr(image):
    """ baidu-ocr服务 APPID AK SK """
    APP_ID = '19445406'
    API_KEY = 'wHEtFBv5vEWxKtN1gEFkFn2H'
    SECRET_KEY = 'voCi58rlvb5DDX3LjxtCqmlVWUxukjHH '
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    imgry = image.convert('L')  # 转化为灰度图
    # 获取图片中的出现次数最多的像素，即为该图片的背景
    max_pixel = get_threshold(imgry)
    # 将图片进行二值化处理
    table = get_bin_table(threshold=max_pixel)
    out = imgry.point(table, '1')
    # 去掉图片中的噪声（孤立点）
    out = cut_noise(out)
    # out.show()
    out.save('clean_captcha.png')
    with open('clean_captcha.png', 'rb') as fp:
        try:
            res = client.basicGeneral(fp.read())
            return res['words_result'][0]['words']
        except Exception as e:
            print("holy-shit!")


def recognize(img_path):
    tup = split(img_path, None, False)
    if tup is None:
        return
    im_res = tup[0]
    boxes = tup[1]
    sec_code = []
    for box in boxes:
        roi = im_res[box[0][1]:box[3][1], box[0][0]:box[1][0]]
        roistd = cv2.resize(roi, (30, 30))
        # show(roistd)
        sample = roistd.reshape((1, 900)).astype(np.float32)
        ret, results, neighbours, distances = model.findNearest(sample, k=3)
        label_id = int(results[0, 0])
        label = id_label_map[label_id]
        sec_code.append(label)
    return ''.join(sec_code)


def get_validcode(browser):
    screenshot_path = "img\\screenshot.png"
    browser.get_screenshot_as_file(screenshot_path)
    element = browser.find_element_by_class_name('sec_code_img')
    # 自己用PS标志基准线去量（像素模式） 从截图中抠出来验证码的区域
    captcha_path = 'img\\captcha.png'
    if os.path.exists(captcha_path):
        os.remove(captcha_path)
    img = Image.open(screenshot_path)
    img = img.crop((753, 1071, 1032, 1153))
    img.save(captcha_path)
    # sec_code = ocr(img)
    sec_code = recognize(captcha_path)
    return sec_code


def get_proxy():
    proxy_url_json = requests.get(url="http://tps.kdlapi.com/api/gettps",
                                  params={'orderid': kdl_orderid, 'num': 1})
    return proxy_url_json.text


def save(username):
    try:
        cursor.execute('insert into user(username) values(%s)', username)
        print("persist ID = ", int(cursor.lastrowid))
        db.commit()
    except:
        db.rollback()


if __name__ == '__main__':
    browser = None
    model, id_label_map = init_model()
    n = 100
    i = 1
    while i <= int(n):
        try:
            # 为防止封锁IP，每次请求都要重新初始化浏览器
            proxy = get_proxy()
            browser = init_browser(proxy)
            browser.delete_all_cookies()

            browser.get(url)
            # 跳转
            show_btn = browser.find_element_by_class_name('comiis_leftnv_top_key')
            show_btn.click()
            turn_btn = browser.find_element_by_xpath('//div[@class="comiis_sidenv_top comiis_sidenv_topv1 f_f"]/a')
            browser.implicitly_wait(1)
            turn_btn.click()
            time.sleep(1)
            reg_btn = browser.find_elements_by_xpath('//div[@class="comiis_reg_link f_ok cl"]/a')[1]
            reg_btn.click()

            # 注册：填充基本信息
            username = ''.join(random.sample(string.ascii_letters + string.digits, 10))
            pwd = "luna123456"
            email_suffix = "@gmail.com"
            inputs_text = browser.find_elements_by_xpath('//input[@type="text"]')
            if len(inputs_text) == 3:
                input_username = inputs_text[0]
                input_username.send_keys(username)
            inputs_pwd = browser.find_elements_by_xpath('//input[@type="password"]')
            if len(inputs_pwd) == 2:
                input_pwd = inputs_pwd[0]
                input_pwd.send_keys(pwd)
                input_repwd = inputs_pwd[1]
                input_repwd.send_keys(pwd)
            input_email = browser.find_elements_by_xpath('//input[@type="email"]')[0]
            input_email.send_keys(username + email_suffix)
            # 注册：处理验证码
            input_validcode = inputs_text[2]
            validcode = get_validcode(browser)
            while validcode is None:
                # 刷新验证码
                browser.find_element_by_class_name('sec_code_img').click()
                validcode = get_validcode(browser)
            print(validcode)
            input_validcode.send_keys(validcode)

            submit_btn = browser.find_element_by_tag_name('button')
            submit_btn.click()
            print("Times = %d, %s registered success!" % (i, username))
            save(username)
            # time.sleep(5)
            # 将账号存到数据库里，便于日后登录
            browser.quit()
            i += 1
        except Exception as e:
            traceback.print_exc()
            print("try to open the browser again……")
            if browser:
                browser.quit()
            continue

    db.close()
