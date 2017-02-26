from custom_tools import get_sites, load_drivers

CHROMEDRIVER_PATH = 'C:/Users/JuliusCeasar/Desktop/chromedriver_test_spike/chromedriver.exe'
UBLOCK_EXTENSION_PATH = 'C:/Users/JuliusCeasar/Desktop/chromedriver_test_spike/uBlock0.chromium'
NUMBER_OF_DRIVERS = 10

websites = get_sites(0, 9)
drivers = load_drivers(NUMBER_OF_DRIVERS, CHROMEDRIVER_PATH, UBLOCK_EXTENSION_PATH)

try:
    for i in xrange(NUMBER_OF_DRIVERS):
        drivers[i].get(websites[i])
        drivers[i].save_screenshot('temp/' + str(i) + '_img.png')
except Exception:
    pass

for d in drivers:
    d.quit()
