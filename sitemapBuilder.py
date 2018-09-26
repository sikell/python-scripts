#!/usr/bin/env python

from bs4 import BeautifulSoup
from argparse import ArgumentParser
from urllib.request import urlretrieve, urlopen
from urllib.parse import unquote
from os import path, makedirs

parser = ArgumentParser(description='Extract link urls of a website.')
parser.add_argument('url', help='url of website to parse')
parser.add_argument('--save', action='store_true', help='write found files into a .txt file')
args = parser.parse_args()

url = args.url
save_to_file = args.save
directory = "result"

try:
    response = urlopen(url)
except:
    print("Could not access URL " + url)
    exit(1)

page = str(BeautifulSoup(response.read().decode("utf8"), "html.parser"))
response.close()


def getURL(page):
    """Extract next url from page.
    :param page: html of web page 
    :return: urls in that page 
    """
    start_link = page.find("a href")
    if start_link == -1:
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1: end_quote]
    return url, end_quote


def filter_url(url):
    """Returns True if all configured filters are passed and False if not."""
    if args.filter_should_contain is not None and args.filter_should_contain not in url:
        return False
    return True


def write_to_file(urls):
    make_dir(directory)
    filename = directory + "/urls.txt"
    f = open(filename, "w+")
    for url in urls:
        f.write(url + "\n")
    print(" -> URLs are written to file " + filename)
    f.close()


def download_file(url):
    """Download a file from given url an use last url segment as filename to directory 'download/'."""
    make_dir(directory)
    image_name = directory + "/" + unquote(url.rsplit('/', 1)[-1])
    urlretrieve(url, image_name)
    print(" -> Save file " + image_name)


def make_dir(dir):
    if not path.exists(dir):
        makedirs(dir)


urls = list()
while True:
    url, n = getURL(page)
    page = page[n:]
    if not url:
        break
    if filter_url(url):
        urls.append(url)

print(str(len(urls)) + " URLs found!")

if distinct:
    urls = set(urls)

for url in urls:
    print(url)
    if download_files:
        download_file(url)

if save_to_file:
    write_to_file(urls)