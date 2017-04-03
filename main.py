from custom_tools import load_sites, load_drivers, load_config, close_drivers, imagefile_to_dphfile
from time import time
from os import remove
from os.path import getsize

# initialization
number_of_drivers = 3
chrome, urls, adj, dph = load_config('config/config.ini')


# change config url_list_path to \penguin-website-colors\scrubbed_top-1m_3-15-17.csv!
websites = load_sites(0, number_of_drivers, urls['url_list_path'])
# e.i websites = [('http://google.com', 'google'), ('http://youtube.com', 'youtube')]

LOAD_START = time()
drivers = load_drivers(number_of_drivers, chrome['driver_path'], chrome['ublock_path'])
print "{:40} {:6.3f} seconds\n".format('Drivers loaded in', time() - LOAD_START)

image_size_sum = 0
data_size_sum = 0

# run code
SCREEN_SHOT_START = time()
try:
    for driver in drivers:
        website = websites.pop(0)

        site_address = website[0]
        site_name = website[1]
        screen_shot_file = 'temp/' + '%s.png' % site_name
        dph_file = 'data/' + dph['dph_template'] % site_name

        driver.get(site_address)
        driver.save_screenshot(screen_shot_file)

        data_size = imagefile_to_dphfile(screen_shot_file, site_name, dph_file)
        data_size_sum += data_size
        image_size = getsize(screen_shot_file)
        image_size_sum += image_size

        print '    [' + site_name + ']: Image size =', image_size, ', Data size =', data_size

        remove(screen_shot_file)

except Exception:
    pass
SCREEN_SHOT_TIME = time() - SCREEN_SHOT_START

print "\n{:40} {:6.3f} seconds".format('Screen shots taken (and parsed!) in', SCREEN_SHOT_TIME)
print 'Average Image size     =', image_size_sum / number_of_drivers
print 'Average Data size      =', data_size_sum / number_of_drivers
print 'Average Time per page  =', SCREEN_SHOT_TIME / number_of_drivers

# clean-up
close_drivers(drivers)
