import requests

def find_jobs(query, location):
    base_url = "https://jobs.github.com/positions.json"
    response = requests.get(base_url)

    return response.json()