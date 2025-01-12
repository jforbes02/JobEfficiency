import requests

def find_jobs(title, location):
    base_url = "https://jobs.github.com/positions.json"
    response = requests.get(base_url)

    filtered_jobs = [
        job for job in jobdb
        if location.lower() in job["locatoin"].lower() and title.lower() in job["title"]
    ]
    return response.json()