import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager #auto downloads correct version of ChromeDriver
#logs whats happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def make_driver():
    '''
    Making Chrome driver for scraping
    '''
    chrome_options = Options()
    chrome_options.add_argument("--headless") #makes it not visible
    chrome_options.add_argument("--disable-gpu") #prevents logging GPU crashes with docker containers
    chrome_options.add_argument("--no-sandbox") #Overcomes permission issues
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-dev-shm-usage") #Prevents chrashes on systems with limited shared memory
    #Windows 11 user agent vvv
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.160 Safari/537.36")

    service = Service(ChromeDriverManager().install()) #works across diff os, simplifies maintenence & deployment
    driver = webdriver.Chrome(service=service, options=chrome_options)

    #timeout
    driver.set_page_load_timeout(30)
    return driver

def find_jobs(title, lo, websites=None):
    """
    :param title: Type of Job (software dev, data analyst, etc...)
    :param lo: Location to search in
    :param site: lIst of sites to search, default=all
    :return: job information
    """
    if websites is None:
        websites = ["github", "indeed", "linkedin", "adzuna"]

    #holds information of searches
    results = {
        "query":{
            "title": title,
            "location": lo
        },
        "results": [],
        "errors": []
    }

    #driver creation
    try:
        driver = make_driver()

        for web in websites:
            try:
                web_function = {
                    "github": search_github_j,
                    "indeed": search_indeed_j,
                    "linkedin": search_linkedin_j,
                    "adzuna": search_adzuna_j,
                }
                if web in web_function:
                    logger.info(f"Searching {web} for {title} in {lo}")




    return

def search_github_j():
    return
def search_indeed_j():
    return
def search_linkedin_j():
    return
def search_adzuna_j():
    return