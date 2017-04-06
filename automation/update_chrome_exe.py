"""Script for updating the local Chrome Driver resourc
    First gets latest version from static url,
    checks if the latest release is already installed,
    and downloads zip for windows.

    Warning: This downloads zipped content. If
    the download site ever gets compromised, 
    this download may be at risk.
"""

from urllib import urlretrieve
from zipfile import ZipFile
from time import time
from os import listdir, rename

latest_release_url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
download_url_template = 'https://chromedriver.storage.googleapis.com/%s/chromedriver_win32.zip'
target_folder = '../static/'

current_versions = [f.rstrip('.exe').lstrip('chromedriver') for f in listdir('../static') if f.startswith('chrome')]
print 'Current installed versions:', current_versions

START = time()
content, header = urlretrieve(latest_release_url)
with open(content, 'r') as release_file:
    latest_version = release_file.readline().strip()
print 'Latest release version number \'%s\' found in %.3f seconds' % (latest_version, time() - START)

if latest_version not in current_versions:
    START = time()
    download_url = download_url_template % latest_version
    print 'download_url =', download_url
    # retrieve zip file and load into ZipFile object
    with ZipFile(urlretrieve(download_url)[0], 'r') as zip_object:
        # save unzipped file into static directory
        new_file = zip_object.extract(zip_object.namelist()[0], target_folder)
        rename(new_file, new_file.replace('.exe', '%s.exe' % latest_version))
    print 'Chrome Driver downloaded in %.3f seconds' % (time() - START)
else:
    print 'You already have the up-to-date version:', latest_version
