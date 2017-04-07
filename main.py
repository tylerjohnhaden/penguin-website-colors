from time import time
from lib.custom_tools import load_sites, load_config
from lib.custom_multithreading import ChromeManager

number_of_drivers = 3
timeout = 30

# initialization
print 'Starting thread and driver initialization'
START = time()
chrome, urls, adj, dph = load_config('config/config.ini')
chrome_manager = ChromeManager(0, load_sites(2000, 2010, urls['url_list_path']), logging='VERBOSE')
chrome_manager.load_drivers(number_of_drivers, timeout, path=chrome['driver_path'], extensions=[chrome['ublock_path']])
print 'Initialization time = %f seconds' % (time() - START)

# run code
try:
    chrome_manager.start()
    chrome_manager.join()
except Exception:
    chrome_manager.emergency_stop()

# clean-up
print 'Total time = %f seconds' % (time() - START)
