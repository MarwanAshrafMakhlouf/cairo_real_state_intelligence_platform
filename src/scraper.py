from fake_useragent import UserAgent
import undetected_chromedriver as uc
from  bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests
from utils import get_logger
import subprocess
import re

import requests

import pandas as pd
import time 
import yaml
# Intialize the logger
logger = get_logger("Scraper")

""" This file contains the code for scraping the data from the website, 
This will be created by the smartScrapper class"""

class SmartScraper:
    def __init__(self, config):
    
        self.session = curl_requests.Session()
        self.driver = None
        self.config = config
    

    def get_chrome_version(self):
        try:
            output = subprocess.check_output(
                r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
                shell=True
            ).decode()
            version = re.search(r'[\d.]+', output).group()
            logger.info(f"Detected Chrome version: {version}")
            return int(version)  # just the major version
        except:
            logger.error("Failed to detect Chrome version")
            return None
    
    def format_url(self, slug):
        if '.com' in slug:
            return slug
        return self.config['data_source']['realstate_website']['base_url'] + slug
        
    def get_realistic_headers(self, referer=None):
        """Generate complete, realistic browser headers"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin' if referer else 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        
        if referer:
            headers['Referer'] = referer
            
        return headers
        
    def try_requests_first(self, url, referer=None):
        """Try fast approach with realistic headers"""
        headers = self.get_realistic_headers(referer=referer)
        
        try:
            response = self.session.get(
                url, 
                headers=headers, 
                timeout=15,
                impersonate="chrome120"
                )
            logger.info(f"Response status: {response.status_code}, length: {len(response.text)}")

            if (('humbucker' in response.text or
                'challenge' in response.text) and
                len(response.text) < 10000):
                return None
            if len(response.text) > 50000:
                logger.info("Content looks valid, using requests response")
                return response.text
        
            return None
            
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None
    
    def use_selenium_fallback(self, url):
        """Fallback to Selenium if needed"""
        if not self.driver:
            version = self.get_chrome_version()
            options = uc.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            self.driver = uc.Chrome(options=options, version_main=version)
        
        self.driver.get(url)
        time.sleep(5)
        return self.driver.page_source
    
    def get_html(self, url, referer=None):
        """Smart approach: try fast method, fallback to slow"""
        self.logger.info("Trying fast approach (requests)...")
        url = self.format_url(url)
        html = self.try_requests_first(url, referer=referer)
        
        if html:
            self.logger.info("Success with requests!")
            return html
        
        logger.info("Challenge detected. Using Selenium...")
        html = self.use_selenium_fallback(url)
        
        # Save cookies for next time
        if self.driver:
            cookies = self.driver.get_cookies()
            for cookie in cookies:
                self.session.cookies.set(
                    cookie['name'], 
                    cookie['value'],  
                    domain=cookie.get('domain', '')
                )
        
        return html
    def scrape_single_page(self, url):
        """Scrape a single page with smart approach"""
        html = self.get_html(url)
        
        soup = BeautifulSoup(html, 'lxml')
        # Your parsing code here
        
        return soup
    
    def scrape_multiple_pages(self, urls):
        """Scrape multiple pages efficiently"""
        results = []
        previous_url = None
        for i, url in enumerate(urls):
            logger.info(f"\nPage {i+1}/{len(urls)}")
            html = self.get_html(url, referer=previous_url)
            
            soup = BeautifulSoup(html, 'lxml')
            # Your parsing code here
        
            results.append(soup)
            previous_url = self.format_url(url)
            time.sleep(2)  # Be nice to server
        
        return results
    
    def close(self):
        if self.driver:
            self.driver.quit()

# A function to create instance of smart scrapper and return one soup page 
def get_page_data(slug, config):

    scrapper = SmartScraper(config)
    
    try:
        
        page_soup = scrapper.scrape_single_page(slug)
       
    finally:    
        scrapper.close()
        logger.info(f"Data extracted for {slug}")
        return page_soup
# A function to create instance of smart scrapper and return multiple soup pages
def get_multiple_pages(slugs, config):
    scrapper = SmartScraper(config)
    try:
        pages_soup = scrapper.scrape_multiple_pages(slugs)
    finally:
        scrapper.close()
        logger.info(f"Data extracted for {len(slugs)} pages")
    return pages_soup


if __name__ == "__main__":
    # first thing we need to read the config file
    with open('../config.yaml', 'r') as f:
        config = yaml.safe_load(f)
  


