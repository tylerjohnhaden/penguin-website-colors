from custom_tools import load_sites, load_config
from time import time
from custom_multithreading import ChromeManager

TOTAL_START = time()

# initialization
INIT_START = time()
number_of_drivers = 3
timeout = 30

chrome, urls, adj, dph = load_config('config/config.ini')
chrome_manager = ChromeManager(0, load_sites(1000, 1006, urls['url_list_path']), logging='VERBOSE')
chrome_manager.load_drivers(number_of_drivers, chrome['driver_path'], timeout, chrome['ublock_path'])
print 'Initialization time = %f seconds' % (time() - INIT_START)

# run code
try:
    chrome_manager.start()
    chrome_manager.join()
except Exception:
    chrome_manager.emergency_stop()

# clean-up
print 'Total time = %f seconds' % (time() - TOTAL_START)
