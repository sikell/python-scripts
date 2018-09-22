#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import argparse

parser = argparse.ArgumentParser(description='Extract link urls of a website.')
parser.add_argument('url', help='url of website to parse')
parser.add_argument('--distinct', action='store_true', help='result list should not contain duplicate link urls, do not preserve order')
args = parser.parse_args()

url = args.url
distinct = args.distinct

response = requests.get(url)
# parse html
page = str(BeautifulSoup(response.content, "html.parser"))

def getURL(page):
    """
    Extract next url from page.
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

urls = list()
while True:
    url, n = getURL(page)
    page = page[n:]
    if url:
        urls.append(url)
    else:
        break

if distinct:
    urls = set(urls)

for url in urls:
    print(url)