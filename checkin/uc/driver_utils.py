
import undetected_chromedriver as uc

mode = ''


def get_driver():
    options = uc.ChromeOptions()
    driver_executable_path = r"C:\SeleniumWebDrivers\ChromeDriver\chromedriver.exe"
    browser_executable_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    options.add_argument("--disable-popup-blocking")
    if mode == "debug":
        options.add_argument('--proxy-server=http://127.0.0.1:7890')
        driver_executable_path = r"C:\Users\32506\AppData\Roaming\undetected_chromedriver\undetected_chromedriver.exe"

    else:
        # 增加无界面选项
        options.add_argument('--headless')
        # 如果不加这个选项，有时定位会出现问题
        options.add_argument('--disable-gpu')

    driver = uc.Chrome(driver_executable_path=driver_executable_path, browser_executable_path=browser_executable_path,
                       options=options)

    return driver



