from pyexpat import features
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from  bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests
from src.utils import get_logger
import subprocess
import re
import json
import os 
import requests
from random import randint
import time
import pandas as pd
import time 
import yaml

# Intialize the logger
logger = get_logger("Scraper")

# Intialized the global variables
CHECKPOINT_FILE = 'data/raw/checkpoint.json'
OUTPUT_FILE = 'data/raw/properties_full_version.csv'
""" This file contains the code for scraping the data from the website, 
This will be created by the smartScrapper class"""

class SmartScraper:
    """A smar scrapper class does the following: 
    1. Try to scrape the using requests with realistic headers and cookies
    2. If it detects a challenge, it falls back to Selenium to get the page source
    3. It saves the cookies from Selenium to use in future requests
    4. It has methods to scrape single or multiple pages with the smart approach
    Args:
        config (dict): The configuration dictionary loaded from config.yaml
        url (str): The URL to scrape
        Note: You don't have to put the url in the constructor
        Also this class is designed to construct the base_url + whatever slug 
        If you want to scrape a full url you can just put it in the slug and the format_url method will handle it
    """
    def __init__(self, config):
        self.logger = get_logger("SmartScraper")
        self.session = curl_requests.Session()
        self.driver = None
        self.config = config
    

    def get_chrome_version(self):
        """Detect the installed Chrome version on Windows"""
        try:
            output = subprocess.check_output(
                r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
                shell=True
            ).decode()
            version = re.search(r'[\d.]+', output).group()
            self.logger.info(f"Detected Chrome version: {version}")
            return int(version)  # just the major version
        except:
            self.logger.error("Failed to detect Chrome version")
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
            self.logger.info(f"Response status: {response.status_code}, length: {len(response.text)}")

            if (('humbucker' in response.text or
                'challenge' in response.text) and
                len(response.text) < 10000):
                return None
            if len(response.text) > 50000:
                self.logger.info("Content looks valid, using requests response")
                return response.text
        
            return None
            
        except Exception as e:
            self.logger.error(f"Request error: {e}")
            return None
    
    def use_selenium_fallback(self, url):
        """Fallback to Selenium if needed"""
        if not self.driver:
            options = Options()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36')

            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
                        )
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.driver.get(url)
        # time.sleep(5)
        return self.driver.page_source
    
    def get_html(self, url, referer=None):
        """Smart approach: try fast method, fallback to slow"""
        self.logger.info("Trying fast approach (requests)...")
        url = self.format_url(url)
        html = self.try_requests_first(url, referer=referer)
        
        if html:
            self.logger.info("Success with requests!")
            return html
        
        self.logger.info("Challenge detected. Using Selenium...")
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
            self.logger.info(f"\nPage {i+1}/{len(urls)}")
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
def get_page_data(slug, scrapper ,config, max_retries = 5):
    """"
    This function is responsible for getting the page data for a single page using the smart scrapper class
    it's job to intiate the class and handle the retries in case of failure and also handle the logging of the process
    Args:
        slug (str): The slug of the page to scrape
        config (dict): The configuration dictionary loaded from config.yaml
        max_retries (int): The maximum number of retries before giving up
    Returns:
        BeautifulSoup object of the page if successful, None if failed after retries + logging everything
    """
   
    attempts = 0
    while True:
        try:
            
            page_soup = scrapper.scrape_single_page(slug)
            scrapper.logger.info(f"Data extracted for {slug}")
            return page_soup
        except Exception as e:
            scrapper.logger.warning(f"Error scraping page {slug}: {e}")
            attempts += 1
            if attempts >= max_retries: 
                scrapper.logger.error(f"Failed to scrape {slug} after {max_retries} attempts: {e}")
                return None
            scrapper.logger.info(f"Retrying {slug} (attempt {attempts}/{max_retries})...")
            time.sleep(5)  # Wait before retrying

            
        finally:
            time.sleep(randint(1,3))  # Random delay to be polite
            
   
       
    
def save_checkpoint(config,last_processed_index):
    """Save the last processed index to a checkpoint file"""
    with open(config['data_source']['file_paths']['CHECKPOINT_FILE'], 'w') as f:
        json.dump({'last_index': last_processed_index}, f)

def load_checkpoint(config):
    """Load the last processed index from the checkpoint file, or return 0 if not found"""
    if os.path.exists(config['data_source']['file_paths']['CHECKPOINT_FILE']):
        with open(config['data_source']['file_paths']['CHECKPOINT_FILE'], 'r') as f:
            return json.load(f)['last_index']
    return 0
# A function to create instance of smart scrapper and return multiple soup pages
def get_multiple_pages(slugs, config):
    
    scrapper = SmartScraper(config)
    try:
        pages_soup = scrapper.scrape_multiple_pages(slugs)
    finally:
        scrapper.close()
        scrapper.logger.info(f"Data extracted for {len(slugs)} pages")
    return pages_soup
# After some extractions I figured some properties are removed from the website. This case must be hanlded
def property_not_available(soup, config):
    """
    Check if the property is sold or unavailable by looking for specific indicators in the page source
    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the page
        config (dict): The configuration dictionary loaded from config.yaml
    Returns:
            bool: True if the property is sold or unavailable, False otherwise
    """
    try:
        sold_indicator = soup.select_one(config['data_source']['realstate_website']['selectors']['is_sold'])
        if sold_indicator:
             return True
        else:
            return False
    except Exception as e:
        logger.error(f"Error handling sold property: {e}")
        return False
# Create the date formatter function 

def standardize_date(date):
    """
        Convert relative date strings to a standardized format (MM-DD-YYYY)
        Args:
            date (str): The relative date string (e.g., "2 days ago", "yesterday", "just now")
        Returns:
            str: The standardized date string in MM-DD-YYYY format, or None if parsing fails
    """
    
    try:
        if 'today' in date.lower() or 'just now' in date.lower() or 'hour' in date.lower() or 'minute' in date.lower() or 'second' in date.lower():
            listing_date = pd.Timestamp.now()
        elif 'yesterday' in date.lower():
            listing_date = pd.Timestamp.now() - pd.Timedelta(days=1)
        elif 'day' in date:
            days_ago = int(date.split()[0])
            listing_date = pd.Timestamp.now() - pd.Timedelta(days=days_ago)
        elif 'week' in date:
            weeks_ago = int(date.split()[0])
            listing_date = pd.Timestamp.now() - pd.Timedelta(weeks=weeks_ago)
        elif 'month' in date:
            months_ago = int(date.split()[0])
            listing_date = pd.Timestamp.now() - pd.Timedelta(days=30*months_ago)
        elif 'year' in date:
            years_ago = int(date.split()[0])
            listing_date = pd.Timestamp.now() - pd.Timedelta(days=365*years_ago)
        else:
            listing_date = None  # Handle unexpected format
        logger.info(f"Parsed date '{date}' to {listing_date}")
        return listing_date.strftime('%m-%d-%Y') if listing_date else None
    except Exception as e:
        logger.error(f"Date parsing error: {e} for date string: {date}")
        return None

# Estracting the basic information
def extract_basic_info(soup,page_data, config):
    """Extract the basic information of the listing such as price, creation date, and seller name
        Args:
            soup (BeautifulSoup): The BeautifulSoup object of the page
            page_data (dict): The dictionary to store the extracted data
            config (dict): The configuration dictionary loaded from config.yaml
        Returns:
            dict: The updated page_data dictionary with the extracted basic information
    """
    try:
       
        # page_title = soup.select_one(config['data_source']['realstate_website']['selectors']['title']).text.strip()
        # page_data['title'] = page_title
        page_data['price'] = soup.select_one(config['data_source']['realstate_website']['selectors']['price']).text.strip()
        page_data['listing_date'] = standardize_date(soup.select_one(config['data_source']['realstate_website']['selectors']['creation_date']).text.strip())
        seller_name = soup.select_one(config['data_source']['realstate_website']['selectors']['seller_name'])
        if not seller_name:
            page_data['seller_name'] = soup.select_one(config['data_source']['realstate_website']['selectors']['already_sold']).text.strip()
        else:
            page_data['seller_name'] = seller_name.text.strip()
        logger.info("Basic info extracted successfully")
        return page_data
    except Exception as e:
        logger.error(f"Error extracting basic info: {e}")
        return {}

def highlights_extractor(config, page_data, soup):
    """
        Extract the highlights of the listing such as number of bedrooms, bathrooms, area, and property subtype:
        each property have a different highlights section.It's expected in the scraped data to have some of highlits fields as nulls.
        Args:
            config (dict): The configuration dictionary loaded from config.yaml
            page_data (dict): The dictionary to store the extracted data
            soup (BeautifulSoup): The BeautifulSoup object of the page
        Returns:
            dict: The updated page_data dictionary with the extracted highlights information
            empty if error happend 
    """
    try:
    #   outer items contains 
        highlights_container = soup.select_one(config['data_source']['realstate_website']['selectors']['highlights_container'])
        outer_items = highlights_container.select(config['data_source']['realstate_website']['selectors']['higlight_items'])

        for item in outer_items:
            spans = item.find_all('span')
            if len(spans) >=2:
                key = spans[0].text.strip().lower()
                value = spans[1].text.strip()
                page_data[key] = value
        page_data['property_subtype'] = page_data.pop('type', None)
        logger.info("Highlights extracted successfully")
        return page_data
    except Exception as e:
        logger.error(f"Error extracting highlights: {e}")
        return {}


def details_extractor(config, page_data, soup):
    """
    It extract the details features from the property page things like payment method
    Every property have different details all of them is inside a container so I loop over them and save key value pairs
    Args:
            config (dict): The configuration dictionary loaded from config.yaml
            page_data (dict): The dictionary to store the extracted data
            soup (BeautifulSoup): The BeautifulSoup object of the page
        Returns:
            dict: The updated page_data dictionary with the extracted highlights information 
            empty if error happend 
    """
    try:
        # Here I extract the other details of the listing such level, payment method, ..etc
        details_container = soup.select_one(config['data_source']['realstate_website']['selectors']['details_container'])
        # print(details_container.prettify())
        details_items = details_container.select(config['data_source']['realstate_website']['selectors']['details_items'])
        spans = details_items[0].find_all('span')
        for i in range(0, len(spans),2):
            key = spans[i].text.strip().lower()
            value = spans[i+1].text.strip().lower()
            page_data[key] = value
        logger.info("Details extracted successfully")
        return page_data
    except Exception as e:
        logger.error(f"Error extracting details: {e}")
        return {}

def additional_features_extractor(config,page_data, soup):
    """
    It extract the additional features of the listing such as if it has a garage, pool,
    the way it's exctracted it's different from the highlights and details as they are not key value 
    If they listed then this property have them Put True if not listed put False
    Args:
            config (dict): The configuration dictionary loaded from config.yaml
            page_data (dict): The dictionary to store the extracted data
            soup (BeautifulSoup): The BeautifulSoup object of the page
        Returns:
            dict: The updated page_data dictionary with the extracted highlights information empty if error happend 
    """
    try:
        # Here I extract the features of the listing
        features_container = soup.select_one(config['data_source']['realstate_website']['selectors']['features_container'])
        features_items = features_container.select(config['data_source']['realstate_website']['selectors']['features_items'])
        for item in features_items:
            spans = item.find_all('span')
            for span in spans:
                key = span.text.strip().lower()
                if key == 'see all':
                    continue
                
                page_data[key] = True
        features = config['data_source']['realstate_website']['features_list']
        for feature in features:
            if page_data[feature] is None:
                page_data[feature] = False
        logger.info("Additional features extracted successfully")
        return page_data
    except Exception as e:
        logger.error(f"Error extracting additional features: {e}")
        return {}
def safe_append_to_csv(new_rows, config):
    # Read existing columns
    file_path = config['data_source']['file_paths']['OUTPUT_FILE']
    existing_columns = pd.read_csv(file_path, nrows=0).columns.tolist()
    
    # Create DataFrame from new rows
    df_chunk = pd.DataFrame(new_rows)
    
    # Find new keys that don't exist in CSV yet
    new_keys = [col for col in df_chunk.columns if col not in existing_columns]
    
    if new_keys:
        logger.warning(f"New columns found, adding to CSV: {new_keys}")
        
        # Read entire CSV, add new columns as NaN, rewrite it
        df_existing = pd.read_csv(file_path)
        for key in new_keys:
            df_existing[key] = None
        df_existing.to_csv(file_path, index=False)
        
        # Update existing_columns to include new keys
        existing_columns = df_existing.columns.tolist()
    
    # Reindex and append normally
    df_chunk = df_chunk.reindex(columns=existing_columns)
    df_chunk.to_csv(file_path, mode='a', header=False, index=False)

def main():
    """The main function to run the scraper, it will read the config file, 
    load the links from the csv file, and loop over them to extract the data 
    and save it to a csv file with checkpointing in case of failure"""
        # first thing we need to read the config file
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    fields = config['data_source']['realstate_website']['fields']
    property_schema = {field: None for field in fields}
    links_df = pd.read_csv(config['data_source']['file_paths']['links_file'])
    start_index = load_checkpoint(config)
    already_created = os.path.exists(config['data_source']['file_paths']['OUTPUT_FILE']) and start_index > 0
    if start_index > 0:
        logger.info(f"Resuming from index {start_index}")
    property_accumelator = []
    skipped_links = []
    scrapper = SmartScraper(config)
     
    for location in links_df.iloc[start_index:].itertuples():
        current_index = location.Index
        
        try:
            page_soup = get_page_data(location.link, scrapper, config)
            if page_soup is None:

                raise Exception(f"Failed to retrieve page for {location.link}")
            page_data = property_schema.copy()
            if property_not_available(page_soup, config):
                logger.info(f"Property at {location.link} is marked as sold or unavailable.")
                page_data['seller_name'] = 'Sold/Unavailable'
            else:
                
                page_data = extract_basic_info(page_soup, page_data, config)
                if not page_data:
                    logger.warning(f"Basic info extraction failed for {location.title}, skipping this listing.")
                    skipped_links.append(location.link)
                    continue

                page_data = highlights_extractor(config, page_data, page_soup)
                if not page_data:
                    raise ValueError("highlights_extractor returned empty dictionary")

                page_data = details_extractor(config, page_data, page_soup)
                if not page_data:
                    raise ValueError("details_extractor returned empty dictionary")

                page_data = additional_features_extractor(config, page_data, page_soup)
                if not page_data:
                    raise ValueError("additional_features_extractor returned empty dictionary")
            page_data['title'] = location.title
            page_data['property_type'] = location.property_type
            page_data['sale_or_rent'] = location.sale_or_rent
            page_data['city'] = location.city
            page_data['area'] = location.area
            page_data['district'] = location.district
            page_data['neighborhood'] = location.neighborhood
   
            property_accumelator.append(page_data)
            if len(property_accumelator) %1000 == 0 and len(property_accumelator) > 0:
                
                if already_created:   
                    safe_append_to_csv(property_accumelator, config)
                else:
                    df_chunk = pd.DataFrame(property_accumelator)
                    df_chunk.to_csv(config['data_source']['file_paths']['OUTPUT_FILE'], index=False)
                    already_created = True
                save_checkpoint(config, current_index + 1)
                logger.info(f"Saved checkpoint at index {current_index + 1}")
                property_accumelator = []
                if skipped_links:
                    logger.warning(f"Skipped links so far: {len(skipped_links)}")   
                    skipped_links_df = pd.DataFrame(skipped_links, columns=['skipped_links'])
                    skipped_links_df.to_csv(config['data_source']['file_paths']['corrupted_links_file'], mode = 'a', header=False, index=False) 
                skipped_links = []

        except Exception as e:
            logger.error(f"Error processing {location.link}: {e}")
            if property_accumelator:
                
                if already_created:   
                     safe_append_to_csv(property_accumelator, config)
                else:
                    df_chunk = pd.DataFrame(property_accumelator)
                    df_chunk.to_csv(config['data_source']['file_paths']['OUTPUT_FILE'], index=False)
                    already_created = True
                save_checkpoint(config, current_index + 1)
                logger.info(f"Saved checkpoint at index {current_index + 1} after error")
            if skipped_links:
                    logger.warning(f"Skipped links so far: {len(skipped_links)}")   
                    skipped_links_df = pd.DataFrame(skipped_links, columns=['skipped_links'])
                    skipped_links_df.to_csv(config['data_source']['file_paths']['corrupted_links_file'], mode = 'a', header=False, index=False) 
            break
    else:
    #Loop completed without break — flush remaining and clear checkpoint
        if property_accumelator:
            
            if already_created:
                     safe_append_to_csv(property_accumelator, config)
            else:
                df_chunk = pd.DataFrame(property_accumelator)
                df_chunk.to_csv(config['data_source']['file_paths']['OUTPUT_FILE'], index=False)
        if skipped_links:
                    logger.warning(f"Skipped links so far: {len(skipped_links)}")   
                    skipped_links_df = pd.DataFrame(skipped_links, columns=['skipped_links'])
                    skipped_links_df.to_csv(config['data_source']['file_paths']['corrupted_links_file'], mode = 'a', header=False, index=False) 

        logger.info("Scraping completed. Checkpoint cleared.")
        
    scrapper.close()

