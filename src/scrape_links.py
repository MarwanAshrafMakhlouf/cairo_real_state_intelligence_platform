from src.scraper import SmartScraper
from src.utils import get_logger
import pandas as pd 
import yaml
from  bs4 import BeautifulSoup
from copy import deepcopy
loger = get_logger('link_scrape')
def filter_locations(config: dict, target_areas: set[str]) -> dict:
    """
    Filter locations config to only include specified area slugs.
    Preserves all keys at every level; drops districts with no matching areas.
    """
    try:
        result = deepcopy(config)  # don't mutate the original
        
        filtered_districts = []
        for district in result.get("locations", []):
            matching_areas = [
                area for area in district.get("areas", [])
                if area["name"] in target_areas
            ]
            if matching_areas:
                district["areas"] = matching_areas
                filtered_districts.append(district)
        
        result["locations"] = filtered_districts
        loger.info('location filtered succesfully')
        return result
    except Exception as e:
        loger.error(f'location filtering failed due to {e}')
        raise e




def base_link_creator(config, areas, subset =False):
    try:
        locations = config['locations']
        empty_pd = []
        if subset:
            subset_config = filter_locations(config, target_areas= areas)
            locations = subset_config['locations']
        for property_type in config['data_source']['realstate_website']['property_types']:
                no_dis = 0
                parts = property_type.split('-')
                type_ = parts[0]
                sale_or_rent = parts[-1]
                logs = []
                for location in locations:
                    district_slug = location['slug']
                    if len(location['areas']) == 0:
                        url = f"{config['data_source']['realstate_website']['base_url']}/{property_type}/{district_slug}/"
                        empty_pd.append({'property_type': type_, 'sale/rent': sale_or_rent, 'city': 'Cairo', 'district': location['district'], 'area': None, 'neighborhood': None, 'link': url})
                        logs.append(url)
                        continue
                    elif len(location['areas']) < 3 and subset == False:
                        no_dis += 1
                        url = f"{config['data_source']['realstate_website']['base_url']}/{property_type}/{district_slug}/"
                        empty_pd.append({'property_type': type_, 'sale/rent': sale_or_rent, 'city': 'Cairo', 'district': location['district'], 'area': None, 'neighborhood': None, 'link': url})
                        logs.append(url)
                    for area in location['areas']:
                    
                        area_slug = area['slug']
                        
                            
                        if len(area['neighborhoods']) == 0 or subset==True:
                            url = f"{config['data_source']['realstate_website']['base_url']}/{property_type}/{area_slug}/"
                            empty_pd.append({'property_type': type_, 'sale/rent': sale_or_rent, 'city': 'Cairo', 'district': location['district'], 'area': area['name'], 'neighborhood': None, 'link': url})
                            logs.append(url)
                            continue
                    
                        
                        for neighborhood in area['neighborhoods']:
                            neighborhood_slug = neighborhood['slug']
                            url = f"{config['data_source']['realstate_website']['base_url']}/{property_type}/{neighborhood_slug}/"
                            empty_pd.append({'property_type': type_, 'sale/rent': sale_or_rent, 'city': 'Cairo', 'district': location['district'], 'area': area['name'], 'neighborhood': neighborhood['name'], 'link': url})
                            logs.append(url)
        loger.info(f'Base links created succesfully')
        return pd.DataFrame(empty_pd)
    except Exception as e:
        loger.error(f'base_link_creation_faild due to {e}')
        raise e
def extract_properties_links(main_page_url, property_schema, scraper, config):
    try:
        # print(main_page_url)
        page_soup = scraper.scrape_single_page(main_page_url)    
        # print(page_soup)
        properties_list_div = page_soup.select_one(config['data_source']['realstate_website']['main_page_selectors']['properties_div'])
    
        stop_pagenation_selector = page_soup.select_one(config['data_source']['realstate_website']['selectors']['stop_pagenation'])
        if stop_pagenation_selector and "Unfortunately we haven't found anything" in stop_pagenation_selector.text:
            loger.info(f"No properties div found for {main_page_url}, skipping extraction")
            return []
        
        properties_unordered_lists = properties_list_div.find_all('ul', recursive=False)
        links = []
        for ul in properties_unordered_lists:
            next_div = ul.find_next('div')
            listed_items = ul.find_all('li')
            next_div_text = next_div.span.text if next_div and next_div.span else "No class found"
            if next_div_text == 'Results from other locations':
                loger.info("Reached the end of listings for this location, stopping extraction")
                break
            for item in listed_items:
                link_container = item.find('a', href=True)
                
                if not link_container:  # expected case — just skip
                    continue
                
                link = link_container['href']
                title = link_container.get('title', 'No title found')
                
                if not link.startswith('/en/ad'):  # filter non-property links
                    continue
                
                try:
                    # keep try/except only for truly unexpected failures
                    prop = property_schema.copy()
                    prop['link'] = link
                    prop['title'] = title
                    links.append(prop)
                except Exception as e:
                    loger.error(f"Unexpected error processing item: {e}")
                    loger.error(f"Problematic item: {item}")  # loger.info the actual HTML so you can debug
        loger.info('extraxted property links done sucessfully')
        # print(links)
        return links
    except Exception as e:      
        loger.error(f"Unexpected error occurred: {e}")
        return []
    

def property_coordinator(df,config, property_schema, scraper):
    all_properties = []
    try:
        
        for location in df.itertuples():
            max_number_of_pages = config['data_source']['realstate_website']['selectors']['max_page_number']
            for i in range(1, max_number_of_pages):
                url =location.link + f"?page={i}"
                properties = extract_properties_links(url, property_schema,config=config, scraper=scraper)
             
                if not properties:
                    loger.info(f"No properties found on page {url}")
                    break

                for prop in properties:
                    prop['property_type'] = location.property_type
                    prop['sale/rent'] = location._2
                    prop['city'] = location.city
                    prop['district'] = location.district
                    prop['area'] = location.area
                    prop['neighborhood'] = location.neighborhood
                all_properties.extend(properties)
            

        loger.info('properties_links_extracted sucssfully')
        return pd.DataFrame(all_properties)
    except Exception as e:
        loger.error(f"Error in property coordinator: {e}")
        return pd.DataFrame(all_properties)
def main():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    scraper = SmartScraper(config)
    fields = config['data_source']['realstate_website']['fields']
    fields.append('link')
    property_schema = {field: None for field in fields}
    base_link_df = base_link_creator(config, areas = {'Rehab City', '3rd Settlement', 'R8', 'R3','Zahraa Madinat Nasr'}, subset=True)
    links_df = property_coordinator(base_link_df, config, property_schema, scraper)
    links_df.to_csv("data/raw/areas_need_to_rescrape.csv")
