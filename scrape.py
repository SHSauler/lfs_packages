#!/usr/bin/env/ python
'''
Scrapes URLs, checks and downloads all packages required to build 
Linux From Scratch. Written for Python 2.7.3 in August 2014.

If this script should fail due to layout changes on the LFS website,
check the LFS URL (lfs) and the regular expression search (regex).
'''
import urllib2
import re

#Link to Linux From Scratch's required packages page
lfs = 'http://www.linuxfromscratch.org/lfs/view/stable/chapter03/packages.html'

def get_package_urls():
    '''Returns a list of package URLs from LSF website'''

    packages = urllib2.urlopen(lfs).read()
    
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
    http://stackoverflow.com/questions/22676\
    /how-do-i-download-a-file-over-http-using-python'''
    
    package_name = url.split('/')[-1]
    open_url = urllib2.urlopen(url)
    filehandle = open(package_name, 'wb')
    meta = open_url.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    
    print("Downloading: %s %s Bytes" % (package_name, file_size))
    
    file_size_dl = 0
    #Default block size for Unix filesystems
    block_sz = 8192
    
    while True:
        buffer = open_url.read(block_sz)
        if not buffer:
            break
            
        file_size_dl += len(buffer)
        filehandle.write(buffer)
        stat_string = r"%10d  [%3.2f%%]"
        status = stat_string % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,
    filehandle.close()
    
def main():
    packages = get_package_urls()
    tested = []
    not_working = []
    for url in packages:
        working = test_if_available(url)
        if working == True:
            tested.append(url)
        else:
            not_working.append(url)
    
    no_of_packs = len(packages)
    available = len(tested)
    print("\nThere are %d of %d packages available." % (available, no_of_packs)
    for url in not_working:
        package_name = url.split('/')[-1]
        print("The package %s at %s is unavailable!" % (package_name, url)
    
    cont = raw_input("Do you wish to continue? (y/n) ")
    
    if cont == 'y':
        for url in tested:
            download_package(url)
    else:
        print("Script aborted.")
    
if __name__ == '__main__':
    main()
