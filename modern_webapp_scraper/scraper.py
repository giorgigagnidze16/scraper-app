import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modern_webapp_scraper.utils import random_delay, backoff_retry

class ModernWebAppScraper:
    def __init__(self, cfg):
        self.cfg = cfg
        self.driver = self._init_driver()

    def _init_driver(self):
        browser = self.cfg['webdriver']['browser'].lower()
        if browser == 'chrome':
            from selenium.webdriver.chrome.options import Options
            opts = Options()
        elif browser == 'firefox':
            from selenium.webdriver.firefox.options import Options
            opts = Options()
        else:
            raise ValueError(f"Unsupported browser: {self.cfg['webdriver']['browser']}")

        if self.cfg['webdriver']['headless']:
            opts.headless = True

        driver_class = getattr(webdriver, browser.capitalize())
        driver = driver_class(options=opts)
        driver.implicitly_wait(self.cfg['webdriver']['implicit_wait'])
        driver.set_page_load_timeout(self.cfg['webdriver']['page_load_timeout'])
        driver.set_script_timeout(self.cfg['webdriver']['script_timeout'])
        return driver

    @backoff_retry(max_attempts=3)
    def login(self):
        if not self.cfg['target']['login']['enabled']:
            return

        d = self.driver
        cfg = self.cfg['target']['login']
        sel = cfg['selectors']
        creds = cfg['credentials']

        d.get(cfg['login_url'])

        def make_by(entry):
            t = entry['type'].lower()
            v = entry['value']
            if t == 'css':
                return By.CSS_SELECTOR, v
            if t == 'xpath':
                return By.XPATH, v
            if t == 'id':
                return By.ID, v
            if t == 'name':
                return By.NAME, v
            if t in ('class', 'class_name'):
                return By.CLASS_NAME, v
            if t in ('tag', 'tag_name'):
                return By.TAG_NAME, v
            raise ValueError(f"Unknown selector type: {t}")

        by_u, val_u = make_by(sel['username_field'])
        d.find_element(by_u, val_u).send_keys(creds['username'])

        by_p, val_p = make_by(sel['password_field'])
        d.find_element(by_p, val_p).send_keys(creds['password'])

        by_b, val_b = make_by(sel['submit_button'])
        d.find_element(by_b, val_b).click()

        WebDriverWait(d, self.cfg['webdriver']['implicit_wait']).until(
            EC.url_contains('/inventory.html')
        )

    def _scroll_infinite(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            random_delay(self.cfg['anti_detection']['min_delay'], self.cfg['anti_detection']['max_delay'])
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def _make_by(self, sel):
        t = sel['type'].lower()
        v = sel['value']
        if t == 'css':
            return By.CSS_SELECTOR, v
        if t == 'xpath':
            return By.XPATH, v
        if t == 'id':
            return By.ID, v
        if t == 'name':
            return By.NAME, v
        if t in ('class', 'class_name'):
            return By.CLASS_NAME, v
        if t in ('tag', 'tag_name'):
            return By.TAG_NAME, v
        raise ValueError(f"Unknown selector type: {t}")

    def _extract_items(self):
        rows = []
        # find all item containers
        items = self.driver.find_elements(
            By.CSS_SELECTOR,
            self.cfg['extraction']['item_selector']
        )

        for item in items:
            row = {}
            for field in self.cfg['extraction']['fields']:
                name = field['name']

                # 1) JS extractor?
                if 'js' in field:
                    try:
                        row[name] = self.driver.execute_script(field['js'])
                    except Exception:
                        row[name] = None
                    continue

                by, val = self._make_by(field['selector'])
                try:
                    elem = item.find_element(by, val)
                    attr = field.get('attribute', 'text')
                    if attr == 'text':
                        value = elem.text
                    else:
                        value = elem.get_attribute(attr)
                except Exception:
                    value = None

                if value is not None and 'post_process' in field:
                    value = eval(
                        field['post_process'],
                        {'value': value, 're': re}
                    )

                row[name] = value

            rows.append(row)

        return rows

    def scrape(self):
        self.login()
        self.driver.get(self.cfg['target']['url'])
        if self.cfg['navigation']['infinite_scroll']:
            self._scroll_infinite()

        all_rows = []
        all_rows.extend(self._extract_items())

        pages = 1
        while pages < self.cfg['navigation']['max_pages']:
            try:
                nxt = self.driver.find_element(By.CSS_SELECTOR, self.cfg['navigation']['pagination_selector'])
                nxt.click()
                WebDriverWait(self.driver, 10).until(EC.staleness_of(nxt))
                random_delay(self.cfg['anti_detection']['min_delay'], self.cfg['anti_detection']['max_delay'])
                all_rows.extend(self._extract_items())
                pages += 1
            except Exception:
                break
        return all_rows

    def close(self):
        self.driver.quit()