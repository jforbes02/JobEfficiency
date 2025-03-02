import logging
import time
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager #auto downloads correct version of ChromeDriver
#logs whats happening
from selenium.webdriver.support import expected_conditions

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
    :param websites: list of sites to search, default=all
    :return: job information
    """
    if websites is None:
        websites = ["indeed", "linkedin", "adzuna"]

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
                    "indeed": search_indeed_j,
                    "linkedin": search_linkedin_j,
                    "adzuna": search_adzuna_j,
                }
                if web in web_function:
                    logger.info(f"Searching {web} for {title} in {lo}")
                    web_results = web_function[web](driver, title, lo)

                    for job in web_results:
                        job["source"] = web

                    results["results"].extend(web_results)
                else:
                    results["errors"].append(f"Search Provider '{web}' not implemented")
            except Exception as e:
                e_message = f"Error searching {web}: {str(e)}"
                logger.error(e_message)
                results["errors"].append(e_message)
    except Exception as e:
        e_message = f"Driver intialization error: {str(e)}"
        logger.error(e_message)
        results["errors"].append(e_message)
    finally:
        #closes driver
        if 'driver' in locals():
            driver.quit()
    results["Total_Results"] = len(results["results"])
    results["Total_errors"] = len(results["errors"])

    return results


def search_indeed_j(driver, title, location):
    """
    Scrape job listings from Indeed

    :param driver: Selenium WebDriver instance
    :param title: Job title to search for
    :param location: Location to search in
    :return: List of job dictionaries
    """
    jobs = []

    try:
        # Format search URL - indeed uses q= for search term and l= for location
        search_url = f"https://www.indeed.com/jobs?q={title}&l={location}"
        logger.info(f"Accessing: {search_url}")

        driver.get(search_url)

        # Wait for job cards to load - the main container for job listings
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "job_seen_beacon"))
        )

        # Find all job cards
        job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")
        logger.info(f"Found {len(job_cards)} job cards on Indeed")

        for card in job_cards:
            try:
                # Extract job details - Indeed has specific class names for each element
                job_title = card.find_element(By.CLASS_NAME, "jobTitle").text
                company = card.find_element(By.CLASS_NAME, "companyName").text
                job_location = card.find_element(By.CLASS_NAME, "companyLocation").text

                # Get job URL (need to click to get actual URL)
                job_link = card.find_element(By.TAG_NAME, "a")
                job_url = job_link.get_attribute("href")

                # Try to get salary if available - salaries are optional on Indeed
                try:
                    salary = card.find_element(By.CLASS_NAME, "salary-snippet").text
                except NoSuchElementException:
                    salary = None

                # Create job dictionary with all the extracted information
                job = {
                    "title": job_title,
                    "company": company,
                    "location": job_location,
                    "url": job_url,
                    "salary": salary,
                    "date_posted": None  # Would need additional processing
                }

                jobs.append(job)
                logger.debug(f"Extracted job: {job_title} at {company}")
            except NoSuchElementException as e:
                logger.warning(f"Could not extract Indeed job details: {str(e)}")

    except Exception as e:
        logger.error(f"Error in Indeed search: {str(e)}")

    return jobs


def search_linkedin_j(driver, title, location):
    """
    Scrape job listings from LinkedIn

    :param driver: Selenium WebDriver instance
    :param title: Job title to search for
    :param location: Location to search in
    :return: List of job dictionaries
    """
    jobs = []

    try:
        # Format search URL - LinkedIn uses keywords= for job title and location= for location
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={title}&location={location}"
        logger.info(f"Accessing: {search_url}")

        driver.get(search_url)

        # Wait for job cards to load
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "base-card"))
        )

        # LinkedIn loads jobs dynamically as you scroll, so scroll down to load more results
        # This is crucial for getting more than just the initial few results
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Allow time for new content to load

        # Find all job cards
        job_cards = driver.find_elements(By.CLASS_NAME, "base-card")
        logger.info(f"Found {len(job_cards)} job cards on LinkedIn")

        for card in job_cards:
            try:
                # Extract job details from LinkedIn's card structure
                job_title = card.find_element(By.CLASS_NAME, "base-search-card__title").text
                company = card.find_element(By.CLASS_NAME, "base-search-card__subtitle").text
                job_location = card.find_element(By.CLASS_NAME, "job-search-card__location").text
                job_url = card.find_element(By.CLASS_NAME, "base-card__full-link").get_attribute("href")

                # Try to get posted date if available
                try:
                    date_posted = card.find_element(By.CLASS_NAME, "job-search-card__listdate").text
                except NoSuchElementException:
                    date_posted = None

                # Create job dictionary
                job = {
                    "title": job_title,
                    "company": company,
                    "location": job_location,
                    "url": job_url,
                    "date_posted": date_posted
                }

                jobs.append(job)
                logger.debug(f"Extracted LinkedIn job: {job_title} at {company}")
            except NoSuchElementException as e:
                logger.warning(f"Could not extract LinkedIn job details: {str(e)}")

    except Exception as e:
        logger.error(f"Error in LinkedIn search: {str(e)}")

    return jobs


def search_adzuna_j(driver, title, location):
    """
    Scrape job listings from Adzuna

    :param driver: Selenium WebDriver instance
    :param title: Job title to search for
    :param location: Location to search in
    :return: List of job dictionaries
    """
    jobs = []

    try:
        # Format search URL - Adzuna uses q= for query and loc= for location
        search_url = f"https://www.adzuna.com/search?q={title}&loc={location}"
        logger.info(f"Accessing: {search_url}")

        driver.get(search_url)

        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "article.w-full"))
        )

        job_cards = driver.find_elements(By.CSS_SELECTOR, "article.w-full")
        logger.info(f"Found {len(job_cards)} job cards on Adzuna")

        for card in job_cards:
            try:
                # Extract job details using Adzuna's structure
                # Adzuna uses h2 for job titles
                job_title = card.find_element(By.CSS_SELECTOR, "h2").text

                # Company name is in a span with text-muted class
                company = card.find_element(By.CSS_SELECTOR, "span.text-muted").text

                # Location is in a separate div element
                job_location = card.find_element(By.CSS_SELECTOR, "div.location-text").text

                # The URL is in the parent anchor tag
                job_url = card.find_element(By.TAG_NAME, "a").get_attribute("href")

                # Try to get salary if available
                try:
                    salary = card.find_element(By.CSS_SELECTOR, "div.salary-text").text
                except NoSuchElementException:
                    salary = None

                # Create job dictionary
                job = {
                    "title": job_title,
                    "company": company,
                    "location": job_location,
                    "url": job_url,
                    "salary": salary,
                    "date_posted": None  # Adzuna doesn't always show posting dates
                }

                jobs.append(job)
                logger.debug(f"Extracted Adzuna job: {job_title} at {company}")
            except NoSuchElementException as e:
                logger.warning(f"Could not extract Adzuna job details: {str(e)}")

    except Exception as e:
        logger.error(f"Error in Adzuna search: {str(e)}")

    return jobs