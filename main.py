#! /usr/bin/python

# TODO: Add documenation

from time import time
from lib.custom_tools import load_sites
from lib.custom_multithreading import ChromeManager
import os
import shutil

number_of_drivers = 15
range_of_websites = (3000, 3200)  # this means that one website will be downloaded [0] = 'http://google.com'
timeout = 30

# these are defaults, just putting them here to show where they would be set
chromedriver_version = 'LATEST'  # if you don't want latest, set to version number, i.e. '2.29'
uBlock_version = 'LATEST'        # if you don't want latest, set to version number, i.e. '1.12.1'
website_list = 'LATEST'          # if you don't want latest, set to version number, i.e. '18.04.2017'

if not os.path.exists('.temp'):
    os.makedirs('.temp')


# initialization
print 'Starting thread and driver initialization'
START = time()
sites = load_sites(range_of_websites[0], range_of_websites[1], website_list)
chrome_manager = ChromeManager(0, sites, logging='VERBOSE')
chrome_manager.load_drivers(number_of_drivers, timeout, chromedriver_version, uBlock_version)
print 'Initialization time = %f seconds' % (time() - START)

# run code
try:
    chrome_manager.start()
    chrome_manager.join()
except Exception:
    chrome_manager.emergency_stop()

if len(os.listdir('.temp')) == 0:
    shutil.rmtree('.temp')

# clean-up
print 'Total time = %f seconds' % (time() - START)
