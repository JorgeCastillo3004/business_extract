from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from datetime import date, timedelta, datetime
from selenium import webdriver
import random
import string
import os
import re
import time
import pandas as pd
from navigator_settings import *
from common import *

def launch_navigator(url, headless=True):
    options = webdriver.ChromeOptions()
    
    # Configuraciones para evitar detección de bot
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-web-security")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # User-Agent aleatorio para Linux
    user_agents = [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    user_agent = random.choice(user_agents)
    options.add_argument(f"user-agent={user_agent}")
    
    if headless:
        options.add_argument('--headless')
    
    # Directorio del perfil de Chrome
    chrome_path = '/home/jorge/.config/google-chrome/'
    options.add_argument(r"user-data-dir={}".format(chrome_path))
    options.add_argument(r"profile-directory=Default")
    
    # Ruta del driver
    drive_path = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=drive_path, options=options)
    
    # Emulación del comportamiento humano
    driver.get(url)
    time.sleep(random.uniform(1, 3))  # Espera aleatoria
    
    # Simulación de movimiento del mouse
    webdriver.ActionChains(driver).move_by_offset(random.randint(0, 10), random.randint(0, 10)).perform()
    
    return driver

def random_sleep(start=1, end=2):
    time.sleep(random.uniform(start, end))

def human_typing(element, text, start=0.05, end=0.15):
    for char in text:
        element.send_keys(char)
        random_sleep(start, end)

def random_mouse_movement(driver):
    action = ActionChains(driver)
    for _ in range(random.randint(5, 10)):
        x_offset = random.randint(0, 20)
        y_offset = random.randint(0, 20)
        action.move_by_offset(x_offset, y_offset).perform()
        random_sleep(0.2, 0.5)

def random_page_interaction(driver):
    actions = [Keys.PAGE_DOWN, Keys.PAGE_UP, Keys.HOME, Keys.END]
    action = ActionChains(driver)
    for _ in range(random.randint(3, 7)):
        action.send_keys(random.choice(actions)).perform()
        random_sleep(0.5, 1.5)

def wait_update_page(driver, url, class_name):
    wait = WebDriverWait(driver, 10)
    current_tab = driver.find_elements(By.CLASS_NAME, class_name)
    driver.get(url)

    if len(current_tab) == 0:
        current_tab = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, class_name)))
    else:
        element_updated = wait.until(EC.staleness_of(current_tab[0]))   

def make_search(driver, category, city):
    search_category = driver.find_element(By.ID, 'search_description')
    search_category.click()

    human_typing(search_category, category, start=0.05, end=0.15)
    search_category.send_keys(Keys.TAB)

    search_localization = driver.find_element(By.ID, 'search_location')
    human_typing(search_localization, city + '\n', start=0.05, end=0.15)

    webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()

def extract_name(block, start_1 = 1, start_2 = 2, end_1 = 3, end_2 = 3):
    random_sleep(start=start_1, end=end_1)
    wait = WebDriverWait(block, 10)
    # company_name = block.find_element(By.XPATH, ".//div[contains(@class, 'businessName')]").text
    company_name = wait.until(EC.presence_of_element_located((By.XPATH, ".//div[starts-with(@class, 'businessName')]")))
    random_sleep(start=start_2, end=end_2)
    return company_name.text

def extract_numeric_value(text):
    # Define la expresión regular para encontrar números, incluyendo decimales
    pattern = r'[-+]?\d*\.\d+|\d+'
    match = re.search(pattern, text)
    
    if match:
        return float(match.group())
    return None

def extract_reviews_rating(block):
    try:
        rating, no_of_reviews = block.find_elements(By.XPATH, ".//div[./span[contains(text(), 'review')]]/span")
        rating = extract_numeric_value(rating.text)
        no_of_reviews = extract_numeric_value(no_of_reviews.text)
        return rating, no_of_reviews
    except:
        return None, None
    
def extract_categories(driver):
    try:
        # Encuentra la sección de categorías
        category_section = driver.find_element(By.CSS_SELECTOR, 'div[aria-labelledby="filterSetCategory"]')

        # Encuentra todos los botones dentro de la sección de categorías
        category_buttons = category_section.find_elements(By.CSS_SELECTOR, 'button.filterToggle__09f24__XF_eF')

        # Extrae el texto de cada botón
        categories = [button.find_element(By.TAG_NAME, 'p').text for button in category_buttons]
        return categories
    except:
        return ''    

def click_more_info(block):
    # click on more info
    wait = WebDriverWait(block, 10)
    more_info = wait.until(EC.element_to_be_clickable((By.XPATH, './/a[contains(text(),"more")]')))
    more_info.click()

def change_windows(driver):
    time.sleep(1)
    all_windows = driver.window_handles    
    driver.switch_to.window(all_windows[1])   

def get_phone_url_addres(driver):
    wait = WebDriverWait(driver, 4)
    try:
        xpath_expression = "//p[contains(text(), 'Business website')]/following-sibling::p/a"
        profile_URL = wait.until(EC.presence_of_element_located((By.XPATH, xpath_expression))).text
        # xpath_expression = "//p[contains(text(), 'Business website')]/following-sibling::p/a"
        # profile_URL = driver.find_element(By.XPATH, xpath_expression).text
    except:
        profile_URL = ''
    print(f"profile_URL {profile_URL}")
    
    try:
        xpath_expression = "//p[contains(text(), 'Phone number')]/following-sibling::p"
        phone_number = driver.find_element(By.XPATH, xpath_expression).text
    except:
        phone_number = ''
    print(f"phone_number: {phone_number}")
    
    try:
        xpath_expression = "//p[a[contains(text(), 'Get Directions')]]/following-sibling::p"
        full_address = driver.find_element(By.XPATH, xpath_expression).text
    except:
        full_address = ''
    print(f"full_address: {full_address}")

    return profile_URL, phone_number, full_address

def get_website(driver):
    try:
        xpath_expression = "//a[.//span[contains(text(), 'Website')]]"
        return driver.find_element(By.XPATH, xpath_expression).get_attribute('href')
    except:
        return ''

def complete_data(city, search_rank, company_name, categories, profile_URL, full_address, phone_numbers, website, rating, no_of_reviews):
    row ={
    'Search Location':city,
    'Search Rank':search_rank,
    'Profile/Company Name':company_name,
    'Category':categories,
    'Profile URL':profile_URL,    
    'Full Address':full_address,
    'Phone Number': phone_numbers,
    'Email Address': '',
    'Website':website,
    'Rating':rating,
    'No. of Reviews':no_of_reviews,
    'Years in Business':'',
    'Email': '',
    'Phone': '',
    'Social Media Profiles': '',
    # 'Facebook': '',
    # 'Twitter': '',
    # 'Instagram': '',
    }
    return row

def extract_search_rank_and_company_name(text, search_counter, index):
    # Define the regular expression pattern
    pattern = r"^(\d+)\.\s*(.+)"
    
    # Search for the pattern in the provided text
    match = re.match(pattern, text)
    
    if match:
        # Extract the search rank and company name
        search_rank = int(match.group(1))
        company_name = match.group(2)
        return search_rank, company_name
    else:        
        search_rank = search_counter + index
        return search_rank, text

def get_more_info(driver, block, max_value = 5):
    if max_value == 1:
        max_value = 2
    count_try = 0
    more_info = block.find_elements(By.XPATH, './/a[contains(text(),"more")]')
    print("Check if more info exist: ",len(more_info))
    while True and more_info:
        # try:
            count_try += 1
            if count_try == max_value:
                break
            click_more_info(block)
            random_sleep(start=2, end=6)
            change_windows(driver)
            profile_URL, phone_numbers, full_address = get_phone_url_addres(driver)
            #############################################
            random_sleep(start=2, end=6)
            website = get_website(driver) # Get business website

            random_sleep(start=2, end=6)
            close_back_main_window(driver)
            return profile_URL, phone_numbers, full_address, website
        # except:                
        #     all_windows = driver.window_handles
        #     if len(all_windows) != 1:
        #         driver.close()
        #         all_windows = driver.window_handles
        #         driver.switch_to.window(all_windows[0])
    return '', '', '', ''

def click_next(driver, search_counter, index, maxtry = 8):
    count = 0
    while count < maxtry:
        print('CN-', count)
        try:
            driver.execute_script("document.body.style.zoom='50%'")
            webdriver.ActionChains(driver).send_keys(Keys.END).perform()
            random_sleep(start=1, end=2)
            webdriver.ActionChains(driver).send_keys(Keys.PAGE_UP).perform()
            random_sleep(start=1, end=2)
            wait = WebDriverWait(driver, 10)
            webdriver.ActionChains(driver).send_keys(Keys.END).perform()
            random_sleep(start=1, end=2)
            xpath_expression = "//button[@type='submit' and not(@disabled) and span[contains(text(), 'Next Page')]]"
            next_page_button = driver.find_elements(By.XPATH, xpath_expression)
            if next_page_button:
                print("Inside next button: ")
                xpath_expression = "//li/div[starts-with(@class, 'container__')]"        
                blocks = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_expression)))    

            #     time.sleep(0.5)
            #     next_page_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[contains(text(), 'Next Page')]]")))
                next_page_button[0].click()

                if len(blocks) != 0: # Check if exists blocks
                    wait.until(EC.staleness_of(blocks[0])) # wait until staleness first block 
                    
                # else:
                blocks = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_expression)))
                search_counter += index + 1

                print("############ CLICK ON NEXT PAGE ############")
                return search_counter, True
            count = maxtry
        except:
            count += 1
    return search_counter, False

def get_current_page(driver):    
    xpath_expression = '//span[@aria-current="true"]//*[contains(@aria-label, "Page")]'
    return int(driver.find_element(By.XPATH, xpath_expression).text)

def click_last_show(driver):
    webdriver.ActionChains(driver).send_keys(Keys.END).perform()
    random_sleep(start=1.5, end = 3.5)
    webdriver.ActionChains(driver).send_keys(Keys.PAGE_UP).perform()
    random_sleep(start=0.3, end = 0.5)
    webdriver.ActionChains(driver).send_keys(Keys.END).perform()
    wait = WebDriverWait(driver, 10)        
    blocks = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li/div[starts-with(@class, 'container__')]")))   

    xpath_expression = '//div[starts-with(@aria-label, "Page:")]'
    elements = driver.find_elements(By.XPATH, xpath_expression)
    clickable_elements = []

    for element in elements:
        wait = WebDriverWait(element, 10)
        clickable = wait.until(EC.element_to_be_clickable((By.XPATH, '.')))
        clickable_elements.append(clickable)

    print(clickable_elements[-1].text, end = ' ')
    show_section(clickable_elements[-1].text, longitud_marco=30)
    clickable_elements[-1].click()   
    
    ###################################
    #     WAIT STALENESS BLOCK        #
    ###################################    
    wait.until(EC.staleness_of(blocks[0])) # wait until staleness first block

def click_last_page_checked(driver, page_number):
    random_sleep(start=1.5, end = 2.5)    
    webdriver.ActionChains(driver).send_keys(Keys.END).perform()
    random_sleep(start=1.5, end = 3.5)
    webdriver.ActionChains(driver).send_keys(Keys.PAGE_UP).perform()
    webdriver.ActionChains(driver).send_keys(Keys.END).perform()
    if page_number != 1:
        driver.execute_script("document.body.style.zoom='50%'")        
        ###################################
        #    LOAD CURRENTS BLOCKS         #
        ###################################        
        xpath_expression = "//li/div[starts-with(@class, 'container__')]"
        # blocks = driver.find_elements(By.XPATH, xpath_expression)
        wait = WebDriverWait(driver, 10)        
        blocks = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li/div[starts-with(@class, 'container__')]")))

        ##########################################
        #  FIND PAGE OF CHECK POINT AND CLICK    #
        ##########################################        
        xpath_expression = f'//div[@aria-label="Page: {page_number}"]'

        while True:
            click_last_show(driver)
            page_number_block = driver.find_elements(By.XPATH, xpath_expression)
            if page_number_block:
                blocks = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li/div[starts-with(@class, 'container__')]")))
                page_number_block[0].click()
                print(f"Click on Page: {page_number}")
                break

            ###################################
            #     WAIT STALENESS BLOCK        #
            ###################################
            wait.until(EC.staleness_of(blocks[0])) # wait until staleness first block
    random_sleep(start=2.5, end = 3.5)

def extract(driver, check_point, folder, outfile):
    # folder = outfile.split('/')[0]
    data = load_json(f'{folder}/data.json')
    search_rank = check_point['search_rank']
    
    while True:
    #     blocks = driver.find_elements(By.XPATH, '//div[@data-testid="serp-ia-card"]')
        enable = False
        wait = WebDriverWait(driver, 10)
        xpath_expression = "//li/div[starts-with(@class, 'container__')]"
        blocks = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_expression)))
        random_sleep(start=0.5, end=1)
        for index, block in enumerate(blocks[:3]): # delete slicing cut
            # clean_screen()
            if index > check_point['index'] or check_point['index'] == 0:
                enable = True
            if enable:
                #############################################
                #         EXTRACT COMPANY NAME              #
                #############################################
                company_name = extract_name(block, start_1 = 1, start_2 = 2, end_1 = 3, end_2 = 3)

                #############################################
                #         EXTRACT SEARCH RANKING            #
                #############################################
                search_rank, company_name =  extract_search_rank_and_company_name(company_name, search_rank, index)
                print(f"search_rank: {search_rank}, company_name: {company_name}")
                random_sleep(start=1.5, end=2.5)
                
                #############################################
                #           EXTRACT REVIEWS                 #
                #############################################
                rating, no_of_reviews = extract_reviews_rating(block)
                random_sleep(start=2.5, end=3.5)

                #############################################
                #         CLICK MORE INFO                   #
                #############################################
                profile_URL, phone_numbers, full_address, website = get_more_info(driver, block, max_value = 5)

                #############################################
                #         EXTRACT CATEGORY                  #
                #############################################    
                categories = extract_categories(driver)

                #############################################
                #         BUILD DATA DICT                   #
                #############################################
                row = complete_data(check_point['location'], search_rank, company_name, categories, profile_URL, full_address,
                              phone_numbers, website, rating, no_of_reviews)
                random_sleep(start=1.5, end=3.5)
                social_links = {}
                if profile_URL != '':
                    social_links = extract_social_media_links(driver, profile_URL)

                row.update(social_links)
                data.append(row)

                # get current page number
                page_number = get_current_page(driver)
                # SAVE CHECK POINT 
                check_point = {'category':check_point['category'],
                                'location':check_point['location'],
                                 'page':page_number,
                                 'index': index,
                                'search_rank':search_rank}
                save_check_point(f'{folder}/checkpoint.json', check_point)
                save_check_point(f'{folder}/data.json', data)
        #############################################
        #         CLICK NEXT PAGE                   #
        #############################################        
        print("Click on next")
        random_sleep(start = 2, end = 5)
        search_rank, flag_next = click_next(driver, search_rank, index)
        check_point['index'] = 0
        print(f"search_rank {search_rank}, flag_next {flag_next}")
        random_sleep(start = 3, end = 6)
        print(f"search_rank {search_rank}")
        if not flag_next:
            break
            print("Last page, break loop")    
        
    df = pd.DataFrame(data)
    df.to_csv(outfile)
    return data
    
def main():
    # CREATE DIRECTORY
    directory_path = 'files_yelp'
    ensure_directory_exists(directory_path)
    
    # DRIVER CREATION AND SETTINGS
    driver = open_firefox_with_profile('https://www.yelp.co.uk/', headless= False, enable_profile=True)
    # driver.set_window_size(1800, 900)
    set_random_window_size(driver)

    # CHECK POINT AND SETTINGS
    check_point = restart_continue(directory_path) # check and load checkpoint.
    # search_settings = load_json('search_settings.json')
    categories, locations, pathfile = get_arguments()
    count = 0
    # try:
    for category in categories:
            for location in locations:                
                show_section(f"Category: {category} location {location}", longitud_marco = 50)
                cond1 = check_point['category'] == category
                cond2 = check_point['location'] == location
                cond3 = check_point['category'] == ''                
                if cond1 and  cond2 or cond3:
                    check_point['category'] = category
                    check_point['location'] = location
                    driver.execute_script("document.body.style.zoom='50%'")
                    make_search(driver, category, location)
                    click_last_page_checked(driver, check_point['page'])
                    random_sleep(start = 4, end= 6)
                    data = extract(driver, check_point, directory_path, pathfile)
                    check_point['category'] = ''
                    check_point['page'] = 1
                    check_point['search_rank'] = 1
                    check_point['index'] = 0
                random_sleep(start=50, end=90)
    # except:
    #     driver.save_screenshot('issue.png')
    #     driver.quit()

if __name__ == "__main__":
    main()