# TODO: Internet connectivity speed benchmark
# TODO: Docs

import os
import shutil
import threading
from time import time, sleep

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

import lib.custom_tools as custom_tools


class Penguin:
    # TODO: compute max run time based on timeout and website list, have display of estimated time of completion, etc.
    def __init__(self, chrome_count):
        self.threads = [threading.Thread(target=self.driver_thread) for __ in xrange(chrome_count)]
        self.driver_functionality = None
        self.page_timeout = 30  # default 30 seconds
        self.is_headless = True  # default headless mode
        self.use_ublock = True  # default use ublock

        self.processor_thread = threading.Thread(target=self.process_thread)
        self.processor_functionality = None
        self.max_queue_length = 0

        self.websites = []
        self.timeout_sites = []

    def processor(self, funct):
        def wrapper():
            return funct()

        self.processor_functionality = wrapper
        return None

    def process_thread(self):
        if self.processor_functionality is None:
            raise NotImplementedError('Processor functionality must be defined, i.e. @Penguin.processor')

        try:
            for i in xrange(10000000):  # ten million
                state, queue_length = self.processor_functionality()
                self.max_queue_length = max(queue_length, self.max_queue_length)
                if state is False:
                    break
        finally:
            pass

    def driver(self, funct):
        def wrapper(websites, driver):
            return funct(websites, driver)

        self.driver_functionality = wrapper
        return None

    def load_driver(self):
        options = Options()
        if self.use_ublock:
            ublock0_path = custom_tools.get_path('uBlock0', target='uBlock0.chromium')
            options.add_argument('load-extension=' + ublock0_path)
        if self.headless:
            options.add_argument('window-size=1300,750')
            options.add_argument('window-position=2000,0')

        chromedriver_path = custom_tools.get_path('chromedriver', target='chromedriver.exe')
        driver = Chrome(executable_path=chromedriver_path, chrome_options=options)
        driver.set_page_load_timeout(self.page_timeout)
        return driver

    def driver_thread(self):
        if self.driver_functionality is None:
            raise NotImplementedError('Driver functionality must be defined, i.e. @Penguin.driver')

        driver = self.load_driver()

        try:
            for i in xrange(10000000):  # ten million
                state, timeout_site = self.driver_functionality(self.websites, driver)
                if timeout_site is not None:
                    self.timeout_sites.append(timeout_site)
                if state is False:
                    break
        finally:
            driver.quit()

    def run(self):
        start = time()
        if not os.path.exists('.temp'):
            os.makedirs('.temp')
        if not os.path.exists('data'):
            os.makedirs('data')

        self.processor_thread.start()
        for t in self.threads:
            t.start()
        for t in self.threads:
            t.join()

        while len(os.listdir('.temp')) != 0:
            sleep(.1)
        shutil.rmtree('.temp')

        self.processor_thread.join()

        return time() - start

    def ublock(self, use_ublock=True):
        self.use_ublock = use_ublock

    def headless(self, is_headless=True):
        self.is_headless = is_headless

    def timeout(self, seconds):
        self.page_timeout = seconds

    def save_timeouts(self):
        with open('data/timeouts.csv', 'a') as timeout_log:
            for line in self.timeout_sites:
                timeout_log.write(line[0] + ', ' + line[1] + '\n')

    def add_websites(self, start, end):
        self.websites.extend(custom_tools.load_sites(start, end))
        return self
