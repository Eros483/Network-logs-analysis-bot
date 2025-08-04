import requests

def check_api_health(url, path):
    """Check if the backend API is running"""
    try:
        response = requests.get(f"{url}{path}")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False