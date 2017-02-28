# TODO: BeautifulSoup handlers
# TODO: Thread objects for drivers, parsers, file manipulation
# TODO: Add logging functionality
# TODO: Missed site handlers

COMPRESSED_COLOR_SPACE = 262144  # 64 ** 3
PROTOCOL_PREFIX = 'http://'
CONFIG_PATH = 'config/config.ini'


def load_sites(a, b, url_list_path, filename_regex):
    from re import match

    site_list = []
    with open(url_list_path, 'r') as f:
        for i, l in enumerate(f):
            if a <= i <= b:
                site_list.append(PROTOCOL_PREFIX + match(filename_regex, l).group('domain'))
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
        d = Chrome(executable_path=chromedriver_path, chrome_options=options)
        d.maximize_window()
        d.set_window_position(1300, 0)
        drivers += [d]

    return drivers


def close_drivers(driver_list):
    for driver in driver_list:
        driver.quit()


def load_config():
    from ConfigParser import ConfigParser
    from os import getcwd
    config = ConfigParser()
    try:
        with open(CONFIG_PATH) as cf:
            config.readfp(cf)
            return dict(config.items("chrome")), dict(config.items("urls")), dict(config.items("adj")), dict(
                config.items("dph"))
    except IOError:
        raise NoConfigFileError(getcwd())


# TODO: create "InvalidFileHeaderFormat" Exception
# TODO: correctly calculate number of nodes

class FileHeaderValueError(Exception):
    """Raise for file header values that do not match what is found in the file"""

    def __init__(self, image, key, expected, actual, *args):
        self.message = "File \'" + image + "\', header value \"" + str(key) + "\":    <expected: " + str(
            expected) + ", actual: " + str(
            actual) + ">"
        super(FileHeaderValueError, self).__init__(self.message, *args)


class NoConfigFileError(Exception):
    """Raise when no config file is found"""

    def __init__(self, path, *args):
        self.message = "No config/config.ini file found in the directory : \"" + path + "\""
        super(NoConfigFileError, self).__init__(self.message, *args)


def convert_adjacency_to_dph(filename_tuple):
    header, adj_list = parse_adjacency_file(filename_tuple[0], filename_tuple[1])
    sorted_pair_list = convert_adjlist_to_pairlist(header, adj_list)
    difference_compressed_pair_list = difference_compression(sorted_pair_list)
    write_pair_list_hex(filename_tuple[2], header, difference_compressed_pair_list)


# TODO: add header value catch statements
def convert_dph_to_adjacency(filename_tuple):
    header, diff_pair_hex_list = parse_dph_file(filename_tuple[0], filename_tuple[1])
    difference_decompressed_pair_list = difference_decompression(diff_pair_hex_list)
    adj_list = convert_pairlist_to_adjlist(header, difference_decompressed_pair_list)
    write_adj_list(filename_tuple[2], header, adj_list)


def write_adj_list(filename, head, adj_list):
    with open(filename, "w") as adj_file:
        adj_file.write(str(head) + "\n")
        for neighbors in adj_list:
            adj_file.write(str(neighbors) + "\n")


def write_pair_list_hex(filename, head, pair_list):
    delimiter = "."
    head["delimiter"] = delimiter
    with open(filename, "w") as dph_file:
        dph_file.write(str(head) + "\n")
        for tuple in pair_list:
            dph_file.write(hex_blanking_format(tuple, delimiter) + "\n")


def hex_blanking_format(t, d):
    s = ""
    if t[0] == 0:
        s += d
    else:
        s += str(hex(t[0])) + d
    if t[1] == 0:
        s += d
    else:
        s += str(hex(t[1])) + d
    if t[2] != 1:
        s += str(hex(t[2]))
    return s.replace("0x", "")


def difference_compression(pair_list):
    last_a = last_b = 0
    for i in xrange(len(pair_list)):
        temp = pair_list[i]
        pair_list[i] = (temp[0] - last_a, temp[1] - last_b, temp[2])
        last_a = temp[0]
        last_b = temp[1]
    return pair_list


def difference_decompression(pair_list):
    last_a = last_b = 0
    for i in xrange(len(pair_list)):
        temp = pair_list[i]
        pair_list[i] = (temp[0] + last_a, temp[1] + last_b, temp[2])
        last_a += temp[0]
        last_b += temp[1]
    return pair_list


# TODO: error checking with header
def convert_pairlist_to_adjlist(head, pair_list):
    adjacency_list = [[] for _ in xrange(COMPRESSED_COLOR_SPACE)]
    for edge in pair_list:
        adjacency_list[edge[0]] += [(edge[1], edge[2])]
    return adjacency_list


# TODO: check for total weight head["total_weight"]
def convert_adjlist_to_pairlist(head, alist):
    if len(alist) != head["nodes"]:
        pass  # raise FileHeaderValueError(head["image"], "nodes", head["nodes"], len(alist))
    raw_pair_list = []
    for a in xrange(len(alist)):
        for tuple in alist[a]:
            edge_pair = sorted([a, tuple[0]])
            raw_pair_list += [(edge_pair[0], edge_pair[1], tuple[1])]
    if len(raw_pair_list) != head["edges"]:
        pass  # raise FileHeaderValueError(head["image"], "edges", head["edges"], len(raw_pair_list))
    return sorted(raw_pair_list)


def parse_adjacency_file(imagename, filename):
    from ast import literal_eval
    with open(filename, "r") as adj_file:
        header_line = adj_file.readline().replace("\n", "")
        header_dictionary = literal_eval(header_line)
        if header_dictionary["image"] != imagename:
            raise FileHeaderValueError(imagename, "image", imagename, header_dictionary["image"])
        adjacency_list = []
        for i, l in enumerate(adj_file):
            adjacency_list += [literal_eval(l.replace("\n", ""))]
        return header_dictionary, adjacency_list


def parse_dph_file(imagename, filename):
    from ast import literal_eval
    with open(filename, "r") as dph_file:
        header_line = dph_file.readline().replace("\n", "")
        header_dictionary = literal_eval(header_line)
        if header_dictionary["image"] != imagename:
            raise FileHeaderValueError(imagename, "image", imagename, header_dictionary["image"])
        dph_list = []
        for i, l in enumerate(dph_file):
            split_line = l.replace("\n", "").split(header_dictionary["delimiter"])
            a = b = 0
            c = 1
            if split_line[0] != "":
                a = int(split_line[0], 16)
            if split_line[1] != "":
                b = int(split_line[1], 16)
            if split_line[2] != "":
                c = int(split_line[2], 16)
            dph_list += [(a, b, c)]
        return header_dictionary, dph_list
