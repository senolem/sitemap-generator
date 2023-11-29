import os
import sys
import requests
import shutil
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

base_url = "https://absoluflash.co"
visited_urls = set()

def crawl_url(url, parent_element):
	if url in visited_urls:
		return
	terminal_width = shutil.get_terminal_size().columns
	output_total = str("(Total {})".format(len(visited_urls)))
	output_link = str("\r\033[KScrapped : {}".format(url))
	if len(output_link + output_total) > terminal_width:
		output_link = output_link[:terminal_width - len(output_total) - 3] + "..."
	print("{} {}".format(output_link, output_total), end='', flush=True)
	visited_urls.add(url)
	try:
		response = requests.get(url)
		if response.status_code == 200:
			soup = BeautifulSoup(response.content, "html.parser")
			url_element = SubElement(parent_element, "url")
			loc = SubElement(url_element, "loc")
			loc.text = url
			for link in soup.find_all("a"):
				href = link.get("href")
				if href:
					href = urljoin(url, href)
					parsed_href = urlparse(href)
					if parsed_href.netloc == urlparse(base_url).netloc:
						crawl_url(href, parent_element)
	except requests.exceptions.RequestException as e:
		print(f"An error occurred while crawling URL: {url}")
		print(e)

def generate_sitemap(url):
	root = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
	crawl_url(url, root)
	tree = minidom.parseString(tostring(root, encoding="unicode"))
	sitemap_xml = tree.toprettyxml(indent="  ")
	with open("sitemap.xml", "w") as f:
		f.write(sitemap_xml)
	print("Sitemap generated successfully.")

generate_sitemap(base_url)