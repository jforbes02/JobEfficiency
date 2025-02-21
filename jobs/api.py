import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
url = "https://www.github.careers/careers-home/jobs"

def find_jobs(title, location):
    base_url = "https://www.github.careers/careers-home/jobs.json"
    response = requests.get(base_url)

    #filtered_jobs = [
        #job for job in jobdb
        #if location.lower() in job["locatoin"].lower() and title.lower() in job["title"]
    #]
    return response.json()



#Selenium (JavaScript)
#driver = webdriver.Chrome()
#driver.get(url)
#job_titles = driver.find_elements(By.CLASS_NAME, "content_type")
#HTML only pages
#result = requests.get(url)

#doc = BeautifulSoup(result.text, "html.parser")
#job_name = doc.find_all(By.CLASS_NAME, class_='content_type')
#parent = job_name[0].parent
#print(job_titles.text)
#driver.quit()