#!/usr/bin/env python

import threading
from re import match
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from urllib.request import urlretrieve, urlopen, Request
from urllib.parse import unquote, urljoin, urlparse
from os import path, makedirs

parser = ArgumentParser(description='Extract link urls of a website.')
parser.add_argument('host', help='host of website to parse (with http/https)')
parser.add_argument('--save', action='store_true',
                    help='write found files into a .txt file')
args = parser.parse_args()

host = args.host
save_to_file = args.save
directory = "result"

class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        threading.Thread.__init__(self)
        self._target = target
        self._args = args
 
    def run(self):
        self._target(*self._args)

def get_url(page):
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


def write_to_file(urls, name):
    make_dir(directory)
    filename = directory + "/" + name + ".txt"
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
    while True:
        url, n = get_url(page)
        page = page[n:]
        if not url:
            break
        urls.append(url)
    return urls


def open_url(url):
    # first make HEAD request to avoid downloading 
    # large content of wrong content type
    try:
        request = Request(url)
        request.get_method = lambda : 'HEAD'
        response = urlopen(request)
    except:
        print("Could not access URL with HEAD " + url)
        return None
    http_message = response.info()
    if http_message.get_content_type() != "text/html":
        print("Wrong content type: " + http_message.get_content_type())
        return False

    # then make normal GET if everything is fine
    try:
        response = urlopen(url)
    except:
        print("Could not open URL " + url)
        return None
    try:
        decoded_page = response.read().decode("utf8")
    except UnicodeDecodeError:
        print("Error: can't decode unicode byte!")
        decoded_page = response.read()
    page = str(BeautifulSoup(decoded_page, "html.parser"))
    response.close()
    return page

thread_lock = threading.Lock()

def process_url(start_url, processed_urls, error_urls):
    thread_lock.acquire()
    processed_urls.add(start_url)
    thread_lock.release()
    print("-> " + start_url)
    page = open_url(start_url)
    if page is None:
        # error while request
        thread_lock.acquire()
        error_urls.add(start_url)
        processed_urls.remove(start_url)
        thread_lock.release()
        return
    if page is False: 
        # of wrong content type
        return
    sub_threads = list()
    for url in find_urls_in_page(page):
        hostname = urlparse(url).netloc
        if hostname is "" or hostname == host:
            constructed_url = urljoin(start_url, url)
            thread_lock.acquire()
            not_already_processed = constructed_url not in processed_urls
            thread_lock.release()
            if not_already_processed:
                subThread = FuncThread(process_url, constructed_url, processed_urls, error_urls)
                sub_threads.append(subThread)
                subThread.start()
        else:
            print("Other host: " + url)
            error_urls.add(url)
    for t in sub_threads:
        t.join()


urls = set()
error_urls = set()
tMain = FuncThread(process_url, host + "/", urls, error_urls)
tMain.start()
tMain.join()

if save_to_file:
    write_to_file(urls, "urls")
    write_to_file(error_urls, "errors")
