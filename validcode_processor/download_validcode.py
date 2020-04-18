from selenium import webdriver
from PIL import Image
import os
import uuid

url = ''

chrome_options = webdriver.ChromeOptions()  # 使用headless无界面浏览器模式
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')

mobile_emulation = {"deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
                    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D)"
                                 " AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"}

chrome_options.add_experimental_option('mobileEmulation', mobile_emulation)
chrome_options.set_capability('pageLoadStrategy', 'eager')
browser = webdriver.Chrome(options=chrome_options)

if __name__ == '__main__':
    browser.get(url)
    dir = "F:\\temp\\validCode\\pre"
    screenshot_path = os.path.join(dir, "screenshot.png")
    n = 1
    while n <= 500:
        browser.get_screenshot_as_file(screenshot_path)
        element = browser.find_element_by_class_name('sec_code_img')
        # 自己用PS标志基准线去量（像素模式）
        # 从截图中抠出来验证码的区域
        captcha_path = os.path.join(dir, '%s.png' % str(uuid.uuid4()).replace('-', ''))
        if os.path.exists(captcha_path):
            os.remove(captcha_path)
        img = Image.open(screenshot_path)
        img = img.crop((752, 643, 1031, 727))
        img.save(captcha_path)
        # 灰度化
        imgry = img.convert('L')  # 转化为灰度图

        # # 获取图片中的出现次数最多的像素，即为该图片的背景
        # max_pixel = get_threshold(imgry)
        # # 将图片进行二值化处理
        # table = get_bin_table(threshold=max_pixel)
        # out = imgry.point(table, '1')
        # # 去掉图片中的噪声（孤立点）
        # out = cut_noise(out)
        # browser.refresh()
        browser.find_element_by_class_name('sec_code_img').click()
        n += 1
