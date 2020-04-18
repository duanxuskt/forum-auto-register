from selenium import webdriver
import traceback
from selenium.webdriver.common.action_chains import ActionChains
import string
import random
import time
import re

url = 'https://www.51highing.com/?fromuser=duanxuskt'

chrome_options = webdriver.ChromeOptions()  # 使用headless无界面浏览器模式
chrome_options.set_capability('pageLoadStrategy', 'eager')
browser = webdriver.Chrome(options=chrome_options)


def switch_window(browser):
    """
    切换window窗口,切换一次后退出
    :return: 无
    """
    curHandle = browser.current_window_handle  # 获取当前窗口聚丙
    allHandle = browser.window_handles  # 获取所有聚丙
    """循环判断，只要不是当前窗口聚丙，那么一定就是新弹出来的窗口，这个很好理解。"""
    for h in allHandle:
        if h != curHandle:
            browser.switch_to.window(h)  # 切换聚丙，到新弹出的窗口
            break


mapping = {'"中指指甲"': '177,149', '"妹子的金戒指"': '196,57',
           '"菊花"': '245,57', '"你想掰开的地方"': '159,87',
           '"妹子的毛"': '220,90', '"左奶""右奶"': '186,150|252,148',
           '"2人的连接处"': '175,100', '"你想要吸的点"': '108,52',
           '"老师的菊花"': '223,104', '"私处"': '180,151', '"不协调的白色物体"': '153,141',
           '"妹子的嘴巴"': '185,34', }


def fetch_code():
    change_btn.click()
    ele = None
    while ele is None:
        try:
            reload = browser.find_element_by_id('dcclick-reload')
            reload.click()
            time.sleep(0.5)
            ele = (browser.find_element_by_xpath('//span[@class="dcclick-font16 dcclick-color-text"]'))
        except Exception as e:
            traceback.print_exc()
            change_btn.click()
            continue
    print(ele)
    print(ele.size)
    txt = ele.text
    while txt == "" or txt == '""':
        change_btn.click()
        ele = (browser.find_element_by_xpath('//span[@class="dcclick-font16 dcclick-color-text"]'))
        txt = ele.text
    return mapping.get(txt)


if __name__ == '__main__':
    n = 100
    i = 1
    while i <= int(n):
        try:
            browser.get(url)
            # 跳转
            time.sleep(3)
            hover_img = browser.find_element_by_xpath('//div[@class="nexDL_unknown"]/img')
            actions = ActionChains(browser)
            actions.move_to_element(hover_img).perform()
            actions.move_to_element(hover_img).perform()
            browser.find_element_by_xpath('//li[@class="nexbdRegs"]/a').click()
            time.sleep(1)
            # 注册
            browser.find_elements_by_xpath('//p[@class="fsb pns cl hm"]/button')[0].click()
            switch_window(browser)
            # time.sleep(3)
            change_btn = browser.find_element_by_xpath('//div[@class="nex_liner_box nex_liner_box_valides"]//a')
            param_r = fetch_code()
            req_str = 'https://www.51highing.com/plugin.php?id=dc_seccode:check&r=%s&ran=%f' % (
                param_r, random.random())
            while param_r is None:
                req_str = 'https://www.51highing.com/plugin.php?id=dc_seccode:check&r=%s&ran=%f' % (
                    param_r, random.random())
                param_r = fetch_code()
            browser.execute_script("window.open('%s')" % req_str)
            handlers = browser.window_handles
            browser.switch_to.window(handlers[1])
            wrap = browser.find_element_by_tag_name('body').text
            code = re.search("(.*)\"(\w{4})\"(.*)", wrap).group(2)
            handlers = browser.window_handles
            browser.close()

            browser.switch_to.window(handlers[0])  # go_back
            # 开始正式进行表单自动注册填充
            inputs_username = browser.find_element_by_xpath('//input[@placeholder="用户名"]')
            username = ''.join(random.sample(string.ascii_letters + string.digits, 10))
            inputs_username.send_keys(username)
            inputs_pwd = browser.find_element_by_xpath('//input[@placeholder="密码"]')
            inputs_repwd = browser.find_element_by_xpath('//input[@placeholder="确认密码"]')
            pwd = "luna123456"
            inputs_pwd.send_keys(pwd)
            inputs_repwd.send_keys(pwd)
            inputs_email = browser.find_element_by_xpath('//input[@placeholder="Email"]')
            email_suffix = "@gmail.com"
            inputs_email.send_keys(username + email_suffix)
            inputs_code = browser.find_element_by_name('seccodeverify')
            inputs_code.send_keys(code)
            # submit
            submit_btn = browser.find_element_by_id('registerformsubmit')
            submit_btn.send_keys("\n")
            print("Times = %d, %s registered success!" % (i, username))
            i += 1
        except Exception as e:
            traceback.print_exc()
            print("重新打开浏览器…………")
            browser.refresh()
            continue
    browser.quit()
