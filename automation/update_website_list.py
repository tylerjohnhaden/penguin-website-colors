"""Script for updating the list of top websites
    Downloads, unzips, and writes unique urls to date-stamped file.
    
    e.g. 
    line from download = '10,google.co.uk'
    ->
    overlap key = 'google'
    line in new list = 'google.co.uk'
"""

from urllib import urlretrieve
from zipfile import ZipFile
from datetime import datetime
from time import time
from os import system

url = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'
current_date = datetime.now()
new_file = '../static/top_sites_scrubbed_%s_%s_%s.csv' % (current_date.month, current_date.day, current_date.year)
overlap_protection = {}

# retrieve zip file and load into ZipFile object
START = time()
with ZipFile(urlretrieve(url)[0], 'r') as zip_object:
    print 'Downloaded file from %s in %.3f seconds' % (url, time() - START)

    START = time()
    with zip_object.open(zip_object.namelist()[0]) as pre_scrubbed_list:
        with open(new_file, 'w') as file_out:
            for old_count, line in enumerate(pre_scrubbed_list):
                # '10,google.co.uk\n' -> 'google.co.uk', 'google'
                full_address = line.strip().split(',')[1]
                base_domain = full_address.split('.')[0]
                # check if base domain is already recorded
                if base_domain not in overlap_protection:
                    overlap_protection[base_domain] = 0
                    file_out.write(full_address + '\n')

new_count = len(overlap_protection)
reduction = 100.0 * (1.0 - (1.0 * new_count / old_count))
print 'Condensed %d urls into %d in %.3f seconds (%.3f%% reduction)' % (old_count, new_count, time() - START, reduction)

# add new file to git repo
system('git add %s' % new_file)
