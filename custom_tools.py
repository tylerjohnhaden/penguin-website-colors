def get_sites(a, b):
    from re import match
    # change to file containing urls
    URL_LIST_PATH = 'C:/Users/JuliusCeasar/Desktop/chromedriver_test_spike/top-1m.csv'
    # change if format of url list changes
    FILENAME_REGEX = '^.*,(?P<domain>.*)\n$'

    site_list = []
    with open(URL_LIST_PATH, 'r') as f:
        for i, l in enumerate(f):
            if a <= i <= b:
                site_list.append('http://' + match(FILENAME_REGEX, l).group('domain'))
    return site_list


def load_drivers(n, chromedriver_path, *extension_args):
    from selenium.webdriver import Chrome
    options = None
    if len(extension_args) > 0:
        from selenium.webdriver.chrome.options import Options
        options = Options()
        for extension in extension_args:
            options.add_argument('load-extension=' + extension)

    drivers = []
    for i in xrange(n):
        drivers += [Chrome(executable_path=chromedriver_path, chrome_options=options)]
    return drivers
