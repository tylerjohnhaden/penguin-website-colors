from custom_tools import load_sites, load_drivers, load_config, close_drivers

# initialization
number_of_drivers = 10
chrome, regex, templates = load_config()
websites = load_sites(0, 9)
drivers = load_drivers(number_of_drivers, chrome['driver_path'], chrome['ublock_path'])

# run code
try:
    for i in xrange(number_of_drivers):
        drivers[i].get(websites[i])
        drivers[i].save_screenshot('temp/' + str(i) + '_img.png')
except Exception:
    pass

# clean-up
close_drivers(drivers)
