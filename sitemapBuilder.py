#!/usr/bin/env python

from re import match
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from urllib.request import urlretrieve, urlopen
from urllib.parse import unquote, urljoin, urlparse
from os import path, makedirs

parser = ArgumentParser(description='Extract link urls of a website.')
parser.add_argument('host', help='host of website to parse (with http/https)')
parser.add_argument('--save', action='store_true', help='write found files into a .txt file')
args = parser.parse_args()

host = args.host
save_to_file = args.save
directory = "result"


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


def write_to_file(urls):
    make_dir(directory)
    filename = directory + "/urls.txt"
    f = open(filename, "w+")
    for url in urls:
        f.write(url + "\n")
    print(" -> URLs are written to file " + filename)
    f.close()


def make_dir(dir):
    if not path.exists(dir):
        makedirs(dir)


def find_urls_in_page(page):
    urls = list()
    if page is None:
        return urls
    while True:
        url, n = getURL(page)
        page = page[n:]
        if not url:
            break
        urls.append(url)
    return urls


def open_url(url):
    try:
        response = urlopen(url)
    except:
        print("Could not access URL " + url)
        return None
    http_message = response.info()
    if http_message.get_content_type() != "text/html":
        print("Wrong content type: " + http_message.get_content_type())
        return None
    try:
        decoded_page = response.read().decode("utf8")
    except UnicodeDecodeError:
        print("Error: can't decode unicode byte!")
        decoded_page = response.read()
    page = str(BeautifulSoup(decoded_page, "html.parser"))
    response.close()
    return page


def process_url(start_url, processed_urls):
    print("-> " + start_url)
    processed_urls.add(start_url)
    for url in find_urls_in_page(open_url(start_url)):
        hostname = urlparse(url).netloc
        if hostname is "" or hostname == host:
            constructed_url = urljoin(start_url, url)
            if constructed_url not in processed_urls:
                process_url(constructed_url, processed_urls)
        else:
            print("Other host: " + url)


urls = set()
process_url(host + "/", urls)

if save_to_file:
    write_to_file(urls)
