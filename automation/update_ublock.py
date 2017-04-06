"""Script for updating the local uBlock Origin resource
    Uses github's api to get latest release url,
    and downloads zip for chrome.
    
    Warning: This downloads zipped content. If
    the download site ever gets compromised, 
    this download may be at risk.
"""

from urllib import urlopen, urlretrieve
from time import time
from zipfile import ZipFile

latest_url = 'https://github.com/gorhill/uBlock/releases/latest'
download_url_template = 'https://github.com/gorhill/uBlock/releases/download/%s/uBlock0.chromium.zip'
target_folder = '../static/'

START = time()
latest_release_base_url = urlopen(latest_url).geturl()
latest_version_number = latest_release_base_url.split('/')[-1]
print 'Latest release version number \'%s\' found in %.3f seconds' % (latest_version_number, time() - START)

download_url = download_url_template % latest_version_number
print 'download_url =', download_url

START = time()
with ZipFile(urlretrieve(download_url)[0], 'r') as zip_object:
    for f in zip_object.namelist():
        if '..' in f:
            print 'Malicious zip file detected! :', f
            break
        zip_object.extract(f, target_folder)

print 'uBlock Origin downloaded and unzipped in %.3f seconds' % (time() - START)
