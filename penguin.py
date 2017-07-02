# TODO: Internet connectivity speed benchmark
# TODO: Docs
import ast
import os
import shutil
import threading
import time

from PIL import Image
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

COMPRESSED_COLOR_SPACE = 262144  # 64 ** 3
STATIC_RESOURCE_PATH = 'static'


# TODO: PROCESSED_DATA_PATH = 'data'


class Penguin:
    # TODO: compute max run time based on timeout and website list, have display of estimated time of completion, etc.
    def __init__(self, chrome_count):
        self.drivers = [threading.Thread(target=self.driver_thread_function) for __ in xrange(chrome_count)]
        self.driver_functionality = None
        self.page_timeout = 30  # default 30 seconds
        self.is_headless = True  # default headless mode
        self.use_ublock = True  # default use ublock

        self.image_handler_thread = threading.Thread(target=self.image_handler_thread_function)
        self.image_handler_functionality = None
        self.max_queue_length = 0

        self.source_enabled = False
        self.source_handler_thread = threading.Thread(target=self.source_handler_thread_function)
        self.source_handler_functionality = None

        self.websites = []
        self.timeout_sites = []

    def image_handler(self, funct):
        def wrapper():
            return funct()

        self.image_handler_functionality = wrapper
        return None

    def image_handler_thread_function(self):
        if self.image_handler_functionality is None:
            raise NotImplementedError('Image Handler functionality must be defined, i.e. @Penguin.image_handler')

        try:
            for i in xrange(10000000):  # ten million
                state, queue_length = self.image_handler_functionality()
                self.max_queue_length = max(queue_length, self.max_queue_length)
                if state is False:
                    break
        finally:
            pass

    def source_handler(self, funct):
        def wrapper():
            return funct()

        self.source_handler_functionality = wrapper
        return None

    def source_handler_thread_function(self):
        if not self.source_enabled:
            raise ValueError('Source is not enabled for this client')

        if self.source_handler_functionality is None:
            raise NotImplementedError('Source Handler functionality must be defined, i.e. @Penguin.source_handler')

        try:
            for i in xrange(10000000):  # ten million
                state = self.source_handler_functionality()
                if state is False:
                    break
        finally:
            pass

    def driver(self, funct):
        def wrapper(websites, driver, timeouts):
            return funct(websites, driver, timeouts)

        self.driver_functionality = wrapper
        return None

    def load_driver(self):
        options = Options()
        if self.use_ublock:
            ublock0_path = get_path('uBlock0', target='uBlock0.chromium')
            options.add_argument('load-extension=' + ublock0_path)
        if self.headless:
            options.add_argument('window-size=1300,750')
            options.add_argument('window-position=2000,0')

        chromedriver_path = get_path('chromedriver', target='chromedriver.exe')
        driver = Chrome(executable_path=chromedriver_path, chrome_options=options)
        driver.set_page_load_timeout(self.page_timeout)
        return driver

    def driver_thread_function(self):
        if self.driver_functionality is None:
            raise NotImplementedError('Driver functionality must be defined, i.e. @Penguin.driver')

        driver = self.load_driver()

        try:
            for i in xrange(5000000):  # five million, gracefully exits after five million iterations
                continue_state = self.driver_functionality(self.websites, driver, self.timeout_sites)
                if continue_state is False:
                    break
        finally:
            driver.quit()

    def run(self):
        start = time.time()

        locked_source_enabled = self.source_enabled

        if not os.path.exists('.temp'):
            os.makedirs('.temp')
        if locked_source_enabled:
            if not os.path.exists('.temp/source'):
                os.makedirs('.temp/source')
        if not os.path.exists('.temp/image'):
            os.makedirs('.temp/image')
        if not os.path.exists('data'):
            os.makedirs('data')

        self.image_handler_thread.start()

        if locked_source_enabled:
            self.source_handler_thread.start()

        for t in self.drivers:
            t.start()
        for t in self.drivers:
            t.join()

        while len(os.listdir('.temp/image')) != 0:
            time.sleep(.1)
        shutil.rmtree('.temp/image')
        self.image_handler_thread.join()

        if locked_source_enabled:
            while len(os.listdir('.temp/source')) != 0:
                time.sleep(.1)
            shutil.rmtree('.temp/source')
            self.source_handler_thread.join()

        shutil.rmtree('.temp')

        return time.time() - start

    def ublock(self, use_ublock=True):
        self.use_ublock = use_ublock

    def headless(self, is_headless=True):
        self.is_headless = is_headless

    def timeout(self, seconds):
        self.page_timeout = seconds

    def source(self, enable=True):
        self.source_enabled = enable

    def save_timeouts(self):
        with open('data/timeouts.csv', 'a') as timeout_log:
            for line in self.timeout_sites:
                timeout_log.write(line[0] + ', ' + line[1] + '\n')

    def add_websites(self, start, end):
        self.websites.extend(load_sites(start, end))
        return self


def get_path(resource, target, version='LATEST'):
    try:
        os.listdir(STATIC_RESOURCE_PATH)
    except OSError:
        raise ValueError('\'%s\' is not a valid path to the static resources' % STATIC_RESOURCE_PATH)

    if resource not in os.listdir(STATIC_RESOURCE_PATH):
        raise ValueError('Specified resource not in the static directory')

    available_versions = os.listdir(STATIC_RESOURCE_PATH + '/' + resource)
    if len(available_versions) == 0:
        raise ValueError('No available resources found in the static/' + resource + ' directory')

    relative_path = os.getcwd().replace('\\', '/')

    if version == 'LATEST':
        return relative_path + '/' + STATIC_RESOURCE_PATH + '/' + resource + '/%s/%s' % (available_versions[-1], target)
    else:
        if 'version_%s' % version in available_versions:
            return relative_path + '/' + STATIC_RESOURCE_PATH + '/' + resource + '/version_%s/%s' % (version, target)
        else:
            raise ValueError('Specified version not found in the static/' + resource + ' directory')


def load_sites(a, b):
    website_path = get_path('websites', target='websites.csv')
    site_list = []
    with open(website_path, 'r') as f:
        for i, line in enumerate(f):
            if a <= i < b:
                full_domain = line.rstrip('\n')
                base_domain = full_domain.split('.')[0]

                site_list.append(('http://' + full_domain, base_domain))
            elif i >= b:
                break
    return site_list


def convert_adjacency_to_dph(adj_filename, imagename, dph_filename):
    header, adj_list = parse_adjacency_file(adj_filename, imagename)
    sorted_pair_list = convert_adjlist_to_pairlist(header, adj_list)
    difference_compressed_pair_list = difference_compression(sorted_pair_list)
    write_pair_list_hex(dph_filename, header, difference_compressed_pair_list)


# TODO: add header value catch statements
def convert_dph_to_adjacency(dph_filename, imagename, adj_filename):
    header, diff_pair_hex_list = parse_dph_file(dph_filename, imagename)
    difference_decompressed_pair_list = difference_decompression(diff_pair_hex_list)
    adj_list = convert_pairlist_to_adjlist(header, difference_decompressed_pair_list)
    write_adj_list(adj_filename, header, adj_list)


def write_adj_list(filename, head, adj_list):
    with open(filename, 'w') as adj_file:
        adj_file.write(str(head) + '\n')
        for neighbors in adj_list:
            adj_file.write(str(neighbors) + '\n')


def write_pair_list_hex(filename, head, pair_list):
    delimiter = '.'
    head['delimiter'] = delimiter
    with open(filename, 'w') as dph_file:
        dph_file.write(str(head) + '\n')
        for tuple in pair_list:
            dph_file.write(hex_blanking_format(tuple, delimiter) + '\n')


def hex_blanking_format(t, d):
    s = ''
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
    return s.replace('0x', '')


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


def color_compression(pixel):
    red = pixel[0]
    green = pixel[1]
    blue = pixel[2]
    int_rep_color = ((red / 4) * (64 ** 2)) + ((green / 4) * 64) + (blue / 4)

    return int_rep_color


def color_decompression(int_rep_color):
    blue = (int_rep_color % 64) * 4
    green = ((int_rep_color / 64) % 64) * 4
    red = (int_rep_color / (64 ** 2)) * 4

    return red, green, blue


# TODO: error checking with header
def convert_pairlist_to_adjlist(head, pair_list):
    adjacency_list = [[] for __ in xrange(COMPRESSED_COLOR_SPACE)]
    for edge in pair_list:
        adjacency_list[edge[0]] += [(edge[1], edge[2])]
    return adjacency_list


# TODO: check for total weight head['total_weight']
def convert_adjlist_to_pairlist(head, alist):
    raw_pair_list = []
    for a in xrange(len(alist)):
        for tuple in alist[a]:
            edge_pair = sorted([a, tuple[0]])
            raw_pair_list += [(edge_pair[0], edge_pair[1], tuple[1])]
    if len(raw_pair_list) != head['edges']:
        pass  # raise FileHeaderValueError(head['image'], 'edges', head['edges'], len(raw_pair_list))
    return sorted(raw_pair_list)


def parse_adjacency_file(imagename, filename):
    with open(filename, 'r') as adj_file:
        header_line = adj_file.readline().replace('\n', '')
        header_dictionary = ast.literal_eval(header_line)
        if header_dictionary['image'] != imagename:
            pass  # TODO: fix -> raise ValueError(imagename, 'image', imagename, header_dictionary['image'])
        adjacency_list = []
        for i, l in enumerate(adj_file):
            adjacency_list += [ast.literal_eval(l.replace('\n', ''))]
        return header_dictionary, adjacency_list


def parse_dph_file(imagename, filename):
    with open(filename, 'r') as dph_file:
        header_line = dph_file.readline().replace('\n', '')
        header_dictionary = ast.literal_eval(header_line)
        if header_dictionary['image'] != imagename:
            pass  # TODO: fix -> raise ValueError(imagename, 'image', imagename, header_dictionary['image'])
        dph_list = []
        for i, l in enumerate(dph_file):
            split_line = l.replace('\n', '').split(header_dictionary['delimiter'])
            a = b = 0
            c = 1
            if split_line[0] != '':
                a = int(split_line[0], 16)
            if split_line[1] != '':
                b = int(split_line[1], 16)
            if split_line[2] != '':
                c = int(split_line[2], 16)
            dph_list += [(a, b, c)]
        return header_dictionary, dph_list


def add_color_edge(a_list, a, b):
    x, y = sorted([a, b])
    for neighbor in a_list[x]:
        if neighbor[0] == y:
            neighbor[1] += 1
            return  # this caused an error in original code (must be inside if statement, not after)
    else:
        a_list[x].append([y, 1])


# returns size of dph file
def imagefile_to_dphfile(image_filename, imagename, dph_filename):
    adjacency_list = [[] for __ in xrange(COMPRESSED_COLOR_SPACE)]
    list1 = []
    list2 = []
    weight_count = 0

    im = Image.open(image_filename).convert('RGB')
    pixel = im.load()
    width, height = im.size
    im.close()

    for y in xrange(0, height + 1, 10):
        for x in xrange(0, width + 1, 10):
            # print x, y
            rgb_pixel = pixel[x, y]
            cur_x = x / 10
            cur_y = y / 10
            list1.append(color_compression(rgb_pixel))
            if cur_x != 0:
                add_color_edge(adjacency_list, list1[cur_x], list1[cur_x - 1])
                weight_count += 1
            if cur_y != 0:
                add_color_edge(adjacency_list, list1[cur_x], list2[cur_x])
                weight_count += 1
        list2 = list(list1)
        list1 = []

    edge_count = 0
    for neighbor_list in adjacency_list:
        edge_count += len(neighbor_list)

    header = {'delimiter': '.', 'image': imagename, 'edges': edge_count, 'total_weight': weight_count}
    sorted_pair_list = convert_adjlist_to_pairlist(header, adjacency_list)
    difference_compressed_pair_list = difference_compression(sorted_pair_list)
    write_pair_list_hex(dph_filename, header, difference_compressed_pair_list)
