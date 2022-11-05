import datetime
import re
from threading import Thread, Lock
import requests
import time
import proxydriver


loc_firefox = r'.\geckodriver.exe'
ffexec = r'C:\Program Files\Mozilla Firefox\firefox.exe'

proxy_lifetime_seconds = 6
loopcount = 150
urls = {
    'rules': 'https://roc.com/rules.php',
    'home': 'https://roc.com/'
}

user_urls = [
    "https://roc.com/recruit.php?uniqid=3mzh", # thirst
    #"https://roc.com/recruit.php?uniqid=715e" # cardboard
]



def load_proxies(path) -> list[str]:
    with open(path, 'r') as f:
        lines = f.readlines()
        res = [line.strip() for line in lines]
    return res


def refresh_proxy():
    proxies = {
        'http': 'http://geo.iproyal.com:12321',
        'https': 'http://geo.iproyal.com:12321',
    }
    r = requests.get('https://ipv4.icanhazip.com', proxies=proxies)
    ip = r.text[r.text.index('<pre>')+5 : r.text.index('</pre>')]
    return r.text.strip()


def sticky_loop(driver: proxydriver.CustomFirefoxDriver):

    def get_ip():
        driver.get('https://ipv4.icanhazip.com')
        src = driver.d.page_source

        return src[src.index('<pre>')+5:src.index('</pre>')]

    proxy_lifetime = datetime.timedelta(seconds=proxy_lifetime_seconds - 1)
    last_ip = get_ip()
    driver.dynamic_update_proxy('geo.iproyal.com','12321')
    for i in range(loopcount):
        print(f'Loop #{i}')
        try:
            
            cur_ip = get_ip()

            while last_ip == cur_ip:
                time.sleep(1)
                cur_ip = get_ip()
            proxy_create_time = datetime.datetime.now()
            last_ip = cur_ip

            for userurl in user_urls:
                try:
                    driver.click_user(userurl)
                except Exception as e:
                    print(e)
                    time.sleep(1)
            
            time_proxy_expires = (proxy_create_time + proxy_lifetime)
            if(time_proxy_expires > datetime.datetime.now()):
                time_till_proxy_expires = time_proxy_expires - datetime.datetime.now()
                seconds = time_till_proxy_expires.total_seconds()
                print(f'Sleeping for {seconds} seconds')
                time.sleep(seconds)

        except Exception as e:
            print(f'Failure: {e}')


print('Opening driver')
driver = proxydriver.CustomFirefoxDriver(ff_loc=loc_firefox, ff_exec=ffexec, urls=urls)
print('Driver opened')

sticky_loop(driver)