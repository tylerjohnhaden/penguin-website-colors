from threading import Thread
from time import strftime


class DataProcessor(Thread):
    def __init__(self, data_processor_id):
        Thread.__init__(self)
        self.data_id = data_processor_id

    def log(self, message):
        print strftime("%c"), ": DATA PROCESSOR THREAD (" + str(self.data_id) + ") :", message

    def run(self):
        pass


class LoadBalancer(Thread):
    def __init__(self, load_balancer_id):
        Thread.__init__(self)
        self.load_id = load_balancer_id

    def log(self, message):
        print strftime("%c"), ": LOAD BALANCER THREAD (" + str(self.load_id) + ") :", message

    def run(self):
        pass


class DriverThread(Thread):
    def __init__(self, driver_thread_id):
        Thread.__init__(self)
        self.drive_id = driver_thread_id

    def log(self, message):
        print strftime("%c"), ": DRIVER THREAD (" + str(self.drive_id) + ") :", message

    def run(self):
        pass
