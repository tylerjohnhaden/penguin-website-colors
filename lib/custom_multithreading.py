from threading import Thread
from psutil import cpu_percent
from time import strftime, sleep
from os import remove, listdir, getcwd

from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.common.exceptions import TimeoutException

from custom_tools import imagefile_to_dphfile


class INDEPENDENT_DataProcessor(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.working_list = []
        print "INITIALIZATION of the data processor"

    @staticmethod
    def log(message):
        print strftime("%c"), ": DATA PROCESSOR THREAD (INDEPENDENT) :", message

    @staticmethod
    def process_image(image_file, image_name, target_file):
        imagefile_to_dphfile(image_file, image_name, target_file)
        remove(image_file)

    @staticmethod
    def process_source(source_file, image_name, target_file):
        with open(source_file, 'r') as in_file:
            with open(target_file, 'w') as out_file:
                # TODO: Implement Beautiful soup here
                out_file.write(in_file.read())
        remove(source_file)

    def run(self):
        while self.running:
            sleep(.3)
            for current in self.working_list[:]:
                self.log('processing ' + current)
                self.process_image('.temp/%s.png' % current, current, 'data/color/%s.dph' % current)
                self.process_source('.temp/%s.html' % current, current, 'data/tags/%s.html' % current)
                self.working_list.remove(current)


class ChromeManager(Thread):
    def __init__(self, chrome_manager_id, websites, logging='NORMAL'):
        Thread.__init__(self)
        self.chrome_manager_id = chrome_manager_id
        self.websites = websites
        self.drivers = []
        self.logging = logging
        self.processorThread = INDEPENDENT_DataProcessor()

    def log(self, message, verbosity='NORMAL'):
        if self.logging == 'OFF':
            return
        elif self.logging == 'NORMAL' and verbosity == 'NORMAL':
            print strftime("%c"), ": CHROME MANAGER THREAD (" + str(self.chrome_manager_id) + ") :", message
        elif self.logging == 'VERBOSE':
            print strftime("%c"), ": CHROME MANAGER THREAD (" + str(self.chrome_manager_id) + ") :", message

    def load_drivers(self, n, timeout, chromedriver_option, uBlock0_option):
        relative_path = getcwd()
        if len(self.drivers) != 0:
            self.log('Tried loading drivers for a second time')
            return False
        if n < 1:
            raise ValueError('n has to be positive')

        available_uBlock0_versions = listdir('static/uBlock0')
        if len(available_uBlock0_versions) == 0:
            raise IOError('No uBlock versions found under \'static/uBlock0\'')
        if uBlock0_option == 'LATEST':
            uBlock0_path = 'static/uBlock0/%s/uBlock0.chromium' % available_uBlock0_versions[-1]
        else:
            if 'version_%s' % uBlock0_option in available_uBlock0_versions:
                uBlock0_path = 'static/uBlock0/version_%s/uBlock0.chromium' % uBlock0_option
            else:
                raise IOError('No such directory \'static/uBlock0/version_%s\' found' % uBlock0_option)

        options = Options()
        options.add_argument('load-extension=' + relative_path + '/' + uBlock0_path)
        options.add_argument('window-size=1300,750')
        options.add_argument('window-position=2000,0')

        available_chromedrivers_versions = listdir('static/chromedriver')
        if len(available_chromedrivers_versions) == 0:
            raise IOError('No chromedriver versions found under \'static/chromedriver\'')
        if chromedriver_option == 'LATEST':
            chromedriver_path = 'static/chromedriver/%s/chromedriver.exe' % available_chromedrivers_versions[-1]
        else:
            if 'version_%s' % chromedriver_option in available_chromedrivers_versions:
                chromedriver_path = 'static/chromedriver/version_%s/chromedriver.exe' % chromedriver_option
            else:
                raise IOError('No such directory \'static/chromedriver/version_%s\' found' % chromedriver_option)

        for driver_id in xrange(n):
            self.drivers.append(
                DriverThread(driver_id, chromedriver_path, options, self.processorThread.working_list, timeout=timeout))
        return True

    def start_all_drivers(self):
        for driver in self.drivers:
            driver.start()
        self.processorThread.start()

    def emergency_stop(self):
        for driver in self.drivers:
            driver.lose_the_will_to_live()
            driver.chrome_driver.quit()
        self.processorThread.running = False

    def run(self):

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
            if not driver.set_new_task(website[0], website[1]):
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

        self.processorThread.running = False
        while self.processorThread.is_alive():
            sleep(2.5)


class DriverThread(Thread):
    def __init__(self, driver_thread_id, chrome_path, options, processorPointer, timeout=-1):
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
        self.processorPointer = processorPointer

    def log(self, message):
        print strftime("%c"), ": DRIVER THREAD (" + str(self.driver_thread_id) + ") :", message

    def set_new_task(self, website, target_file):
        if self.busy:
            return False
        self.current_website = website
        self.current_target_file = target_file
        self.busy = True
        return True

    def run(self):
        while self.i_have_the_will_to_live:
            if self.busy:
                try:
                    self.log('taking screen shot')
                    self.chrome_driver.get(self.current_website)
                    self.chrome_driver.save_screenshot('.temp/' + self.current_target_file + '.png')
                    with open('.temp/' + self.current_target_file + '.html', 'w') as source_file:
                        source_file.write(self.chrome_driver.page_source.encode('utf-8'))

                    # send new task to processor thread
                    self.processorPointer.append(self.current_target_file)
                except TimeoutException:
                    self.log('Timeout on %s' % self.current_website)
                self.busy = False
            else:
                sleep(.5)
        self.done = True
        self.chrome_driver.quit()

    def lose_the_will_to_live(self):
        self.log('I lost the will to live')
        self.i_have_the_will_to_live = False
