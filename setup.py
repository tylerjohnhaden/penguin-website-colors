#! /usr/bin/python

# TODO: make chromedriver executable on linux systems
# TODO: finish this doc string:
"""The first script to be run in this project.

If this is the first time running in this directory,
it should look something like this:

    penguin-website-colors/
        examples/
            ...
        .gitignore
        __init__.py
        license.txt
        penguin.py
        README.md
        setup.py

In this case, the setup tool will build the necessary
project structure. At each step, if the directory entity
is already found, it will be skipped.
"""

import argparse
import platform
import sys
import os
import urllib
import time
from zipfile import ZipFile

parser = argparse.ArgumentParser()
parser.add_argument('--check-system', help='Validates system for dependency compatibility', action="store_true")
parser.add_argument('--no-chromedriver', help='Skips local chromedriver installation', action="store_true")
parser.add_argument('--no-uBlock0', help='Skips local uBlock0 installation', action="store_true")
parser.add_argument('--no-websites', help='Skips local website list installation', action="store_true")
args = parser.parse_args()

STATIC_RESOURCES = {'chromedriver': {'latest': 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE',
                                     'zip': 'https://chromedriver.storage.googleapis.com/%s/chromedriver_%s.zip'},
                    'uBlock0': {'latest': 'https://github.com/gorhill/uBlock/releases/latest',
                                'zip': 'https://github.com/gorhill/uBlock/releases/download/%s/uBlock0.chromium.zip'},
                    'websites': {'zip': 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'}}


def update_static_resources(operating_system, exclusions=None):
    """Resource handler, builds missing directories and calls respective resource update functions.
    
    Default behavior is to look for and create missing folders:
    
        ./static
            /chromedriver
            /uBlock0
            /websites
    
    Serial calls to update functions for each resource in 'STATIC_RESOURCES'. Calls are hard-coded.
    
    Args:
        operating_system (str): System and architecture necessary to download Chromedriver.
            Without Chromedriver, this whole project is non-functional so there is no point in downloading
            any other resources without a supported os.
            
        exclusions (iterable, optional): Any keys in 'STATIC_RESOURCES' that should be ignored when updating.
            Defaults to None. Although 'STATIC_RESOURCES' is hard-coded, 'exclusions' is not checked for 
            extraneous input.
    """
    global STATIC_RESOURCES

    if exclusions is None:
        exclusions = []

    # create static directory if not present
    if not os.path.exists('static'):
        os.makedirs('static')

    # create separate directories for each non-excluded resource
    for resource in STATIC_RESOURCES.keys():
        if resource not in exclusions and not os.path.exists('static/%s' % resource):
            os.makedirs('static/%s' % resource)

    if 'chromedriver' not in exclusions:
        update_chromedriver(operating_system)

    if 'uBlock0' not in exclusions:
        update_uBlock0()

    if 'websites' not in exclusions:
        update_websites()


def update_chromedriver(formatted_os):
    """Chromedriver version control and download handler.
    
    Looks in 'static/chromedriver' for currently installed versions. Looks at Google's api for latest release.
    If the last local version, ordered by version number in ascending order, matches the latest release, do nothing.
    Otherwise, download zip from Google, unzip and place into new version directory 'static/chromedriver/version_%s'.
    
    Will throw UserWarning if one of the file names in the zip folder contains either '/' at the beginning, or '..'
    anywhere as this allows for path manipulation and is most likely a sign of a malicious payload.
    
    Args:
        formatted_os (str): Correctly formatted system + architecture. Can be inserted straight into zip url.
    """
    global STATIC_RESOURCES

    print '\nUPDATING CHROMEDRIVER ...'

    # list locally available versions
    installed_versions = os.listdir('static/chromedriver')
    print '\n    Currently Installed Versions:'
    if len(installed_versions) == 0:
        print '    - (none)'
    else:
        for version in installed_versions[:-1]:
            print '    - %s' % version
        print '    - %s (newest)' % installed_versions[-1]

    # fetch latest release number from google
    content, header = urllib.urlretrieve(STATIC_RESOURCES['chromedriver']['latest'])
    with open(content, 'r') as release_file:
        latest_release = release_file.readline().strip()
    print '\n    Latest Release Version:\n    - version_%s' % latest_release

    if len(installed_versions) != 0 and 'version_%s' % latest_release == installed_versions[-1]:
        print '\n    Latest chromedriver is already installed.'
    else:
        start = time.time()

        version_directory = 'static/chromedriver/version_%s' % latest_release
        zip_url = STATIC_RESOURCES['chromedriver']['zip'] % (latest_release, formatted_os)
        print '\n    Downloading newest release from %s' % zip_url

        # retrieve zip file and load into ZipFile object
        content, header = urllib.urlretrieve(zip_url)
        with ZipFile(content, 'r') as zip_object:
            if any(f.startswith('/') or '..' in f for f in zip_object.namelist()):
                raise UserWarning('MALICIOUS DOWNLOAD DETECTED: %s\n    contains suspicious path manipulation!\n%s' %
                                  (zip_url, '\n    -> '.join(zip_object.namelist())))

            # create new directory for the latest version
            os.makedirs(version_directory)

            # extract into new directory
            zip_object.extract(zip_object.namelist()[0], version_directory)
        print '    Chromedriver downloaded and unzipped in %.2f seconds' % (time.time() - start)


def update_uBlock0():
    """uBlock Origin version control and download handler.
    
    Looks in 'static/uBlock0' for currently installed versions. Looks at Gitbub's api for latest release.
    If the last local version, ordered by version number in ascending order, matches the latest release, do nothing.
    Otherwise, download zip from Github, unzip and place into new version directory 'static/uBlock0/version_%s'.
    
    Will throw UserWarning if one of the file names in the zip folder contains either '/' at the beginning, or '..'
    anywhere as this allows for path manipulation and is most likely a sign of a malicious payload.
    """
    global STATIC_RESOURCES

    print '\nUPDATING UBLOCK ORIGIN ...'

    # list locally available versions
    installed_versions = os.listdir('static/uBlock0')
    print '\n    Currently Installed Versions:'
    if len(installed_versions) == 0:
        print '    - (none)'
    else:
        for version in installed_versions[:-1]:
            print '    - %s' % version
        print '    - %s (newest)' % installed_versions[-1]

    # fetch latest release number from Github
    latest_redirect = urllib.urlopen(STATIC_RESOURCES['uBlock0']['latest']).geturl()  # Github api redirects to latest
    latest_release = latest_redirect.split('/')[-1]
    print '\n    Latest Release Version:\n    - version_%s' % latest_release

    if len(installed_versions) != 0 and 'version_%s' % latest_release == installed_versions[-1]:
        print '\n    Latest uBlock0 is already installed.'
    else:
        start = time.time()

        version_directory = 'static/uBlock0/version_%s' % latest_release
        zip_url = STATIC_RESOURCES['uBlock0']['zip'] % latest_release
        print '\n    Downloading newest release from %s' % zip_url

        # retrieve zip file and load into ZipFile object
        content, header = urllib.urlretrieve(zip_url)
        with ZipFile(content, 'r') as zip_object:
            if any(f.startswith('/') or '..' in f for f in zip_object.namelist()):
                raise UserWarning('MALICIOUS DOWNLOAD DETECTED: %s\n    contains suspicious path manipulation!\n%s' %
                                  (zip_url, '\n    -> '.join(zip_object.namelist())))

            # create new directory for the latest version
            os.makedirs(version_directory)

            # extract into new directory
            for f in zip_object.namelist():
                zip_object.extract(f, version_directory)
        print '    uBlock0 downloaded and unzipped in %.2f seconds' % (time.time() - start)


def update_websites():
    """Alexa Top Million Websites version control and download handler.

        Looks in 'static/websites' for currently installed versions. Looks at Alexa's api for latest release.
        If the last local version, ordered by version number in ascending order, matches the latest release, do nothing.
        Otherwise, download zip from Alexa, unzip and place into new version directory 'static/websites/version_%s'.

        Will throw UserWarning if one of the file names in the zip folder contains either '/' at the beginning, or '..'
        anywhere as this allows for path manipulation and is most likely a sign of a malicious payload.
        """
    global STATIC_RESOURCES

    print '\nUPDATING WEBSITES ...'

    # list locally available versions
    installed_versions = os.listdir('static/websites')
    print '\n    Currently Installed Versions:'
    if len(installed_versions) == 0:
        print '    - (none)'
    else:
        for version in installed_versions[:-1]:
            print '    - %s' % version
        print '    - %s (newest)' % installed_versions[-1]

    # latest version is today's date
    latest_release = time.strftime('%d.%m.%Y')
    print '\n    Latest Release Version:\n    - version_%s' % latest_release

    if len(installed_versions) != 0 and 'version_%s' % latest_release == installed_versions[-1]:
        print '\n    Latest website list is already installed.'
    else:
        start = time.time()

        version_directory = 'static/websites/version_%s' % latest_release
        new_csv_path = version_directory + '/websites.csv'
        zip_url = STATIC_RESOURCES['websites']['zip']
        print '\n    Downloading newest release from %s' % zip_url

        # retrieve zip file and load into ZipFile object
        content, header = urllib.urlretrieve(zip_url)
        with ZipFile(content, 'r') as zip_object:
            if any(f.startswith('/') or '..' in f for f in zip_object.namelist()):
                raise UserWarning('MALICIOUS DOWNLOAD DETECTED: %s\n    contains suspicious path manipulation!\n%s' %
                                  (zip_url, '\n    -> '.join(zip_object.namelist())))

            # create new directory for the latest version
            os.makedirs(version_directory)

            with zip_object.open(zip_object.namelist()[0]) as pre_scrubbed_list:
                with open(new_csv_path, 'w') as scrubbed_list_as_csv:
                    # use a dictionary to check overlapping domains
                    collision_dictionary = dict()

                    for pre_scrubbed_count, line in enumerate(pre_scrubbed_list):
                        # '10,google.co.uk\n' -> 'google.co.uk', 'google'
                        full_address = line.strip().split(',')[1]
                        base_domain = full_address.split('.')[0]

                        # check if base domain is already recorded
                        if base_domain not in collision_dictionary:
                            collision_dictionary[base_domain] = 0
                            scrubbed_list_as_csv.write(full_address + '\n')
        scrubbed_count = len(collision_dictionary)
        reduction = 100.0 * (1.0 - (1.0 * scrubbed_count / pre_scrubbed_count))
        print '    Websites downloaded and unzipped in %.2f seconds' % (time.time() - start)
        print '    Condensed %d urls into %d (%.3f%% reduction)' % (pre_scrubbed_count, scrubbed_count, reduction)


def check_os():
    """Detect system and architecture of local system.
    
    Chromedriver runs platform specific, download urls look like:
    
        '... /2.29/chromedriver_win32.zip'
        '... /2.29/chromedriver_mac32.zip'
        '... /2.29/chromedriver_linux32.zip'
        '... /2.29/chromedriver_linux64.zip'
    
    Returns:
        tuple (bool, str, str): The first element is if the detected system and architecture is valid.
            The second is the properly formatted system and architecture for Chromedriver download url.
            The third is a 'user-friendly' representation of the system.
    """
    operating_system = sys.platform

    if operating_system.startswith('linux'):
        # get system architecture, necessary only if linux
        architecture = platform.architecture()[0].rstrip('bit')
        return True, 'linux%s' % architecture, 'Linux'
    elif operating_system == 'win32':
        return True, 'win32', 'Windows'
    elif operating_system == 'darwin':
        return True, 'mac32', 'MacOS'
    else:
        return False, '', operating_system


if __name__ == "__main__":
    if args.check_system:
        valid, url_format, detected_system = check_os()
        if valid:
            print 'VALID: Detected operating system \'%s\' is supported.' % detected_system
        else:
            print 'INVALID: Detected operating system \'%s\' is not supported.' % detected_system
    else:
        if args.no_chromedriver and args.no_uBlock0 and args.no_websites:
            import this
            quit()

        exclusions = []
        if args.no_chromedriver:
            exclusions.append('chromedriver')
        if args.no_uBlock0:
            exclusions.append('uBlock0')
        if args.no_websites:
            exclusions.append('websites')

        print 'Running Setup\nExclusions = %s\n%s\n' % (str(exclusions), '*' * 50)
        valid, url_format, detected_system = check_os()
        if valid:
            print 'Detected operating system \'%s\' is supported.' % detected_system
            update_static_resources(url_format, exclusions)
