from threading import Thread
from psutil import cpu_percent


class DataProcessor(Thread):
    def __init__(self, data_processor_id):
        Thread.__init__(self)
        self.data_processor_id = data_processor_id

    def log(self, message):
        from time import strftime
        print strftime("%c"), ": DATA PROCESSOR THREAD (" + str(self.data_processor_id) + ") :", message

    def process_image(self, image_file, image_name, target_file):
        from custom_tools import imagefile_to_dphfile
        from os import remove
        size = imagefile_to_dphfile(image_file, image_name, target_file)
        remove(image_file)
        return size


class LoadBalancer(Thread):
    def __init__(self, load_balancer_id):
        Thread.__init__(self)
        self.load_balancer_id = load_balancer_id

    def log(self, message):
        from time import strftime
        print strftime("%c"), ": LOAD BALANCER THREAD (" + str(self.load_balancer_id) + ") :", message

    def run(self):
        pass


class ChromeManager(Thread):
    def __init__(self, chrome_manager_id, websites, logging='NORMAL'):
        Thread.__init__(self)
        self.chrome_manager_id = chrome_manager_id
        self.websites = websites
        self.drivers = []
        self.logging = logging

    def log(self, message, verbosity='NORMAL'):
        from time import strftime
        if self.logging == 'OFF':
            return
        elif self.logging == 'NORMAL' and verbosity == 'NORMAL':
            print strftime("%c"), ": CHROME MANAGER THREAD (" + str(self.chrome_manager_id) + ") :", message
        elif self.logging == 'VERBOSE':
            print strftime("%c"), ": CHROME MANAGER THREAD (" + str(self.chrome_manager_id) + ") :", message

    def load_drivers(self, n, timeout, path, extensions):
        if len(self.drivers) != 0:
            self.log('Tried loading drivers for a second time')
            return False
        if n < 1:
            raise AttributeError('n has to be positive')

        options = None
        if len(extensions) > 0:
            from selenium.webdriver.chrome.options import Options
            options = Options()
            for extension in extensions:
                options.add_argument('load-extension=' + extension)
            options.add_argument('window-size=1300,750')
            options.add_argument('window-position=2000,0')

        for driver_id in xrange(n):
            self.drivers.append(DriverThread(driver_id, path, options, timeout=timeout))
        return True

    def start_all_drivers(self):
        for driver in self.drivers:
            driver.start()

    def emergency_stop(self):
        for driver in self.drivers:
            driver.lose_the_will_to_live()
            driver.chrome_driver.quit()

    def run(self):
        from time import sleep

        self.start_all_drivers()

        if len(self.drivers) == 0:
            self.log('Tried running with zero initialized drivers')
            return

        count = 0
        while len(self.websites) > 0:
            if count == 5:
                self.log(('UPDATE: %d websites left to go' % len(self.websites)) +
                         ("  CPU: %f" % cpu_percent(1)), 'VERBOSE')
                count = 0
            else:
                count += 1
            # self.log('running')
            driver = self.drivers.pop(0)
            website = self.websites.pop()
            if not driver.set_new_task(website[0], 'temp/%s.png' % website[1]):
                self.websites.append(website)
            self.drivers.append(driver)
            sleep(.5)

        # close all Driver Threads
        self.log('Killing my children!')
        for driver in self.drivers:
            driver.lose_the_will_to_live()

        while len(self.drivers) > 0:
            self.log('UPDATE: %d drivers left to go' % len(self.drivers), 'VERBOSE')
            driver = self.drivers.pop(0)
            if not driver.done:
                self.drivers.append(driver)
                sleep(2.5)


class DriverThread(Thread):
    def __init__(self, driver_thread_id, chrome_path, options, timeout=-1):
        from selenium.webdriver import Chrome
        Thread.__init__(self)
        self.driver_thread_id = driver_thread_id

        # Chrome options and initialization
        self.chrome_driver = Chrome(executable_path=chrome_path, chrome_options=options)
        if timeout > 0:
            self.chrome_driver.set_page_load_timeout(timeout)

        self.current_website = ''
        self.current_target_file = ''
        self.busy = False
        self.i_have_the_will_to_live = True
        self.done = False

    def log(self, message):
        from time import strftime
        print strftime("%c"), ": DRIVER THREAD (" + str(self.driver_thread_id) + ") :", message

    def set_new_task(self, website, target_file):
        if self.busy:
            return False
        self.current_website = website
        self.current_target_file = target_file
        self.busy = True
        return True

    def run(self):
        from time import sleep
        from selenium.common.exceptions import TimeoutException

        while self.i_have_the_will_to_live:
            if self.busy:
                try:
                    self.log('taking screen shot!')
                    self.screenshot(self.current_website, self.current_target_file)
                except TimeoutException as e:
                    self.log('Timeout on %s' % self.current_website)
                self.busy = False
            else:
                sleep(.5)
        self.done = True
        self.chrome_driver.quit()

    def screenshot(self, website, target_file):
        from os.path import getsize
        self.chrome_driver.get(website)
        self.chrome_driver.save_screenshot(target_file)
        return getsize(target_file)

    def lose_the_will_to_live(self):
        self.log('I lost the will to live')
        self.i_have_the_will_to_live = False
