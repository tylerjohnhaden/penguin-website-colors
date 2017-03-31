from custom_tools import load_sites, load_drivers, load_config, close_drivers
import time

# initialization
number_of_drivers = 2
chrome, urls, adj, dph = load_config()
websites = load_sites(0, 1, urls['url_list_path'], urls['url_regex'])
LOAD_START = time.time()
drivers = load_drivers(number_of_drivers, chrome['driver_path'], chrome['ublock_path'])
print "Drivers loaded in     {:6.3f} seconds".format(time.time() - LOAD_START)

# run code
SCREEN_SHOT_START = time.time()
try:
    for i in xrange(number_of_drivers):
        drivers[i].get(websites[i])
        drivers[i].save_screenshot('temp/' + str(i) + '_img.png')
except Exception:
    pass
print "Screen shots taken in {:6.3f} seconds".format(time.time() - SCREEN_SHOT_START)

# clean-up
close_drivers(drivers)
