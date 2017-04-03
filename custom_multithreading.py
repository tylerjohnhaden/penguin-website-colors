from threading import Thread


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


class DriverThread(Thread):
    def __init__(self, driver_thread_id, chrome_driver):
        Thread.__init__(self)
        self.driver_thread_id = driver_thread_id
        self.chrome_driver = chrome_driver

    def log(self, message):
        print strftime("%c"), ": DRIVER THREAD (" + str(self.driver_thread_id) + ") :", message

    def screenshot(self, website, target_file):
        from os.path import getsize
        self.chrome_driver.get(website)
        self.chrome_driver.save_screenshot(target_file)
        return getsize(target_file)
