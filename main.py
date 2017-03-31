from custom_tools import load_sites, load_drivers, load_config, close_drivers, imagefile_to_dphfile
from time import time
from os import remove

# initialization
number_of_drivers = 5
chrome, urls, adj, dph = load_config()
websites = load_sites(0, 4, urls['url_list_path'], urls['url_regex'])
LOAD_START = time()
drivers = load_drivers(number_of_drivers, chrome['driver_path'], chrome['ublock_path'])
print "{:40} {:6.3f} seconds".format('Drivers loaded in', time() - LOAD_START)

# run code
SCREEN_SHOT_START = time()
try:
    for i in xrange(number_of_drivers):
        imagename = 'site_' + str(i)                               # arbitrary name for site
        imagefile = 'temp/' + '%s.png' % imagename                   # path to screen shot
        dphfile = 'data/' + dph['dph_template'] % imagename            # path to future dph data file

        drivers[i].get(websites.pop(0))                                    # get next website
        drivers[i].save_screenshot(imagefile)                                # download screen shot
        file_size = imagefile_to_dphfile(imagefile, imagename, dphfile)        # convert screen shot to dph

        print '    {:10} file size = {:>7d} bytes'.format(imagename, file_size)    # log

        remove(imagefile)                                                              # delete screen shot
except Exception:
    pass

print "{:40} {:6.3f} seconds".format('Screen shots taken (and parsed!) in', time() - SCREEN_SHOT_START)

# clean-up
close_drivers(drivers)
