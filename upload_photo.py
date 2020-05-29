import os

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, \
    StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import os
import time

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

def click_button_by_label(label:str,max_wait =10,show=True,element_type:str="*"):
    driver.implicitly_wait(10)

    def _by_xpath(try_times = 3) -> webdriver.remote.webelement.WebElement:
        driver.implicitly_wait(10)
        if show:
            print(f"INFO: RUN ON PAGE: {driver.title}")
        buttons = driver.find_elements_by_xpath(f"//{element_type}[text()='{label}']")

        while len(buttons)< 0 and try_times > 0:

            buttons = driver.find_elements_by_xpath(f"//{element_type}[text()='{label}']")
            try_times-=1
            time.sleep(1)

        return buttons[0]

    button = _by_xpath()
    current_wait_time_for_element_ready = 0
    while 1:
        try:
            print(f"try: click: {label}: {button.text}")
            button.click()
            print(f"OK: click!")
            break
        except ElementClickInterceptedException:
            button = button.find_element_by_xpath("./..")
            print(f"W: click fail! go to parent element:{button.text}")

        except ElementNotInteractableException as e: # js of element not ready
            current_wait_time_for_element_ready += 1
            print(f"W: click fail! waited for {current_wait_time_for_element_ready},current element: {button.text}, try to find: {label} ")
            time.sleep(1)
            assert current_wait_time_for_element_ready <= max_wait, f"timeout: {e}"
            button = _by_xpath()
            button = button[0]

        except StaleElementReferenceException as e: #element is not attached to the page document
            print("W: click fail! element not ready! wait")
            time.sleep(1)
            button = _by_xpath()
            button = button[0]


def find_css_key_input(xpath, content, try_option=False):
    driver.implicitly_wait(2)

    if try_option:
        try:
            field = driver.find_element_by_css_selector(xpath)
            field.send_keys(content)
        except:
            pass
    else:
        field = driver.find_element_by_css_selector(xpath)
        field.send_keys(content)


def check_element_exist_by_label(label: str, element_type:str='*')->bool:
    try:
        field = driver.find_elements_by_xpath(f"//{element_type}[text()='{label}']")
        print(f"OK: Label \'{label}\' exist!")
        return True
    except:
        return False




chrome_options = webdriver.ChromeOptions()

# not capture memory
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')

# show windows or not
chrome_options.add_argument('--headless')


#mobile mode
#chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1')


# disable notifications
prefs = {
    'profile.default_content_setting_values' :
        {
        'notifications' : 2
         }
}
chrome_options.add_experimental_option('prefs', prefs)

try:
    driver = webdriver.Chrome(executable_path=f'{os.getcwd()}/lib/chromedriver', options=chrome_options)
except:
    driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(360, 1280)
driver.implicitly_wait(10)

url = 'https://www.facebook.com/'
driver.get(url)
driver.implicitly_wait(10)


username, password = "0910365567", "!gavin840511"
find_css_key_input(xpath="input[type='text']", content=username, try_option=True)
find_css_key_input(xpath="input[type='email']", content=username, try_option=True)
find_css_key_input(xpath="input[type='password']", content=password)
driver.implicitly_wait(2)

#button= driver.find_elements_by_xpath("//*[contains(text(), '登入')]") or driver.find_elements_by_xpath("//*[contains(text(), 'Log In')]")
ActionChains(driver).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()
driver.implicitly_wait(30)

assert check_element_exist_by_label(label="建立貼文") and check_element_exist_by_label(label="平行城市")

click_button_by_label(label='平行城市')
driver.implicitly_wait(10)

assert check_element_exist_by_label(label="發佈工具")

click_button_by_label(label='發佈工具')
driver.implicitly_wait(10)
assert check_element_exist_by_label(label="觸及人數")

click_button_by_label(label='建立貼文')
driver.implicitly_wait(10)


assert check_element_exist_by_label(label="接收訊息")
field = driver.find_element_by_xpath(f"//*[contains(@aria-label, \"撰寫貼文\")]")
field.click()
field.send_keys("我最愛的工作機ＱＱ")
driver.implicitly_wait(10)

click_button_by_label(label='相片／影片')
driver.implicitly_wait(10)




"""
##<input accept="video/*,  video/x-m4v, video/webm, video/x-ms-wmv, video/x-msvideo, video/3gpp, video/flv, video/x-flv, video/mp4, video/quicktime, video/mpeg, video/ogv, .ts, .mkv, image/*, image/heic, image/heif" multiple="" name="composer_photo" display="inline-block" type="file" class="_n _5f0v" id="js_1y">
##field = driver.find_element_by_name(name='composer_photo')
"""

driver.find_element_by_name("composer_photo").send_keys(os.getcwd()+"/lib/img/sample.jpg")
time.sleep(10)


click_button_by_label(label='貼文將會顯示在 Instagram')
driver.implicitly_wait(10)

click_button_by_label(label='立即分享', element_type="span")
driver.implicitly_wait(10)

time.sleep(10)
print('OK: Success!')
driver.implicitly_wait(15)
driver.quit()