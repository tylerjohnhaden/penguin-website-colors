#! /usr/bin/python
"""Simple example use of the penguin package."""

import logging
import os
import time

from selenium.common.exceptions import TimeoutException

import penguin

penguin.STATIC_RESOURCE_PATH = '../static'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler('simple_example.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

number_of_chrome_drivers = 3
number_of_websites = 3

if __name__ == "__main__":
    logger.info('')
    logger.info('Starting "simple_example" penguin client --->')
    logger.info('==========================================================')

    P = penguin.Penguin(chrome_count=number_of_chrome_drivers)
    logger.debug('Created new Penguin with {} chrome drivers'.format(number_of_chrome_drivers))

    # load websites from csv, by default uses latest available file
    P.add_websites(0, number_of_websites)
    logger.debug('Loaded {} websites'.format(number_of_websites))

    # Decorator, used to define what the driver thread does, must take in the website list and driver object, must
    # return whether to keep running and if the url timed out
    @P.driver
    def driver_functionality(websites, chrome, timeouts):
        try:
            url, name = websites.pop(0)
        except IndexError:
            # No more websites to load, False stops thread iteration
            logger.info('Chrome driving thread returned empty website list.. closing thread.')
            return False

        try:
            chrome.get(url)
        except TimeoutException:
            # Took too long to fetch website, save url and name in timeout
            timeouts.append((url, name))
            logger.warning('Timeout occurred for site (\'{}\',\'{}\'), appending to timeout list.'.format(url, name))
            return True

        chrome.save_screenshot('.temp/image/' + name + '.png')
        logger.debug('Chrome driving thread saved a screenshot for \'{}\'.'.format(name))
        # with open('.temp/source/' + name + '.html', 'w') as source_file:
        #     source_file.write(chrome.page_source.encode('utf-8'))

        return True


    # defines what the image processing thread does,
    # must return whether to keep going and length of files found in .temp
    @P.image_handler
    def image_handler_functionality():
        try:
            queue = os.listdir('.temp/image')
        except OSError:
            # .temp/image directory is gone, False stops thread iteration
            logger.info('Image handler thread returned empty image directory.. closing thread.')
            return False, 0

        for current_file in queue:
            input_path = '.temp/image/' + current_file
            input_name = current_file.rstrip('.png')
            output_path = 'data/' + input_name + '.dph'
            penguin.imagefile_to_dphfile(input_path, input_name, output_path)
            logger.debug('Image handler thread processed \'{}\' into \'{}\'.'.format(input_path, output_path))
            os.remove(input_path)

        time.sleep(.13)
        return True, len(queue)


    # @P.source_handler
    # def source_handler_functionality():
    #     try:
    #         queue = os.listdir('.temp/source')
    #     except OSError:
    #         # .temp/source directory is gone, False stops thread iteration
    #         return False
    #
    #     for current_file in queue:
    #         for __ in xrange(100000):
    #             try:
    #                 os.rename('.temp/source/' + current_file, 'data/' + current_file)
    #                 break
    #             except OSError:
    #                 try:
    #                     # If here, then os.rename might have tried to rename a file to an already existing path
    #                     os.remove('data/' + current_file)
    #                     # If this succeeds, then there was indeed a path in the way
    #                 except OSError:
    #                     # If here, then the problem is that the source file is still being writen to
    #                     time.sleep(.05)
    #
    #     time.sleep(.13)
    #     return True

    print "Starting"
    logger.info('Beginning client execution.')
    elapsed_time = P.run()
    logger.debug('Image handler thread finished with ' +
                 'a maximum processing queue length of {}.'.format(P.max_queue_length))
    logger.info('Finished client execution in {:.2f} seconds'.format(elapsed_time))
    print "\nFinished in %.2f seconds" % elapsed_time
    print "Maximum processing queue length =", P.max_queue_length
    P.save_timeouts()
