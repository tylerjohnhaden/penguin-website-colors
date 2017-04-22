#! /usr/bin/python
# TODO: do doc string

import os
import time
import sys

from selenium.common.exceptions import TimeoutException

import penguin

if __name__ == "__main__":
    # instantiate new Penguin object, this should take <1 second because there is no chrome initialization yet
    P = penguin.Penguin(chrome_count=2)

    # load websites from csv, by default uses latest available file
    P.add_websites(0, 3)

    P.headless()         # DEFAULT
    # penguin.headless(False)  #    -     display browser in view
    P.ublock()           # DEFAULT
    # penguin.ublock(False)    #    -     don't use ublock0
    P.timeout(30)        # DEFAULT

    # Decorator, used to define what the driver thread does, must take in the website list and driver object, must
    # return whether to keep running and if the url timed out
    @P.driver
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

    # defines what the processing thread does, must return whether to keep going and length of files found in .temp
    @P.processor
    def this_name_literally_doesnt_matter():
        try:
            queue = os.listdir('.temp')
            for current_file in queue:
                input_path = '.temp/' + current_file
                input_name = current_file.rstrip('.png')
                output_path = 'data/' + input_name + '.dph'
                penguin.imagefile_to_dphfile(input_path, input_name, output_path)
                os.remove(input_path)
            size = len(queue)
            if size > 8:
                pass
            elif size > 4:
                time.sleep(.1)
            else:
                time.sleep(.6)
        except OSError:  # TODO: figure out linux equivalent
            return False, 0
        return True, size

    print "Starting"
    elapsed_time = P.run()
    print "\nFinished in %.2f seconds" % elapsed_time
    print "Maximum processing queue length =", P.max_queue_length
    P.save_timeouts()
