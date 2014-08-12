#!/usr/bin/env/ python
'''
Scrapes URLs, checks and downloads all packages and patches
required to build Linux From Scratch. Works with Python 2.7.3.

Copyright (C) 2014 Steffen Sauler

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''

#TODO: Catch keyboard interrupt

import urllib2
import re

#Links to Linux From Scratch's required packages & patches
lfs = 'http://www.linuxfromscratch.org/lfs/view/stable/chapter03/packages.html'
ptch = 'http://www.linuxfromscratch.org/lfs/view/stable/chapter03/patches.html'


def test_if_lfs_exists(lfs_url):
    '''Can we reach the LFS page to scrape the packages?'''
    lfs_type = lfs_url.split('/')[-1][:-5]
    try:
        exist = urllib2.urlopen(lfs_url).read()
        return 1
    except urllib2.URLError:
        print("LFS URL to %s not available." % lfs_type)
    
def get_package_urls(url):
    '''Returns a list of package & patch URLs from LSF website'''

    packages = urllib2.urlopen(url).read()
    
    #The following regular expression finds the download-URLs.
    #If this script fails, it's most likely a layout-change on the LFS website.
    regex = 'Download: <a class=\"ulink\" href=\s+"(.*?)">'
    result = re.findall(regex, packages)
    return result

def test_if_available(url):
    '''Testing URLS before download. If some packages are missing, this
       has to be clearly pointed out.'''
    
    package_name = url.split('/')[-1]
    try:
        open_url = urllib2.urlopen(url)
        print("Package %s: available" % package_name)
        return True
    except urllib2.HTTPError, http_err:
        if http_err.code == 404:
            errorstring = "Package %s: HTTP Error 404, not found at this URL."
            print(errorstring % package_name)
            return False
        else:
            errorstring = "Package %s: HTTPError %s, %s"
            print(errorstring % (package_name, http_err.code, http_err.reason))
            return False
    except urllib2.URLError, url_err:
        errorstring = "Package %s: Error %s"
        print(errorstring % (package_name, url_err.reason))
        return False

def download_package(url):
    '''partly from PabloG and Bjoern Pollex at:
    http://stackoverflow.com/a/22776/286994'''
    
    package_name = url.split('/')[-1]
    open_url = urllib2.urlopen(url)
    filehandle = open(package_name, 'wb')
    file_size = int(open_url.info()["Content-Length"])
    
    print("Downloading: %s (%d Bytes)" % (package_name, file_size))
    
    file_size_dl = 0
    #Default block size for Unix filesystems: 8192
    block_sz = 8*1024
    
    while True:
        buffer = open_url.read(block_sz)
        if not buffer:
            break
            
        file_size_dl += len(buffer)
        filehandle.write(buffer)
        stat_string = r"%10d  [%3.1f%%]"
        percentage = float(file_size_dl * 100) / file_size
        status = stat_string % (file_size_dl, percentage)
        status = status + chr(8)*(len(status)+1)
        sys.stdout.write(status)
    filehandle.close()
    
def iterate(lfs_url):
    #Which URL are we processing? Packages or patches?
    lfs_type = lfs_url.split('/')[-1][:-5]
    packages = get_package_urls(lfs_url)
    
    tested = []
    not_working = []
    
    #Is the d/l URL valid?
    for url in packages:
        working = test_if_available(url)
        if working == True:
            tested.append(url)
        else:
            not_working.append(url)
    
    no_of_packs = len(packages)
    no_available = len(tested)
    
    #How many packages are available? E.g. 62/62
    avail_string = "\nThere are %d of %d %s available."
    print(avail_string % (no_available, no_of_packs, lfs_type))
    
    #Giving details on packages missing
    for url in not_working:
        package_name = url.split('/')[-1]
        package_string = "The %s %s at %s is unavailable!"
        print(package_string % (lfs_type[:-1], package_name, url))

    cont = raw_input("Do you wish to continue? (y/n) \n")
    
    if cont == 'y':
        for url in tested:
            download_package(url)
            
def download_test():
    '''Testing d/l function without having to check URLs first'''
    pass
    
def main():
    
    if test_if_lfs_exists(lfs) == 1:
        iterate(lfs)                 # Checking and downloading packages
    if test_if_lfs_exists(ptch) == 1:
        iterate(ptch)                # -"- patches
    
if __name__ == '__main__':
    main()
