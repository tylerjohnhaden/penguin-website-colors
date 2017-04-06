from os import listdir, remove
from time import time

start = time()
count = 0
for f in listdir('../temp/'):
    if f.endswith('.png'):
        remove(f)
        count += 1
print "Removed {:d} files in {:8.5f} seconds".format(count, (time() - start))
