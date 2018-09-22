#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import argparse
import urllib.request
import os

parser = argparse.ArgumentParser(description='Extract link urls of a website.')
parser.add_argument('url', help='url of website to parse')
parser.add_argument('--distinct', action='store_true', help='result list should not contain duplicate link urls, do not preserve order')
parser.add_argument('--filter-should-contain', help='only parse urls containing given string')
parser.add_argument('--download', action='store_true', help='save all found urls to files')
args = parser.parse_args()

url = args.url
distinct = args.distinct
download_files = args.download
directory = "downloads"

response = requests.get(url)
# parse html
page = str(BeautifulSoup(response.content, "html.parser"))

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

def filter(url):
    """Returns True if all configured filters are passed and False if not."""
    if args.filter_should_contain is not None and args.filter_should_contain not in url:
        return False
    return True

def downloadFile(url):
    """Download a file from given url an use last url segment as filename to directory 'download/'."""
    if not os.path.exists(directory):
        os.makedirs(directory)
    image_name = directory + "/" + url.rsplit('/', 1)[-1]
    urllib.request.urlretrieve(url, image_name)

urls = list()
while True:
    url, n = getURL(page)
    page = page[n:]
    if not url:
        break
    if filter(url):
        urls.append(url)

if distinct:
    urls = set(urls)

for url in urls:
    print(url)
    if download_files:
        downloadFile(url)