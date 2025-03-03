import requests
import json

def find_jobs(input, location=None, limit=20):
    """

    :param input: Title or Keywords
    :param location: optional location filtering
    :param limit: limit due to using api
    :return: Search or Error info
    """
    api_url = 'https://api.apijobs.dev/v1/job/search' #for api request
    headers = {
        'apikey': '84d0e54f25b14966446b1642c36fc13ae3fdd0cfb7bd8bc20a11522b9733e5ad',
        'Content-Type': 'application/json',
    }

    payload = {
        "i": input,
        "limit": limit
    }
    if location and location.strip():
        payload["location"] = location

    try:
        response = requests.post(
            api_url,
            headers=headers,
            data = json.dumps(payload),#formats
            timeout=10
        )
        response.raise_for_status() #success check
        return{
            "success":True,
            "data": response.json(),
            "error":None
        }
    except requests.exceptions.RequestException as e: #failed request
        return{
            "success": False,
            "data": None,
            "error": f"API request failed: {str(e)}"
        }
    except json.JSONDecodeError: #bad response
        return {
            "success": False,
            "data": None,
            "error": "Invalid response from API"
        }
