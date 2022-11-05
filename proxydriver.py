import time
from selenium import webdriver
from selenium.webdriver.common.by import By


class ClickTimeoutException(Exception):
    pass

class CustomFirefoxDriver:
    def __init__(self, ff_loc, ff_exec, urls):
        self._urls = urls

        options = webdriver.FirefoxOptions()
        options.binary_location = ff_exec
        options.set_preference('permissions.default.image', 2)

        self._driver = webdriver.Firefox(
            executable_path=ff_loc, options=options) 

        self._driver.set_page_load_timeout(15)
        self._driver.set_script_timeout(30)

        self._driver.get(urls['rules'])

    def get(self, url):
        self._driver.get(url)
    
    def clear_data(self):
        #self._driver.get("about:config")
        self._driver.delete_all_cookies()


    def disable_proxy(self):
        self._driver.get("about:config")
        setupScript = f"""var prefs = Components.classes["@mozilla.org/preferences-service;1"]
                .getService(Components.interfaces.nsIPrefBranch);
                prefs.setIntPref("network.proxy.type", 0); """
        
        self._driver.execute_script(setupScript)

    def dynamic_update_proxy(self, host, port):
        self._driver.get("about:config")
        setupScript = f"""var prefs = Components.classes["@mozilla.org/preferences-service;1"]
                .getService(Components.interfaces.nsIPrefBranch);

                prefs.setIntPref("network.proxy.type", 1);
                prefs.setCharPref("network.proxy.http", "{host}");
                prefs.setIntPref("network.proxy.http_port", "{port}");
                prefs.setCharPref("network.proxy.ssl", "{host}");
                prefs.setIntPref("network.proxy.ssl_port", "{port}");
                prefs.setCharPref("network.proxy.ftp", "${host}");
                prefs.setIntPref("network.proxy.ftp_port", "{port}");"""

        self._driver.execute_script(setupScript)

    def dynamic_update_proxy_with_creds(self, host, port, username, password):
        self._driver.proxy = {
            'http': f'http://{username}:{password}@{host}:{port}',
            'https': f'https://{username}:{password}@{host}:{port}',
        }

        self.dynamic_update_proxy(
            f'{username}:{password}@{host}',
            port
        )

    def _wait_for_click(self, time_s: int):
        elapsed = 0.0

        while 'uniqid' in self._driver.current_url and elapsed < time_s:
            time.sleep(.5)
            elapsed += .5
        
        if 'uniqid' in self._driver.current_url:
            raise ClickTimeoutException('Click failed to register')


    def click_user(self, url: str):
        self._driver.get(url)

        time.sleep(0.3)

        recform = self._driver.find_element(value='recruit_form')
        eles = recform.find_elements(by=By.CSS_SELECTOR, value='*')
        eles[2].click()

        self._wait_for_click(15)

    def toggle_javascript(self, state: bool):
        self._driver.get("about:config")
        setupScript = f"""var prefs = Components.classes["@mozilla.org/preferences-service;1"]
                .getService(Components.interfaces.nsIPrefBranch);
                prefs.setIntPref("network.proxy.type", {str(state).lower()}); """
        
        self._driver.execute_script(setupScript)

    def enter_proxy_creds(self, username: str, password: str):
        self._driver.switch_to.alert.send_keys(username + webdriver.common.keys.Keys.TAB + password)
        self._driver.switch_to.alert.accept()

    def test_connection(self) -> bool:
        try:
            self._driver.get(self._urls)
            if ': Rules' not in self._driver.title:
                return False
        except Exception:
            return False
        return True
    
    @property
    def d(self) -> webdriver.Firefox:
        return self._driver