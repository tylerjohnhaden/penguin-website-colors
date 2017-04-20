#! /usr/bin/python
# TODO: do doc string

import os
import time
import sys

from selenium.common.exceptions import TimeoutException

from penguin import Penguin
import lib.custom_tools as custom_tools

if __name__ == "__main__":
    penguin = Penguin(chrome_count=10)
    penguin.add_websites(1000, 1200)


    @penguin.driver
    def functionality(websites, chrome):
        try:
            sys.stdout.write('\r' + str(len(websites)))
            url, name = websites.pop(0)
            try:
                chrome.get(url)
            except TimeoutException:
                return True, (url, name)
            chrome.save_screenshot('.temp/' + name + '.png')
        except IndexError:
            return False, None
        return True, None


    @penguin.processor
    def this_name_literally_doesnt_matter():
        try:
            queue = os.listdir('.temp')
            for current_file in queue:
                input_path = '.temp/' + current_file
                input_name = current_file.rstrip('.png')
                output_path = 'data/' + input_name + '.dph'
                custom_tools.imagefile_to_dphfile(input_path, input_name, output_path)
                os.remove(input_path)
            size = len(queue)
            if size > 8:
                time.sleep(0.01)
            elif size > 4:
                time.sleep(.1)
            else:
                time.sleep(.3)
        except WindowsError:  # TODO: figure out linux equivalent
            return False, 0
        return True, size


    elapsed_time = penguin.run()
    print "Finished in %s seconds" % elapsed_time
    penguin.save_timeouts()
