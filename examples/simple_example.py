#! /usr/bin/python
"""Simple example use of the penguin package."""

import os
import time

from selenium.common.exceptions import TimeoutException

import penguin

penguin.STATIC_RESOURCE_PATH = '../static'

if __name__ == "__main__":
    P = penguin.Penguin(chrome_count=2)

    # load websites from csv, by default uses latest available file
    P.add_websites(0, 3)

    # Decorator, used to define what the driver thread does, must take in the website list and driver object, must
    # return whether to keep running and if the url timed out
    @P.driver
    def driver_functionality(websites, chrome, timeouts):
        # TODO: add logging
        try:
            url, name = websites.pop(0)
        except IndexError:
            # No more websites to load, False stops thread iteration
            return False

        try:
            chrome.get(url)
        except TimeoutException:
            # Took too long to fetch website, save url and name in timeout
            timeouts.append((url, name))
            return True

        chrome.save_screenshot('.temp/' + name + '.png')
        return True


    # defines what the processing thread does, must return whether to keep going and length of files found in .temp
    @P.processor
    def processor_functionality():
        try:
            queue = os.listdir('.temp')
        except OSError:
            # .temp directory is gone, False stops thread iteration
            return False, 0

        for current_file in queue:
            input_path = '.temp/' + current_file
            input_name = current_file.rstrip('.png')
            output_path = 'data/' + input_name + '.dph'
            penguin.imagefile_to_dphfile(input_path, input_name, output_path)
            os.remove(input_path)
        time.sleep(.1)
        return True, len(queue)


    print "Starting"
    elapsed_time = P.run()
    print "\nFinished in %.2f seconds" % elapsed_time
    print "Maximum processing queue length =", P.max_queue_length
    P.save_timeouts()
