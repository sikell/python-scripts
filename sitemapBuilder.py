#!/usr/bin/env python

import threading
from re import match
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from urllib.request import urlretrieve, urlopen, Request
from urllib.parse import unquote, urljoin, urlparse
from urllib.error import HTTPError, URLError
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

class Error():
    def __init__(self, message):
        self._message = message

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
    print("-> " + url)
    # first make HEAD request to avoid downloading 
    # large content of wrong content type
    try:
        request = Request(url)
        request.get_method = lambda : 'HEAD'
        response = urlopen(request)
    except HTTPError as error:
        return Error(str(error.code) + " - " + error.reason)
    except URLError as error:
        return Error(error.reason)
    except:
        print("Could not access URL with HEAD " + url)
        return Error("Unknown Exception")
    http_message = response.info()
    if http_message.get_content_type() != "text/html":
        return False

    # then make normal GET if everything is fine
    try:
        response = urlopen(url)
    except:
        print("Could not open URL " + url)
        return Error("Failed to access URL!")
    try:
        decoded_page = response.read().decode("utf8")
    except UnicodeDecodeError:
        print("Error: can't decode unicode byte!")
        decoded_page = response.read()
    page = str(BeautifulSoup(decoded_page, "html.parser"))
    response.close()
    return page

def process_url(start_url, processed_urls, error_urls, foreign_hosts, thread_lock):
    thread_lock.acquire()
    if start_url in processed_urls:
        thread_lock.release()
        return
    processed_urls.add(start_url)
    thread_lock.release()

    page = open_url(start_url)
    if isinstance(page, Error):
        # error while request
        thread_lock.acquire()
        error_urls.add(start_url + " >>>> " + page._message)
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
            subThread = FuncThread(process_url, constructed_url, processed_urls, error_urls, foreign_hosts, thread_lock)
            sub_threads.append(subThread)
            subThread.start()
        else:
            print("Other host: " + url)
            foreign_hosts.add(url)
    for t in sub_threads:
        t.join()


processed_urls = set()
error_urls = set()
foreign_hosts = set()
thread_lock = threading.Lock()

tMain = FuncThread(process_url, host + "/", processed_urls, error_urls, foreign_hosts, thread_lock)
tMain.start()
tMain.join()

if save_to_file:
    write_to_file(processed_urls, "urls")
    write_to_file(foreign_hosts, "foreign")
    write_to_file(error_urls, "errors")
